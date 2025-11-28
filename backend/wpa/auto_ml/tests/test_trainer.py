import pytest
import pandas as pd
from sklearn.datasets import make_classification
from ..pipelines.builder import create_full_pipeline
from ..trainer import train_model_with_cv

@pytest.fixture
def sample_classification_data():
    """Creates a sample dataset for classification tasks."""
    X, y = make_classification(
        n_samples=100, n_features=10, n_informative=5, n_redundant=0, random_state=42
    )
    X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(10)])
    y = pd.Series(y, name="target")
    # Add some categorical features for the preprocessor
    X['cat_feature_1'] = ['A', 'B'] * 50
    X['cat_feature_2'] = ['X', 'Y', 'Z', 'W'] * 25
    return X, y

def test_train_model_with_cv_classification(sample_classification_data):
    """
    Tests the core training and cross-validation function on a classification task.
    """
    X, y = sample_classification_data
    model_key = "random_forest_classifier"
    numeric_features = [f for f in X.columns if X[f].dtype != 'object']
    categorical_features = [f for f in X.columns if X[f].dtype == 'object']

    # 1. Create the pipeline
    pipeline = create_full_pipeline(
        model_key=model_key,
        numeric_features=numeric_features,
        categorical_features=categorical_features
    )

    # 2. Train the model
    result = train_model_with_cv(pipeline, X, y, scoring="accuracy")

    # 3. Assert the results
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "model" in result
    assert "cv_mean_score" in result
    assert "cv_std_score" in result
    assert "fit_time" in result

    # Check if the score is plausible (for this simple dataset, it should be > 0.7)
    assert result["cv_mean_score"] > 0.7
    assert result["cv_std_score"] < 0.3
