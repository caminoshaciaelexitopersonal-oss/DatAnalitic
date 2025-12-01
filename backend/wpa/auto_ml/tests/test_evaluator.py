import unittest
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import Pipeline
from backend.wpa.auto_ml.evaluator import evaluate_model
from backend.wpa.auto_ml.pipelines.builder import create_full_pipeline

class TestEvaluator(unittest.TestCase):

    def setUp(self):
        # Classification data
        self.X_cls = pd.DataFrame({'feature1': [1, 2, 3, 4], 'feature2': ['A', 'B', 'A', 'B']})
        self.y_cls = pd.Series([0, 1, 0, 1])
        cls_model = LogisticRegression()
        self.cls_pipeline = create_full_pipeline(
            cls_model, 'classification', ['feature1'], ['feature2']
        )
        self.cls_pipeline.fit(self.X_cls, self.y_cls)

        # Regression data
        self.X_reg = pd.DataFrame({'feature1': [1, 2, 3, 4]})
        self.y_reg = pd.Series([1.1, 2.2, 3.3, 4.4])
        reg_model = LinearRegression()
        self.reg_pipeline = create_full_pipeline(
            reg_model, 'regression', ['feature1'], []
        )
        self.reg_pipeline.fit(self.X_reg, self.y_reg)

    def test_evaluate_classification_model(self):
        results = evaluate_model(self.cls_pipeline, self.X_cls, self.y_cls, 'classification')
        self.assertIn('metrics', results)
        self.assertIn('accuracy', results['metrics'])
        self.assertIn('f1_score', results['metrics'])
        self.assertIn('roc_auc', results['metrics'])

    def test_evaluate_regression_model(self):
        results = evaluate_model(self.reg_pipeline, self.X_reg, self.y_reg, 'regression')
        self.assertIn('metrics', results)
        self.assertIn('mse', results['metrics'])
        self.assertIn('r2_score', results['metrics'])

if __name__ == '__main__':
    unittest.main()
