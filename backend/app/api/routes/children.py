from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.child import ChildCreate, ChildResponse
from app.repositories.child_repository import ChildRepository

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
