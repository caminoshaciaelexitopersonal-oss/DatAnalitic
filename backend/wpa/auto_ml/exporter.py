import joblib
import json
import os
import zipfile
from typing import Dict, Any

def export_model(pipeline, model_key: str, output_dir: str, run_id: str) -> str:
    """
    Saves the trained pipeline, its metadata, and creates a zip archive.
    """
    export_path = os.path.join(output_dir, "exported_models", run_id)
    os.makedirs(export_path, exist_ok=True)

    # 1. Save the pipeline object
    pipeline_path = os.path.join(export_path, "pipeline.joblib")
    joblib.dump(pipeline, pipeline_path)

    # 2. Save metadata
    metadata = {
        "model_key": model_key,
        "mlflow_run_id": run_id,
        "scikit-learn_version": joblib.__version__ # Basic dependency tracking
    }
    metadata_path = os.path.join(export_path, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)

    # 3. Create a zip archive for easy download
    zip_path = os.path.join(output_dir, "exporter", f"{model_key}_{run_id}.zip")
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(pipeline_path, arcname="pipeline.joblib")
        zf.write(metadata_path, arcname="metadata.json")

    return zip_path
