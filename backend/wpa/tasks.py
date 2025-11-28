"""
This module contains the master Celery task orchestrator for the WPA layer,
ensuring full system interoperability.
"""
import os
import json
import uuid
import pandas as pd
from sklearn.model_selection import train_test_split
from backend.celery_worker import celery_app
from backend.core.state_store import get_state_store
from backend.core.config import config
from backend.wpa.auto_analysis.target_detector import detect_target
from backend.wpa.auto_analysis.eda_intelligent_service import run_eda
from backend.wpa.report_generator import docx_generator, excel_generator, pdf_generator

@celery_app.task(name="wpa.master_pipeline_task")
def master_pipeline_task(job_id: str):
    """
    The master orchestrator task for the entire SADI analysis pipeline.
    """
    state_store = get_state_store()
    output_dir = os.path.join(config.PROCESSED_DATA_DIR, job_id)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # --- Step 1: Load Data ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Loading Data"})

        job = state_store.get_job(uuid.UUID(job_id))
        if not job or not job.original_filename:
            raise ValueError(f"Job or original_filename not found for job_id: {job_id}")

        raw_file_content = state_store.load_raw_file(job_id, job.original_filename)
        if not raw_file_content:
            raise FileNotFoundError(f"Raw file not found in storage for job_id: {job_id}")

        temp_csv_path = os.path.join(output_dir, "data_snapshot.csv")
        with open(temp_csv_path, "wb") as f:
            f.write(raw_file_content.read())

        # --- Step 2: Target Detection ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Target Detection"})
        print(f"Running Target Detection for job_id: {job_id}")
        target_result = detect_target(input_csv_path=temp_csv_path, job_id=job_id, out_base=output_dir)
        selected_target = target_result.get("selected_target")
        print(f"Target detection complete. Selected target: {selected_target}")

        # --- Step 3: EDA ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "EDA"})
        df = pd.read_csv(temp_csv_path)
        inferred_types = {col: 'numeric' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical' for col in df.columns}
        run_eda(df, inferred_types, job_id)

        # --- Step 4: AutoML (Conditional) ---
        if selected_target and not target_result.get("requires_user_confirmation"):
            state_store.save_job_status(job_id, {"status": "running", "stage": "AutoML"})
            print(f"Proceeding to AutoML for target: {selected_target}")

            from backend.wpa.auto_ml.tasks import run_full_automl

            # Perform train-test split
            X = df.drop(columns=[selected_target])
            y = df[selected_target]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Save the split data to new CSVs for the AutoML task
            train_csv_path = os.path.join(output_dir, "train_data.csv")
            test_csv_path = os.path.join(output_dir, "test_data.csv")
            X_train.join(y_train).to_csv(train_csv_path, index=False)
            X_test.join(y_test).to_csv(test_csv_path, index=False)

            # Construct the request for the AutoML task
            automl_request = {
                "train_csv_path": train_csv_path,
                "test_csv_path": test_csv_path,
                "target": selected_target,
                "params": {
                    # Default models to run for this integrated pipeline
                    "models": ["logistic_regression", "random_forest_classifier"]
                }
            }

            # Run AutoML task synchronously for simplicity in this integrated pipeline.
            # A more advanced implementation might use Celery chains or chords.
            run_full_automl(job_id, automl_request)

        # --- Step 5: Report Generation ---
        state_store.save_job_status(job_id, {"status": "running", "stage": "Generating Reports"})
        docx_path = docx_generator.create_docx(job_id, output_dir)
        excel_path = excel_generator.create_excel(job_id, output_dir)
        pdf_path = pdf_generator.create_pdf(job_id, output_dir)

        # --- Step 6: Centralized Logging & Finalization ---
        # Update manifest with report paths
        manifest_path = os.path.join(output_dir, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r+") as f:
                manifest = json.load(f)
                manifest["reports"] = {
                    "docx": os.path.relpath(docx_path, output_dir),
                    "xlsx": os.path.relpath(excel_path, output_dir),
                    "pdf": os.path.relpath(pdf_path, output_dir),
                    "generated_at": pd.Timestamp.now().isoformat(),
                }
                f.seek(0)
                json.dump(manifest, f, indent=2)
                f.truncate()

        # Log key artifacts to MLflow
        import mlflow
        mlflow.set_experiment("SADI/unified_pipeline")
        with mlflow.start_run(run_name=f"job_{job_id}") as run:
            run_id = run.info.run_id
            mlflow.log_param("job_id", job_id)
            mlflow.log_artifacts(output_dir, artifact_path="job_artifacts")

            # Add run_id to the manifest
            if os.path.exists(manifest_path):
                with open(manifest_path, "r+") as f:
                    manifest = json.load(f)
                    manifest["mlflow_run_id"] = run_id
                    f.seek(0)
                    json.dump(manifest, f, indent=2)
                    f.truncate()

        state_store.save_job_status(job_id, {"status": "completed", "stage": "Finished", "mlflow_run_id": run_id})

    except Exception as e:
        print(f"Master pipeline failed for job_id {job_id}: {e}")
        state_store.save_job_status(job_id, {"status": "failed", "error": str(e)})
