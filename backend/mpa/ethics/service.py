import mlflow
from typing import Dict, Any
from sklearn.base import is_classifier
from fairlearn.metrics import MetricFrame, selection_rate
import pandas as pd
import tempfile
import os

class AIEthicsService:
    """
    MPA service for AI ethics tasks, including bias audits and model card generation.
    """
    def __init__(self, mlflow_tracking_uri: str):
        mlflow.set_tracking_uri(mlflow_tracking_uri)

    def run_bias_audit(self, run_id: str, sensitive_feature: str, label_column: str) -> Dict[str, Any]:
        """
        Runs a bias audit on a trained model from an MLflow run.
        """
        # Load the model and dataset from MLflow artifacts
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.sklearn.load_model(model_uri)

        dataset_path = self._download_artifact(run_id, "data/processed_data.parquet")
        if not dataset_path:
            raise FileNotFoundError("Could not find processed_data.parquet artifact for the given run.")

        data = pd.read_parquet(dataset_path)

        if sensitive_feature not in data.columns or label_column not in data.columns:
            raise ValueError("Sensitive feature or label column not in the dataset.")

        y_true = data[label_column]
        y_pred = model.predict(data.drop(columns=[label_column]))
        sensitive_features = data[sensitive_feature]

        # Use MetricFrame from Fairlearn to calculate metrics grouped by sensitive feature
        metrics = {'selection_rate': selection_rate}
        grouped_on_feature = MetricFrame(metrics=metrics,
                                         y_true=y_true,
                                         y_pred=y_pred,
                                         sensitive_features=sensitive_features)

        return {
            "overall_selection_rate": grouped_on_feature.overall,
            "selection_rate_by_group": grouped_on_feature.by_group,
            "disparity": grouped_on_feature.difference(),
        }

    def generate_model_card(self, run_id: str) -> str:
        """
        Generates a Model Card in Markdown format for a given MLflow run.
        """
        run = mlflow.get_run(run_id)
        params = run.data.params
        metrics = run.data.metrics

        model_card = f"""
# Model Card for Run: {run_id}

## Model Details
- **Model Type:** {params.get('model_type', 'N/A')}
- **Training Date:** {run.info.start_time.strftime('%Y-%m-%d %H:%M:%S')}

## Performance Metrics
| Metric | Value |
|--------|-------|
"""
        for key, value in metrics.items():
            model_card += f"| {key} | {value:.4f} |\n"

        model_card += "\n## Intended Use\n- This model is intended for...\n"
        model_card += "\n## Ethical Considerations\n- Potential biases related to... should be monitored.\n"

        # Save the model card as an artifact
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write(model_card)
            tmp_path = tmp.name

        mlflow.log_artifact(tmp_path, "model_card")
        os.remove(tmp_path)

        return model_card

    def _download_artifact(self, run_id: str, artifact_path: str) -> str:
        """Helper to download an artifact to a temporary directory."""
        try:
            return mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path=artifact_path)
        except Exception:
            return None

# --- Dependency Injection ---
def get_ai_ethics_service() -> AIEthicsService:
    # This service is stateful regarding MLflow URI, but for now, we can instantiate it
    # directly. A more robust implementation might use a singleton with configuration.
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    return AIEthicsService(mlflow_tracking_uri=tracking_uri)
