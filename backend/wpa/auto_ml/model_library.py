"""
This module contains the model registry and wrappers for all algorithms
supported by the AutoML engine, following the "Plan Científico".
"""
from typing import Dict, Any
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans

# The MODEL_REGISTRY will store wrappers for all 52 algorithms.
MODEL_REGISTRY: Dict[str, Any] = {}

class ModelWrapper:
    """Base class for all model wrappers to ensure a consistent interface."""
    def __init__(self, model_class, **params):
        # Ensure 'random_state' is set for reproducibility where applicable
        if 'random_state' in model_class().get_params():
            params.setdefault('random_state', 42)
        self.model = model_class(**params)

    def fit(self, X, y):
        # Clustering models have a different fit signature
        if y is None:
            return self.model.fit(X)
        return self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

# --- Wrapper Implementations ---

class LogisticRegressionWrapper(ModelWrapper):
    def __init__(self, **params):
        params.setdefault('max_iter', 200)
        super().__init__(model_class=LogisticRegression, **params)

class RandomForestClassifierWrapper(ModelWrapper):
    def __init__(self, **params):
        params.setdefault('n_estimators', 100)
        super().__init__(model_class=RandomForestClassifier, **params)

class KMeansWrapper(ModelWrapper):
    def __init__(self, **params):
        params.setdefault('n_clusters', 8)
        super().__init__(model_class=KMeans, **params)

    def fit(self, X, y=None):
        # KMeans fit method doesn't take y
        return self.model.fit(X)

# --- Registering Models ---

def register_model(key: str):
    def decorator(cls):
        MODEL_REGISTRY[key] = cls
        return cls
    return decorator

@register_model("logistic_regression")
class LogisticRegressionWrapper(ModelWrapper):
    def __init__(self, **params):
        params.setdefault('max_iter', 200)
        super().__init__(model_class=LogisticRegression, **params)

@register_model("random_forest_classifier")
class RandomForestClassifierWrapper(ModelWrapper):
    def __init__(self, **params):
        params.setdefault('n_estimators', 100)
        super().__init__(model_class=RandomForestClassifier, **params)

@register_model("kmeans")
class KMeansWrapper(ModelWrapper):
    def __init__(self, **params):
        params.setdefault('n_clusters', 8)
        super().__init__(model_class=KMeans, **params)

    def fit(self, X, y=None):
        # KMeans fit method doesn't take y
        return self.model.fit(X)

# --- Factory Function ---

def get_model_by_key(key: str, params: Dict = None):
    """Factory function to get a model instance from the registry."""
    if key not in MODEL_REGISTRY:
        raise ValueError(f"Model key '{key}' not found in the registry.")

    wrapper_class = MODEL_REGISTRY[key]
    return wrapper_class(**(params or {}))
