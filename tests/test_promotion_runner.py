import sys
import unittest
from pathlib import Path
from unittest import mock

from harness import promotion_runner


class PromotionRunnerTests(unittest.TestCase):
    def test_default_submission_file_is_supervisor_owned(self) -> None:
        self.assertEqual(promotion_runner.DEFAULT_SUBMISSION_FILE, Path("agents/supervisor/submission.csv"))

    def test_main_submits_with_resolved_submission_path(self) -> None:
        submission_file = Path("agents/supervisor/submission.csv")
        expected_path = (promotion_runner.REPO_ROOT / submission_file).resolve()

        with mock.patch.object(
            sys,
            "argv",
            [
                "promotion_runner",
                "--hash",
                "abc123",
                "--tag",
                "mar28",
                "--submission-file",
                str(submission_file),
            ],
        ), mock.patch("harness.promotion_runner.subprocess.run") as run_mock:
            promotion_runner.main()

        run_mock.assert_called_once_with(
            [
                "uv",
                "run",
                "kaggle",
                "competitions",
                "submit",
                "-c",
                promotion_runner.COMPETITION,
                "-f",
                str(expected_path),
                "-m",
                "abc123",
            ],
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
