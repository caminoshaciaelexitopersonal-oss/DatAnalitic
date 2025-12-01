import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, r2_score, mean_absolute_error
)
from fairlearn.metrics import MetricFrame, demographic_parity_difference, equalized_odds_difference
from typing import Dict, Any, List

def _get_classification_metrics(y_true, y_pred, y_proba=None) -> Dict[str, float]:
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average='weighted'),
        "recall": recall_score(y_true, y_pred, average='weighted'),
        "f1_score": f1_score(y_true, y_pred, average='weighted'),
    }
    if y_proba is not None:
        metrics["roc_auc"] = roc_auc_score(y_true, y_proba, average='weighted', multi_class='ovr')
    return metrics

def _get_regression_metrics(y_true, y_pred) -> Dict[str, float]:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mse": mse,
        "rmse": np.sqrt(mse),
        "mae": mean_absolute_error(y_true, y_pred),
        "r2_score": r2_score(y_true, y_pred),
    }

def _get_fairness_metrics(y_true, y_pred, sensitive_features: pd.Series) -> Dict[str, float]:
    """Calculates fairness metrics using fairlearn."""
    fairness_metrics = {}

    # Demographic Parity
    dpd = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_features)
    fairness_metrics["demographic_parity_difference"] = dpd

    # Equalized Odds
    eod = equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive_features)
    fairness_metrics["equalized_odds_difference"] = eod

    return fairness_metrics

def evaluate_model(
    pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    problem_type: str,
    sensitive_feature_column: str = None
) -> Dict[str, Any]:
    """
    Evaluates a trained pipeline on a test set, including standard and fairness metrics.
    """
    y_pred = pipeline.predict(X_test)
    y_proba = None

    results = {}

    if problem_type == "classification":
        if hasattr(pipeline, "predict_proba"):
            y_proba = pipeline.predict_proba(X_test)[:, 1] # Assuming binary for now
        results["metrics"] = _get_classification_metrics(y_test, y_pred, y_proba)
    elif problem_type == "regression":
        results["metrics"] = _get_regression_metrics(y_test, y_pred)
    else:
        results["metrics"] = {}

    # Fairness evaluation
    if sensitive_feature_column and sensitive_feature_column in X_test.columns:
        sensitive_features = X_test[sensitive_feature_column]
        results["fairness_metrics"] = _get_fairness_metrics(y_test, y_pred, sensitive_features)

    return results
