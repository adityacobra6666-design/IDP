import os
import cv2
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ResourceNotFoundException, VideoProcessingException
from app.cv.face import FaceDetector
from app.cv.pose import PoseDetector
from app.cv.gaze import GazeTargetTracker
from app.cv.features import calculate_blur_score
from app.cv.feature_extractor import FeatureExtractor
from app.services.video_service import VideoService
from app.services.quality_service import QualityService
from app.repositories.session_repository import SessionRepository
from app.repositories.recording_repository import RecordingRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.task_repository import TaskRepository

class AnalysisService:
    def __init__(self, db: DBSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.recording_repo = RecordingRepository(db)
        self.analysis_repo = AnalysisRepository(db)
        self.task_repo = TaskRepository(db)

    def process_session_recording(self, session_id: str) -> Dict[str, Any]:
        """
        Main end-to-end execution pipeline for video analysis.
        """
        logger.info(f"Starting video analysis pipeline for session_id: {session_id}")
        
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundException(f"Session '{session_id}' not found")

        recording = self.recording_repo.get_by_session_id(session_id)
        if not recording:
            raise VideoProcessingException(f"No video recording found for session '{session_id}'")

        file_path = Path(recording.storage_path)
        if not file_path.exists():
            raise VideoProcessingException(f"Recording file missing at path: {file_path}")

        # 1. Video Metadata Extraction & Validation
        meta = VideoService.validate_video_file(file_path)
        
        # Update recording metadata in DB
        recording.duration_seconds = meta["duration_seconds"]
        recording.fps = meta["fps"]
        recording.width = meta["width"]
        recording.height = meta["height"]
        self.db.commit()

        # Update Session status to ANALYZING
        self.session_repo.update_status(session_id, "ANALYZING")

        # 2. Run Computer Vision Pipeline on sampled frames
        face_detector = FaceDetector()
        pose_detector = PoseDetector()
        gaze_tracker = GazeTargetTracker()

        sampled_blur_scores = []
        face_detected_count = 0
        pose_detected_count = 0
        
        joint_evaluations = []
        child_poses = []
        annotated_frame_paths = []

        total_sampled = 0
        saved_frames_limit = 5
        annotated_dir = settings.PROCESSED_DIR / session_id
        os.makedirs(annotated_dir, exist_ok=True)

        try:
            for frame_idx, timestamp_sec, frame in VideoService.extract_sampled_frames(file_path, max_samples=100):
                total_sampled += 1
                
                # Blur score
                blur = calculate_blur_score(frame)
                sampled_blur_scores.append(blur)

                # Face CV
                face_data = face_detector.process_frame(frame)
                if face_data.get("detected"):
                    face_detected_count += 1

                # Pose CV
                pose_data = pose_detector.process_frame(frame)
                if pose_data.get("detected"):
                    pose_detected_count += 1
                    child_poses.append(pose_data.get("landmarks", []))
                else:
                    child_poses.append([])

                # Joint Attention Gaze tracking
                gaze_eval = gaze_tracker.evaluate_frame_attention(face_data, active_target="TARGET_RIGHT")
                joint_evaluations.append(gaze_eval)

                # Save representative annotated frame snapshots
                if len(annotated_frame_paths) < saved_frames_limit and (face_data.get("detected") or pose_data.get("detected")):
                    ann_frame = face_detector.draw_landmarks(frame, face_data)
                    ann_frame = pose_detector.draw_landmarks(ann_frame, pose_data)
                    
                    status_text = f"Frame: {frame_idx} | Face: {face_data.get('detected')} | Pose: {pose_data.get('detected')}"
                    cv2.putText(ann_frame, status_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                    frame_name = f"annotated_frame_{len(annotated_frame_paths)+1}.jpg"
                    frame_dest = annotated_dir / frame_name
                    cv2.imwrite(str(frame_dest), ann_frame)
                    annotated_frame_paths.append(f"/processed/{session_id}/{frame_name}")

        finally:
            face_detector.close()
            pose_detector.close()

        # 3. Input Quality Gate Assessment
        qa_result = QualityService.evaluate_quality(
            meta=meta,
            sampled_blur_scores=sampled_blur_scores,
            face_detected_count=face_detected_count,
            pose_detected_count=pose_detected_count,
            total_sampled_frames=total_sampled
        )

        logger.info(f"[CV] Total frames sampled: {total_sampled}")
        logger.info(f"[CV] Face-detected frames: {face_detected_count} (ratio: {qa_result['face_visibility_ratio']})")
        logger.info(f"[CV] Pose-detected frames: {pose_detected_count} (ratio: {qa_result['pose_visibility_ratio']})")

        # Save Quality Assessment to DB
        qa_record = self.analysis_repo.save_quality_assessment(
            recording_id=recording.id,
            overall_score=qa_result["overall_score"],
            resolution_ok=qa_result["resolution_ok"],
            blur_score=qa_result["blur_score"],
            face_visibility_ratio=qa_result["face_visibility_ratio"],
            pose_visibility_ratio=qa_result["pose_visibility_ratio"],
            status=qa_result["status"],
            reasons=qa_result["reasons"]
        )

        # 4. Extract Core + Task Specific Features
        task = self.task_repo.get_by_id(recording.task_id)
        task_code = task.code if task else "joint_attention"

        feature_res = FeatureExtractor.extract_all_features(
            task_code=task_code,
            meta=meta,
            qa_result=qa_result,
            joint_evaluations=joint_evaluations,
            child_poses=child_poses,
            fps=meta["fps"]
        )

        all_features = feature_res["all_features_list"]
        joint_summary = feature_res["joint_summary"]
        imitation_summary = feature_res["imitation_summary"]

        # Persist features in DB
        self.analysis_repo.save_behavioral_features(recording.id, all_features)
        logger.info(f"[FEATURE] Extracted and persisted {len(all_features)} behavioral features into database.")

        # Check if quality gate rejected analysis for session status
        if qa_result["status"] == "REASSESSMENT_REQUIRED":
            logger.warning(f"Quality gate rejected video for session {session_id}. Reasons: {qa_result['reasons']}")
            self.session_repo.update_status(session_id, "REASSESSMENT_REQUIRED")
            
            mo = self.analysis_repo.save_model_output(
                session_id=session_id,
                overall_confidence_level="REASSESSMENT_REQUIRED",
                joint_attention_summary=joint_summary,
                imitation_summary=imitation_summary,
                evidence_quality={"score": qa_result["overall_score"], "status": "INSUFFICIENT_EVIDENCE"},
                annotated_video_path=None,
                annotated_frame_paths=annotated_frame_paths
            )
            return self.get_session_analysis_results(session_id)

        # 5. Calculate Evidence Quality / Confidence Level
        evidence_score = (qa_result["face_visibility_ratio"] + qa_result["pose_visibility_ratio"]) / 2.0
        if evidence_score >= 0.7 and qa_result["overall_score"] >= 70:
            confidence_level = "HIGH"
            explanation = "Sufficient face/pose landmark visibility and high image sharpness."
        elif evidence_score >= 0.4:
            confidence_level = "MEDIUM"
            explanation = "Moderate subject visibility. Some frames missing complete landmark tracking."
        else:
            confidence_level = "LOW"
            explanation = "Low subject visibility in recording."

        evidence_quality = {
            "score": round(evidence_score, 2),
            "quality_score": qa_result["overall_score"],
            "explanation": explanation
        }

        # 6. Persist Model Output & Update Session Status
        self.analysis_repo.save_model_output(
            session_id=session_id,
            overall_confidence_level=confidence_level,
            joint_attention_summary=joint_summary,
            imitation_summary=imitation_summary,
            evidence_quality=evidence_quality,
            annotated_video_path=None,
            annotated_frame_paths=annotated_frame_paths
        )

        self.session_repo.update_status(session_id, "COMPLETED")
        logger.info(f"Successfully completed analysis for session_id: {session_id}")

        return self.get_session_analysis_results(session_id)

    def get_session_analysis_results(self, session_id: str) -> Dict[str, Any]:
        """Fetch complete aggregated analysis results for a session."""
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundException(f"Session '{session_id}' not found")

        recording = self.recording_repo.get_by_session_id(session_id)
        if not recording:
            raise ResourceNotFoundException(f"No recording found for session '{session_id}'")

        qa = self.analysis_repo.get_quality_assessment(recording.id)
        features = self.analysis_repo.get_behavioral_features(recording.id)
        model_output = self.analysis_repo.get_model_output(session_id)
        task = self.task_repo.get_by_id(recording.task_id)

        task_code = task.code if task else "joint_attention"
        task_name = task.name if task else "Standardized Task"

        quality_dict = {
            "id": qa.id if qa else "",
            "recording_id": recording.id,
            "overall_score": qa.overall_score if qa else 0.0,
            "resolution_ok": qa.resolution_ok if qa else False,
            "blur_score": qa.blur_score if qa else 0.0,
            "face_visibility_ratio": qa.face_visibility_ratio if qa else 0.0,
            "pose_visibility_ratio": qa.pose_visibility_ratio if qa else 0.0,
            "status": qa.status if qa else "REASSESSMENT_REQUIRED",
            "reasons_json": qa.reasons_json if qa else ["No quality assessment record"],
            "created_at": qa.created_at if qa else session.created_at
        }

        features_list = [
            {
                "feature_name": f.feature_name,
                "value": f.value,
                "unit": f.unit,
                "source": f.source,
                "valid": f.valid,
                "confidence": f.confidence
            }
            for f in features
        ]

        conf_level = model_output.overall_confidence_level if model_output else "REASSESSMENT_REQUIRED"
        ev_quality = model_output.evidence_quality_json if model_output else {}
        explanation = ev_quality.get("explanation", "Analysis quality pending")

        return {
            "session_id": session.id,
            "task_code": task_code,
            "task_name": task_name,
            "processing_status": session.status,
            "quality": quality_dict,
            "features": features_list,
            "joint_attention_summary": model_output.joint_attention_summary_json if model_output else None,
            "imitation_summary": model_output.imitation_summary_json if model_output else None,
            "confidence": {
                "level": conf_level,
                "evidence_quality_score": ev_quality.get("score", 0.0),
                "explanation": explanation
            },
            "warnings": qa.reasons_json if qa and qa.status == "REASSESSMENT_REQUIRED" else [],
            "annotated_video_url": model_output.annotated_video_path if model_output else None,
            "annotated_frame_urls": model_output.annotated_frame_paths_json if model_output else [],
            "created_at": session.created_at
        }
