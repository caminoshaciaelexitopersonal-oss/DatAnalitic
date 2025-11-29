import mlflow
from typing import List, Dict, Any
import os
import pandas as pd
import hashlib
import git
import matplotlib.pyplot as plt
import json

# Import the model library to ensure all models are registered
import backend.wpa.auto_ml.model_library

# Use absolute imports to fix module resolution issues in tests
from backend.wpa.auto_ml.trainer import train_model_with_cv
from backend.wpa.auto_ml.evaluator import evaluate_model
from backend.wpa.auto_ml.explainability import explain_model
from backend.wpa.auto_ml.exporter import export_model
from backend.wpa.auto_ml.model_card import create_model_card
from backend.wpa.auto_ml.selection_engine import select_best_model
from backend.wpa.auto_ml.data_utils import get_output_dir
from backend.wpa.auto_ml.pipelines.builder import create_full_pipeline
from backend.wpa.auto_ml.model_registry import MODEL_REGISTRY
from backend.core.state_store import StateStore

def run_automl_orchestration(
    job_id: str,
    user_id: str,
    state_store: StateStore,
    X_train, y_train, X_test, y_test,
    problem_type: str,
    numeric_features: List[str],
    categorical_features: List[str],
    model_candidates: List[str],
    scoring: str,
    use_hpo: bool = False
) -> Dict[str, Any]:
    """
    Orchestrates the full end-to-end AutoML process.
    """
    mlflow.set_experiment("SADI/auto_ml")

    # --- Standardized Metadata ---
    dataset_hash = hashlib.sha256(pd.util.hash_pandas_object(X_train, index=True).values).hexdigest()
    try:
        repo = git.Repo(search_parent_directories=True)
        git_commit = repo.head.object.hexsha
    except (git.InvalidGitRepositoryError, ValueError):
        git_commit = "unknown"

    with mlflow.start_run(run_name=f"automl_job_{job_id}") as parent_run:
        mlflow.log_param("job_id", job_id)
        mlflow.log_param("problem_type", problem_type)
        mlflow.set_tag("user_id", user_id)
        mlflow.set_tag("git_commit", git_commit)
        mlflow.set_tag("dataset_hash", dataset_hash)

        all_results = []

        for model_key in model_candidates:
            with mlflow.start_run(run_name=f"trial_{model_key}", nested=True) as child_run:
                run_id = child_run.info.run_id
                mlflow.log_param("model_key", model_key)

 
                model_class = MODEL_REGISTRY.get(model_key)
                if not model_class:
                    print(f"Model key {model_key} not found in registry. Skipping.")
                    continue

                model_wrapper = model_class()
                sklearn_model = model_wrapper.get_model()

                pipeline = create_full_pipeline(
                    model=sklearn_model,
                    problem_type=problem_type,
                    numeric_features=numeric_features,
                    categorical_features=categorical_features
                )
 

                training_result = train_model_with_cv(pipeline, X_train, y_train, scoring=scoring)

                if training_result["status"] != "success":
                    all_results.append(training_result)
                    continue

                mlflow.log_metric("cv_mean_score", training_result["cv_mean_score"])
                mlflow.log_metric("cv_std_score", training_result["cv_std_score"])
                mlflow.log_metric("fit_time", training_result["fit_time"])

                trained_pipeline = training_result["model"]
                evaluation_results = evaluate_model(trained_pipeline, X_test, y_test, problem_type)
                mlflow.log_metrics(evaluation_results["metrics"])
                mlflow.log_metrics(evaluation_results.get("fairness_metrics", {}))

 
                shap_artifacts = explain_model(trained_pipeline, X_train)
                if shap_artifacts:
                    # Save artifacts to state store
                    for name, fig in shap_artifacts.get("figure_artifacts", {}).items():
                        state_store.save_figure_artifact(job_id, f"explainability/{run_id}/{name}", fig)
                        plt.close(fig) # Close figure to free memory
                    for name, data in shap_artifacts.get("json_artifacts", {}).items():
                         state_store.save_json_artifact(job_id, f"explainability/{run_id}/{name}", data)

                    # Log to MLflow
                    temp_dir = f"/tmp/{run_id}"
                    os.makedirs(temp_dir, exist_ok=True)
                    for name, data in shap_artifacts.get("json_artifacts", {}).items():
                        with open(os.path.join(temp_dir, name), 'w') as f:
                            json.dump(data, f)
                    mlflow.log_artifacts(temp_dir, artifact_path="explainability")


                exported_path = export_model(trained_pipeline, model_key, get_output_dir(job_id), run_id)
 
                model_card = create_model_card(
                    model_key, training_result, evaluation_results, shap_artifacts
                )

                trial_result = {
                    **training_result,
                    "evaluation": evaluation_results,
                    "model_card": model_card,
                    "exported_path": exported_path,
                    "mlflow_run_id": run_id,
                    "model_key": model_key
                }
                all_results.append(trial_result)

 
        best_model_trial = select_best_model(all_results, metric_to_optimize=f"cv_mean_score")
 

        if best_model_trial:
            mlflow.set_tag("best_model", best_model_trial["model_key"])
            mlflow.log_metric("best_model_score", best_model_trial["cv_mean_score"])

        return {
            "all_results": all_results,
            "best_model_trial": best_model_trial
        }
