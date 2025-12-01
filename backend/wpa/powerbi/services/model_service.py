"""
model_service.py

Service that wraps the AutoML recommender (automl_recommender.py),
provides chart/model recommendations and light AutoML orchestration.

Key functions:
  - recommend_dashboard(dataset_name, sample_limit=5000)
  - is_ready()
  - explain_model(run_id or model_obj)
  - quick_autopredictability(dataset_name, target, max_samples=2000)

Integrations:
  - DataService to fetch dataframes
  - automl_recommender.AutoMLRecommender (cheap, local)
  - Optional MLflow logging (if MLFLOW_TRACKING_URI set)
"""

import os
import json
import logging
from typing import Dict, Any, Optional

import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc

from backend.wpa.powerbi.services.data_service import DataService
from backend.wpa.auto_ml.automl_recommender import AutoMLRecommender

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

DATA_SERVICE = DataService()
RECOMMENDER = AutoMLRecommender(verbose=False)


class ModelService:
    def __init__(self, mlflow_enabled: Optional[bool] = None):
        self._ready = True
        self._mlflow_enabled = mlflow_enabled if mlflow_enabled is not None else bool(os.environ.get("MLFLOW_TRACKING_URI"))
        if self._mlflow_enabled:
            try:
                import mlflow
                self._mlflow = mlflow
            except Exception:
                logger.warning("mlflow not installed or configured; disabling mlflow integration")
                self._mlflow_enabled = False
                self._mlflow = None
        else:
            self._mlflow = None

    def is_ready(self) -> bool:
        """Return true if service initialization succeeded."""
        return self._ready

    # ---------------------------
    # Main recommendation entrypoint
    # ---------------------------
    def recommend_dashboard(self, dataset_name: str, sample_limit: int = 5000) -> Dict[str, Any]:
        """
        dataset_name: a path, table name or special identifier recognized by DataService.execute_query
        sample_limit: number of rows to sample for profiling
        Returns the recommendation dict produced by AutoMLRecommender.
        """
        logger.info("recommend_dashboard called for %s (sample=%s)", dataset_name, sample_limit)
        # create query request accepted by DataService
        req = {"source": "local", "path": dataset_name, "limit": sample_limit}
        # If dataset_name is not a path and looks like a registered data source, you can change source to 'sql' or others
        try:
            df = DATA_SERVICE.execute_query(req)
        except Exception as e:
            logger.exception("Failed to load dataset %s: %s", dataset_name, e)
            raise

        # limit columns for extremely wide datasets
        max_cols = int(os.environ.get("SADI_RECOMMENDER_MAX_COLS", 200))
        if df.shape[1] > max_cols:
            logger.info("Dataset has %s cols, sampling first %s cols for performance", df.shape[1], max_cols)
            df = df.iloc[:, :max_cols]

        rec = RECOMMENDER.recommend(df, max_samples=sample_limit)

        # Optionally log to MLflow as artifact
        if self._mlflow_enabled and self._mlflow:
            try:
                run = self._mlflow.start_run(run_name=f"recommendation/{os.path.basename(dataset_name)}")
                self._mlflow.log_dict(rec, "recommendation.json")
                self._mlflow.end_run()
            except Exception as e:
                logger.warning("Failed to log recommendation to MLflow: %s", e)

        return rec

    # ---------------------------
    # Quick predictability helper
    # ---------------------------
    def quick_autopredictability(self, dataset_name: str, target: str, max_samples: int = 2000) -> Dict[str, Any]:
        """
        Runs the quick_predictability function from recommender on the named dataset/target.
        """
        req = {"source": "local", "path": dataset_name, "limit": max_samples}
        df = DATA_SERVICE.execute_query(req)
        # forward to quick_predictability in recommender
        from backend.wpa.auto_ml.automl_recommender import quick_predictability
        return quick_predictability(df, target, max_samples=max_samples)

    # ---------------------------
    # Explain model placeholder
    # ---------------------------
    # ---------------------------
    # ML Visualization Data Generators
    # ---------------------------
    def get_confusion_matrix(self, model_obj: Any, df_test: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """Calculates confusion matrix."""
        X_test = df_test.drop(columns=[target_col])
        y_true = df_test[target_col]
        y_pred = model_obj.predict(X_test)

        cm = confusion_matrix(y_true, y_pred)
        labels = model_obj.classes_ if hasattr(model_obj, 'classes_') else ['0', '1']

        return {"matrix": cm.tolist(), "labels": [str(l) for l in labels]}

    def get_roc_curve(self, model_obj: Any, df_test: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """Calculates ROC curve data."""
        if not hasattr(model_obj, "predict_proba"):
            return {"error": "Model does not support predict_proba, cannot generate ROC curve."}

        X_test = df_test.drop(columns=[target_col])
        y_true = df_test[target_col]
        y_scores = model_obj.predict_proba(X_test)[:, 1]

        fpr, tpr, _ = roc_curve(y_true, y_scores)
        roc_auc = auc(fpr, tpr)

        return {
            "points": [{"fpr": f, "tpr": t} for f, t in zip(fpr, tpr)],
            "auc": roc_auc
        }

    def explain_model(self, model_obj_or_run_id: Any, df_sample: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Produces an explainability summary, focusing on permutation importance.
        """
        try:
            model = None
            if self._mlflow_enabled and isinstance(model_obj_or_run_id, str) and self._mlflow:
                try:
                    model_uri = f"runs:/{model_obj_or_run_id}/model"
                    model = self._mlflow.pyfunc.load_model(model_uri)
                except Exception as e:
                    logger.warning("Failed to load model from mlflow: %s", e)
                    return {"error": str(e)}
            elif hasattr(model_obj_or_run_id, "predict"):
                model = model_obj_or_run_id

            if model is None:
                return {"error": "Unsupported model identifier"}

            if df_sample is None:
                return {"error": "Sample dataframe not provided for explanation"}

            # Permutation Importance is more universally applicable than SHAP
            try:
                from sklearn.inspection import permutation_importance

                # Align columns with model's expected features
                model_features = getattr(model, "feature_names_in_", df_sample.columns.drop(df_sample.columns[-1])) # Heuristic
                X = df_sample[model_features]
                y = df_sample.iloc[:, -1] # Heuristic for target column

                res = permutation_importance(model, X, y, n_repeats=10, random_state=42)

                importances = [{"feature": f, "importance": float(i)} for f, i in zip(X.columns, res.importances_mean)]
                importances.sort(key=lambda x: x["importance"], reverse=True)

                return {"permutation_importance": importances}

            except Exception as e:
                logger.exception("Permutation importance failed: %s", e)
                return {"error": str(e)}

        except Exception as e:
            logger.exception("explain_model failed: %s", e)
            return {"error": str(e)}
