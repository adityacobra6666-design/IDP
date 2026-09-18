from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.task import TaskResponse
from app.repositories.task_repository import TaskRepository

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    """List all standardized behavioral tasks."""
    repo = TaskRepository(db)
    repo.seed_default_tasks()
    return repo.get_all()

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get standardized task by ID."""
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found."
        )
    return task
