from sklearn.svm import SVC, SVR
import pandas as pd
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model
from typing import Dict, Any

@register_model('SVC')
class SVCWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = SVC(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'C': ('float', [1e-3, 1e3], 'log'),
            'gamma': ('float', [1e-4, 1e-1], 'log'),
            'kernel': ('categorical', ['linear', 'rbf'])
        }

    def get_model(self):
        return self.model

@register_model('SVR')
class SVRWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = SVR(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'C': ('float', [1e-3, 1e3], 'log'),
            'gamma': ('float', [1e-4, 1e-1], 'log'),
            'kernel': ('categorical', ['linear', 'rbf'])
        }

    def get_model(self):
        return self.model
