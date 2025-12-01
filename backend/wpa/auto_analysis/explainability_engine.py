import pandas as pd
import shap
import mlflow
import matplotlib.pyplot as plt
from typing import Dict, Any
import os
import tempfile

class ExplainabilityEngine:
    """
    Generates and logs SHAP-based explanations for a trained model.
    """
    def __init__(self, df: pd.DataFrame, target: str, best_model_run_id: str):
        self.df = df
        self.target = target
        self.run_id = best_model_run_id
        self.model = self._load_model()

    def _load_model(self):
        """Loads the scikit-learn model from the specified MLflow run."""
        model_uri = f"runs:/{self.run_id}/model"
        return mlflow.sklearn.load_model(model_uri)

    def _get_transformed_data(self) -> pd.DataFrame:
        """Applies the preprocessing pipeline to the input data."""
        X = self.df.drop(columns=[self.target])

        # The preprocessor is the first step in the pipeline
        preprocessor = self.model.steps[0][1]
        transformed_X = preprocessor.transform(X)

        # Get feature names after transformation (e.g., after one-hot encoding)
        feature_names = preprocessor.get_feature_names_out()

        return pd.DataFrame(transformed_X, columns=feature_names, index=X.index)

    def run_and_log_explanations(self):
        """
        Generates SHAP summary and feature importance plots and logs them to MLflow.
        """
        transformed_X = self._get_transformed_data()

        # The actual model is the second step in the pipeline
        model = self.model.steps[1][1]

        # 1. Generate SHAP explanations
        explainer = shap.Explainer(model, transformed_X)
        shap_values = explainer(transformed_X)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 2. Create and save SHAP summary plot
            plt.figure()
            shap.summary_plot(shap_values, transformed_X, show=False)
            summary_path = os.path.join(tmpdir, "shap_summary.png")
            plt.savefig(summary_path)
            plt.close()
            mlflow.log_artifact(summary_path, "explainability", run_id=self.run_id)

            # 3. Create and save Feature Importance plot (if available)
            if hasattr(model, 'feature_importances_'):
                plt.figure()
                importances = model.feature_importances_
                feature_names = transformed_X.columns
                feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
                feature_importance_df = feature_importance_df.sort_values('importance', ascending=False).head(20)

                plt.barh(feature_importance_df['feature'], feature_importance_df['importance'])
                plt.title('Top 20 Feature Importances')
                plt.gca().invert_yaxis()
                plt.tight_layout()

                importance_path = os.path.join(tmpdir, "feature_importance.png")
                plt.savefig(importance_path)
                plt.close()
                mlflow.log_artifact(importance_path, "explainability", run_id=self.run_id)
