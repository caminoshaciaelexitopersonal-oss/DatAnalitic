import unittest
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from backend.wpa.auto_ml.pipelines.builder import create_full_pipeline

class TestPipelineBuilder(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            'numeric_1': [1, 2, 3, 4, 5],
            'numeric_2': [1.1, 2.2, 3.3, 4.4, 5.5],
            'categorical_1': ['A', 'B', 'A', 'C', 'B'],
            'text_1': ['this is text', 'more text here', 'text is good', 'a b c', 'd e f']
        })
        self.numeric_features = ['numeric_1', 'numeric_2']
        self.categorical_features = ['categorical_1']
        self.text_features = ['text_1']
        self.model = LogisticRegression()

    def test_create_basic_pipeline(self):
        pipeline = create_full_pipeline(
            model=self.model,
            problem_type='classification',
            numeric_features=self.numeric_features,
            categorical_features=self.categorical_features
        )
        self.assertIsInstance(pipeline, Pipeline)
        self.assertIn('preprocessor', pipeline.named_steps)
        self.assertIn('classifier', pipeline.named_steps)

    def test_create_pipeline_with_text_features(self):
        pipeline = create_full_pipeline(
            model=self.model,
            problem_type='classification',
            numeric_features=self.numeric_features,
            categorical_features=self.categorical_features,
            text_features=self.text_features
        )
        self.assertIsInstance(pipeline, Pipeline)
        preprocessor = pipeline.named_steps['preprocessor']
        self.assertIn('text', [t[0] for t in preprocessor.transformers])

    def test_create_pipeline_with_polynomial_features(self):
        feature_config = {
            'polynomial_features': {'enabled': True, 'degree': 2}
        }
        pipeline = create_full_pipeline(
            model=self.model,
            problem_type='classification',
            numeric_features=self.numeric_features,
            categorical_features=self.categorical_features,
            feature_engineering_config=feature_config
        )
        self.assertIsInstance(pipeline, Pipeline)
        self.assertIn('poly_features', pipeline.named_steps)

if __name__ == '__main__':
    unittest.main()
