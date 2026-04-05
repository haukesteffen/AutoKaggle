import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from harness import analysis_runner


class AnalysisRunnerTests(unittest.TestCase):
    def test_inactive_task_exits_without_running(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            task_file = root / "state/analyst-task.md"
            task_file.parent.mkdir(parents=True)
            task_file.write_text("# Active Analyst Task\nstatus: none\n")

            stdout = io.StringIO()
            with mock.patch.object(analysis_runner, "REPO_ROOT", root), mock.patch.object(
                sys,
                "argv",
                ["analysis_runner"],
            ), mock.patch("harness.analysis_runner.subprocess.run") as run, mock.patch(
                "sys.stdout",
                stdout,
            ):
                analysis_runner.main()

            run.assert_not_called()
            self.assertEqual(stdout.getvalue().strip(), "status: no_active_hypothesis")
            self.assertFalse((root / "artifacts").exists())

    def test_success_writes_stdout_artifact_without_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            task_file = root / "state/analyst-task.md"
            task_file.parent.mkdir(parents=True)
            task_file.write_text(
                "# Active Analyst Task\n"
                "status: active\n"
                "id: A-001\n"
                "at: 2026-03-29T10:45Z\n"
                "q: Does feature hashing help?\n"
                "reference: experiment=abc123, knowledge=AK-001\n"
            )

            completed = subprocess.CompletedProcess(
                args=["python", "analysis.py"],
                returncode=0,
                stdout="Finding: yes\n",
                stderr="debug noise\n",
            )

            stdout = io.StringIO()
            with mock.patch.object(analysis_runner, "REPO_ROOT", root), mock.patch.object(
                sys,
                "argv",
                ["analysis_runner"],
            ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed), mock.patch(
                "sys.stdout",
                stdout,
            ):
                analysis_runner.main()

            stdout_file = root / "artifacts/A-001/analysis-stdout.txt"
            self.assertEqual(stdout_file.read_text(), "Finding: yes\n")
            self.assertFalse((root / "artifacts/A-001/analysis-run.log").exists())
            self.assertEqual(
                stdout.getvalue().strip(),
                "status: success; stdout written to artifacts/A-001/analysis-stdout.txt",
            )

    def test_failure_writes_error_log_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            task_file = root / "state/analyst-task.md"
            task_file.parent.mkdir(parents=True)
            task_file.write_text(
                "# Active Analyst Task\n"
                "status: active\n"
                "id: A-001\n"
                "at: 2026-03-29T10:45Z\n"
                "q: Does feature hashing help?\n"
            )

            completed = subprocess.CompletedProcess(
                args=["python", "analysis.py"],
                returncode=2,
                stdout="partial output\n",
                stderr="Traceback: boom\n",
            )

            stderr = io.StringIO()
            with mock.patch.object(analysis_runner, "REPO_ROOT", root), mock.patch.object(
                sys,
                "argv",
                ["analysis_runner"],
            ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed), redirect_stderr(
                stderr
            ):
                with self.assertRaises(SystemExit) as exc:
                    analysis_runner.main()

            self.assertEqual(exc.exception.code, 2)
            self.assertFalse((root / "artifacts/A-001/analysis-stdout.txt").exists())

            errors = (root / "artifacts/A-001/analysis-run.log").read_text()
            self.assertIn("id: A-001", errors)
            self.assertIn("q: Does feature hashing help?", errors)
            self.assertIn("exit_code: 2", errors)
            self.assertIn("stdout:\npartial output", errors)
            self.assertIn("stderr:\nTraceback: boom", errors)

            stderr_text = stderr.getvalue()
            self.assertIn("details written to", stderr_text)
            self.assertIn("[analysis stdout]", stderr_text)
            self.assertIn("[analysis stderr]", stderr_text)

    def test_success_normalizes_default_repo_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as otherdir:
            root = Path(tmpdir).resolve()
            task_file = root / "state/analyst-task.md"
            task_file.parent.mkdir(parents=True)
            task_file.write_text(
                "# Active Analyst Task\n"
                "status: active\n"
                "id: A-001\n"
                "q: Does feature hashing help?\n"
            )

            completed = subprocess.CompletedProcess(
                args=["python", "analysis.py"],
                returncode=0,
                stdout="Finding: yes\n",
                stderr="",
            )

            original_cwd = os.getcwd()
            os.chdir(otherdir)
            try:
                with mock.patch.object(
                    analysis_runner,
                    "REPO_ROOT",
                    root,
                ), mock.patch.object(
                    sys,
                    "argv",
                    ["analysis_runner"],
                ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed):
                    analysis_runner.main()
            finally:
                os.chdir(original_cwd)

            stdout_file = root / "artifacts/A-001/analysis-stdout.txt"
            self.assertEqual(stdout_file.read_text(), "Finding: yes\n")

    def test_parse_args_has_no_findings_file_option(self) -> None:
        with mock.patch.object(sys, "argv", ["analysis_runner"]):
            args = analysis_runner._parse_args()

        self.assertFalse(hasattr(args, "findings_file"))

    def test_failure_normalizes_relative_error_log_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as otherdir:
            root = Path(tmpdir).resolve()
            task_file = root / "state/analyst-task.md"
            task_file.parent.mkdir(parents=True)
            task_file.write_text(
                "# Active Analyst Task\n"
                "status: active\n"
                "id: A-001\n"
                "q: Does feature hashing help?\n"
            )

            completed = subprocess.CompletedProcess(
                args=["python", "analysis.py"],
                returncode=2,
                stdout="partial output\n",
                stderr="Traceback: boom\n",
            )

            original_cwd = os.getcwd()
            os.chdir(otherdir)
            try:
                with mock.patch.object(
                    analysis_runner,
                    "REPO_ROOT",
                    root,
                ), mock.patch.object(
                    sys,
                    "argv",
                    [
                        "analysis_runner",
                        "--errors-file",
                        "reports/analysis-run.log",
                    ],
                ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed):
                    with self.assertRaises(SystemExit):
                        analysis_runner.main()
            finally:
                os.chdir(original_cwd)

            errors = (root / "reports/analysis-run.log").read_text()
            self.assertIn("id: A-001", errors)


if __name__ == "__main__":
    unittest.main()
