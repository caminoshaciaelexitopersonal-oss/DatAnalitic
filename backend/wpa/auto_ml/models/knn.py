from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model
from typing import Dict, Any

@register_model('KNeighborsClassifier')
class KNeighborsClassifierWrapper(BaseModelWrapper):
    def __init__(self, params: Dict[str, Any] = None):
        self.model = KNeighborsClassifier(**(params or {}))
        self.params = params or {}

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_neighbors': ('int', [3, 15]),
            'weights': ('categorical', ['uniform', 'distance']),
            'p': ('int', [1, 2])
        }

    def get_model(self):
        return self.model
