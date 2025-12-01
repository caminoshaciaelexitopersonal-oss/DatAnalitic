from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from xgboost import XGBClassifier, XGBRegressor
import pandas as pd
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model
from typing import Dict, Any

@register_model('GradientBoostingClassifier')
class GradientBoostingClassifierWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = GradientBoostingClassifier(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [10, 1000]),
            'learning_rate': ('float', [0.01, 0.3], 'log'),
            'max_depth': ('int', [3, 10])
        }

    def get_model(self):
        return self.model

@register_model('LightGBMClassifier')
class LightGBMClassifierWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = LGBMClassifier(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [50, 500]),
            'learning_rate': ('float', [0.01, 0.2], 'log'),
        }

    def get_model(self):
        return self.model

@register_model('XGBoostClassifier')
class XGBoostClassifierWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = XGBClassifier(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [50, 500]),
            'learning_rate': ('float', [0.01, 0.2], 'log'),
        }

    def get_model(self):
        return self.model

@register_model('GradientBoostingRegressor')
class GradientBoostingRegressorWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = GradientBoostingRegressor(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [10, 1000]),
            'learning_rate': ('float', [0.01, 0.3], 'log'),
            'max_depth': ('int', [3, 10])
        }

    def get_model(self):
        return self.model

@register_model('LightGBMRegressor')
class LightGBMRegressorWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = LGBMRegressor(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [50, 500]),
            'learning_rate': ('float', [0.01, 0.2], 'log'),
        }

    def get_model(self):
        return self.model

@register_model('XGBoostRegressor')
class XGBoostRegressorWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = XGBRegressor(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', [50, 500]),
            'learning_rate': ('float', [0.01, 0.2], 'log'),
        }

    def get_model(self):
        return self.model
