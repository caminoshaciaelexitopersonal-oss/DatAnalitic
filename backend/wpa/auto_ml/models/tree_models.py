from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model
from typing import Dict, Any

@register_model('RandomForestClassifier')
class RandomForestClassifierWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = RandomForestClassifier(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [10, 1000]),
            'max_depth': ('int', [3, 20]),
            'min_samples_split': ('float', [0.1, 1.0])
        }

    def get_model(self):
        return self.model

@register_model('DecisionTreeClassifier')
class DecisionTreeClassifierWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = DecisionTreeClassifier(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'max_depth': ('int', [3, 20]),
            'min_samples_split': ('float', [0.1, 1.0])
        }

    def get_model(self):
        return self.model

@register_model('RandomForestRegressor')
class RandomForestRegressorWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = RandomForestRegressor(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [10, 1000]),
            'max_depth': ('int', [3, 20]),
            'min_samples_split': ('float', [0.1, 1.0])
        }

    def get_model(self):
        return self.model

@register_model('ExtraTreesRegressor')
class ExtraTreesRegressorWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = ExtraTreesRegressor(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [10, 1000]),
            'max_depth': ('int', [3, 20]),
            'min_samples_split': ('float', [0.1, 1.0])
        }

    def get_model(self):
        return self.model
