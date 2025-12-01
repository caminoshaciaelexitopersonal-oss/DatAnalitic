
import os
import json
from functools import lru_cache
from typing import Dict, Any, Optional, List
import pandas as pd
import redis
import boto3
from botocore.client import Config
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from contextlib import contextmanager
from io import BytesIO

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sadi_user:sadi_password@postgres:5432/sadi_db")
MINIO_URL = os.getenv("MINIO_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "sadi_minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "sadi_minio_secret")
MINIO_BUCKET = "sadi"

# --- SQLAlchemy ORM Models ---
Base = declarative_base()

class SessionModel(Base):
    __tablename__ = "sessions"
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship("JobModel", back_populates="session")

class JobModel(Base):
    __tablename__ = "jobs"
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"))
    job_type = Column(String)
    original_filename = Column(String)
    status = Column(String, default="running")
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("SessionModel", back_populates="jobs")
    steps = relationship("MCPStepModel", back_populates="job")

class MCPStepModel(Base):
    __tablename__ = "mcp_steps"
    step_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"))
    description = Column(Text)
    payload = Column(JSON)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    job = relationship("JobModel", back_populates="steps")
 
class ModelScoreboardModel(Base):
    __tablename__ = "model_scoreboard"
    mlflow_run_id = Column(String, primary_key=True)
    model_key = Column(String, index=True)
    composite_score = Column(Float, index=True)
    metrics = Column(JSON)
    artifact_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserModel(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer") # e.g., admin, viewer, editor
    disabled = Column(Boolean, default=False)

# --- StateStore Service ---
class StateStore:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        # self._initialize_db() # This is now handled by Alembic
        try:
            self.redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)), db=0, decode_responses=True)
            self.redis_client.ping()
        except redis.exceptions.ConnectionError as e:
            raise RuntimeError(f"Could not connect to Redis. Error: {e}")
        try:
            self.s3_client = boto3.client('s3', endpoint_url=MINIO_URL, aws_access_key_id=MINIO_ACCESS_KEY, aws_secret_access_key=MINIO_SECRET_KEY, config=Config(signature_version='s3v4'))
            if MINIO_BUCKET not in [b['Name'] for b in self.s3_client.list_buckets().get('Buckets', [])]:
                self.s3_client.create_bucket(Bucket=MINIO_BUCKET)
        except Exception as e:
            raise RuntimeError(f"Could not connect to MinIO. Error: {e}")

    # --- MCP Methods ---
    def create_session(self, db: Session) -> SessionModel:
        new_session = SessionModel()
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    def get_session(self, db: Session, session_id: uuid.UUID) -> Optional[SessionModel]:
        return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

    def create_job(self, db: Session, session_id: uuid.UUID, job_type: str, filename: str) -> Optional[JobModel]:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not session:
            return None
        new_job = JobModel(session_id=session_id, job_type=job_type, original_filename=filename)
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job

    def get_job(self, db: Session, job_id: uuid.UUID) -> Optional[JobModel]:
        return db.query(JobModel).filter(JobModel.job_id == job_id).first()

    def create_mcp_step(self, db: Session, job_id: uuid.UUID, description: str, payload: Optional[Dict]) -> Optional[MCPStepModel]:
        job = db.query(JobModel).filter(JobModel.job_id == job_id).first()
        if not job:
            return None
        new_step = MCPStepModel(job_id=job_id, description=description, payload=payload)
        db.add(new_step)
        db.commit()
        db.refresh(new_step)
        return new_step

    def update_scoreboard(self, db: Session, trial_result: Dict[str, Any]):
        scoreboard_entry = ModelScoreboardModel(
            mlflow_run_id=trial_result.get("mlflow_run_id"),
            model_key=trial_result.get("model_key"),
            composite_score=trial_result.get("composite_score"),
            metrics=trial_result.get("evaluation", {}).get("metrics"),
            artifact_path=trial_result.get("exported_path")
        )
        db.merge(scoreboard_entry)
        db.commit()

    # --- Artifact and Job Status Methods ---
    def save_raw_file(self, job_id: str, filename: str, content: bytes):
        key = f"raw/{job_id}/{filename}"
        self.s3_client.put_object(Bucket=MINIO_BUCKET, Key=key, Body=content)

    def save_dataframe(self, job_id: str, df: pd.DataFrame):
        buffer = BytesIO(); df.to_parquet(buffer, index=False); buffer.seek(0)
        self.s3_client.put_object(Bucket=MINIO_BUCKET, Key=f"{job_id}/data.parquet", Body=buffer.getvalue())

    def load_dataframe(self, job_id: str) -> Optional[pd.DataFrame]:
        try:
            response = self.s3_client.get_object(Bucket=MINIO_BUCKET, Key=f"{job_id}/data.parquet")
            return pd.read_parquet(BytesIO(response['Body'].read()))
        except self.s3_client.exceptions.NoSuchKey:
            return None

    def load_raw_file(self, job_id: str, filename: str) -> Optional[BytesIO]:
        try:
            key = f"raw/{job_id}/{filename}"
            response = self.s3_client.get_object(Bucket=MINIO_BUCKET, Key=key)
            return BytesIO(response['Body'].read())
        except self.s3_client.exceptions.NoSuchKey:
            return None

    def save_job_status(self, job_id: str, status: Dict[str, Any]):
        self.redis_client.set(f"job_status:{job_id}", json.dumps(status))

    def load_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        status_json = self.redis_client.get(f"job_status:{job_id}")
        return json.loads(status_json) if status_json else None

    def save_schema_metadata(self, job_id: str, metadata: Dict[str, Any]):
        self.save_json_artifact(job_id, "metadata.json", metadata)

    def save_json_artifact(self, job_id: str, artifact_name: str, data: Dict[str, Any]):
        json_bytes = json.dumps(data, indent=2).encode('utf-8')
        key = f"processed/{job_id}/{artifact_name}"
        self.s3_client.put_object(Bucket=MINIO_BUCKET, Key=key, Body=BytesIO(json_bytes))

    def load_json_artifact(self, job_id: str, artifact_name: str) -> Optional[Dict[str, Any]]:
        key = f"processed/{job_id}/{artifact_name}"
        try:
            response = self.s3_client.get_object(Bucket=MINIO_BUCKET, Key=key)
            content = response['Body'].read()
            return json.loads(content)
        except self.s3_client.exceptions.NoSuchKey:
            return None

    def save_figure_artifact(self, job_id: str, artifact_name: str, fig):
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        key = f"processed/{job_id}/{artifact_name}"
        self.s3_client.put_object(Bucket=MINIO_BUCKET, Key=key, Body=buffer)

    def save_report_artifact(self, job_id: str, artifact_name: str, content: bytes):
        key = f"processed/{job_id}/reports/{artifact_name}"
        self.s3_client.put_object(Bucket=MINIO_BUCKET, Key=key, Body=content)

    def artifact_exists(self, job_id: str, artifact_name: str) -> bool:
        key = f"processed/{job_id}/{artifact_name}"
        try:
            self.s3_client.head_object(Bucket=MINIO_BUCKET, Key=key)
            return True
        except self.s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
 
    def load_artifact_as_bytes(self, job_id: str, artifact_name: str) -> Optional[bytes]:
        key = f"processed/{job_id}/{artifact_name}"
        try:
            response = self.s3_client.get_object(Bucket=MINIO_BUCKET, Key=key)
            return response['Body'].read()
        except self.s3_client.exceptions.NoSuchKey:
            return None

@lru_cache()
def get_state_store() -> StateStore:
    return StateStore()
