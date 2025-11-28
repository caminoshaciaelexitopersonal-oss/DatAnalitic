import pandas as pd
import pytest
import os
import shutil
import json
from backend.wpa.auto_analysis.eda_intelligent_service import EDAIntelligentService

@pytest.fixture
def eda_service():
    """Provides an EDAIntelligentService instance with a sample DataFrame."""
    job_id = "test_eda_job"
    output_dir = f"data/processed/{job_id}/"

    # Cleanup before test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    data = {
        'numeric': [1, 2, 3, None, 5],
        'categorical': ['A', 'B', 'A', 'C', 'B'],
        'binary': [0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    inferred_types = {'numeric': 'numeric', 'categorical': 'categorical', 'binary': 'numeric'}

    service = EDAIntelligentService(df, inferred_types, job_id)

    yield service # Provide the service to the test

    # Cleanup after test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

def test_auto_summary_creates_json(eda_service):
    """Tests that auto_summary creates the expected JSON file."""
    eda_service.auto_summary()

    expected_path = os.path.join(eda_service.output_dir, "summary_statistics.json")
    assert os.path.exists(expected_path)

    with open(expected_path, "r") as f:
        data = json.load(f)

    assert "numeric" in data
    assert "categorical" in data
    assert "binary" in data
    assert data["numeric"]["count"] == 4

def test_missing_report_creates_json_and_png(eda_service):
    """Tests that missing_report creates both a JSON report and a PNG heatmap."""
    eda_service.missing_report()

    expected_json_path = os.path.join(eda_service.output_dir, "missing_values_report.json")
    expected_png_path = os.path.join(eda_service.output_dir, "missing_values_heatmap.png")

    assert os.path.exists(expected_json_path)
    assert os.path.exists(expected_png_path)

    with open(expected_json_path, "r") as f:
        data = json.load(f)

    assert "numeric" in data
    assert data["numeric"]["count"] == 1
    assert data["numeric"]["percentage"] == 20.0
    assert data["categorical"]["count"] == 0
