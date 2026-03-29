import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from harness import scientist_runner


class ScientistRunnerTests(unittest.TestCase):
    def test_inactive_task_exits_without_running(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_file = root / "scientist-task.md"
            results_file = root / "scientist-results.md"
            experiment_file = root / "experiment.py"
            experiment_file.write_text("EXPERIMENT_NAME = 'demo'\n")
            task_file.write_text("# Active Scientist Task\nstatus: none\n")

            with mock.patch.object(
                sys,
                "argv",
                [
                    "scientist_runner",
                    "--task-file",
                    str(task_file),
                    "--results-file",
                    str(results_file),
                    "--experiment-path",
                    str(experiment_file),
                ],
            ), mock.patch("harness.scientist_runner.subprocess.run") as run:
                scientist_runner.main()

            run.assert_not_called()
            self.assertFalse(results_file.exists())

    def test_success_kept_appends_results_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_file = root / "scientist-task.md"
            results_file = root / "scientist-results.md"
            experiment_file = root / "experiment.py"
            experiment_file.write_text("EXPERIMENT_NAME = 'demo'\n")
            task_file.write_text(
                "# Active Scientist Task\n"
                "status: active\n"
                "id: S-001\n"
                "at: 2026-03-29T12:00Z\n"
                "goal: Test demo experiment.\n"
                "keep_if: mean_cv_roc_auc > 0.910000\n"
                "reference: result=S-000, knowledge=SK-001\n"
            )

            completed = subprocess.CompletedProcess(
                args=["python", "-m", "harness.experiment_runner"],
                returncode=0,
                stdout=(
                    "---\n"
                    "experiment_name:   demo\n"
                    "status:            ok\n"
                    "mean_cv_roc_auc:   0.916540\n"
                    "std_cv_roc_auc:    0.001083\n"
                ),
                stderr="",
            )

            with mock.patch.object(
                sys,
                "argv",
                [
                    "scientist_runner",
                    "--task-file",
                    str(task_file),
                    "--results-file",
                    str(results_file),
                    "--experiment-path",
                    str(experiment_file),
                ],
            ), mock.patch("harness.scientist_runner.subprocess.run", return_value=completed):
                scientist_runner.main()

            results = results_file.read_text()
            code = scientist_runner._code_fingerprint(experiment_file)
            self.assertIn("| S-001 |", results)
            self.assertIn(f"| {code} | kept | 0.916540 | 0.001083 | +0.000000 | Test demo experiment. |", results)

    def test_success_discarded_uses_previous_best_for_delta(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_file = root / "scientist-task.md"
            results_file = root / "scientist-results.md"
            experiment_file = root / "experiment.py"
            experiment_file.write_text("EXPERIMENT_NAME = 'demo'\n")
            results_file.write_text(
                "# Scientist Results\n\n"
                "| id | code | status | score | std | delta_best | desc |\n"
                "|----|------|--------|-------|-----|------------|------|\n"
                "| S-000 | abc1234 | kept | 0.916540 | 0.001083 | +0.000000 | prior best |\n"
            )
            task_file.write_text(
                "# Active Scientist Task\n"
                "status: active\n"
                "id: S-002\n"
                "goal: Test weaker experiment.\n"
                "keep_if: mean_cv_roc_auc > 0.920000\n"
            )

            completed = subprocess.CompletedProcess(
                args=["python", "-m", "harness.experiment_runner"],
                returncode=0,
                stdout=(
                    "---\n"
                    "experiment_name:   weaker\n"
                    "status:            ok\n"
                    "mean_cv_roc_auc:   0.916228\n"
                    "std_cv_roc_auc:    0.001041\n"
                ),
                stderr="",
            )

            with mock.patch.object(
                sys,
                "argv",
                [
                    "scientist_runner",
                    "--task-file",
                    str(task_file),
                    "--results-file",
                    str(results_file),
                    "--experiment-path",
                    str(experiment_file),
                ],
            ), mock.patch("harness.scientist_runner.subprocess.run", return_value=completed):
                scientist_runner.main()

            results = results_file.read_text()
            self.assertIn("| S-002 |", results)
            self.assertIn("| discarded | 0.916228 | 0.001041 | -0.000312 | Test weaker experiment. |", results)

    def test_invalid_writes_error_log_without_results_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task_file = root / "scientist-task.md"
            results_file = root / "scientist-results.md"
            experiment_file = root / "experiment.py"
            experiment_file.write_text("EXPERIMENT_NAME = 'demo'\n")
            results_file.write_text(
                "# Scientist Results\n\n"
                "| id | code | status | score | std | delta_best | desc |\n"
                "|----|------|--------|-------|-----|------------|------|\n"
            )
            task_file.write_text(
                "# Active Scientist Task\n"
                "status: active\n"
                "id: S-003\n"
                "goal: Test broken experiment.\n"
            )

            completed = subprocess.CompletedProcess(
                args=["python", "-m", "harness.experiment_runner"],
                returncode=scientist_runner.INVALID_EXIT_CODE,
                stdout="---\nstatus:            invalid\n",
                stderr="Traceback: boom\n",
            )

            stderr = io.StringIO()
            with mock.patch.object(
                sys,
                "argv",
                [
                    "scientist_runner",
                    "--task-file",
                    str(task_file),
                    "--results-file",
                    str(results_file),
                    "--experiment-path",
                    str(experiment_file),
                ],
            ), mock.patch("harness.scientist_runner.subprocess.run", return_value=completed), redirect_stderr(
                stderr
            ):
                with self.assertRaises(SystemExit) as exc:
                    scientist_runner.main()

            self.assertEqual(exc.exception.code, scientist_runner.INVALID_EXIT_CODE)
            results = results_file.read_text()
            self.assertNotIn("S-003", results)
            errors = (root / "scientist-errors.md").read_text()
            self.assertIn("## S-003", errors)
            self.assertIn("goal: Test broken experiment.", errors)
            self.assertIn("stderr:\nTraceback: boom", errors)
            self.assertIn("details written to", stderr.getvalue())

    def test_extract_task_metadata_supports_reference(self) -> None:
        task = scientist_runner._extract_task_metadata(
            "# Active Scientist Task\n"
            "status: active\n"
            "id: S-004\n"
            "goal: Test parse.\n"
            "keep_if: mean_cv_roc_auc >= 0.916540\n"
            "reference: result=S-003, knowledge=SK-009\n"
        )
        self.assertEqual(task.task_id, "S-004")
        self.assertEqual(task.status, "active")
        self.assertEqual(task.goal, "Test parse.")
        self.assertEqual(task.keep_if, "mean_cv_roc_auc >= 0.916540")
        self.assertEqual(task.reference, "result=S-003, knowledge=SK-009")

    def test_missing_keep_if_defaults_to_unconditional_keep(self) -> None:
        task = scientist_runner._extract_task_metadata(
            "# Active Scientist Task\n"
            "status: active\n"
            "id: S-005\n"
            "goal: Test default keep rule.\n"
        )
        self.assertEqual(task.keep_if, "mean_cv_roc_auc > -inf")
        self.assertTrue(scientist_runner._evaluate_keep_if(task.keep_if, 0.0))


if __name__ == "__main__":
    unittest.main()
