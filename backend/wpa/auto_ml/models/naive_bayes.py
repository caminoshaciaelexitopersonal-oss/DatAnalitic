from sklearn.naive_bayes import GaussianNB
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from backend.wpa.auto_ml.model_registry import register_model

@register_model('GaussianNB')
class GaussianNBWrapper(BaseModelWrapper):
    def __init__(self, params=None):
        model = GaussianNB()
        super().__init__(model, params)
