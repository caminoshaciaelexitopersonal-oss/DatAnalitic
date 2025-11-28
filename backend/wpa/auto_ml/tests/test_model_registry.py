import pytest
from backend.wpa.auto_ml.model_registry import get_model, MODEL_REGISTRY
# Explicitly import the model files to ensure they are registered
from backend.wpa.auto_ml.models import classifiers, regressors, clustering
import pandas as pd
from sklearn.datasets import make_classification

@pytest.fixture
def sample_data():
    X, y = make_classification(n_samples=100, n_features=10, n_informative=5, n_redundant=0, random_state=42)
    return pd.DataFrame(X), pd.Series(y)

def test_get_model(sample_data):
    X, y = sample_data
    model_wrapper = get_model('logistic_regression')
    assert isinstance(model_wrapper, classifiers.LogisticRegressionWrapper)
    model_wrapper.fit(X, y)
    predictions = model_wrapper.predict(X)
    assert len(predictions) == 100

def test_model_registry():
    assert 'logistic_regression' in MODEL_REGISTRY
    assert 'random_forest_classifier' in MODEL_REGISTRY
    assert 'lightgbm_classifier' in MODEL_REGISTRY
    assert 'xgboost_classifier' in MODEL_REGISTRY
    assert 'linear_regression' in MODEL_REGISTRY
    assert 'random_forest_regressor' in MODEL_REGISTRY
    assert 'kmeans' in MODEL_REGISTRY
    assert 'knn_classifier' in MODEL_REGISTRY
    assert 'svc' in MODEL_REGISTRY
