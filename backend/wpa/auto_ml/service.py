import pandas as pd
from typing import Dict, Any
import json
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import (
    f1_score, r2_score, accuracy_score, precision_score, recall_score, roc_auc_score,
    mean_absolute_error, mean_squared_error
)
import mlflow
import numpy as np

from backend.wpa.auto_ml.model_mapping import MODEL_MAP

class AutoMlService:
    """
    Service for running the automated machine learning pipeline.
    """
    def __init__(self, state_store):
        self.state_store = state_store
        with open('backend/config/config.json', 'r') as f:
            self.config = json.load(f)['ml_engine']

    def _detect_problem_type(self, X: pd.DataFrame, y: pd.Series = None) -> str:
        """Detects if the problem is classification, regression, clustering, or timeseries."""
        if y is None:
            # Simple heuristic: if no target, it could be clustering or anomaly detection
            # We will rely on the model type in MODEL_MAP to distinguish further.
            return "unsupervised"

        # Check for datetime column for timeseries forecasting
        if X.select_dtypes(include=['datetime64']).shape[1] > 0:
            return "timeseries"

        if y.dtype in ['int64', 'object', 'category'] and y.nunique() / len(y) < 0.2:
            return "classification"
        else:
            return "regression"

    def run_automl_pipeline(self, job_id: str, df: pd.DataFrame, target_variable: str) -> Dict[str, Any]:
        """
        Orchestrates the AutoML process: problem detection, model training,
        evaluation, and selection.
        """
        print(f"[{job_id}] Starting AutoML pipeline for target: {target_variable}")

        y = None
        if target_variable:
            X = df.drop(columns=[target_variable])
            y = df[target_variable]
        else:
            X = df

        # Keep datetime columns for timeseries
        feature_cols = X.select_dtypes(include=['number', 'category', 'object', 'datetime64']).columns.tolist()
        X = X[feature_cols]

        problem_type = self._detect_problem_type(X, y)
        print(f"[{job_id}] Detected problem type: {problem_type}")

        X_train, X_test, y_train, y_test = (None, None, None, None)
        if problem_type == "timeseries":
            # Time-based split
            split_point = int(len(df) * 0.8)
            X_train, X_test = X[:split_point], X[split_point:]
            y_train, y_test = y[:split_point], y[split_point:]
        elif y is not None:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        else: # Unsupervised
            X_train = X

        # --- Create a robust preprocessing pipeline ---
        numeric_features = X_train.select_dtypes(include=['number']).columns.tolist()
        categorical_features = X_train.select_dtypes(include=['category', 'object']).columns.tolist()

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ],
            remainder='passthrough'
        )

        results = []
        best_model_pipeline = None
        best_score = -1

        for model_name, params in self.config['algorithms'].items():
            if not params['enabled']:
                continue

            model_info = MODEL_MAP.get(model_name)
            if not model_info or model_info['type'] != problem_type:
                continue

            with mlflow.start_run(run_name=f"{job_id}_{model_name}", nested=True):
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("problem_type", problem_type)

                try:
                    print(f"[{job_id}] Training {model_name}...")

                    # Create a full pipeline with preprocessing and the model
                    model_pipeline = Pipeline(steps=[
                        ('preprocessor', preprocessor),
                        ('model', model_info['model']())
                    ])

                    model_pipeline.fit(X_train, y_train) # y_train will be None for clustering

                    if problem_type in ["classification", "regression"]:
                        y_pred = model_pipeline.predict(X_test)

                        metrics = {}
                        score = 0

                        if problem_type == "classification":
                            # Handling binary vs multiclass for metrics like roc_auc
                            is_multiclass = len(np.unique(y_train)) > 2
                            average_method = 'weighted' if is_multiclass else 'binary'

                            metrics = {
                                "accuracy": accuracy_score(y_test, y_pred),
                                "f1_score": f1_score(y_test, y_pred, average=average_method),
                                "precision": precision_score(y_test, y_pred, average=average_method, zero_division=0),
                                "recall": recall_score(y_test, y_pred, average=average_method, zero_division=0),
                            }
                            # roc_auc_score requires predict_proba for multiclass
                            if hasattr(model_pipeline, "predict_proba"):
                                y_proba = model_pipeline.predict_proba(X_test)
                                if is_multiclass:
                                    metrics["roc_auc"] = roc_auc_score(y_test, y_proba, multi_class='ovr')
                                else:
                                    metrics["roc_auc"] = roc_auc_score(y_test, y_proba[:, 1])

                            score = metrics["f1_score"] # Use F1 as the primary score for ranking

                        else: # regression
                            metrics = {
                                "r2_score": r2_score(y_test, y_pred),
                                "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                                "mae": mean_absolute_error(y_test, y_pred),
                            }
                            score = metrics["r2_score"] # Use R2 as the primary score for ranking

                        mlflow.log_metrics(metrics)
                        print(f"[{job_id}] ... {model_name} score: {score:.4f}")
                        results.append({"model": model_name, "score": score, "metrics": metrics})

                        if score > best_score:
                            best_score = score
                            best_model_pipeline = model_pipeline
                            mlflow.sklearn.log_model(model_pipeline, "best-model-pipeline")
                    else: # clustering
                        print(f"[{job_id}] ... {model_name} fitted.")
                        results.append({"model": model_name, "score": "N/A"})
                        # For clustering, we can consider the first model as the "best" for now
                        if best_model_pipeline is None:
                            best_model_pipeline = model_pipeline
                            mlflow.sklearn.log_model(model_pipeline, "best-model-pipeline")

                except Exception as e:
                    print(f"[{job_id}] Failed to train {model_name}. Error: {e}")
                    mlflow.log_param("error", str(e))

        results.sort(key=lambda x: x.get('score', -1), reverse=True)
        best_result = results[0] if results else {}

        automl_artifacts = {
            "summary": {
                "problem_type": problem_type,
                "best_model_name": best_result.get('model', "None"),
                "best_model_score": best_result.get('score', -1),
                "best_model_metrics": best_result.get('metrics', {}),
                "ranking": results,
            },
            "best_model": best_model_pipeline,
            "feature_importance": None # Placeholder
        }

        return automl_artifacts
