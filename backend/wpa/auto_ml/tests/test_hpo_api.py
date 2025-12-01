import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import os
import uuid

# Set environment variables for testing
os.environ['SECRET_KEY'] = 'test_secret_key'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Mock StateStore before it's imported by the app
with patch('backend.core.state_store.StateStore') as MockStateStore:
    from backend.main import app

import pytest

@pytest.mark.skip(reason="AutoML module is not yet fully integrated and tested.")
class TestHPOApi(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.job_id = str(uuid.uuid4())
        self.model_name = 'RandomForestRegressor'

    @patch('backend.wpa.auto_ml.api.get_state_store')
    @patch('backend.wpa.auto_ml.api.run_hpo_study.delay')
    def test_submit_hpo_job_success(self, mock_run_hpo_study, mock_get_state_store):
        # Mock the StateStore to return a valid job
        mock_state_store = MagicMock()
        mock_job = MagicMock()
        mock_state_store.get_job.return_value = mock_job
        mock_get_state_store.return_value = mock_state_store

        # Mock the Celery task
        mock_task = MagicMock()
        mock_task.id = 'test_task_id'
        mock_run_hpo_study.return_value = mock_task

        # Make the request
        response = self.client.post(
            "/unified/v1/wpa/auto-ml/hpo/submit",
            json={
                "job_id": self.job_id,
                "model_name": self.model_name,
                "n_trials": 10,
                "scoring": "r2"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['celery_task_id'], 'test_task_id')

        # Verify that the Celery task was called with the correct arguments
        mock_run_hpo_study.assert_called_once()
        call_args = mock_run_hpo_study.call_args[0]
        self.assertEqual(call_args[0], self.job_id)
        self.assertEqual(call_args[1]['model_name'], self.model_name)

if __name__ == '__main__':
    unittest.main()
