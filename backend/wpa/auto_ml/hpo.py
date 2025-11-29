from backend.celery_worker import celery_app
from backend.wpa.auto_ml.hpo_service import HPOService
from backend.core.state_store import StateStore
from backend.wpa.auto_ml.model_registry import get_model
import pandas as pd
import io
import mlflow

@celery_app.task(name="automl.run_hpo_study")
def run_hpo_study(job_id: str, request: dict):
    """
    Celery task to run an HPO study.
    """
    state_store = StateStore()

    try:
        # Load data from StateStore
        X_train_bytes = state_store.load_artifact_as_bytes(job_id, "X_train.parquet")
        X_train_df = pd.read_parquet(io.BytesIO(X_train_bytes))

        y_train_bytes = state_store.load_artifact_as_bytes(job_id, "y_train.parquet")
        y_train_df = pd.read_parquet(io.BytesIO(y_train_bytes))

        y_train = y_train_df.squeeze()

        # Get model wrapper
        model_wrapper = get_model(request['model_name'])

        # Start MLflow run
        with mlflow.start_run(run_name=f"hpo_study_{job_id}_{request['model_name']}") as parent_run:
            mlflow.log_param("job_id", job_id)
            mlflow.log_param("model_name", request['model_name'])

            # Instantiate and run HPOService
            hpo_service = HPOService(
                model_wrapper=model_wrapper,
                X=X_train_df,
                y=y_train,
                n_trials=request['n_trials'],
                scoring=request['scoring']
            )
            best_params = hpo_service.optimize()

            # Log best params to parent run
            mlflow.log_params({"best_params": best_params})

            # Save results
            state_store.save_json_artifact(job_id, f"hpo_results_{request['model_name']}.json", best_params)
            state_store.save_job_status(job_id, {"status": "completed", "stage": "hpo"})

        return {"status": "SUCCESS", "best_params": best_params}

    except Exception as e:
        state_store.save_job_status(job_id, {"status": "failed", "stage": "hpo", "error": str(e)})
        return {"status": "FAILURE", "error": str(e)}
