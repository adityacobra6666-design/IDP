import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.child import ChildCreate, ChildResponse
from app.schemas.questionnaire import ParentQuestionnaireCreate, ParentQuestionnaireResponse
from app.repositories.child_repository import ChildRepository
from app.repositories.questionnaire_repository import QuestionnaireRepository
from app.core.logging import logger

router = APIRouter(prefix="/children", tags=["Children"])

@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(child_in: ChildCreate, db: Session = Depends(get_db)):
    """Create a new child profile record."""
    repo = ChildRepository(db)
    existing = repo.get_by_external_id(child_in.external_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Child with external_id '{child_in.external_id}' already exists."
        )
    return repo.create(child_in)

@router.get("", response_model=List[ChildResponse])
def list_children(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered children profiles."""
    repo = ChildRepository(db)
    return repo.get_all(skip=skip, limit=limit)

@router.get("/{child_id}", response_model=ChildResponse)
def get_child(child_id: str, db: Session = Depends(get_db)):
    """Get child profile by ID."""
    repo = ChildRepository(db)
    child = repo.get_by_id(child_id)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID '{child_id}' not found."
        )
    return child

@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(child_id: str, db: Session = Depends(get_db)):
    """Delete child profile and all associated sessions, recordings, assessments, features, outputs, and files."""
    repo = ChildRepository(db)
    deleted_ok, video_files, processed_dirs = repo.delete(child_id)
    if not deleted_ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID '{child_id}' not found."
        )

    # Perform file cleanup for deleted child's sessions
    for vf in video_files:
        try:
            if vf.exists():
                vf.unlink()
                logger.info(f"Cleaned up video recording file: {vf}")
        except Exception as e:
            logger.warning(f"Failed to delete recording file {vf}: {e}")

    for pd in processed_dirs:
        try:
            if pd.exists() and pd.is_dir():
                shutil.rmtree(pd)
                logger.info(f"Cleaned up processed directory: {pd}")
        except Exception as e:
            logger.warning(f"Failed to delete processed directory {pd}: {e}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{child_id}/questionnaire", response_model=ParentQuestionnaireResponse)
def get_parent_questionnaire(child_id: str, db: Session = Depends(get_db)):
    """Retrieve parent questionnaire for specified child profile."""
    child_repo = ChildRepository(db)
    if not child_repo.get_by_id(child_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID '{child_id}' not found."
        )
    q_repo = QuestionnaireRepository(db)
    quest = q_repo.get_by_child_id(child_id)
    if not quest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent questionnaire not completed"
        )
    return quest

@router.post("/{child_id}/questionnaire", response_model=ParentQuestionnaireResponse)
@router.put("/{child_id}/questionnaire", response_model=ParentQuestionnaireResponse)
def save_parent_questionnaire(child_id: str, questionnaire_in: ParentQuestionnaireCreate, db: Session = Depends(get_db)):
    """Create or update parent questionnaire for specified child profile."""
    child_repo = ChildRepository(db)
    if not child_repo.get_by_id(child_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID '{child_id}' not found."
        )
    q_repo = QuestionnaireRepository(db)
    return q_repo.save_or_update(child_id, questionnaire_in)
