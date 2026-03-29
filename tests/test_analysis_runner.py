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
    def test_inactive_hypothesis_exits_without_running(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            hypothesis_file = root / "analyst-hypothesis.md"
            findings_file = root / "analyst-findings.md"
            hypothesis_file.write_text("# Active Analyst Hypothesis\nstatus: none\n")

            stdout = io.StringIO()
            with mock.patch.object(
                sys,
                "argv",
                [
                    "analysis_runner",
                    "--hypothesis-file",
                    str(hypothesis_file),
                    "--findings-file",
                    str(findings_file),
                ],
            ), mock.patch("harness.analysis_runner.subprocess.run") as run, mock.patch(
                "sys.stdout",
                stdout,
            ):
                analysis_runner.main()

            run.assert_not_called()
            self.assertEqual(stdout.getvalue().strip(), "status: no_active_hypothesis")
            self.assertFalse(findings_file.exists())
            self.assertFalse((root / "analysis-errors.md").exists())

    def test_success_appends_findings_without_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            hypothesis_file = root / "analyst-hypothesis.md"
            findings_file = root / "analyst-findings.md"
            hypothesis_file.write_text(
                "# Active Analyst Hypothesis\n"
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

            with mock.patch.object(
                sys,
                "argv",
                [
                    "analysis_runner",
                    "--hypothesis-file",
                    str(hypothesis_file),
                    "--findings-file",
                    str(findings_file),
                ],
            ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed):
                analysis_runner.main()

            findings = findings_file.read_text()
            self.assertIn("## A-001", findings)
            self.assertIn("q: Does feature hashing help?", findings)
            self.assertIn("conf: *(fill in: high | medium | low)*", findings)
            self.assertIn("reference: experiment=abc123, knowledge=AK-001", findings)
            self.assertIn("evidence:\nFinding: yes", findings)
            self.assertIn("follow_up:\n- *(fill in yes/no hypothesis)*", findings)
            self.assertEqual(findings.count("- *(fill in yes/no hypothesis)*"), 3)
            self.assertNotIn("debug noise", findings)
            self.assertFalse((root / "analysis-errors.md").exists())

    def test_failure_skips_findings_and_writes_error_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            hypothesis_file = root / "analyst-hypothesis.md"
            findings_file = root / "analyst-findings.md"
            findings_file.write_text("## Existing finding\n")
            hypothesis_file.write_text(
                "# Active Analyst Hypothesis\n"
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
            with mock.patch.object(
                sys,
                "argv",
                [
                    "analysis_runner",
                    "--hypothesis-file",
                    str(hypothesis_file),
                    "--findings-file",
                    str(findings_file),
                ],
            ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed), redirect_stderr(
                stderr
            ):
                with self.assertRaises(SystemExit) as exc:
                    analysis_runner.main()

            self.assertEqual(exc.exception.code, 2)
            self.assertEqual(findings_file.read_text(), "## Existing finding\n")

            errors = (root / "analysis-errors.md").read_text()
            self.assertIn("## A-001", errors)
            self.assertIn("q: Does feature hashing help?", errors)
            self.assertIn("exit_code: `2`", errors)
            self.assertIn("stdout:\npartial output", errors)
            self.assertIn("stderr:\nTraceback: boom", errors)

            stderr_text = stderr.getvalue()
            self.assertIn("details written to", stderr_text)
            self.assertIn("[analysis stdout]", stderr_text)
            self.assertIn("[analysis stderr]", stderr_text)

    def test_extract_title_prefers_id_and_supports_legacy_formats(self) -> None:
        self.assertEqual(
            analysis_runner._extract_title(
                "# Active Analyst Hypothesis\n"
                "status: active\n"
                "id: A-001\n"
                "q: Does feature hashing help?\n"
            ),
            "A-001",
        )
        self.assertEqual(analysis_runner._extract_title("**Question:** Legacy title"), "Legacy title")

    def test_success_normalizes_relative_repo_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as otherdir:
            root = Path(tmpdir)
            hypothesis_file = root / "agents/analyst/analyst-hypothesis.md"
            findings_file = root / "agents/analyst/analyst-findings.md"
            hypothesis_file.parent.mkdir(parents=True)
            hypothesis_file.write_text(
                "# Active Analyst Hypothesis\n"
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
                    [
                        "analysis_runner",
                        "--hypothesis-file",
                        "agents/analyst/analyst-hypothesis.md",
                        "--findings-file",
                        "agents/analyst/analyst-findings.md",
                    ],
                ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed):
                    analysis_runner.main()
            finally:
                os.chdir(original_cwd)

            findings = findings_file.read_text()
            self.assertIn("## A-001", findings)

    def test_failure_normalizes_default_error_log_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as otherdir:
            root = Path(tmpdir)
            hypothesis_file = root / "agents/analyst/analyst-hypothesis.md"
            findings_file = root / "agents/analyst/analyst-findings.md"
            hypothesis_file.parent.mkdir(parents=True)
            hypothesis_file.write_text(
                "# Active Analyst Hypothesis\n"
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
                        "--hypothesis-file",
                        "agents/analyst/analyst-hypothesis.md",
                        "--findings-file",
                        "agents/analyst/analyst-findings.md",
                    ],
                ), mock.patch("harness.analysis_runner.subprocess.run", return_value=completed):
                    with self.assertRaises(SystemExit):
                        analysis_runner.main()
            finally:
                os.chdir(original_cwd)

            errors = (root / "agents/analyst/analysis-errors.md").read_text()
            self.assertIn("## A-001", errors)


if __name__ == "__main__":
    unittest.main()
