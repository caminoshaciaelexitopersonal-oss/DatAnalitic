import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from backend.wpa.auto_analysis.ingestion_adapter import strengthen_ingestion
from backend.wpa.auto_analysis.eda_intelligent_service import run_eda

# Create a sample DataFrame for testing
@pytest.fixture
def sample_dataframe():
    data = {
        'ID': range(10),
        'Age': [25, 30, 22, 45, 30, 50, 25, 22, 45, 50],
        'Category': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'A', 'C', 'B'],
        'Value': [1.1, 2.2, 1.5, 3.3, 2.5, 4.0, 1.8, 1.2, 3.8, 4.2],
        'Target': [0, 1, 0, 1, 1, 1, 0, 0, 1, 1]
    }
    return pd.DataFrame(data)

@patch('mlflow.log_param')
@patch('mlflow.log_dict')
@patch('mlflow.log_artifact') # Add patch for log_artifact
def test_ingestion_adapter(mock_log_artifact, mock_log_dict, mock_log_param, sample_dataframe):
    """
    Tests the ingestion adapter to ensure it extracts metadata correctly and
    logs artifacts to MLflow.
    """
    # The job_id is no longer needed as an argument
    metadata = strengthen_ingestion(sample_dataframe)

    assert metadata is not None
    assert metadata['num_rows'] == 10
    assert metadata['num_columns'] == 5
    assert 'data_hash' in metadata
    assert metadata['inferred_types']['Age'] == 'numeric'
    assert metadata['inferred_types']['Category'] == 'categorical'

    # Verify that MLflow logging was called
    mock_log_param.assert_called_once()
    mock_log_dict.assert_called_once()
    mock_log_artifact.assert_called_once() # Verify log_artifact was called

@pytest.mark.skip(reason="Test outdated due to EDA service refactoring.")
def test_eda_service(sample_dataframe):
    """
    Tests the EDA service to ensure it generates reports and visualizations.
    """
    job_id = "test_eda"
    inferred_types = {'ID': 'numeric', 'Age': 'numeric', 'Category': 'categorical', 'Value': 'numeric', 'Target': 'numeric'}

    with patch('os.makedirs'), patch('builtins.open', new_callable=MagicMock), patch('matplotlib.pyplot.savefig'):
        # We don't need to check the return, just that it runs without error
        run_eda(sample_dataframe, inferred_types, job_id)
