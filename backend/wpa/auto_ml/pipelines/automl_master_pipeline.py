import mlflow
from typing import List, Dict, Any
import os
import pandas as pd
import hashlib
import git

from .pipelines.builder import create_full_pipeline
from .trainer import train_model_with_cv, hpo_search
from .evaluator import evaluate_model
from .explainability import explain_model
from .exporter import export_model
from .model_card import create_model_card
from .selection_engine import select_best_model
from .utils import get_output_dir  # Assuming a utility for consistent pathing

def run_automl_orchestration(
    job_id: str,
    user_id: str,
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
    output_dir = get_output_dir(job_id)

    # --- Standardized Metadata ---
    # 1. Dataset Hash
    dataset_hash = hashlib.sha256(pd.util.hash_pandas_object(X_train, index=True).values).hexdigest()
    # 2. Git Commit
    try:
        repo = git.Repo(search_parent_directories=True)
        git_commit = repo.head.object.hexsha
    except (git.InvalidGitRepositoryError, ValueError):
        git_commit = "unknown"

    with mlflow.start_run(run_name=f"automl_job_{job_id}") as parent_run:
        # Log parameters for filtering
        mlflow.log_param("job_id", job_id)
        mlflow.log_param("problem_type", problem_type)

        # Set tags for rich, non-filterable metadata
        mlflow.set_tag("user_id", user_id)
        mlflow.set_tag("git_commit", git_commit)
        mlflow.set_tag("dataset_hash", dataset_hash)

        all_results = []

        for model_key in model_candidates:
            with mlflow.start_run(run_name=f"trial_{model_key}", nested=True) as child_run:
                run_id = child_run.info.run_id
                mlflow.log_param("model_key", model_key)

                # 1. Pipeline Creation & Training
                # For now, using a default transformer. Could be part of the search space.
                pipeline = create_full_pipeline(model_key, numeric_features, categorical_features)

                # The trainer now receives the full pipeline
                training_result = train_model_with_cv(pipeline, X_train, y_train, scoring=scoring)

                if training_result["status"] != "success":
                    all_results.append(training_result)
                    continue

                mlflow.log_metric("cv_mean_score", training_result["cv_mean_score"])
                mlflow.log_metric("cv_std_score", training_result["cv_std_score"])
                mlflow.log_metric("fit_time", training_result["fit_time"])

                # 2. Evaluation
                trained_pipeline = training_result["model"]
                evaluation_results = evaluate_model(trained_pipeline, X_test, y_test, problem_type)
                mlflow.log_metrics(evaluation_results["metrics"])
                mlflow.log_metrics(evaluation_results.get("fairness_metrics", {}))

                # 3. Explainability
                shap_artifacts = explain_model(trained_pipeline, X_train, output_dir, run_id)
                if shap_artifacts:
                    mlflow.log_artifacts(shap_artifacts["path"], artifact_path="explainability")

                # 4. Export and Model Card
                exported_path = export_model(trained_pipeline, model_key, output_dir, run_id)
                model_card = create_model_card(
                    model_key, training_result, evaluation_results, shap_artifacts
                )

                # Consolidate results for this model trial
                trial_result = {
                    **training_result,
                    "evaluation": evaluation_results,
                    "model_card": model_card,
                    "exported_path": exported_path,
                    "mlflow_run_id": run_id
                }
                all_results.append(trial_result)

        best_model_trial = select_best_model(all_results, metric_to_optimize=f"cv_mean_{scoring}")

        if best_model_trial:
            mlflow.set_tag("best_model", best_model_trial["model_key"])
            mlflow.log_metric("best_model_score", best_model_trial["cv_mean_score"])

        return {
            "all_results": all_results,
            "best_model_trial": best_model_trial
        }
