from typing import List, Optional
from sqlalchemy.orm import Session as DBSession, joinedload
from app.models.entities import Session, Child, Recording
from app.schemas.session import SessionCreate

class SessionRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def get_by_id(self, session_id: str) -> Optional[Session]:
        return self.db.query(Session)\
            .options(joinedload(Session.recordings), joinedload(Session.child), joinedload(Session.model_output))\
            .filter(Session.id == session_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Session]:
        return self.db.query(Session)\
            .options(joinedload(Session.recordings), joinedload(Session.child))\
            .order_by(Session.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_child_id(self, child_id: str) -> List[Session]:
        return self.db.query(Session)\
            .filter(Session.child_id == child_id)\
            .order_by(Session.created_at.desc()).all()

    def create(self, session_in: SessionCreate) -> Session:
        db_session = Session(
            child_id=session_in.child_id,
            status="CREATED",
            notes=session_in.notes
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def update_status(self, session_id: str, status: str) -> Optional[Session]:
        session = self.get_by_id(session_id)
        if session:
            session.status = status
            self.db.commit()
            self.db.refresh(session)
        return session

    def delete(self, session_id: str) -> bool:
        session = self.get_by_id(session_id)
        if not session:
            return False
        self.db.delete(session)
        self.db.commit()
        return True
