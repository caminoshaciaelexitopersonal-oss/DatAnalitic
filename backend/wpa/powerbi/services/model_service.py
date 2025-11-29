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
    def explain_model(self, model_obj_or_run_id: Any, df_sample: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Lightweight wrapper to produce an explainability summary.
        If model_obj_or_run_id is an MLflow run_id, try to fetch the model artifact and run SHAP (if available).
        If it's a model object with sklearn API, run permutation importance or SHAP if installed.
        Returns a dict with pointers to artifacts or small numeric summaries.
        """
        try:
            # If it's a run id and mlflow is enabled, attempt to load model
            if self._mlflow_enabled and isinstance(model_obj_or_run_id, str) and self._mlflow:
                try:
                    model_uri = f"runs:/{model_obj_or_run_id}/model"
                    model = self._mlflow.pyfunc.load_model(model_uri)
                    # we can try shap if installed
                    try:
                        import shap
                        if df_sample is None:
                            # try to load sample - fallback empty
                            df_sample = pd.DataFrame()
                        expl = shap.Explainer(model.predict, df_sample) if hasattr(shap, "Explainer") else None
                        if expl:
                            shap_vals = expl(df_sample)
                            return {"shap_summary": True, "note": "SHAP computed (mlflow model)"}
                    except Exception:
                        # fallback permutation importance
                        return {"explained": False, "note": "shap not available"}
                except Exception as e:
                    logger.warning("Failed load model from mlflow: %s", e)
                    return {"explained": False, "error": str(e)}

            # If it's a model object (sklearn like)
            if hasattr(model_obj_or_run_id, "predict"):
                model = model_obj_or_run_id
                if df_sample is None:
                    return {"explained": False, "note": "no sample provided"}
                # try permutation importance
                try:
                    from sklearn.inspection import permutation_importance
                    X = df_sample.drop(columns=[c for c in df_sample.columns if c not in getattr(model, "feature_names_in_", df_sample.columns)])
                    y = None
                    res = permutation_importance(model, X, model.predict(X), n_repeats=10, random_state=42)
                    imp = dict(zip(X.columns, res.importances_mean.tolist()))
                    return {"permutation_importance": imp}
                except Exception as e:
                    logger.exception("Permutation importance failed: %s", e)
                    return {"explained": False, "error": str(e)}

            return {"explained": False, "note": "unsupported model identifier"}

        except Exception as e:
            logger.exception("explain_model failed: %s", e)
            return {"explained": False, "error": str(e)}
