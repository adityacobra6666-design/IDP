from typing import List, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.entities import Child
from app.schemas.child import ChildCreate
from app.core.config import settings

class ChildRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, child_id: str) -> Optional[Child]:
        return self.db.query(Child).filter(Child.id == child_id).first()

    def get_by_external_id(self, external_id: str) -> Optional[Child]:
        return self.db.query(Child).filter(Child.external_id == external_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Child]:
        return self.db.query(Child).order_by(Child.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, child_in: ChildCreate) -> Child:
        max_num = self.db.query(func.max(Child.profile_number)).scalar() or 0
        new_num = max_num + 1

        db_child = Child(
            external_id=child_in.external_id,
            age_months=child_in.age_months,
            gender=child_in.gender,
            notes=child_in.notes,
            profile_number=new_num
        )
        self.db.add(db_child)
        self.db.commit()
        self.db.refresh(db_child)
        return db_child

    def delete(self, child_id: str) -> Tuple[bool, List[Path], List[Path]]:
        child = self.get_by_id(child_id)
        if not child:
            return False, [], []

        video_files: List[Path] = []
        processed_dirs: List[Path] = []

        for session in child.sessions:
            processed_dirs.append(settings.PROCESSED_DIR / session.id)
            for rec in session.recordings:
                if rec.storage_path:
                    video_files.append(Path(rec.storage_path))

        self.db.delete(child)
        self.db.commit()

        return True, video_files, processed_dirs
