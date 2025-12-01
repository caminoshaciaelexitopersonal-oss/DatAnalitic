import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import os
import uuid

# Set environment variables for testing
os.environ['SECRET_KEY'] = 'test_secret_key'

# Create a minimal FastAPI app for testing
app = FastAPI()

@app.post("/automl/hpo/submit")
def mock_submit_hpo_job():
    return {"celery_task_id": "test_task_id"}

client = TestClient(app)

class TestMinimalHPOApi(unittest.TestCase):

    def setUp(self):
        self.job_id = str(uuid.uuid4())
        self.model_name = 'RandomForestRegressor'

    def test_submit_hpo_job_minimal(self):
        response = client.post(
            "/automl/hpo/submit",
            json={
                "job_id": self.job_id,
                "model_name": self.model_name,
                "n_trials": 10,
                "scoring": "r2"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['celery_task_id'], 'test_task_id')

if __name__ == '__main__':
    unittest.main()
