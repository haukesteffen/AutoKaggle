import io
import json
import sys
import unittest
from contextlib import ExitStack, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from kagglesdk.competitions.types.submission_status import SubmissionStatus

from harness import promotion_runner


class FakeSubmitResponse:
    def __init__(self, ref: int, message: str):
        self.ref = ref
        self.message = message


class FakeSubmission:
    def __init__(
        self,
        *,
        ref: int,
        description: str,
        file_name: str,
        status: SubmissionStatus,
        public_score: str = "",
        private_score: str = "",
        error_description: str = "",
        team_name: str = "",
        date: datetime | None = None,
    ):
        self.ref = ref
        self.description = description
        self.file_name = file_name
        self.status = status
        self.public_score = public_score
        self.private_score = private_score
        self.error_description = error_description
        self.team_name = team_name
        self.date = date


class FakeApi:
    def __init__(self, submissions: list[list[FakeSubmission]], submit_ref: int = 42, submit_message: str = "accepted"):
        self._submissions = submissions
        self._index = 0
        self.submit_ref = submit_ref
        self.submit_message = submit_message
        self.submit_calls: list[tuple[str, str, str, bool]] = []
        self.authenticate_calls = 0

    def authenticate(self) -> None:
        self.authenticate_calls += 1

    def competition_submit(self, file_name: str, message: str, competition: str, quiet: bool = False) -> FakeSubmitResponse:
        self.submit_calls.append((file_name, message, competition, quiet))
        return FakeSubmitResponse(self.submit_ref, self.submit_message)

    def competition_submissions(self, competition: str, page_size: int = 20):
        if self._index < len(self._submissions):
            current = self._submissions[self._index]
            self._index += 1
            return current
        return self._submissions[-1]


class PromotionRunnerTests(unittest.TestCase):
    def test_main_emits_json_for_scored_submission(self) -> None:
        hash_value = "abcdef1"
        with TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / hash_value
            artifact_dir.mkdir()
            (artifact_dir / "test-preds.npy").write_bytes(b"ready")

            pending = FakeSubmission(
                ref=42,
                description=hash_value,
                file_name="submission.csv",
                status=SubmissionStatus.PENDING,
            )
            complete = FakeSubmission(
                ref=42,
                description=hash_value,
                file_name="submission.csv",
                status=SubmissionStatus.COMPLETE,
                public_score="0.91821",
                team_name="team-a",
                date=datetime(2026, 3, 28, 12, 34, 56, tzinfo=timezone.utc),
            )
            api = FakeApi([[pending], [complete]])

            def fake_create_submission_csv(_artifact_dir: Path, output: Path) -> Path:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text("id,Churn\n1,0.1\n")
                return output

            exit_code, payload = self._run_main(
                [
                    "promotion_runner",
                    "--hash",
                    hash_value,
                    "--tag",
                    "mar28",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--cv-score",
                    "0.916481",
                    "--poll-interval-seconds",
                    "0.01",
                ],
                create_api=api,
                create_submission_csv=fake_create_submission_csv,
                rank=142,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["hash"], hash_value)
        self.assertEqual(payload["terminal_status"], "scored")
        self.assertEqual(payload["submission_status"], "complete")
        self.assertEqual(payload["submission_id"], 42)
        self.assertEqual(payload["lb_rank"], 142)
        self.assertAlmostEqual(payload["lb_score"], 0.91821)
        self.assertEqual(payload["submitted_at"], "2026-03-28T12:34Z")
        self.assertEqual(payload["cv_score"], 0.916481)
        self.assertIsNone(payload["error_category"])
        self.assertEqual(len(api.submit_calls), 1)
        self.assertEqual(api.submit_calls[0][1], hash_value)
        self.assertTrue(payload["submission_file"].endswith("/submission.csv"))

    def test_main_times_out_with_machine_readable_error(self) -> None:
        hash_value = "abcdef1"
        with TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / hash_value
            artifact_dir.mkdir()
            (artifact_dir / "test-preds.npy").write_bytes(b"ready")

            pending = FakeSubmission(
                ref=42,
                description=hash_value,
                file_name="submission.csv",
                status=SubmissionStatus.PENDING,
            )
            api = FakeApi([[pending]])

            exit_code, payload = self._run_main(
                [
                    "promotion_runner",
                    "--hash",
                    hash_value,
                    "--tag",
                    "mar28",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--timeout-seconds",
                    "0",
                    "--poll-interval-seconds",
                    "0.01",
                ],
                create_api=api,
                create_submission_csv=self._fake_create_submission_csv,
            )

        self.assertEqual(exit_code, 124)
        self.assertEqual(payload["terminal_status"], "timeout")
        self.assertEqual(payload["submission_status"], "pending")
        self.assertEqual(payload["error_category"], "poll_timeout")
        self.assertIn("not scored", payload["error_message"])

    def test_main_reports_validation_errors_as_json(self) -> None:
        hash_value = "abcdef1"
        with TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / hash_value
            artifact_dir.mkdir()

            exit_code, payload = self._run_main(
                [
                    "promotion_runner",
                    "--hash",
                    hash_value,
                    "--tag",
                    "mar28",
                    "--artifact-dir",
                    str(artifact_dir),
                ],
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["terminal_status"], "error")
        self.assertEqual(payload["error_category"], "validation_error")
        self.assertIn("test-preds.npy", payload["error_message"])

    def test_lookup_leaderboard_rank_walks_pages(self) -> None:
        entry1 = mock.Mock(team_name="team-a", score="0.92000")
        entry2 = mock.Mock(team_name="team-b", score="0.91900")
        entry3 = mock.Mock(team_name="team-c", score="0.91821")

        with mock.patch(
            "harness.promotion_runner._fetch_leaderboard_page",
            side_effect=[
                ([entry1, entry2], "next-token"),
                ([entry3], ""),
            ],
        ):
            rank = promotion_runner._lookup_leaderboard_rank(
                api=mock.sentinel.api,
                team_name="team-c",
                score=0.91821,
                page_size=2,
            )

        self.assertEqual(rank, 3)

    def _run_main(
        self,
        argv: list[str],
        *,
        create_api: FakeApi | None = None,
        create_submission_csv=None,
        rank: int | None = None,
    ) -> tuple[int, dict]:
        stdout = io.StringIO()
        patches = [
            mock.patch.object(sys, "argv", argv),
            mock.patch("harness.promotion_runner.time.sleep", return_value=None),
        ]

        if create_api is not None:
            patches.append(mock.patch("harness.promotion_runner._create_api", return_value=create_api))
        if create_submission_csv is not None:
            patches.append(
                mock.patch("harness.promotion_runner.create_submission_csv", side_effect=create_submission_csv)
            )
        if rank is not None:
            patches.append(mock.patch("harness.promotion_runner._safe_lookup_leaderboard_rank", return_value=rank))

        with redirect_stdout(stdout), ExitStack() as stack:
            for patcher in patches:
                stack.enter_context(patcher)
            try:
                promotion_runner.main()
            except SystemExit as exc:
                return int(exc.code), json.loads(stdout.getvalue())

        return 0, json.loads(stdout.getvalue())

    def _fake_create_submission_csv(self, _artifact_dir: Path, output: Path) -> Path:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("id,Churn\n1,0.1\n")
        return output


if __name__ == "__main__":
    unittest.main()
