import unittest
from backend.wpa.auto_ml.selection_engine import select_best_model

class TestSelectionEngine(unittest.TestCase):

    def test_select_best_model(self):
        results = [
            {'status': 'success', 'cv_mean_score': 0.8},
            {'status': 'success', 'cv_mean_score': 0.9},
            {'status': 'failure', 'cv_mean_score': 0.7}
        ]

        best_model = select_best_model(results, 'cv_mean_score')
        self.assertEqual(best_model['cv_mean_score'], 0.9)

    def test_select_best_model_empty_list(self):
        best_model = select_best_model([], 'cv_mean_score')
        self.assertIsNone(best_model)

if __name__ == '__main__':
    unittest.main()
