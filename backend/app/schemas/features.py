from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BehavioralFeatureItem(BaseModel):
    feature_name: str
    value: float
    unit: str
    source: str
    valid: bool
    confidence: float

    class Config:
        from_attributes = True

class BehavioralFeatureResponse(BehavioralFeatureItem):
    id: str
    recording_id: str
    created_at: datetime
