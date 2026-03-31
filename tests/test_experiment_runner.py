import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from harness import experiment_runner


class _FakeQueue:
    def __init__(self, messages):
        self._messages = list(messages)

    def get(self, timeout):
        if self._messages:
            return self._messages.pop(0)
        raise AssertionError("queue should not be polled again in this test")


class _FakeProcess:
    def start(self) -> None:
        return None

    def is_alive(self) -> bool:
        return False

    def join(self, timeout=None) -> None:
        return None


class _FakeContext:
    def __init__(self, messages):
        self._messages = messages

    def Queue(self):
        return _FakeQueue(self._messages)

    def Process(self, target, args):
        return _FakeProcess()


class ExperimentRunnerTests(unittest.TestCase):
    def test_main_uses_invalid_exit_code_for_invalid_worker_errors(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        fake_context = _FakeContext(
            [
                {
                    "type": "error",
                    "experiment_name": "broken_experiment",
                    "traceback": "Traceback: boom\n",
                    "classification": "invalid",
                }
            ]
        )

        task = mock.Mock(status="active", task_id="S-100")
        with mock.patch("harness.experiment_runner.read_task_metadata", return_value=task), mock.patch(
            "harness.experiment_runner.mp.get_context", return_value=fake_context
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                experiment_runner.main()

        self.assertEqual(exc.exception.code, experiment_runner.INVALID_EXIT_CODE)
        self.assertIn("status:            invalid", stdout.getvalue())
        self.assertIn("Traceback: boom", stderr.getvalue())

    def test_main_requires_active_task(self) -> None:
        stderr = io.StringIO()
        task = mock.Mock(status="none", task_id="S-100")
        with mock.patch("harness.experiment_runner.read_task_metadata", return_value=task), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                experiment_runner.main()

        self.assertEqual(exc.exception.code, 1)
        self.assertIn("scientist task must be active", stderr.getvalue())

    def test_main_writes_artifacts_to_task_id_directory(self) -> None:
        result = mock.Mock(
            timed_out=False,
            completed_folds=experiment_runner.N_SPLITS,
            mean_score=0.91,
            std_score=0.01,
            training_seconds=1.5,
        )
        fake_context = _FakeContext(
            [
                {"type": "start", "experiment_name": "demo"},
                {"type": "result", "experiment_name": "demo", "result": result, "oof_preds": mock.sentinel.oof},
            ]
        )
        task = mock.Mock(status="active", task_id="S-101")

        with TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "S-101"
            with mock.patch("harness.experiment_runner.read_task_metadata", return_value=task), mock.patch(
                "harness.experiment_runner.mp.get_context", return_value=fake_context
            ), mock.patch(
                "harness.experiment_runner.default_artifact_dir", return_value=artifact_dir
            ), mock.patch(
                "harness.experiment_runner._generate_artifacts"
            ) as generate_artifacts:
                experiment_runner.main()

        generate_artifacts.assert_called_once()
        self.assertEqual(generate_artifacts.call_args.args[0], artifact_dir.resolve())
        self.assertIs(generate_artifacts.call_args.args[1], mock.sentinel.oof)

    def test_clean_artifact_dir_rejects_existing_terminal_outputs(self) -> None:
        with TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "S-102"
            artifact_dir.mkdir()
            (artifact_dir / "oof-preds.npy").write_bytes(b"done")

            with self.assertRaises(FileExistsError):
                experiment_runner._ensure_clean_artifact_dir(artifact_dir)

    def test_classify_exception_marks_contract_failures_invalid(self) -> None:
        self.assertEqual(experiment_runner._classify_exception(ValueError("bad shape")), "invalid")
        self.assertEqual(experiment_runner._classify_exception(SyntaxError("bad syntax")), "invalid")
        self.assertEqual(experiment_runner._classify_exception(RuntimeError("infra failure")), "error")


if __name__ == "__main__":
    unittest.main()
