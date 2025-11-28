import uuid
from fastapi import APIRouter, File, UploadFile, Depends, Form
from backend.mpa.ingestion.service import IngestionService, get_ingestion_service
from backend.core.security import User, require_role
from backend.schemas import Role

# --- API Router for Ingestion MPA ---
router = APIRouter(tags=["MPA - Ingestion"])

@router.post("/upload-file/", operation_id="uploadFile")
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(require_role(Role.DATA_SCIENTIST))
):
    """
    Handles file uploads and processes them using the IngestionService.
    This is the new MPA-based endpoint for file ingestion.
    **Requires DATA_SCIENTIST role.**
    """
    df = await ingestion_service.process_uploaded_file(file, session_id)
    # Return filename and a confirmation message, not the full data.
    return {
        "filename": file.filename,
        "message": f"File processed and associated with session {session_id}.",
        "user": current_user.username
    }
