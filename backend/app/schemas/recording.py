from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RecordingResponse(BaseModel):
    id: str
    session_id: str
    task_id: str
    original_filename: str
    storage_path: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
