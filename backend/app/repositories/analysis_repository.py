from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from app.models.entities import QualityAssessment, BehavioralFeatures, ModelOutput

class AnalysisRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def save_quality_assessment(self, recording_id: str, overall_score: float, resolution_ok: bool, blur_score: float, face_visibility_ratio: float, pose_visibility_ratio: float, status: str, reasons: List[str]) -> QualityAssessment:
        # Delete existing if any for this recording
        self.db.query(QualityAssessment).filter(QualityAssessment.recording_id == recording_id).delete()
        
        qa = QualityAssessment(
            recording_id=recording_id,
            overall_score=overall_score,
            resolution_ok=resolution_ok,
            blur_score=blur_score,
            face_visibility_ratio=face_visibility_ratio,
            pose_visibility_ratio=pose_visibility_ratio,
            status=status,
            reasons_json=reasons
        )
        self.db.add(qa)
        self.db.commit()
        self.db.refresh(qa)
        return qa

    def get_quality_assessment(self, recording_id: str) -> Optional[QualityAssessment]:
        return self.db.query(QualityAssessment).filter(QualityAssessment.recording_id == recording_id).first()

    def save_behavioral_features(self, recording_id: str, features_list: List[Dict[str, Any]]) -> List[BehavioralFeatures]:
        self.db.query(BehavioralFeatures).filter(BehavioralFeatures.recording_id == recording_id).delete()
        
        db_features = []
        for feat in features_list:
            bf = BehavioralFeatures(
                recording_id=recording_id,
                feature_name=feat["feature_name"],
                value=float(feat["value"]),
                unit=str(feat["unit"]),
                source=str(feat.get("source", "video_cv")),
                valid=bool(feat.get("valid", True)),
                confidence=float(feat.get("confidence", 1.0))
            )
            self.db.add(bf)
            db_features.append(bf)
            
        self.db.commit()
        return db_features

    def get_behavioral_features(self, recording_id: str) -> List[BehavioralFeatures]:
        return self.db.query(BehavioralFeatures).filter(BehavioralFeatures.recording_id == recording_id).all()

    def save_model_output(self, session_id: str, overall_confidence_level: str, joint_attention_summary: Optional[Dict[str, Any]], imitation_summary: Optional[Dict[str, Any]], evidence_quality: Dict[str, Any], annotated_video_path: Optional[str], annotated_frame_paths: List[str]) -> ModelOutput:
        self.db.query(ModelOutput).filter(ModelOutput.session_id == session_id).delete()
        
        mo = ModelOutput(
            session_id=session_id,
            overall_confidence_level=overall_confidence_level,
            joint_attention_summary_json=joint_attention_summary,
            imitation_summary_json=imitation_summary,
            evidence_quality_json=evidence_quality,
            annotated_video_path=annotated_video_path,
            annotated_frame_paths_json=annotated_frame_paths
        )
        self.db.add(mo)
        self.db.commit()
        self.db.refresh(mo)
        return mo

    def get_model_output(self, session_id: str) -> Optional[ModelOutput]:
        return self.db.query(ModelOutput).filter(ModelOutput.session_id == session_id).first()
