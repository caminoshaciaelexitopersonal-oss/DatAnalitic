import uuid
import pandas as pd
from backend.core.state_store import get_state_store
from backend.wpa.tasks import master_pipeline_task
import os

def run_integration_test():
    """
    Simulates a job start and runs the master pipeline task directly
    for end-to-end testing.
    """
    print("--- Starting Integration Test ---")

    # 1. Setup
    state_store = get_state_store()
    job_id = str(uuid.uuid4())
    filename = "test_data.csv"

    print(f"Generated Job ID: {job_id}")

    # 2. Simulate File Upload
    # We need to manually create a "job" record in the DB so the pipeline can find it.
    # This is a bit of a hack, but necessary for this test approach.
    db_session = state_store.SessionLocal()
    try:
        # Create a dummy session to satisfy foreign key constraints
        session_orm = state_store.create_session(db_session)
        state_store.create_job(db_session, session_orm.session_id, "integration_test", filename)
    finally:
        db_session.close()

    # Now, save the raw file to MinIO
    with open(filename, 'rb') as f:
        content = f.read()
    state_store.save_raw_file(job_id, filename, content)
    print("Simulated file upload complete. File saved to MinIO.")

    # 3. Invoke Pipeline
    print("Invoking master_pipeline_task directly...")
    # Use .apply() for more control, but .delay() is simpler for this test
    result = master_pipeline_task.delay(job_id)

    print(f"Task sent to Celery. Task ID: {result.id}")
    print("--- Test Initiated ---")
    print("Monitor the 'worker' logs to see the pipeline execution.")

if __name__ == "__main__":
    # This script needs to be run from the root of the repository
    # where test_data.csv is located.
    # It also assumes the required environment variables are set up
    # for the StateStore to connect to DB, Redis, and MinIO.
    run_integration_test()
