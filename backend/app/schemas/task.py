from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    code: str = Field(..., description="Unique task code, e.g. joint_attention, imitation")
    name: str = Field(..., description="Human-readable task name")
    description: Optional[str] = None
    category: str = Field(..., description="Category: joint_attention, imitation, etc.")

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
