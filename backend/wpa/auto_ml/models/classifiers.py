from typing import Dict, Any
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import lightgbm as lgb
import xgboost as xgb
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model

@register_model('logistic_regression')
class LogisticRegressionWrapper(BaseModelWrapper):
    """Wrapper for the scikit-learn Logistic Regression model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = LogisticRegression(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'C': ('float', (1e-5, 1e2), 'log'),
            'penalty': ('categorical', ['l1', 'l2']),
            'solver': ('categorical', ['liblinear', 'saga'])
        }

@register_model('random_forest_classifier')
class RandomForestClassifierWrapper(BaseModelWrapper):
    """Wrapper for the scikit-learn RandomForestClassifier model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = RandomForestClassifier(**self.params)

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
            'criterion': ('categorical', ['gini', 'entropy'])
        }

@register_model('lightgbm_classifier')
class LGBMClassifierWrapper(BaseModelWrapper):
    """Wrapper for the LightGBM Classifier model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = lgb.LGBMClassifier(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', (100, 2000)),
            'learning_rate': ('float', (0.01, 0.3), 'log'),
            'num_leaves': ('int', (20, 3000)),
            'max_depth': ('int', (-1, 50)),
            'reg_alpha': ('float', (0.0, 1.0)),
            'reg_lambda': ('float', (0.0, 1.0)),
        }

@register_model('xgboost_classifier')
class XGBClassifierWrapper(BaseModelWrapper):
    """Wrapper for the XGBoost Classifier model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = xgb.XGBClassifier(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_estimators': ('int', (100, 2000)),
            'learning_rate': ('float', (0.01, 0.3), 'log'),
            'max_depth': ('int', (3, 15)),
            'subsample': ('float', (0.5, 1.0)),
            'colsample_bytree': ('float', (0.5, 1.0)),
            'gamma': ('float', (0, 5)),
        }

@register_model('knn_classifier')
class KNeighborsClassifierWrapper(BaseModelWrapper):
    """Wrapper for the scikit-learn KNeighborsClassifier model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = KNeighborsClassifier(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_neighbors': ('int', (1, 50)),
            'weights': ('categorical', ['uniform', 'distance']),
            'p': ('int', (1, 2)),
        }

@register_model('svc')
class SVCWrapper(BaseModelWrapper):
    """Wrapper for the scikit-learn SVC model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = SVC(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'C': ('float', (1e-5, 1e5), 'log'),
            'kernel': ('categorical', ['linear', 'poly', 'rbf', 'sigmoid']),
            'degree': ('int', (2, 5)),
            'gamma': ('categorical', ['scale', 'auto']),
        }
