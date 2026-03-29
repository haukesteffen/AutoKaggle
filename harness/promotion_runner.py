from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.competitions.types.competition_api_service import ApiGetLeaderboardRequest
from kagglesdk.competitions.types.submission_status import SubmissionStatus

from agents.supervisor.submission import create_submission_csv
from harness.dataset import COMPETITION

DEFAULT_ARTIFACTS_ROOT = Path("artifacts")
DEFAULT_SUBMISSION_FILENAME = "submission.csv"
DEFAULT_POLL_INTERVAL_SECONDS = 30.0
DEFAULT_TIMEOUT_SECONDS = 30.0 * 60.0
DEFAULT_LEADERBOARD_PAGE_SIZE = 100
DEFAULT_SUBMISSIONS_PAGE_SIZE = 100
DEFAULT_KAGGLE_ATTEMPTS = 3
HASH_PATTERN = re.compile(r"[0-9a-f]{7,40}")
TRANSIENT_KAGGLE_TOKENS = (
    "429",
    "500",
    "502",
    "503",
    "504",
    "connection aborted",
    "connection reset",
    "dns",
    "gateway timeout",
    "rate limit",
    "service unavailable",
    "temporarily unavailable",
    "timed out",
    "timeout",
    "too many requests",
)
AUTH_KAGGLE_TOKENS = (
    "401",
    "403",
    "credentials",
    "forbidden",
    "kaggle.json",
    "unauthorized",
)
RATE_LIMIT_TOKENS = ("429", "rate limit", "too many requests")

T = TypeVar("T")


@dataclass
class PromotionResult:
    hash: str
    competition: str
    artifact_dir: str
    submission_file: str
    submitted_at: str | None
    cv_score: float | None
    submission_id: int | None
    kaggle_message: str | None
    terminal_status: str
    submission_status: str | None
    lb_score: float | None
    lb_rank: int | None
    polling_seconds: float
    error_category: str | None
    error_message: str | None


class PromotionFailure(RuntimeError):
    def __init__(self, result: PromotionResult, exit_code: int):
        super().__init__(result.error_message or result.error_category or result.terminal_status)
        self.result = result
        self.exit_code = exit_code


def main() -> None:
    args = _parse_args()
    try:
        result = _run_promotion(args)
    except PromotionFailure as exc:
        _emit_result(exc.result)
        raise SystemExit(exc.exit_code) from exc

    _emit_result(result)


def _run_promotion(args: argparse.Namespace) -> PromotionResult:
    artifact_dir = _normalize_repo_path(args.artifact_dir or _default_artifact_dir(args.hash))
    submission_file = _normalize_repo_path(args.submission_file or artifact_dir / DEFAULT_SUBMISSION_FILENAME)
    result = PromotionResult(
        hash=args.hash,
        competition=COMPETITION,
        artifact_dir=str(artifact_dir),
        submission_file=str(submission_file),
        submitted_at=None,
        cv_score=args.cv_score,
        submission_id=None,
        kaggle_message=None,
        terminal_status="error",
        submission_status=None,
        lb_score=None,
        lb_rank=None,
        polling_seconds=0.0,
        error_category=None,
        error_message=None,
    )

    _validate_inputs(args, artifact_dir, submission_file, result)
    _ensure_submission_file(args, artifact_dir, submission_file, result)

    api = _create_api()
    try:
        _call_with_retry(api.authenticate)
    except Exception as exc:
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category=_classify_kaggle_error(exc),
            error_message=f"failed to authenticate with Kaggle: {_exception_text(exc)}",
        )

    try:
        submit_response = _call_with_retry(
            lambda: api.competition_submit(
                str(submission_file),
                args.hash,
                COMPETITION,
                quiet=True,
            )
        )
    except Exception as exc:
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category=_classify_kaggle_error(exc),
            error_message=f"failed to submit to Kaggle: {_exception_text(exc)}",
        )

    result.submission_id = submit_response.ref or None
    result.kaggle_message = _none_if_empty(submit_response.message)
    result.submitted_at = _utc_timestamp()

    poll_start = time.perf_counter()
    deadline = time.monotonic() + args.timeout_seconds
    while True:
        try:
            submission = _call_with_retry(
                lambda: _get_submission(
                    api=api,
                    submission_id=result.submission_id,
                    hash_value=args.hash,
                    submission_file=submission_file,
                    page_size=args.submissions_page_size,
                )
            )
        except Exception as exc:
            result.polling_seconds = _elapsed_seconds(poll_start)
            _fail(
                result,
                exit_code=1,
                terminal_status="error",
                error_category=_classify_kaggle_error(exc),
                error_message=f"failed to poll Kaggle submissions: {_exception_text(exc)}",
            )

        if submission is not None:
            result.submitted_at = _format_datetime(submission.date) or result.submitted_at
            result.submission_status = _submission_status_name(submission.status)
            if submission.status == SubmissionStatus.ERROR:
                result.polling_seconds = _elapsed_seconds(poll_start)
                result.kaggle_message = _none_if_empty(submission.error_description) or result.kaggle_message
                _fail(
                    result,
                    exit_code=1,
                    terminal_status="error",
                    error_category="submission_error",
                    error_message=submission.error_description or "Kaggle marked the submission as failed",
                )
            if submission.status == SubmissionStatus.COMPLETE:
                result.polling_seconds = _elapsed_seconds(poll_start)
                result.lb_score = _submission_score(submission.public_score, submission.private_score)
                result.lb_rank = _safe_lookup_leaderboard_rank(
                    api=api,
                    team_name=submission.team_name,
                    score=result.lb_score,
                    page_size=args.leaderboard_page_size,
                )
                result.terminal_status = "scored"
                return result

        if time.monotonic() >= deadline:
            result.polling_seconds = _elapsed_seconds(poll_start)
            _fail(
                result,
                exit_code=124,
                terminal_status="timeout",
                error_category="poll_timeout",
                error_message=f"submission was not scored within {args.timeout_seconds:.0f} seconds",
            )

        time.sleep(args.poll_interval_seconds)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--submission-file", type=Path)
    parser.add_argument("--cv-score", type=float)
    parser.add_argument("--force-regenerate-submission-file", action="store_true")
    parser.add_argument("--poll-interval-seconds", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS)
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--leaderboard-page-size", type=int, default=DEFAULT_LEADERBOARD_PAGE_SIZE)
    parser.add_argument("--submissions-page-size", type=int, default=DEFAULT_SUBMISSIONS_PAGE_SIZE)
    return parser.parse_args()


def _validate_inputs(
    args: argparse.Namespace,
    artifact_dir: Path,
    submission_file: Path,
    result: PromotionResult,
) -> None:
    if HASH_PATTERN.fullmatch(args.hash) is None:
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message=f"hash must look like a git commit id, got {args.hash!r}",
        )
    if artifact_dir.name != args.hash:
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message=f"artifact directory must end with the hash {args.hash!r}",
        )
    if not artifact_dir.is_dir():
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message=f"artifact directory does not exist: {artifact_dir}",
        )
    if not (artifact_dir / "test-preds.npy").is_file():
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message=f"missing required artifact: {artifact_dir / 'test-preds.npy'}",
        )
    if submission_file.exists() and not submission_file.is_file():
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message=f"submission path exists but is not a file: {submission_file}",
        )
    if args.poll_interval_seconds <= 0:
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message="poll interval must be greater than zero",
        )
    if args.timeout_seconds < 0:
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message="timeout must be zero or greater",
        )
    if args.leaderboard_page_size <= 0 or args.submissions_page_size <= 0:
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="validation_error",
            error_message="page sizes must be greater than zero",
        )


def _ensure_submission_file(
    args: argparse.Namespace,
    artifact_dir: Path,
    submission_file: Path,
    result: PromotionResult,
) -> None:
    if args.force_regenerate_submission_file or not submission_file.exists():
        try:
            create_submission_csv(artifact_dir, submission_file)
        except Exception as exc:
            _fail(
                result,
                exit_code=1,
                terminal_status="error",
                error_category="submission_file_generation_error",
                error_message=f"failed to generate submission.csv: {_exception_text(exc)}",
            )

    if not submission_file.is_file():
        _fail(
            result,
            exit_code=1,
            terminal_status="error",
            error_category="submission_file_generation_error",
            error_message=f"submission file was not created: {submission_file}",
        )


def _create_api() -> KaggleApi:
    return KaggleApi()


def _call_with_retry(call: Callable[[], T], attempts: int = DEFAULT_KAGGLE_ATTEMPTS) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return call()
        except Exception as exc:
            last_exc = exc
            if attempt == attempts or not _is_transient_kaggle_error(exc):
                raise
            time.sleep(min(5.0 * attempt, 30.0))

    assert last_exc is not None
    raise last_exc


def _get_submission(
    api: KaggleApi,
    submission_id: int | None,
    hash_value: str,
    submission_file: Path,
    page_size: int,
):
    submissions = api.competition_submissions(COMPETITION, page_size=page_size) or []
    target_file_name = submission_file.name

    if submission_id is not None:
        for submission in submissions:
            if submission is not None and submission.ref == submission_id:
                return submission

    for submission in submissions:
        if submission is None:
            continue
        if submission.description.strip() != hash_value:
            continue
        if submission.file_name and submission.file_name != target_file_name:
            continue
        return submission

    return None


def _safe_lookup_leaderboard_rank(
    api: KaggleApi,
    team_name: str,
    score: float | None,
    page_size: int,
) -> int | None:
    if not team_name or score is None:
        return None

    try:
        return _call_with_retry(lambda: _lookup_leaderboard_rank(api, team_name, score, page_size))
    except Exception:
        return None


def _lookup_leaderboard_rank(
    api: KaggleApi,
    team_name: str,
    score: float,
    page_size: int,
) -> int | None:
    next_page_token = ""
    rank = 1
    while True:
        entries, next_page_token = _fetch_leaderboard_page(
            api=api,
            page_size=page_size,
            page_token=next_page_token,
        )
        if not entries:
            return None

        for entry in entries:
            if entry is None:
                continue
            if entry.team_name == team_name and _scores_match(entry.score, score):
                return rank
            rank += 1

        if not next_page_token:
            return None


def _fetch_leaderboard_page(
    api: KaggleApi,
    page_size: int,
    page_token: str,
) -> tuple[list[Any], str]:
    with api.build_kaggle_client() as kaggle:
        request = ApiGetLeaderboardRequest()
        request.competition_name = COMPETITION
        request.page_size = page_size
        request.page_token = page_token
        response = kaggle.competitions.competition_api_client.get_leaderboard(request)

    return list(response.submissions or []), response.next_page_token or ""


def _submission_score(public_score: str, private_score: str) -> float | None:
    parsed_public = _parse_score(public_score)
    if parsed_public is not None:
        return parsed_public
    return _parse_score(private_score)


def _parse_score(value: str) -> float | None:
    stripped = value.strip()
    if not stripped:
        return None
    return float(stripped)


def _scores_match(score_text: str, expected_score: float) -> bool:
    parsed_score = _parse_score(score_text)
    if parsed_score is None:
        return False
    return abs(parsed_score - expected_score) < 1e-12


def _classify_kaggle_error(exc: Exception) -> str:
    message = _exception_text(exc).lower()
    if any(token in message for token in AUTH_KAGGLE_TOKENS):
        return "kaggle_auth_error"
    if any(token in message for token in RATE_LIMIT_TOKENS):
        return "kaggle_rate_limit"
    return "kaggle_api_error"


def _is_transient_kaggle_error(exc: Exception) -> bool:
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    message = _exception_text(exc).lower()
    return any(token in message for token in TRANSIENT_KAGGLE_TOKENS)


def _default_artifact_dir(hash_value: str) -> Path:
    return DEFAULT_ARTIFACTS_ROOT / "experiments" / hash_value


def _normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def _submission_status_name(status: Any) -> str | None:
    if status is None:
        return None
    return getattr(status, "name", str(status)).lower()


def _none_if_empty(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _elapsed_seconds(start: float) -> float:
    return round(time.perf_counter() - start, 3)


def _exception_text(exc: Exception) -> str:
    parts = [str(exc)]
    for attr in ("status", "status_code", "reason", "body"):
        value = getattr(exc, attr, None)
        if value:
            parts.append(str(value))
    return " | ".join(part for part in parts if part)


def _emit_result(result: PromotionResult) -> None:
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


def _fail(
    result: PromotionResult,
    *,
    exit_code: int,
    terminal_status: str,
    error_category: str,
    error_message: str,
) -> None:
    result.terminal_status = terminal_status
    result.error_category = error_category
    result.error_message = error_message
    raise PromotionFailure(result, exit_code)


if __name__ == "__main__":
    main()
