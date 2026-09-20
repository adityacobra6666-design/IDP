from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.schemas.quality import QualityAssessmentResponse
from app.schemas.features import BehavioralFeatureResponse
from app.repositories.recording_repository import RecordingRepository
from app.repositories.analysis_repository import AnalysisRepository

router = APIRouter(prefix="/sessions", tags=["Analysis Results"])

@router.get("/{session_id}/quality", response_model=QualityAssessmentResponse)
def get_session_quality(session_id: str, db: Session = Depends(get_db)):
    """Get input Quality Gate evaluation for a session."""
    rec_repo = RecordingRepository(db)
    rec = rec_repo.get_by_session_id(session_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"No recording found for session '{session_id}'.")

    analysis_repo = AnalysisRepository(db)
    qa = analysis_repo.get_quality_assessment(rec.id)
    if not qa:
        raise HTTPException(status_code=404, detail=f"No quality assessment found for session '{session_id}'.")
    return qa

@router.get("/{session_id}/features", response_model=List[BehavioralFeatureResponse])
def get_session_features(session_id: str, db: Session = Depends(get_db)):
    """Get extracted behavioral feature metrics for a session."""
    rec_repo = RecordingRepository(db)
    rec = rec_repo.get_by_session_id(session_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"No recording found for session '{session_id}'.")

    analysis_repo = AnalysisRepository(db)
    features = analysis_repo.get_behavioral_features(rec.id)
    return features

@router.get("/{session_id}/results")
def get_session_results(session_id: str, db: Session = Depends(get_db)):
    """Get complete structured analysis result for a session."""
    from app.services.analysis_service import AnalysisService

    service = AnalysisService(db)
    try:
        return service.get_session_analysis_results(session_id)
    except ResourceNotFoundException as re:
        raise HTTPException(status_code=404, detail=str(re))
