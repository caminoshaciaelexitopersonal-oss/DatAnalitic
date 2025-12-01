import pandas as pd
import io
import os
import json
import chardet
from typing import List, Optional
from sqlalchemy import create_engine, text
from fastapi import Depends, UploadFile, HTTPException
from prometheus_client import Counter, Histogram

from backend.core.state_store import StateStore, get_state_store
from backend.mpa.quality.service import DataQualityService, get_data_quality_service
from backend.mpa.ingestion.schema_validator import validate_dataframe

# --- Prometheus Metrics ---
INGESTION_FILES_PROCESSED_TOTAL = Counter(
    "ingestion_files_processed_total", "Total files processed", ["file_type", "status"]
)
INGESTION_FILE_SIZE_BYTES = Histogram(
    "ingestion_file_size_bytes", "Distribution of file sizes",
    buckets=[10*1024, 100*1024, 1*1024*1024, 10*1024*1024]
)

class IngestionService:
    """
    Modular Process Architecture (MPA) service for robust data ingestion from multiple sources.
    """
    def __init__(self, state_store: StateStore, quality_service: DataQualityService):
        self.state_store = state_store
        self.quality_service = quality_service
        self.sql_engine = create_engine('sqlite:///:memory:') # In-memory DB for SQL file processing

    def _read_excel(self, content: bytes) -> pd.DataFrame:
        """Reads an Excel file, handling multiple sheets by concatenating them."""
        xls = pd.ExcelFile(content)
        if len(xls.sheet_names) > 1:
            return pd.concat([pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names], ignore_index=True)
        return pd.read_excel(xls)

    def _read_json(self, content: bytes) -> pd.DataFrame:
        """Reads a JSON file, normalizing nested structures."""
        data = json.loads(content)
        return pd.json_normalize(data)

    def _read_csv(self, content: bytes) -> pd.DataFrame:
        """Reads a CSV file, auto-detecting delimiter and encoding."""
        try:
            encoding = chardet.detect(content)['encoding'] or 'utf-8'
            decoded_content = content.decode(encoding)
        except (UnicodeDecodeError, TypeError):
            decoded_content = content.decode('latin-1')

        # Auto-detect delimiter
        sniffer = pd.io.common.sniff_text(decoded_content, 1024)
        delimiter = sniffer.delimiter if sniffer else ','

        return pd.read_csv(io.StringIO(decoded_content), sep=delimiter)

    def _read_sql(self, content: bytes) -> Optional[pd.DataFrame]:
        """Executes a SQL file against the in-memory SQLite engine."""
        query = content.decode('utf-8')
        with self.sql_engine.connect() as connection:
            if query.strip().upper().startswith("SELECT"):
                return pd.read_sql(text(query), connection)
            else:
                connection.execute(text(query))
        return None

    async def _read_and_process_file_content(self, file_path: str, content: bytes) -> Optional[pd.DataFrame]:
        """Dispatcher to select the correct reader based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        df = None
        try:
            if ext in ['.xlsx', '.xls']:
                df = self._read_excel(content)
            elif ext == '.json':
                df = self._read_json(content)
            elif ext == '.csv':
                df = self._read_csv(content)
            elif ext == '.sql':
                df = self._read_sql(content)

            if df is not None:
                INGESTION_FILES_PROCESSED_TOTAL.labels(file_type=ext, status="success").inc()
                INGESTION_FILE_SIZE_BYTES.observe(len(content))
            return df
        except Exception as e:
            INGESTION_FILES_PROCESSED_TOTAL.labels(file_type=ext, status="error").inc()
            print(f"Error processing file {file_path}: {e}")
            return None

    async def process_uploaded_file(self, file: UploadFile, job_id: str) -> pd.DataFrame:
        """Processes a single file uploaded via the API."""
        content = await file.read()
        df = await self._read_and_process_file_content(file.filename, content)

        if df is None:
            raise HTTPException(status_code=422, detail="Failed to process file.")

        # Save the main dataframe artifact using job_id
        self.state_store.save_dataframe(job_id, df)

        # --- Schema Validation ---
        schema_metadata = validate_dataframe(df)
        self.state_store.save_schema_metadata(job_id, schema_metadata)

        # --- Data Quality Assurance on Ingestion ---
        quality_report = self.quality_service.get_quality_report(df)
        self.state_store.save_json_artifact(
            job_id, "quality_report.json", quality_report.model_dump()
        )

        return df

# --- Dependency Injection ---
def get_ingestion_service(
    state_store: StateStore = Depends(get_state_store),
    quality_service: DataQualityService = Depends(get_data_quality_service)
) -> IngestionService:
    """
    Dependency injector for the IngestionService.
    """
    return IngestionService(state_store, quality_service)
