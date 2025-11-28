# backend/mpa/etl/service.py
import os
import sqlite3
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import json

class EtlService:
    """
    Robust ETL Service for ingesting and standardizing various file formats.
    """
    SUPPORTED_EXT = (".csv", ".tsv", ".xlsx", ".xls", ".json", ".parquet", ".sql")

    def __init__(self, state_store):
        self.state_store = state_store

    def ingest_file(self, file_path: str, session_id: str, db_uri: Optional[str] = None) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXT:
            raise ValueError(f"Unsupported file extension: {ext}")

        df = None
        if ext in (".csv", ".tsv"):
            df = pd.read_csv(file_path, sep=("," if ext == ".csv" else "\t"), engine='python')
        elif ext in (".xlsx", ".xls"):
            xls = pd.ExcelFile(file_path, engine="openpyxl")
            if len(xls.sheet_names) > 1:
                df = pd.concat([pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names], ignore_index=True)
            else:
                df = pd.read_excel(xls)
        elif ext == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.json_normalize(data)
        elif ext == ".parquet":
            df = pd.read_parquet(file_path)
        elif ext == ".sql":
            if db_uri is None:
                raise ValueError("db_uri must be provided for .sql ingestion")

            with open(file_path, "r", encoding="utf-8") as f:
                query = f.read().strip()

            # Security Hardening: Only allow a single SELECT statement
            if not query.upper().strip().startswith("SELECT") or ';' in query:
                raise ValueError("Security violation: Only single SELECT statements are allowed.")

            con = sqlite3.connect(db_uri)
            try:
                df = pd.read_sql_query(query, con)
            finally:
                con.close()

        if df is None:
             metadata = {"rows": 0, "cols": 0, "columns": [], "dtypes": {}}
        else:
            df = self.standardize_df(df)
            self.state_store.save_dataframe(session_id, df, append=True)
            metadata = {
                "rows": int(df.shape[0]), "cols": int(df.shape[1]), "columns": list(df.columns),
                "dtypes": {c: str(dtype) for c, dtype in df.dtypes.items()},
            }
        return metadata

    def standardize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in df.columns:
            series = df[col]

            # Convert columns containing lists/dicts to JSON strings to make them hashable
            if any(isinstance(i, (list, dict)) for i in series.dropna()):
                df[col] = series.apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
                continue

            if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series):
                continue

            if series.dtype == object:
                series = series.replace(r'^\s*$', np.nan, regex=True).replace(["NA", "N/A", "null", "None"], np.nan)
                cleaned_series = series.astype(str).str.strip()
                is_percent = cleaned_series.str.contains("%", na=False)

                numeric_candidate = cleaned_series.str.replace(r'[$,]', '', regex=True)
                numeric_candidate = numeric_candidate.str.replace(r'[(](.*)[)]', r'-\1', regex=True)
                numeric_candidate = numeric_candidate.str.replace('%', '', regex=False)

                coerced = pd.to_numeric(numeric_candidate, errors='coerce')

                if coerced.notna().sum() / max(1, series.notna().sum()) >= 0.8:
                    if is_percent.any():
                        coerced = coerced / 100.0
                    df[col] = coerced
                    continue

                try:
                    dt = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
                    if dt.notna().sum() / max(1, series.notna().sum()) >= 0.8:
                        df[col] = dt
                        continue
                except Exception:
                    pass

                df[col] = series
        return df
