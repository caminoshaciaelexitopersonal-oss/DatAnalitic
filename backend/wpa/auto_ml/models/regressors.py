from typing import Dict, Any
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model

@register_model('linear_regression')
class LinearRegressionWrapper(BaseModelWrapper):
    """Wrapper for the scikit-learn Linear Regression model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = LinearRegression(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'fit_intercept': ('categorical', [True, False])
        }

@register_model('random_forest_regressor')
class RandomForestRegressorWrapper(BaseModelWrapper):
    """Wrapper for the scikit-learn RandomForestRegressor model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = RandomForestRegressor(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', (10, 1000)),
            'max_depth': ('int', (3, 50)),
            'min_samples_split': ('float', (0.1, 1.0)),
            'min_samples_leaf': ('float', (0.1, 0.5)),
        }
