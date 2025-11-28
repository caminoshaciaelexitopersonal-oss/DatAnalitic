from typing import Dict, Any
import pandas as pd
from sklearn.cluster import KMeans
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model

@register_model('kmeans')
class KMeansWrapper(BaseModelWrapper):
    """Wrapper for the scikit-learn KMeans model."""

    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = KMeans(**self.params)

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        self.model.fit(X)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.model.predict(X)

    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        return {
            'n_clusters': ('int', (2, 20)),
            'init': ('categorical', ['k-means++', 'random']),
            'n_init': ('int', (5, 50)),
            'max_iter': ('int', (100, 1000)),
        }
