from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ChildBase(BaseModel):
    external_id: str = Field(..., description="Unique anonymized external ID for the child, e.g. C-1029")
    age_months: int = Field(..., ge=6, le=180, description="Age of child in months")
    gender: str = Field(..., description="Gender: Male, Female, Other")
    notes: Optional[str] = None

class ChildCreate(ChildBase):
    pass

class ChildResponse(ChildBase):
    id: str
    profile_number: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
