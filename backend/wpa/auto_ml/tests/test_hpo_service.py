import pytest
from backend.wpa.auto_ml.hpo_service import HPOService
from backend.wpa.auto_ml.models.classifiers import LogisticRegressionWrapper
import pandas as pd
from sklearn.datasets import make_classification

@pytest.fixture
def sample_data():
    X, y = make_classification(n_samples=100, n_features=10, n_informative=5, n_redundant=0, random_state=42)
    return pd.DataFrame(X), pd.Series(y)

def test_hpo_service(sample_data):
    X, y = sample_data
    model_wrapper = LogisticRegressionWrapper()
    hpo_service = HPOService(model_wrapper, X, y, n_trials=5, scoring='accuracy')
    best_params = hpo_service.optimize()

    assert isinstance(best_params, dict)
    assert 'C' in best_params
    assert 'penalty' in best_params
    assert 'solver' in best_params
