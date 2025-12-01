from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os

from backend.mpa.delivery.delivery_service import DeliveryService
# Placeholder for authentication dependency
# from backend.mcp.services.auth_service import get_current_user_dep

router = APIRouter(
    prefix="/mpa/delivery",
    tags=["MPA - Code Delivery"],
    # dependencies=[Depends(get_current_user_dep)] # Secure endpoints
)

@router.get("/job/{job_id}/package", response_class=FileResponse)
def download_package(job_id: str):
    """
    Generates and downloads the full code delivery package for a job.
    """
    try:
        service = DeliveryService(job_id=job_id)
        zip_path = service.create_package()

        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Generated package not found.")

        # Return the file as a response, making it a download
        return FileResponse(
            path=zip_path,
            filename=f"sadi_delivery_{job_id}.zip",
            media_type="application/zip"
        )
    except ValueError as e:
        # Raised by pre-delivery validation
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch-all for other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# TODO: Implement the other two endpoints for code and notebook only
# @router.get("/job/{job_id}/code")
# def download_code(job_id: str):
#     # ... implementation ...
#
# @router.get("/job/{job_id}/notebook")
# def download_notebook(job_id: str):
#     # ... implementation ...
