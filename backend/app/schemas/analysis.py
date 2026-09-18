from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.schemas.quality import QualityAssessmentResponse
from app.schemas.features import BehavioralFeatureItem

class ConfidenceResult(BaseModel):
    level: str = Field(..., description="Overall confidence level: HIGH, MEDIUM, LOW, REASSESSMENT_REQUIRED")
    evidence_quality_score: float = Field(..., description="Calculated evidence quality score (0.0 - 1.0)")
    explanation: str

class AnalysisResultResponse(BaseModel):
    session_id: str
    task_code: str
    task_name: str
    processing_status: str
    quality: QualityAssessmentResponse
    features: List[BehavioralFeatureItem]
    joint_attention_summary: Optional[Dict[str, Any]] = None
    imitation_summary: Optional[Dict[str, Any]] = None
    confidence: ConfidenceResult
    warnings: List[str] = Field(default_factory=list)
    annotated_video_url: Optional[str] = None
    annotated_frame_urls: List[str] = Field(default_factory=list)
    created_at: datetime
