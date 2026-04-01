import unittest

import numpy as np
import pandas as pd

from harness import dataset


class DatasetTests(unittest.TestCase):
    def test_encode_target_labels_uses_canonical_order(self) -> None:
        encoded = dataset.encode_target_labels(pd.Series(["High", "Low", "Medium", "Low"]))
        np.testing.assert_array_equal(encoded, np.array([0, 1, 2, 1]))

    def test_predict_class_probabilities_aligns_model_class_order(self) -> None:
        class FakeModel:
            classes_ = np.array([2, 0, 1])

            def predict_proba(self, X):
                return np.array(
                    [
                        [0.70, 0.10, 0.20],
                        [0.10, 0.60, 0.30],
                    ]
                )

        X = pd.DataFrame({"feature": [1, 2]})
        pred = dataset.predict_class_probabilities(FakeModel(), X)

        np.testing.assert_allclose(
            pred,
            np.array(
                [
                    [0.10, 0.20, 0.70],
                    [0.60, 0.30, 0.10],
                ]
            ),
        )

    def test_score_fold_uses_balanced_accuracy_from_argmax_predictions(self) -> None:
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array(
            [
                [0.80, 0.10, 0.10],
                [0.60, 0.25, 0.15],
                [0.10, 0.20, 0.70],
                [0.70, 0.20, 0.10],
                [0.20, 0.70, 0.10],
                [0.10, 0.70, 0.20],
            ]
        )

        self.assertAlmostEqual(dataset.score_fold(y_true, y_pred), 2.0 / 3.0)

    def test_decode_target_labels_rejects_out_of_range_indices(self) -> None:
        with self.assertRaises(ValueError):
            dataset.decode_target_labels(np.array([3]))


if __name__ == "__main__":
    unittest.main()
