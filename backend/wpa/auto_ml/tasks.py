import io
from backend.celery_worker import celery_app
 
from backend.wpa.auto_ml.pipelines.automl_master_pipeline import run_automl_orchestration
from backend.core.state_store import StateStore
import pandas as pd
 

@celery_app.task(name="automl.run_full_automl")
def run_full_automl(job_id: str, request: dict):
    """
    Celery task to run the full AutoML pipeline.
    NOTE: The underlying implementation is currently broken and disabled.
    """
 
    state_store = StateStore()

    try:
        # Load data from StateStore, wrapping bytes in BytesIO for pandas
        X_train_bytes = state_store.load_artifact_as_bytes(job_id, "X_train.parquet")
        X_train_df = pd.read_parquet(io.BytesIO(X_train_bytes))

        y_train_bytes = state_store.load_artifact_as_bytes(job_id, "y_train.parquet")
        y_train_df = pd.read_parquet(io.BytesIO(y_train_bytes))

        X_test_bytes = state_store.load_artifact_as_bytes(job_id, "X_test.parquet")
        X_test_df = pd.read_parquet(io.BytesIO(X_test_bytes))

        y_test_bytes = state_store.load_artifact_as_bytes(job_id, "y_test.parquet")
        y_test_df = pd.read_parquet(io.BytesIO(y_test_bytes))

        metadata = state_store.load_json_artifact(job_id, "metadata.json")

        y_train = y_train_df.squeeze()
        y_test = y_test_df.squeeze()

        # Extract parameters from request and metadata
        problem_type = metadata.get("problem_type")
        target_column = metadata.get("target_column")
        numeric_features = [c for c in X_train_df.columns if X_train_df[c].dtype != 'object']
        categorical_features = [c for c in X_train_df.columns if X_train_df[c].dtype == 'object']

        model_candidates = request.get("model_candidates", ["LogisticRegression", "RandomForestClassifier"])
        scoring = request.get("scoring", "accuracy" if problem_type == "classification" else "r2")

        # Run the orchestration
        results = run_automl_orchestration(
            job_id=job_id,
            user_id=request.get("user_id", "default_user"),
            state_store=state_store,
            X_train=X_train_df,
            y_train=y_train,
            X_test=X_test_df,
            y_test=y_test,
            problem_type=problem_type,
            numeric_features=numeric_features,
            categorical_features=categorical_features,
            model_candidates=model_candidates,
            scoring=scoring
        )

        # Store results
        state_store.save_json_artifact(job_id, "automl_results.json", results)
        state_store.save_job_status(job_id, {"status": "completed", "stage": "automl"})

        return {"status": "SUCCESS", "results_summary": f"Best model: {results.get('best_model_trial', {}).get('model_key')}"}

    except Exception as e:
        state_store.save_job_status(job_id, {"status": "failed", "stage": "automl", "error": str(e)})
        return {"status": "FAILURE", "error": str(e)}
 
