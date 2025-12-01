from sklearn.linear_model import LogisticRegression, LinearRegression, ElasticNet, Lasso, Ridge
import pandas as pd
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model
from typing import Dict, Any

@register_model('LogisticRegression')
class LogisticRegressionWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = LogisticRegression(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'C': ('float', [1e-5, 1e2], 'log'),
            'solver': ('categorical', ['liblinear', 'saga'])
        }

    def get_model(self):
        return self.model

@register_model('LinearRegression')
class LinearRegressionWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = LinearRegression(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {} # No hyperparameters to tune for LinearRegression

    def get_model(self):
        return self.model

@register_model('ElasticNet')
class ElasticNetWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = ElasticNet(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'alpha': ('float', [1e-4, 1.0], 'log'),
            'l1_ratio': ('float', [0, 1.0])
        }

    def get_model(self):
        return self.model

@register_model('Lasso')
class LassoWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = Lasso(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'alpha': ('float', [1e-4, 1.0], 'log')
        }

    def get_model(self):
        return self.model

@register_model('Ridge')
class RidgeWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = Ridge(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'alpha': ('float', [1e-4, 1.0], 'log')
        }

    def get_model(self):
        return self.model
