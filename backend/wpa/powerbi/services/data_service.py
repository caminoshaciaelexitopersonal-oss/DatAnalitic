# backend/wpa/powerbi/services/data_service.py
"""
DataService: unified service to load data for PowerBI-like dashboards.

Capabilities:
 - load from local CSV/XLSX/Parquet
 - load from SQL (via SQLAlchemy connection string)
 - stream large files to temp and read by chunks
 - use GoogleDriveConnector and OneDriveConnector when source == 'gdrive' or 'onedrive'
 - execute simple SQL-like queries (when passed) or return full df
 - execute widget queries (simple group by / aggregation)
 - basic input sanitation and size checks
"""

import os
import io
import tempfile
import json
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

import pandas as pd
import sqlalchemy
from sqlalchemy import text

from backend.wpa.powerbi.services.cache_service import CacheService
# these connectors were provided earlier
from backend.wpa.powerbi.services.drive_connectors import GoogleDriveConnector, OneDriveConnector

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

CACHE = CacheService()

# ENV keys for SQL connections can be used like: SADI_DB_POSTGRES="postgresql://user:pass@host:5432/db"
SQL_CONNECTIONS = {
    k.split("SADI_DB_")[-1].lower(): v
    for k, v in os.environ.items() if k.startswith("SADI_DB_")
}


class DataService:
    def __init__(self):
        # instantiate connectors lazily
        self._gdrive = None
        self._onedrive = None

    # -------------------------
    # Helpers
    # -------------------------
    def _get_gdrive(self) -> GoogleDriveConnector:
        if self._gdrive is None:
            try:
                self._gdrive = GoogleDriveConnector.from_service_account()
            except Exception as e:
                logger.warning("GoogleDriveConnector init failed: %s", e)
                raise
        return self._gdrive

    def _get_onedrive(self) -> OneDriveConnector:
        if self._onedrive is None:
            try:
                self._onedrive = OneDriveConnector.from_env()
            except Exception as e:
                logger.warning("OneDriveConnector init failed: %s", e)
                raise
        return self._onedrive

    def get_available_connectors(self) -> List[str]:
        return ["local_csv", "local_xlsx", "parquet", "sql", "gdrive", "onedrive", "s3", "api"]

    # -------------------------
    # Execute general query request
    # -------------------------
    def execute_query(self, req: Dict[str, Any]) -> pd.DataFrame:
        """
        req: {
            'query': Optional[str],   # SQL or 'select' like string OR path
            'source': 'local'|'sql'|'gdrive'|'onedrive'|'s3'|'api'|'parquet',
            'path': Optional[str],    # used for local/gdrive/onedrive
            'conn': Optional[str],    # sql connection key from env e.g. 'postgres'
            'limit': Optional[int],   # sample rows
            'params': Optional[dict]
        }
        Returns pandas.DataFrame
        """
        # normalize input
        query = req.get("query")
        source = req.get("source", "local")
        path = req.get("path")
        limit = req.get("limit")
        params = req.get("params") or {}

        # caching: safe key
        cache_key = f"execute_query:{json.dumps(req, sort_keys=True, default=str)}"
        cached = CACHE.get(cache_key)
        if cached is not None:
            logger.debug("cache hit %s", cache_key)
            return pd.DataFrame(cached)

        try:
            if source in ("local", "file"):
                if not path:
                    raise ValueError("path required for local source")
                df = self._read_local_path(path, limit=limit)
            elif source == "parquet":
                if not path:
                    raise ValueError("path required for parquet")
                df = pd.read_parquet(path)
                if limit:
                    df = df.head(limit)
            elif source == "sql":
                # when query provided, use it; else read table at path
                conn_key = req.get("conn") or list(SQL_CONNECTIONS.keys())[0] if SQL_CONNECTIONS else None
                if not conn_key:
                    raise RuntimeError("No SQL connection configured in env (SADI_DB_*)")
                conn_url = SQL_CONNECTIONS.get(conn_key)
                engine = sqlalchemy.create_engine(conn_url, pool_pre_ping=True)
                if query:
                    with engine.connect() as conn:
                        df = pd.read_sql_query(text(query), conn, params=params)
                else:
                    # read table name in path
                    if not path:
                        raise ValueError("path (table name) required when source=sql and no query")
                    df = pd.read_sql_table(path, engine)
                if limit:
                    df = df.head(limit)
            elif source == "gdrive":
                g = self._get_gdrive()
                df = g.download_file_to_df(path, sample=limit)
            elif source == "onedrive":
                od = self._get_onedrive()
                # path may be "drive_id:/path/to/file" or "me:/path"
                # we accept either "drive_id|path" or item id
                if "|" in path:
                    drive_id, p = path.split("|", 1)
                    df = od.download_item_to_df(drive_id, p, sample=limit)
                else:
                    # try as item id on default drive 'me'
                    df = od.download_item_to_df("me", path, sample=limit)
            elif source == "s3":
                # support s3://bucket/key or path
                s3_path = path
                df = self._read_s3(s3_path, limit=limit)
            elif source == "api":
                # request remote API that returns JSON list of rows
                df = self._read_api(path, params=params, limit=limit)
            else:
                raise ValueError(f"Unknown source: {source}")

            # basic post-processing: sanitize column names
            df = self._sanitize_df(df)
            CACHE.set(cache_key, df.to_dict(orient="records"))
            return df
        except Exception as e:
            logger.exception("execute_query failed: %s", e)
            raise

    # -------------------------
    # Widget-level query: process aggregation/group-by
    # -------------------------
    def execute_widget_query(self, widget_config: Dict[str, Any], filters: Optional[str] = None) -> pd.DataFrame:
        """
        widget_config example:
          {'query': 'SELECT region, SUM(amount) as total FROM sales GROUP BY region', 'type': 'bar', ...}
        Or a declarative config:
          {'source':'local','path':'/data/sales.csv','group_by':['region'],'agg':{'amount':'sum'}}
        filters: optional JSON string with filter conditions, e.g. {"year":2023,"region":"North"}
        """
        # support simple SQL queries or declarative config
        if "query" in widget_config and widget_config.get("query"):
            # run via execute_query with source maybe specified
            req = {"query": widget_config["query"], "source": widget_config.get("source", "sql"), "conn": widget_config.get("conn")}
            df = self.execute_query(req)
        else:
            # declarative
            source = widget_config.get("source", "local")
            path = widget_config.get("path")
            df = self.execute_query({"source": source, "path": path})
            group_by = widget_config.get("group_by")
            agg = widget_config.get("agg")
            if group_by and agg:
                df = df.groupby(group_by).agg(agg).reset_index()
        # apply filters
        if filters:
            try:
                filt = json.loads(filters)
                for k, v in filt.items():
                    if k in df.columns:
                        df = df[df[k] == v]
            except Exception:
                logger.warning("Could not apply filters: %s", filters)
        # limit rows for widgets
        max_rows = widget_config.get("max_rows", 10000)
        if len(df) > max_rows:
            df = df.head(max_rows)
        return df

    # -------------------------
    # Low-level readers
    # -------------------------
    def _read_local_path(self, path: str, limit: Optional[int] = None) -> pd.DataFrame:
        if path.startswith("http://") or path.startswith("https://"):
            # remote CSV
            return pd.read_csv(path, nrows=limit) if limit else pd.read_csv(path)
        if path.lower().endswith(".csv"):
            df = pd.read_csv(path)
        elif path.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(path)
        elif path.lower().endswith(".parquet"):
            df = pd.read_parquet(path)
        else:
            # try CSV by default
            df = pd.read_csv(path)
        if limit:
            df = df.head(limit)
        return df

    def _read_s3(self, s3_path: str, limit: Optional[int] = None) -> pd.DataFrame:
        # expects s3://bucket/key
        try:
            import s3fs
            fs = s3fs.S3FileSystem()
            if s3_path.lower().endswith(".parquet"):
                df = pd.read_parquet(s3_path, storage_options={"anon": False})
            else:
                with fs.open(s3_path, "rb") as fh:
                    df = pd.read_csv(fh)
            if limit:
                df = df.head(limit)
            return df
        except Exception as e:
            logger.exception("S3 read failed: %s", e)
            raise

    def _read_api(self, url: str, params: Optional[dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        import requests
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data)
        if limit:
            df = df.head(limit)
        return df

    def _sanitize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # sanitize column names to be consistent
        df = df.copy()
        df.columns = [str(c).strip().replace(" ", "_").replace("-", "_") for c in df.columns]
        return df
