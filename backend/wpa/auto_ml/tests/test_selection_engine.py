import pytest
from ..selection_engine import calculate_composite_score

@pytest.fixture
def sample_config():
    """Provides a sample weight configuration."""
    return {
        "weights": {
            "cv_mean_accuracy": 1.0,
            "demographic_parity_difference": -0.5,
            "fit_time": -0.1
        },
        "normalization_factors": {
            "fit_time": 100
        }
    }

def test_calculate_composite_score(sample_config):
    """
    Tests the composite score calculation.
    """
    trial_result = {
        "status": "success",
        "cv_mean_accuracy": 0.95,
        "fit_time": 50.0,
        "evaluation": {
            "fairness_metrics": {
                "demographic_parity_difference": 0.1
            }
        }
    }

    # Expected score:
    # accuracy: 0.95 * 1.0 = 0.95
    # fairness: abs(0.1) * -0.5 = -0.05
    # fit_time: (50.0 / 100) * -0.1 = -0.05
    # Total = 0.95 - 0.05 - 0.05 = 0.85
    expected_score = 0.85

    actual_score = calculate_composite_score(trial_result, sample_config)

    assert actual_score == pytest.approx(expected_score)
