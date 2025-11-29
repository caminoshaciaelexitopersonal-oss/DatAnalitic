import unittest

class TestAutoMLModuleImports(unittest.TestCase):
    def test_imports(self):
        try:
            from backend.wpa.auto_ml import api
            from backend.wpa.auto_ml import automl_recommender
            from backend.wpa.auto_ml import data_utils
            from backend.wpa.auto_ml import evaluator
            from backend.wpa.auto_ml import explainability
            from backend.wpa.auto_ml import exporter
            from backend.wpa.auto_ml import hpo_service
            from backend.wpa.auto_ml import model_card
            from backend.wpa.auto_ml import model_library
            from backend.wpa.auto_ml import model_registry
            from backend.wpa.auto_ml import schemas
            from backend.wpa.auto_ml import scoring
            from backend.wpa.auto_ml import selection_engine
            from backend.wpa.auto_ml import tasks
            from backend.wpa.auto_ml import trainer
            from backend.wpa.auto_ml import utils
            from backend.wpa.auto_ml.controllers import automl_controller
            from backend.wpa.auto_ml.pipelines import automl_master_pipeline
            from backend.wpa.auto_ml.pipelines import builder
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import module: {e}")

if __name__ == '__main__':
    unittest.main()
