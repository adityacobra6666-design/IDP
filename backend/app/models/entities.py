import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from app.models.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Child(Base):
    __tablename__ = "children"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    external_id = Column(String(50), unique=True, nullable=False, index=True)
    age_months = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    profile_number = Column(Integer, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="child", cascade="all, delete-orphan")
    questionnaire = relationship("ParentQuestionnaire", back_populates="child", uselist=False, cascade="all, delete-orphan")

class ParentQuestionnaire(Base):
    __tablename__ = "parent_questionnaires"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    developmental_context = Column(JSON, nullable=True)
    communication = Column(JSON, nullable=True)
    social_interaction = Column(JSON, nullable=True)
    attention_engagement = Column(JSON, nullable=True)
    imitation_play = Column(JSON, nullable=True)
    sensory_context = Column(JSON, nullable=True)
    parent_observations = Column(Text, nullable=True)
    session_context = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    child = relationship("Child", back_populates="questionnaire")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'joint_attention', 'imitation'
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recordings = relationship("Recording", back_populates="task")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    session_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="CREATED", index=True)  # CREATED, RECORDING_UPLOADED, ANALYZING, COMPLETED, REASSESSMENT_REQUIRED, FAILED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    child = relationship("Child", back_populates="sessions")
    recordings = relationship("Recording", back_populates="session", cascade="all, delete-orphan")
    model_output = relationship("ModelOutput", back_populates="session", uselist=False, cascade="all, delete-orphan")

class Recording(Base):
    __tablename__ = "recordings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=True)
    fps = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="recordings")
    task = relationship("Task", back_populates="recordings")
    quality_assessment = relationship("QualityAssessment", back_populates="recording", uselist=False, cascade="all, delete-orphan")
    features = relationship("BehavioralFeatures", back_populates="recording", cascade="all, delete-orphan")

class QualityAssessment(Base):
    __tablename__ = "quality_assessments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    recording_id = Column(String(36), ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)  # 0.0 - 100.0
    resolution_ok = Column(Boolean, nullable=False, default=True)
    blur_score = Column(Float, nullable=False)
    face_visibility_ratio = Column(Float, nullable=False)
    pose_visibility_ratio = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)  # VALID, REASSESSMENT_REQUIRED
    reasons_json = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recording = relationship("Recording", back_populates="quality_assessment")

class BehavioralFeatures(Base):
    __tablename__ = "behavioral_features"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    recording_id = Column(String(36), ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)  # e.g., 'video_cv', 'audio'
    valid = Column(Boolean, nullable=False, default=True)
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recording = relationship("Recording", back_populates="features")

class ModelOutput(Base):
    __tablename__ = "model_outputs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_confidence_level = Column(String(50), nullable=False)  # HIGH, MEDIUM, LOW, REASSESSMENT_REQUIRED
    joint_attention_summary_json = Column(JSON, nullable=True)
    imitation_summary_json = Column(JSON, nullable=True)
    evidence_quality_json = Column(JSON, nullable=False)
    annotated_video_path = Column(String(500), nullable=True)
    annotated_frame_paths_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="model_output")
