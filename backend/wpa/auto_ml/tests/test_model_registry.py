import unittest
from backend.wpa.auto_ml.model_registry import get_model, MODEL_REGISTRY
import backend.wpa.auto_ml.model_library # Import to register all models

class TestModelRegistry(unittest.TestCase):

    def test_classification_models_are_registered(self):
        self.assertIn('LogisticRegression', MODEL_REGISTRY)
        self.assertIn('RandomForestClassifier', MODEL_REGISTRY)
        self.assertIn('GradientBoostingClassifier', MODEL_REGISTRY)
        self.assertIn('SVC', MODEL_REGISTRY)
        self.assertIn('KNeighborsClassifier', MODEL_REGISTRY)
        self.assertIn('GaussianNB', MODEL_REGISTRY)
        self.assertIn('DecisionTreeClassifier', MODEL_REGISTRY)
        self.assertIn('LightGBMClassifier', MODEL_REGISTRY)
        self.assertIn('XGBoostClassifier', MODEL_REGISTRY)

    def test_regression_models_are_registered(self):
        self.assertIn('LinearRegression', MODEL_REGISTRY)
        self.assertIn('ElasticNet', MODEL_REGISTRY)
        self.assertIn('Lasso', MODEL_REGISTRY)
        self.assertIn('Ridge', MODEL_REGISTRY)
        self.assertIn('SVR', MODEL_REGISTRY)
        self.assertIn('RandomForestRegressor', MODEL_REGISTRY)
        self.assertIn('GradientBoostingRegressor', MODEL_REGISTRY)
        self.assertIn('LightGBMRegressor', MODEL_REGISTRY)
        self.assertIn('XGBoostRegressor', MODEL_REGISTRY)
        self.assertIn('ExtraTreesRegressor', MODEL_REGISTRY)

    def test_clustering_models_are_registered(self):
        self.assertIn('kmeans', MODEL_REGISTRY)
        self.assertIn('dbscan', MODEL_REGISTRY)
        self.assertIn('agglomerative_clustering', MODEL_REGISTRY)
        self.assertIn('birch', MODEL_REGISTRY)
        self.assertIn('gaussian_mixture', MODEL_REGISTRY)
        self.assertIn('minibatch_kmeans', MODEL_REGISTRY)

    def test_get_model_instantiates_correctly(self):
        model_wrapper = get_model('LogisticRegression')
        from backend.wpa.auto_ml.models.linear_models import LogisticRegressionWrapper
        self.assertIsInstance(model_wrapper, LogisticRegressionWrapper)

if __name__ == '__main__':
    unittest.main()
