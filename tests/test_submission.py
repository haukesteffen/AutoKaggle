import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import numpy as np
import pandas as pd

from agents.supervisor import submission


class SubmissionTests(unittest.TestCase):
    def test_create_submission_csv_decodes_class_labels(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact_dir = root / "artifacts" / "S-001"
            artifact_dir.mkdir(parents=True)
            test_path = root / "test.csv"
            output_path = root / "submission.csv"

            pd.DataFrame({"id": [10, 11], "feature": [1.0, 2.0]}).to_csv(test_path, index=False)
            np.save(
                artifact_dir / "test-preds.npy",
                np.array(
                    [
                        [0.80, 0.10, 0.10],
                        [0.20, 0.15, 0.65],
                    ]
                ),
            )

            with mock.patch.object(submission, "TEST_PATH", test_path):
                written_path = submission.create_submission_csv(artifact_dir, output_path)

            result = pd.read_csv(written_path)
            self.assertEqual(result.columns.tolist(), ["id", "Irrigation_Need"])
            self.assertEqual(result["Irrigation_Need"].tolist(), ["High", "Medium"])

    def test_create_submission_csv_rejects_non_matrix_predictions(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact_dir = root / "artifacts" / "S-001"
            artifact_dir.mkdir(parents=True)
            test_path = root / "test.csv"
            output_path = root / "submission.csv"

            pd.DataFrame({"id": [10, 11], "feature": [1.0, 2.0]}).to_csv(test_path, index=False)
            np.save(artifact_dir / "test-preds.npy", np.array([0.2, 0.8]))

            with mock.patch.object(submission, "TEST_PATH", test_path):
                with self.assertRaises(ValueError):
                    submission.create_submission_csv(artifact_dir, output_path)


if __name__ == "__main__":
    unittest.main()
