import pandas as pd
import pytest
import matplotlib.pyplot as plt
from backend.wpa.auto_analysis.eda_intelligent_service import EDAIntelligentService

@pytest.fixture
def eda_service():
    """Provides an EDAIntelligentService instance with a sample DataFrame."""
    data = {
        'numeric': [1, 2, 3, None, 5],
        'categorical': ['A', 'B', 'A', 'C', 'B'],
        'binary': [0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    inferred_types = {'numeric': 'numeric', 'categorical': 'categorical', 'binary': 'numeric'}

    # Correctly instantiate the service
    service = EDAIntelligentService(df, inferred_types)

    yield service

def test_run_automated_eda_returns_artifacts(eda_service):
    """Tests that run_automated_eda returns the expected artifact structure."""
    artifacts = eda_service.run_automated_eda()

    assert "json_artifacts" in artifacts
    assert "figure_artifacts" in artifacts

    # Check for specific JSON artifacts
    assert "summary_statistics.json" in artifacts["json_artifacts"]
    assert "missing_values_report.json" in artifacts["json_artifacts"]

    # Check for specific figure artifacts
    assert "missing_values_heatmap.png" in artifacts["figure_artifacts"]
    assert "numeric_distribution.png" in artifacts["figure_artifacts"]

    # Close the figures to prevent memory leaks
    for fig in artifacts["figure_artifacts"].values():
        if fig:
            plt.close(fig)

def test_summary_statistics_content(eda_service):
    """Tests the content of the summary statistics artifact."""
    artifacts = eda_service.run_automated_eda()
    summary = artifacts["json_artifacts"]["summary_statistics.json"]

    assert "numeric" in summary
    assert "categorical" in summary
    assert "binary" in summary
    assert summary["numeric"]["count"] == 4

    # Close figures
    for fig in artifacts["figure_artifacts"].values():
        if fig:
            plt.close(fig)

def test_missing_report_content(eda_service):
    """Tests the content of the missing values report artifact."""
    artifacts = eda_service.run_automated_eda()
    missing_report = artifacts["json_artifacts"]["missing_values_report.json"]

    assert "numeric" in missing_report
    assert missing_report["numeric"]["count"] == 1
    assert missing_report["numeric"]["percentage"] == 20.0
    assert missing_report["categorical"]["count"] == 0

    # Close figures
    for fig in artifacts["figure_artifacts"].values():
        if fig:
            plt.close(fig)
