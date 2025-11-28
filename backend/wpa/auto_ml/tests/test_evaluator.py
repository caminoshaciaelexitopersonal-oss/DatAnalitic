import pytest
import pandas as pd
import numpy as np
from backend.wpa.auto_ml.evaluator import get_classification_metrics, get_regression_metrics

def test_get_classification_metrics():
    """
    Tests the classification metrics calculation.
    """
    y_true = pd.Series([0, 1, 0, 1])
    y_pred = pd.Series([0, 1, 0, 1])
    y_prob = np.array([[0.9, 0.1], [0.1, 0.9], [0.8, 0.2], [0.2, 0.8]])

    metrics = get_classification_metrics(y_true, y_pred, y_prob)

    assert metrics['accuracy'] == 1.0
    assert metrics['f1_score'] == 1.0
    assert 'roc_auc' in metrics

def test_get_regression_metrics():
    """
    Tests the regression metrics calculation.
    """
    y_true = pd.Series([1, 2, 3, 4])
    y_pred = pd.Series([1, 2, 3, 4])

    metrics = get_regression_metrics(y_true, y_pred)

    assert metrics['mae'] == 0.0
    assert metrics['mse'] == 0.0
    assert metrics['r2_score'] == 1.0
