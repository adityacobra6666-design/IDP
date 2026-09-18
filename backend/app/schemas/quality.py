from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class QualityAssessmentResponse(BaseModel):
    id: str
    recording_id: str
    overall_score: float = Field(..., description="Overall video quality score (0-100)")
    resolution_ok: bool
    blur_score: float = Field(..., description="Variance of Laplacian blur score")
    face_visibility_ratio: float = Field(..., description="Ratio of sampled frames where face is visible")
    pose_visibility_ratio: float = Field(..., description="Ratio of sampled frames where pose landmarks are visible")
    status: str = Field(..., description="Quality Gate decision: VALID or REASSESSMENT_REQUIRED")
    reasons_json: List[str] = Field(default_factory=list, description="Transparent quality evaluation reasons")
    created_at: datetime

    class Config:
        from_attributes = True
