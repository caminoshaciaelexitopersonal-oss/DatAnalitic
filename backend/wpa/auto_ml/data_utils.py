"""
This module provides utility functions for data loading, validation,
splitting, and snapshotting, as defined in the "Plan Científico".
"""
import pandas as pd
import os

def load_and_validate_data(path: str) -> pd.DataFrame:
    """Loads data and performs initial validation."""
    # TODO: Implement robust data loading and validation
    df = pd.read_csv(path)
    return df

def train_test_split_stratified(df: pd.DataFrame, target: str, problem_type: str):
    """Performs stratified train-test split."""
    # TODO: Implement stratified splitting logic
    pass

def get_output_dir(job_id: str) -> str:
    """
    Returns the standardized output directory for a given job.
    This function is a placeholder and should be updated to use the StateStore.
    """
    # This is a temporary solution. In a real system, this would be
    # managed by the StateStore to return a MinIO path.
    path = f"/tmp/sadi_jobs/{job_id}/automl"
    os.makedirs(path, exist_ok=True)
    return path
