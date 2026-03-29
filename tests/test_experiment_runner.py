import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
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

        with mock.patch.object(
            sys,
            "argv",
            ["experiment_runner"],
        ), mock.patch("harness.experiment_runner.mp.get_context", return_value=fake_context), redirect_stdout(
            stdout
        ), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                experiment_runner.main()

        self.assertEqual(exc.exception.code, experiment_runner.INVALID_EXIT_CODE)
        self.assertIn("status:            invalid", stdout.getvalue())
        self.assertIn("Traceback: boom", stderr.getvalue())

    def test_classify_exception_marks_contract_failures_invalid(self) -> None:
        self.assertEqual(experiment_runner._classify_exception(ValueError("bad shape")), "invalid")
        self.assertEqual(experiment_runner._classify_exception(SyntaxError("bad syntax")), "invalid")
        self.assertEqual(experiment_runner._classify_exception(RuntimeError("infra failure")), "error")


if __name__ == "__main__":
    unittest.main()
