import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from backend.wpa.auto_ml.service import AutoMlService

@pytest.fixture
def mock_state_store():
    """Fixture for a mocked StateStore."""
    return MagicMock()

@patch('backend.wpa.auto_ml.service.mlflow')
def test_automl_service_classification(mock_mlflow, mock_state_store):
    """
    Tests the AutoML service with a simple classification problem.
    MLflow is mocked to prevent external service dependency.
    """
    # 1. Arrange: Create a toy dataset
    data = {
        'feature1': [i for i in range(100)],
        'feature2': [i * 2 for i in range(100)],
        'target': ([0] * 50) + ([1] * 50)
    }
    df = pd.DataFrame(data)
    job_id = "test-job-123"
    target_variable = "target"

    # 2. Act: Run the AutoML service
    automl_service = AutoMlService(mock_state_store)
    artifacts = automl_service.run_automl_pipeline(job_id, df, target_variable)

    # 3. Assert: Check the output artifacts
    assert artifacts is not None
    assert "summary" in artifacts
    assert "best_model" in artifacts

    summary = artifacts["summary"]
    assert "best_model_name" in summary
    assert "best_model_score" in summary
    assert summary["best_model_score"] > 0.5 # Expect a reasonable score

    assert artifacts["best_model"] is not None

    # Check that at least one model was tried
    assert len(summary["ranking"]) > 0
    print(f"Best model found: {summary['best_model_name']} with score {summary['best_model_score']:.4f}")
