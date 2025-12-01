"""
This module contains the master Celery task orchestrator for the WPA layer,
ensuring full system interoperability by using the StateStore for all I/O.
"""
import uuid
import pandas as pd
import mlflow
from fastapi import UploadFile
from io import BytesIO

from backend.celery_worker import celery_app
from backend.core.state_store import get_state_store
from backend.wpa.auto_analysis.target_detector import detect_target
from backend.wpa.auto_analysis.eda_intelligent_service import EDAIntelligentService
from backend.mpa.ingestion.service import get_ingestion_service
from backend.mpa.etl.service import EtlService
from backend.wpa.auto_ml.service import AutoMlService

@celery_app.task(name="wpa.master_pipeline_task")
def master_pipeline_task(job_id: str):
    """
    The master orchestrator task for the SADI analysis pipeline, refactored to be stateless.
    It reads inputs from the StateStore and writes all artifacts back to it.
    """
    state_store = get_state_store()
    manifest = {"job_id": job_id, "steps": []}

    try:
        # --- Step 1: Data Ingestion & Validation ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Ingesting Data"})

        job = state_store.get_job(uuid.UUID(job_id))
        if not job or not job.original_filename:
            raise ValueError(f"Job or original_filename not found for job_id: {job_id}")

        raw_file_bytes = state_store.load_raw_file(job_id, job.original_filename)
        if not raw_file_bytes:
            raise FileNotFoundError(f"Raw file not found in storage for job_id: {job_id}")

        # Use the IngestionService to process the file correctly
        # NOTE: Since this is a Celery task (sync), we need to run the async service method in an event loop.
        import asyncio
        from backend.mpa.ingestion.service import get_ingestion_service

        # Resolve services using the application's dependency injectors
        ingestion_service = get_ingestion_service(state_store=state_store)

        mock_upload_file = UploadFile(filename=job.original_filename, file=raw_file_bytes)
        df = asyncio.run(ingestion_service.process_uploaded_file(mock_upload_file, job_id))

        if df is None:
            raise ValueError("Dataframe could not be processed by IngestionService.")

        manifest["steps"].append({"step": "ingestion", "status": "completed"})

        # --- Step 2: Data Cleaning & Standardization ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Cleaning Data"})
        etl_service = EtlService(state_store=state_store)
        cleaned_df = etl_service.standardize_df(df)
        state_store.save_dataframe(job_id, cleaned_df) # Overwrite with the cleaned version
        df = cleaned_df # Continue with the cleaned dataframe

        manifest["steps"].append({"step": "cleaning", "status": "completed"})


        # --- Step 3: Target Detection ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Target Detection"})
        target_results = detect_target(df, job_id)

        state_store.save_json_artifact(job_id, "target.json", target_results["target_decision"])
        state_store.save_json_artifact(job_id, "eda/summary.json", target_results["eda_summary"])

        manifest["dataset_hash"] = target_results["dataset_hash"]
        manifest["steps"].append({"step": "target_detection", "status": "completed", "result": target_results["target_decision"]})
        selected_target = target_results["target_decision"].get("selected_target")

        # --- Step 4: Exploratory Data Analysis (EDA) ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "EDA"})
        inferred_types = {col: 'numeric' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical' for col in df.columns}

        eda_service = EDAIntelligentService(df, inferred_types)
        eda_artifacts = eda_service.run_automated_eda()

        for name, artifact in eda_artifacts["json_artifacts"].items():
            state_store.save_json_artifact(job_id, f"eda/{name}", artifact)
        for name, fig in eda_artifacts["figure_artifacts"].items():
            if fig is not None:
                state_store.save_figure_artifact(job_id, f"eda/{name}", fig)

        manifest["steps"].append({"step": "eda", "status": "completed"})

        # --- Step 5: AutoML (Conditional) ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "AutoML"})
        if selected_target:
            automl_service = AutoMlService(state_store)
            automl_artifacts = automl_service.run_automl_pipeline(job_id, df, selected_target)

            # Save artifacts
            state_store.save_json_artifact(job_id, "automl_summary.json", automl_artifacts["summary"])
            if automl_artifacts["best_model"]:
                import pickle
                model_bytes = pickle.dumps(automl_artifacts["best_model"])
                state_store.save_report_artifact(job_id, "best_model.pkl", model_bytes) # Using save_report_artifact for simplicity

            manifest["steps"].append({"step": "automl", "status": "completed", "result": automl_artifacts["summary"]})
        else:
            print(f"INFO: Skipping AutoML for job_id {job_id} as no target variable was detected.")
            manifest["steps"].append({"step": "automl", "status": "skipped", "details": "No target variable detected"})

        # --- Step 6: Report Generation ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Report Generation"})

        final_report = {
            "quality_report": state_store.load_json_artifact(job_id, "quality_report.json"),
            "eda_summary": state_store.load_json_artifact(job_id, "eda/summary.json"),
            "target_detection": state_store.load_json_artifact(job_id, "target.json"),
            "automl_results": state_store.load_json_artifact(job_id, "automl_summary.json"),
        }

        state_store.save_json_artifact(job_id, "final_report.json", final_report)
        manifest["reports"] = {"final_report_json": "final_report.json"}
        manifest["steps"].append({"step": "report_generation", "status": "completed"})

        # --- Step 7: Centralized Logging & Finalization ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Finalizing"})

        with mlflow.start_run(run_name=f"job_{job_id}") as run:
            run_id = run.info.run_id
            mlflow.log_param("job_id", job_id)
            manifest["mlflow_run_id"] = run_id

            # Log the final manifest as an artifact in MLflow
            state_store.save_json_artifact(job_id, "manifest.json", manifest)
            mlflow.log_dict(manifest, "manifest.json")

        state_store.save_job_status(job_id, {"status": "completed", "stage": "Finished", "mlflow_run_id": run_id})

    except Exception as e:
        import traceback
        traceback.print_exc()
        error_message = f"Master pipeline failed for job_id {job_id}: {e}"
        print(error_message)
        state_store.save_job_status(job_id, {"status": "failed", "error": error_message})
        manifest["steps"].append({"step": "error", "status": "failed", "detail": error_message})
    finally:
        # Always save the final manifest
        state_store.save_json_artifact(job_id, "manifest.json", manifest)
