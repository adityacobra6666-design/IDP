from typing import Optional
from sqlalchemy.orm import Session as DBSession
from app.models.entities import Recording

class RecordingRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def get_by_id(self, recording_id: str) -> Optional[Recording]:
        return self.db.query(Recording).filter(Recording.id == recording_id).first()

    def get_by_session_id(self, session_id: str) -> Optional[Recording]:
        return self.db.query(Recording).filter(Recording.session_id == session_id).order_by(Recording.created_at.desc()).first()

    def create(self, session_id: str, task_id: str, original_filename: str, storage_path: str, file_size_bytes: int, duration_seconds: float = None, fps: float = None, width: int = None, height: int = None) -> Recording:
        recording = Recording(
            session_id=session_id,
            task_id=task_id,
            original_filename=original_filename,
            storage_path=storage_path,
            file_size_bytes=file_size_bytes,
            duration_seconds=duration_seconds,
            fps=fps,
            width=width,
            height=height
        )
        self.db.add(recording)
        self.db.commit()
        self.db.refresh(recording)
        return recording
