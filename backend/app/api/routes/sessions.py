import os
import shutil
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ResourceNotFoundException, VideoProcessingException
from app.schemas.session import SessionCreate, SessionResponse, SessionDetailResponse
from app.schemas.recording import RecordingResponse
from app.schemas.analysis import AnalysisResultResponse
from app.repositories.session_repository import SessionRepository
from app.repositories.child_repository import ChildRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.recording_repository import RecordingRepository
from app.services.video_service import VideoService

router = APIRouter(prefix="/sessions", tags=["Sessions & Video Analysis"])

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    """Create a new behavioral monitoring session."""
    child_repo = ChildRepository(db)
    task_repo = TaskRepository(db)
    
    if not child_repo.get_by_id(session_in.child_id):
        raise HTTPException(status_code=404, detail=f"Child profile '{session_in.child_id}' not found.")
        
    if not task_repo.get_by_id(session_in.task_id):
        raise HTTPException(status_code=404, detail=f"Task '{session_in.task_id}' not found.")

    session_repo = SessionRepository(db)
    return session_repo.create(session_in)

@router.get("", response_model=List[SessionResponse])
def list_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all sessions."""
    repo = SessionRepository(db)
    return repo.get_all(skip=skip, limit=limit)

@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get detailed session information including child and recordings."""
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """
    Delete session, associated database records (recording, QA, features, model output),
    and associated uploaded/processed file assets. Does NOT delete the child profile.
    """
    session_repo = SessionRepository(db)
    session = session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    # 1. Collect recording file paths for deletion
    files_to_remove = []
    for rec in session.recordings:
        if rec.storage_path:
            files_to_remove.append(Path(rec.storage_path))

    # 2. Collect processed annotated frames directory for deletion
    processed_dir = settings.PROCESSED_DIR / session_id

    # 3. Delete DB record (Cascades delete to recordings, quality_assessments, behavioral_features, model_outputs)
    deleted_ok = session_repo.delete(session_id)
    if not deleted_ok:
        raise HTTPException(status_code=500, detail="Failed to delete session record from database.")

    # 4. Perform safe filesystem cleanup
    for file_path in files_to_remove:
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Cleaned up session video recording file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete recording file {file_path}: {e}")

    try:
        if processed_dir.exists() and processed_dir.is_dir():
            shutil.rmtree(processed_dir)
            logger.info(f"Cleaned up processed directory: {processed_dir}")
    except Exception as e:
        logger.warning(f"Failed to delete processed directory {processed_dir}: {e}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{session_id}/recording", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
def upload_recording(
    session_id: str,
    task_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a real task video recording for a session."""
    session_repo = SessionRepository(db)
    session = session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    task_repo = TaskRepository(db)
    if not task_repo.get_by_id(task_id):
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")

    # Generate safe storage filename
    ext = Path(file.filename).suffix.lower()
    if not ext:
        ext = ".mp4"
    safe_filename = f"{session_id}_{uuid.uuid4().hex[:8]}{ext}"
    storage_path = settings.UPLOAD_DIR / safe_filename

    try:
        with open(storage_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save video upload file.")

    # Validate video file format
    try:
        meta = VideoService.validate_video_file(storage_path)
    except VideoProcessingException as ve:
        if storage_path.exists():
            storage_path.unlink()
        raise HTTPException(status_code=400, detail=str(ve))

    recording_repo = RecordingRepository(db)
    recording = recording_repo.create(
        session_id=session_id,
        task_id=task_id,
        original_filename=file.filename,
        storage_path=str(storage_path),
        file_size_bytes=meta["file_size_bytes"],
        duration_seconds=meta["duration_seconds"],
        fps=meta["fps"],
        width=meta["width"],
        height=meta["height"]
    )

    session_repo.update_status(session_id, "RECORDING_UPLOADED")
    return recording

@router.post("/{session_id}/analyze")
def trigger_analysis(session_id: str, db: Session = Depends(get_db)):
    """Trigger the computer vision and feature extraction analysis pipeline."""
    from app.services.analysis_service import AnalysisService

    service = AnalysisService(db)
    try:
        res = service.process_session_recording(session_id)
        return res
    except ResourceNotFoundException as re:
        raise HTTPException(status_code=404, detail=str(re))
    except VideoProcessingException as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unhandled exception during video analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")
