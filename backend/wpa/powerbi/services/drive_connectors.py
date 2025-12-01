"""
drive_connectors.py

Google Drive / Google Sheets connector and Microsoft OneDrive (Graph API) connector.

Usage:
  from drive_connectors import GoogleDriveConnector, OneDriveConnector
  g = GoogleDriveConnector()
  df = g.download_file_to_df(file_id_or_path)
  od = OneDriveConnector()
  df2 = od.download_file_to_df(drive_item_id_or_path)

Notes / Security:
 - Do NOT hardcode credentials. Use environment variables or secret store.
 - For Google: prefer a Service Account JSON (when accessing files in GCP project or
   shared drives). For user files / Google Sheets you may need OAuth user consent.
 - For OneDrive (work/school) use Microsoft identity platform (Azure App registration)
   with client_id/client_secret and delegated permissions (or app-only for application
   permission scenarios).
 - Install:
     pip install google-auth google-auth-oauthlib google-api-python-client gspread pandas openpyxl msal requests
"""

import os
import io
import json
import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


# -----------------------------
# Google Drive + Google Sheets
# -----------------------------
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import gspread
    from gspread_dataframe import get_as_dataframe, set_with_dataframe
except Exception:
    # If imports fail, connectors will raise at use time with explicit error.
    service_account = None
    build = None
    MediaIoBaseDownload = None
    gspread = None
    get_as_dataframe = None


class GoogleDriveConnector:
    """
    Connector for Google Drive and Google Sheets.

    Configuration (recommended):
      - Set env var GOOGLE_APPLICATION_CREDENTIALS to the path of the service account JSON.
      - For user OAuth, set up OAuth client and pass credentials.json path into `from_oauth`.

    Methods:
      - from_service_account(): classmethod to instantiate using service account.
      - download_file(file_id, dest_path): download binary file from Drive.
      - download_file_to_df(file_id_or_path): convenience to return pandas DataFrame (CSV/Excel/Sheets).
      - download_sheet(sheet_id, worksheet_name): returns DataFrame from Google Sheet.

    Example:
      g = GoogleDriveConnector.from_service_account()
      df = g.download_file_to_df("1xX...fileId...")
    """

    SCOPES = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    def __init__(self, credentials=None):
        if build is None:
            raise RuntimeError("google-api packages not installed. pip install google-api-python-client gspread gspread-dataframe google-auth")
        self.creds = credentials
        self.drive_service = build("drive", "v3", credentials=self.creds)
        self.sheets_service = build("sheets", "v4", credentials=self.creds)
        self.auth_sess = AuthorizedSession(self.creds) if self.creds else None

    @classmethod
    def from_service_account(cls, sa_json_path: Optional[str] = None):
        """
        Instantiate using service account JSON file.
        Use when accessing files in shared drives or via domain service account.
        """
        sa_path = sa_json_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not sa_path or not os.path.exists(sa_path):
            raise FileNotFoundError("Service account JSON not found. Set GOOGLE_APPLICATION_CREDENTIALS or pass sa_json_path.")
        creds = service_account.Credentials.from_service_account_file(sa_path, scopes=cls.SCOPES)
        return cls(credentials=creds)

    def download_file(self, file_id: str, dest_path: str, mime_type: Optional[str] = None):
        """
        Downloads a file from Google Drive by file_id to dest_path.
        If mime_type provided (e.g., export google-sheet to csv): use files().export
        """
        if not self.drive_service:
            raise RuntimeError("Drive service not initialized.")
        try:
            if mime_type:
                # Google Docs/Sheets export
                request = self.drive_service.files().export_media(fileId=file_id, mimeType=mime_type)
                fh = io.FileIO(dest_path, mode="wb")
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fh.close()
            else:
                # normal file download
                request = self.drive_service.files().get_media(fileId=file_id)
                fh = io.FileIO(dest_path, mode="wb")
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fh.close()
            return dest_path
        except Exception as e:
            logger.exception("Failed to download file from Google Drive: %s", e)
            raise

    def download_file_to_df(self, file_id_or_path: str, sheet_name: Optional[str] = None, sample: Optional[int] = None) -> pd.DataFrame:
        """
        Download a Drive file (CSV/Excel) or Google Sheet and return a pandas DataFrame.
        If file_id_or_path looks like a path on disk, read local file instead.
        """
        # Local path
        if os.path.exists(file_id_or_path):
            return pd.read_csv(file_id_or_path) if file_id_or_path.lower().endswith(".csv") else pd.read_excel(file_id_or_path)

        # If it's a Google Sheets id (heuristic: contains '/d/' or looks like file id)
        # Attempt to download sheet as CSV via export endpoint
        try:
            if "/spreadsheets/" in file_id_or_path or "docs.google.com/spreadsheets" in file_id_or_path or len(file_id_or_path) > 20:
                # Extract id if full url
                fid = file_id_or_path.split("/d/")[-1].split("/")[0] if "/d/" in file_id_or_path else file_id_or_path
                export_mime = "text/csv"
                tmp = f"/tmp/gdrive_{fid}.csv"
                self.download_file(fid, tmp, mime_type=export_mime)
                df = pd.read_csv(tmp)
                if sample:
                    return df.head(sample)
                return df
        except Exception:
            logger.exception("Falling back: try reading as regular csv or via sheets API.")

        # Last-resort: try to treat as file id and attempt csv then xlsx
        for ext, reader in [(".csv", pd.read_csv), (".xlsx", pd.read_excel)]:
            try:
                tmp = f"/tmp/gdrive_{file_id_or_path}{ext}"
                self.download_file(file_id_or_path, tmp)
                df = reader(tmp)
                if sample:
                    return df.head(sample)
                return df
            except Exception:
                continue

        raise RuntimeError("Could not retrieve Google Drive file as DataFrame. Verify file id or path.")


# -----------------------------
# OneDrive connector (Microsoft Graph)
# -----------------------------
try:
    import requests
    from msal import ConfidentialClientApplication
except Exception:
    requests = None
    ConfidentialClientApplication = None


class OneDriveConnector:
    """
    OneDrive / Microsoft Graph file downloader.

    Configuration:
      - Set env vars:
          ONEDRIVE_CLIENT_ID
          ONEDRIVE_CLIENT_SECRET
          ONEDRIVE_TENANT_ID   (for org accounts)
      - Or pass credentials to `from_client_credentials`

    Methods:
      - download_item(item_id, dest_path)
      - download_item_to_df(item_id_or_path)
      - download_by_path(drive_id, path)
    """

    DEFAULT_SCOPE = ["https://graph.microsoft.com/.default"]

    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        if requests is None or ConfidentialClientApplication is None:
            raise RuntimeError("msal or requests not installed. pip install msal requests")
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.app = ConfidentialClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_id}", client_credential=client_secret)

    @classmethod
    def from_env(cls):
        cid = os.environ.get("ONEDRIVE_CLIENT_ID")
        sec = os.environ.get("ONEDRIVE_CLIENT_SECRET")
        tid = os.environ.get("ONEDRIVE_TENANT_ID")
        if not cid or not sec or not tid:
            raise RuntimeError("ONEDRIVE_CLIENT_ID/ONEDRIVE_CLIENT_SECRET/ONEDRIVE_TENANT_ID must be set")
        return cls(cid, sec, tid)

    def _get_token(self):
        token = self.app.acquire_token_for_client(scopes=self.DEFAULT_SCOPE)
        if "access_token" not in token:
            raise RuntimeError(f"Failed to acquire token: {token}")
        return token["access_token"]

    def download_item(self, drive_id: str, item_id: str, dest_path: str):
        """
        Download a drive item given drive_id and item_id.
        For personal OneDrive, drive_id can be 'me' (or omitted).
        """
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        # Use the content endpoint
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
        r = requests.get(url, headers=headers, stream=True)
        if r.status_code >= 400:
            logger.error("Graph API download failed: %s - %s", r.status_code, r.text)
            raise RuntimeError(f"Download failed: {r.status_code} {r.text}")
        with open(dest_path, "wb") as fh:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
        return dest_path

    def download_by_path(self, drive_id: str, path: str, dest_path: str):
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        # path must be URL-encoded; Graph supports /root:/path:/content
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{path}:/content"
        r = requests.get(url, headers=headers, stream=True)
        if r.status_code >= 400:
            logger.error("Graph API download by path failed: %s - %s", r.status_code, r.text)
            raise RuntimeError(f"Download failed: {r.status_code} {r.text}")
        with open(dest_path, "wb") as fh:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
        return dest_path

    def download_item_to_df(self, drive_id_or_me: str, item_id_or_path: str, sample: Optional[int] = None) -> pd.DataFrame:
        """
        Try to infer whether the argument is an item id or a path.
        If path contains '.' (file extension) or '/', treat as path.
        """
        dest = f"/tmp/onedrive_{item_id_or_path.replace('/', '_')}"
        # try path first
        try:
            if "/" in item_id_or_path or "." in item_id_or_path:
                # treat as path
                ext = os.path.splitext(item_id_or_path)[1].lower()
                if not ext:
                    ext = ".csv"
                dest = dest + ext
                self.download_by_path(drive_id_or_me, item_id_or_path, dest)
            else:
                # treat as item id
                # attempt csv then xlsx
                for ext in [".csv", ".xlsx"]:
                    try:
                        dtmp = dest + ext
                        self.download_item(drive_id_or_me, item_id_or_path, dtmp)
                        if ext == ".csv":
                            df = pd.read_csv(dtmp)
                        else:
                            df = pd.read_excel(dtmp)
                        if sample:
                            return df.head(sample)
                        return df
                    except Exception:
                        continue
        except Exception as e:
            logger.exception("OneDrive download failed: %s", e)
            raise

        # fallback: try to read dest if it exists
        if os.path.exists(dest):
            try:
                if dest.lower().endswith(".csv"):
                    df = pd.read_csv(dest)
                else:
                    df = pd.read_excel(dest)
                if sample:
                    return df.head(sample)
                return df
            except Exception:
                pass

        raise RuntimeError("Could not read OneDrive item as DataFrame. Verify path or item id.")
