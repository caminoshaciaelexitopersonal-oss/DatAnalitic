from typing import Dict, Any
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model

@register_model('kmeans')
class KMeansWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn KMeans."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = KMeans(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'n_clusters': ('int', (2, 20))}

@register_model('dbscan')
class DBSCANWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn DBSCAN."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = DBSCAN(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.fit_predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'eps': ('float', (0.1, 2.0))}

@register_model('agglomerative_clustering')
class AgglomerativeClusteringWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn AgglomerativeClustering."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = AgglomerativeClustering(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.fit_predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'n_clusters': ('int', (2, 20))}
