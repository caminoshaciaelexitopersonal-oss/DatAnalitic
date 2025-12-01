import pytest
from fastapi.testclient import TestClient
import zipfile
import json
from unittest.mock import patch

from backend.app_factory import create_app
from backend.mpa.delivery.delivery_service import DeliveryService

# Create a TestClient instance for making API requests
client = TestClient(create_app())

@pytest.fixture
def mock_metadata():
    """Fixture to mock the job metadata retrieval."""
    return {
        "job_id": "test_job_123",
        "status": "COMPLETED",
        "dtl_completed": True,
        "algorithm_used": "TestAlgo",
        "parameters": {"param": "value"}
    }

def test_delivery_service_creates_valid_package(tmp_path, mock_metadata):
    """
    Tests that the DeliveryService creates a zip file with the correct structure.
    """
    with patch('backend.mpa.delivery.delivery_service._get_job_metadata', return_value=mock_metadata):
        # Use a temporary directory for test outputs
        service = DeliveryService(job_id="test_job_123")
        service.package_dir = tmp_path / "package"
        service.zip_path = tmp_path / "delivery.zip"
        os.makedirs(service.package_dir, exist_ok=True)

        zip_path = service.create_package()

        assert os.path.exists(zip_path)

        # Verify the contents of the zip file
        with zipfile.ZipFile(zip_path, 'r') as zf:
            filenames = zf.namelist()
            assert "manifest.json" in filenames
            assert "README.md" in filenames
            assert "src/model_training.py" in filenames

            # Check manifest content
            with zf.open("manifest.json") as f:
                manifest = json.load(f)
                assert manifest["job_id"] == "test_job_123"
                assert "code_sha256" in manifest

def test_download_package_endpoint_success(mock_metadata):
    """
    Tests the GET /mpa/delivery/job/{job_id}/package endpoint for a successful case.
    """
    with patch('backend.mpa.delivery.delivery_service._get_job_metadata', return_value=mock_metadata):
        response = client.get("/unified/v1/mpa/delivery/job/test_job_123/package")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]
        assert "sadi_delivery_test_job_123.zip" in response.headers["content-disposition"]

        # Check if the response content is a valid zip file (at least check the header)
        assert response.content.startswith(b'PK')

def test_download_package_endpoint_job_not_completed():
    """
    Tests that the endpoint returns a 400 error if the job has not completed.
    """
    incomplete_metadata = {
        "job_id": "test_job_456",
        "status": "RUNNING",
        "dtl_completed": True,
    }
    with patch('backend.mpa.delivery.delivery_service._get_job_metadata', return_value=incomplete_metadata):
        response = client.get("/unified/v1/mpa/delivery/job/test_job_456/package")

        assert response.status_code == 400
        assert "has not completed successfully" in response.json()["detail"]
