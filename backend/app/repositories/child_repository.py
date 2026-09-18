from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import Child
from app.schemas.child import ChildCreate

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
        db_child = Child(
            external_id=child_in.external_id,
            age_months=child_in.age_months,
            gender=child_in.gender,
            notes=child_in.notes
        )
        self.db.add(db_child)
        self.db.commit()
        self.db.refresh(db_child)
        return db_child
