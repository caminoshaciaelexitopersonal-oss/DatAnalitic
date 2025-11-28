from typing import Dict, Any
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model

@register_model('linear_regression')
class LinearRegressionWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn Linear Regression."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = LinearRegression(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series): self.model.fit(X, y)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'fit_intercept': ('categorical', [True, False])}

@register_model('ridge_regression')
class RidgeWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn Ridge Regression."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = Ridge(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series): self.model.fit(X, y)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'alpha': ('float', (1e-5, 1e2), 'log')}

@register_model('lasso_regression')
class LassoWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn Lasso Regression."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = Lasso(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series): self.model.fit(X, y)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'alpha': ('float', (1e-5, 1e2), 'log')}

@register_model('elasticnet_regression')
class ElasticNetWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn ElasticNet Regression."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = ElasticNet(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series): self.model.fit(X, y)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'alpha': ('float', (1e-5, 1e2), 'log'), 'l1_ratio': ('float', (0.0, 1.0))}

@register_model('random_forest_regressor')
class RandomForestRegressorWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn RandomForestRegressor."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = RandomForestRegressor(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series): self.model.fit(X, y)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'n_estimators': ('int', (10, 1000)), 'max_depth': ('int', (3, 50))}
