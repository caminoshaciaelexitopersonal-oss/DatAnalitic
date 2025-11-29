import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from backend.wpa.auto_ml.tasks import run_full_automl
from backend.core.state_store import StateStore

@pytest.mark.skip(reason="AutoML module is not yet fully integrated and tested.")
class TestE2EAutoMLFlow(unittest.TestCase):

    def setUp(self):
        self.job_id = "test_job_123"
        self.user_id = "test_user"

        # Create mock data with enough samples for 5-fold CV
        self.X_train = pd.DataFrame({
            'numeric_1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'categorical_1': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
        })
        self.y_train = pd.DataFrame({'target': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]})
        self.X_test = pd.DataFrame({'numeric_1': [11, 12], 'categorical_1': ['B', 'C']})
        self.y_test = pd.DataFrame({'target': [1, 0]})
        self.metadata = {
            "problem_type": "classification",
            "target_column": "target"
        }
        self.request = {
            "user_id": self.user_id,
            "model_candidates": ["LogisticRegression"],
            "scoring": "accuracy"
        }

    @patch('backend.wpa.auto_ml.tasks.StateStore')
    def test_run_full_automl_e2e(self, MockStateStore):
        # Setup mock StateStore
        mock_state_store_instance = MockStateStore.return_value

        # --- Mock artifact loading ---
        # Use a dictionary to map artifact names to mock data
        artifacts = {
            "X_train.parquet": self.X_train.to_parquet(),
            "y_train.parquet": self.y_train.to_parquet(),
            "X_test.parquet": self.X_test.to_parquet(),
            "y_test.parquet": self.y_test.to_parquet(),
        }
        mock_state_store_instance.load_artifact_as_bytes.side_effect = lambda job_id, name: artifacts.get(name)
        mock_state_store_instance.load_json_artifact.return_value = self.metadata

        # --- Run the task ---
        # The task will now use the mocked StateStore instance internally
        result = run_full_automl(self.job_id, self.request)

        # --- Debugging ---
        if result['status'] == 'FAILURE':
            print(f"AutoML task failed with error: {result.get('error')}")

        # --- Assertions ---
        self.assertEqual(result['status'], 'SUCCESS', "The AutoML task failed unexpectedly.")

        # Verify that key artifacts were saved
        # Get the call arguments for save_json_artifact
        save_json_calls = mock_state_store_instance.save_json_artifact.call_args_list
        # Check if 'automl_results.json' was saved
        was_automl_results_saved = any(
            call[0][1] == 'automl_results.json' for call in save_json_calls
        )
        self.assertTrue(was_automl_results_saved, "automl_results.json was not saved.")

        # Verify job status was updated to 'completed'
        mock_state_store_instance.save_job_status.assert_called_with(
            self.job_id,
            {"status": "completed", "stage": "automl"}
        )

if __name__ == '__main__':
    unittest.main()
