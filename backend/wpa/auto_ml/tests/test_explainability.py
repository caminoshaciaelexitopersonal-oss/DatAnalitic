import unittest
import pandas as pd
from sklearn.linear_model import LogisticRegression
from backend.wpa.auto_ml.pipelines.builder import create_full_pipeline
from backend.wpa.auto_ml.explainability import explain_model

class TestExplainability(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            'numeric_1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'categorical_1': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C'],
            'target': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        })
        self.numeric_features = ['numeric_1']
        self.categorical_features = ['categorical_1']
        self.X = self.data[self.numeric_features + self.categorical_features]
        self.y = self.data['target']

        self.model = LogisticRegression()
        self.pipeline = create_full_pipeline(
            model=self.model,
            problem_type='classification',
            numeric_features=self.numeric_features,
            categorical_features=self.categorical_features
        )
        self.pipeline.fit(self.X, self.y)

    def test_explain_model_returns_artifacts(self):
        artifacts = explain_model(self.pipeline, self.X)

        self.assertIsNotNone(artifacts)
        self.assertIn('json_artifacts', artifacts)
        self.assertIn('figure_artifacts', artifacts)
        self.assertIn('shap_summary.json', artifacts['json_artifacts'])
        self.assertIn('shap_summary_bar.png', artifacts['figure_artifacts'])

if __name__ == '__main__':
    unittest.main()
