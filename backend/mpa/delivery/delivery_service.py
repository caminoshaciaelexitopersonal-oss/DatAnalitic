import os
import zipfile
import hashlib
import json
from datetime import datetime
from typing import Dict, Any

# Placeholder for a function to get job metadata from the database or state store
def _get_job_metadata(job_id: str) -> Dict[str, Any]:
    """Retrieves metadata for a given job."""
    # This should be implemented to fetch real data
    return {
        "job_id": job_id,
        "status": "COMPLETED", # Assume success for now
        "algorithm_used": "RandomForestClassifier",
        "timestamp": datetime.now().isoformat(),
        "parameters": {"n_estimators": 100, "random_state": 42},
        # DTL completion status should come from the job's state
        "dtl_completed": True,
    }

class DeliveryService:
    """
    Handles the creation and validation of code delivery packages.
    """
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.metadata = _get_job_metadata(job_id)
        self.package_dir = f"/tmp/delivery_{job_id}"
        self.zip_path = f"/tmp/delivery_{job_id}.zip"

        os.makedirs(self.package_dir, exist_ok=True)

    def _pre_delivery_validation(self) -> None:
        """
        Validates that the job is in a state suitable for delivery.
        Raises an exception if validation fails.
        """
        if self.metadata["status"] != "COMPLETED":
            raise ValueError(f"Job {self.job_id} has not completed successfully.")

        if not self.metadata.get("dtl_completed"):
            raise ValueError(f"DTL process was not completed for job {self.job_id}.")

        # Add other critical checks here, e.g., model trained correctly
        print("Pre-delivery validation passed.")

    def create_package(self) -> str:
        """
        Orchestrates the creation of the full delivery package.
        Returns the path to the final zip file.
        """
        print(f"Starting package creation for job {self.job_id}...")
        self._pre_delivery_validation()

        # 1. Generate code structure (placeholder)
        self._generate_code_structure()

        # 2. Generate manifest.json
        self._generate_manifest()

        # 3. TODO: Add other artifacts (reports, notebooks, etc.)

        # 4. Create the zip archive
        self._create_zip_archive()

        print(f"Package created successfully at {self.zip_path}")
        return self.zip_path

    def _generate_code_structure(self):
        """Creates the modular Python code structure."""
        src_dir = os.path.join(self.package_dir, "src")
        os.makedirs(src_dir, exist_ok=True)

        # Create placeholder Python files
        files_to_create = [
            "__init__.py", "preprocessing.py", "model_training.py", "utils.py"
        ]
        for filename in files_to_create:
            with open(os.path.join(src_dir, filename), "w") as f:
                f.write(f"# {filename} for job {self.job_id}\n")

        with open(os.path.join(self.package_dir, "README.md"), "w") as f:
            f.write(f"# SADI Code Delivery for Job ID: {self.job_id}\n")

    def _generate_manifest(self):
        """Generates the manifest.json file with metadata and hashes."""
        # Calculate SHA-256 hash of the generated code for traceability
        code_hash = hashlib.sha256()
        src_dir = os.path.join(self.package_dir, "src")
        for filename in sorted(os.listdir(src_dir)):
            filepath = os.path.join(src_dir, filename)
            with open(filepath, "rb") as f:
                code_hash.update(f.read())

        manifest_data = {
            "job_id": self.job_id,
            "package_version": "1.0.0",
            "generation_date": datetime.now().isoformat(),
            "code_sha256": code_hash.hexdigest(),
            "algorithm_used": self.metadata.get("algorithm_used"),
            "parameters": self.metadata.get("parameters"),
        }

        manifest_path = os.path.join(self.package_dir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f, indent=4)

    def _create_zip_archive(self):
        """Creates the final zip archive of the package directory."""
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(self.package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.package_dir)
                    zf.write(file_path, arcname)

if __name__ == '__main__':
    # Example usage for testing
    test_job_id = "job_12345"
    service = DeliveryService(job_id=test_job_id)
    zip_file_path = service.create_package()
    print(f"Test package available at: {zip_file_path}")
