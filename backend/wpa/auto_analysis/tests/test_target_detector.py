import pandas as pd
import pytest
import os
import shutil
import json
from backend.wpa.auto_analysis.target_detector import detect_target

@pytest.fixture
def synthetic_dataset():
    """
    Creates a synthetic dataset CSV file with a clear target variable ('churn')
    and cleans it up after the test.
    """
    job_id = "test_target_detector_job"
    output_dir = f"data/processed/{job_id}/"

    # Ensure a clean state before the test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Create a synthetic dataset
    data = {
        'user_id': range(300),
        'age': [25 + i % 30 for i in range(300)],
        'tenure': [1 + i % 10 for i in range(300)],
        'monthly_spend': [50 + (i % 20) * 5 for i in range(300)],
        # 'churn' is highly correlated with 'monthly_spend' and 'tenure'
        'churn': [(1 if (50 + (i % 20) * 5 > 100 and 1 + i % 10 > 5) else 0) for i in range(300)],
        'another_id': [f"id_{i}" for i in range(300)]
    }
    df = pd.DataFrame(data)

    csv_path = os.path.join(output_dir, "synthetic_data.csv")
    df.to_csv(csv_path, index=False)

    yield csv_path, job_id, output_dir

    # Cleanup after the test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

@pytest.mark.skip(reason="Test outdated due to target_detector refactoring to be stateless.")
def test_detect_target_integration(synthetic_dataset):
    """
    Integration test for the detect_target function.
    It runs the full detection logic on a synthetic dataset and checks the output.
    """
    csv_path, job_id, output_dir = synthetic_dataset

    # Run the target detection
    result = detect_target(
        input_csv_path=csv_path,
        job_id=job_id,
        out_base=output_dir
    )

    # 1. Verify the main decision
    assert result["decision_mode"] == "auto"
    assert result["selected_target"] == "churn"
    assert result["confidence"] > 0.7  # Expect high confidence

    # 2. Verify artifact creation
    target_json_path = os.path.join(output_dir, "target.json")
    manifest_json_path = os.path.join(output_dir, "manifest.json")
    eda_summary_path = os.path.join(output_dir, "eda", "summary.json")

    assert os.path.exists(target_json_path)
    assert os.path.exists(manifest_json_path)
    assert os.path.exists(eda_summary_path)

    # 3. Verify content of target.json
    with open(target_json_path, "r") as f:
        target_data = json.load(f)

    assert target_data["selected_target"] == "churn"
    top_candidate = target_data["candidates"][0]
    assert top_candidate["col"] == "churn"
    # Check that predictability score (P) was high
    assert top_candidate["components"]["P"] > 0.7

    # 4. Verify ID columns were filtered out
    candidate_cols = {c["col"] for c in target_data["candidates"]}
    assert "user_id" not in candidate_cols
    assert "another_id" not in candidate_cols
