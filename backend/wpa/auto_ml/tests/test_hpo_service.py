import unittest
import pandas as pd
import mlflow
from backend.wpa.auto_ml.hpo_service import HPOService
from backend.wpa.auto_ml.models.tree_models import RandomForestClassifierWrapper
from sklearn.datasets import make_classification
import backend.wpa.auto_ml.model_library

import pytest

@pytest.mark.skip(reason="AutoML module is not yet fully integrated and tested.")
class TestHPOService(unittest.TestCase):

    def setUp(self):
        X, y = make_classification(n_samples=50, n_features=5, n_informative=3, n_redundant=0, random_state=42)
        self.X = pd.DataFrame(X, columns=[f'f{i}' for i in range(5)])
        self.y = pd.Series(y)
        self.model_wrapper = RandomForestClassifierWrapper()

    def test_hpo_service_optimization(self):
        with mlflow.start_run() as parent_run:
            hpo_service = HPOService(
                model_wrapper=self.model_wrapper,
                X=self.X,
                y=self.y,
                n_trials=3, # Keep low for testing
                scoring='accuracy'
            )
            best_params = hpo_service.optimize()

            self.assertIsInstance(best_params, dict)
            self.assertIn('n_estimators', best_params)

            # Verify that nested runs were created
            client = mlflow.tracking.MlflowClient()
            child_runs = client.search_runs(
                experiment_ids=[parent_run.info.experiment_id],
                filter_string=f"tags.mlflow.parentRunId = '{parent_run.info.run_id}'"
            )
            self.assertEqual(len(child_runs), 3)

if __name__ == '__main__':
    unittest.main()
