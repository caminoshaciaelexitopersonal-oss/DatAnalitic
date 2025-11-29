import unittest
import pandas as pd
import mlflow
from sklearn.linear_model import LogisticRegression
from backend.wpa.auto_ml.pipelines.builder import create_full_pipeline
from backend.wpa.auto_ml.trainer import train_model_with_cv

import pytest

@pytest.mark.skip(reason="AutoML module is not yet fully integrated and tested.")
class TestTrainer(unittest.TestCase):

    def setUp(self):
        # Use a larger dataset for 5-fold CV
        self.X = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'feature2': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        })
        self.y = pd.Series([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        model = LogisticRegression()
        self.pipeline = create_full_pipeline(
            model, 'classification', ['feature1'], ['feature2']
        )

    def test_train_model_with_5_fold_cv(self):
        with mlflow.start_run():
            result = train_model_with_cv(self.pipeline, self.X, self.y, scoring='accuracy', cv=5)

            self.assertEqual(result['status'], 'success')
            self.assertIn('model', result)
            self.assertIn('cv_mean_score', result)
            self.assertIn('cv_std_score', result)
            self.assertIn('fit_time', result)
            self.assertAlmostEqual(result['cv_mean_score'], 1.0)

    def test_train_model_with_3_fold_cv(self):
        with mlflow.start_run():
            result = train_model_with_cv(self.pipeline, self.X, self.y, scoring='accuracy', cv=3)

            self.assertEqual(result['status'], 'success')
            self.assertIn('model', result)
            self.assertIn('cv_mean_score', result)
            self.assertIn('cv_std_score', result)
            self.assertIn('fit_time', result)
            self.assertAlmostEqual(result['cv_mean_score'], 1.0)

if __name__ == '__main__':
    unittest.main()
