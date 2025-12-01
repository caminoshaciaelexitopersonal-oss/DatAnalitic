# backend/mpa/etl/service.py
import pandas as pd
import numpy as np
import json

class EtlService:
    """
    Service for standardizing and cleaning dataframes.
    This service is stateless and operates purely on dataframes in memory.
    """
    def __init__(self, state_store):
        self.state_store = state_store

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
