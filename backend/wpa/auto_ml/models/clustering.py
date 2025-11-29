from typing import Dict, Any
import pandas as pd
 
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, Birch, MiniBatchKMeans
from sklearn.mixture import GaussianMixture
 
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
 
    def get_model(self): return self.model
 

@register_model('dbscan')
class DBSCANWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn DBSCAN."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = DBSCAN(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.fit_predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'eps': ('float', (0.1, 2.0))}
 
    def get_model(self): return self.model

@register_model('agglomerative_clustering')
class AgglomerativeClusteringWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn AgglomerativeClustering."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = AgglomerativeClustering(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.fit_predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'n_clusters': ('int', (2, 20))}
    def get_model(self): return self.model

@register_model('birch')
class BirchWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn Birch."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = Birch(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'n_clusters': ('int', (2, 20))}
    def get_model(self): return self.model

@register_model('gaussian_mixture')
class GaussianMixtureWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn GaussianMixture."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = GaussianMixture(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'n_components': ('int', (2, 20))}
    def get_model(self): return self.model

@register_model('minibatch_kmeans')
class MiniBatchKMeansWrapper(BaseModelWrapper):
    """Wrapper for scikit-learn MiniBatchKMeans."""
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.model = MiniBatchKMeans(**self.params)
    def fit(self, X: pd.DataFrame, y: pd.Series = None): self.model.fit(X)
    def predict(self, X: pd.DataFrame) -> pd.Series: return self.model.predict(X)
    def get_hyperparameter_search_space(self) -> Dict[str, Any]: return {'n_clusters': ('int', (2, 20))}
    def get_model(self): return self.model
 
