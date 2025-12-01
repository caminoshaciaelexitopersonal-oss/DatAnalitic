import pandas as pd
import hashlib
import json
import mlflow
import os
import tempfile
from typing import Dict, Any, List

class IngestionAdapter:
    """
    Strengthens the ingestion pipeline by adding validation, metadata extraction,
    and data versioning for traceability in MLflow.
    """

    def __init__(self, dataframe: pd.DataFrame):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")
        self.df = dataframe.copy()

    def schema_validator(self) -> bool:
        if self.df.empty:
            raise ValueError("DataFrame is empty. No data to process.")
        print("Schema validation successful: DataFrame is not empty.")
        return True

    def _calculate_data_hash(self) -> str:
        """Calculates a SHA-256 hash of the DataFrame to version the input data."""
        data_bytes = self.df.to_numpy().tobytes()
        return hashlib.sha256(data_bytes).hexdigest()

    def metadata_extractor(self) -> Dict[str, Any]:
        """Extracts key metadata from the DataFrame for logging."""
        metadata = {
            "num_rows": len(self.df),
            "num_columns": len(self.df.columns),
            "column_names": self.df.columns.tolist(),
            "inferred_types": self.column_type_inference(),
            "data_hash": self._calculate_data_hash(),
            "null_percentages": {
                col: (self.df[col].isnull().sum() / len(self.df)) * 100
                for col in self.df.columns
            },
            "cardinality": {
                col: self.df[col].nunique() for col in self.df.columns
            },
            "potential_risks": self._identify_risks()
        }
        print("Metadata extraction complete.")
        return metadata

    def column_type_inference(self) -> Dict[str, str]:
        inferred_types = {}
        for col in self.df.columns:
            numeric_col = pd.to_numeric(self.df[col], errors='coerce')
            if not numeric_col.isnull().all():
                inferred_types[col] = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                inferred_types[col] = 'datetime'
            else:
                inferred_types[col] = 'categorical'
        print("Column type inference complete.")
        return inferred_types

    def _identify_risks(self) -> List[str]:
        risks = []
        if self.df.duplicated().any():
            risks.append("Duplicate rows detected.")
        pii_keywords = ['email', 'phone', 'ssn', 'address', 'nombre', 'id']
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in pii_keywords):
                risks.append(f"Column '{col}' may contain Personally Identifiable Information (PII).")
        print(f"Risk identification complete. Found {len(risks)} potential risks.")
        return risks

def strengthen_ingestion(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Entrypoint function to run the ingestion strengthening process and log
    data versioning artifacts and parameters to the active MLflow run.
    """
    adapter = IngestionAdapter(df)
    adapter.schema_validator()
    metadata = adapter.metadata_extractor()

    print("Logging data artifacts and parameters to MLflow for lineage...")
    mlflow.log_param("data_hash", metadata["data_hash"])
    mlflow.log_dict(metadata, "ingestion_metadata.json")

    # --- Correctly save DataFrame as a Parquet artifact ---
    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_path = os.path.join(tmpdir, "processed_data.parquet")
        df.to_parquet(parquet_path, index=False)
        mlflow.log_artifact(parquet_path, "data")

    print("Data lineage artifacts saved to MLflow.")

    return metadata
