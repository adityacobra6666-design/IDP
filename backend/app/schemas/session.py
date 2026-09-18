from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.recording import RecordingResponse
from app.schemas.child import ChildResponse

class SessionCreate(BaseModel):
    child_id: str
    task_id: str
    notes: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    child_id: str
    session_date: datetime
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    recordings: List[RecordingResponse] = []

    class Config:
        from_attributes = True

class SessionDetailResponse(SessionResponse):
    child: ChildResponse
