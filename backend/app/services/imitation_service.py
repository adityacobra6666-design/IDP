import numpy as np
from typing import List, Dict, Any
from app.cv.features import compute_pose_similarity

class ImitationService:
    @classmethod
    def analyze_imitation(
        cls,
        child_poses: List[List[Dict[str, float]]],
        reference_poses: Optional[List[List[Dict[str, float]]]] = None,
        fps: float = 30.0
    ) -> Dict[str, Any]:
        """
        Analyze Motor Imitation metrics comparing child pose sequence with reference posture sequence.
        """
        if not child_poses:
            return {
                "pose_similarity": 0.0,
                "movement_consistency": 0.0,
                "movement_completion_proxy": 0.0,
                "response_latency_sec": 0.0,
                "features_list": []
            }

        similarities = []
        frame_time_step = 1.0 / max(1.0, fps)

        for idx, c_pose in enumerate(child_poses):
            if not c_pose:
                continue
                
            # If reference sequence is available, compare frame-wise or to target posture
            if reference_poses and idx < len(reference_poses) and reference_poses[idx]:
                ref_pose = reference_poses[idx]
            else:
                # Default canonical reference posture: arms raised motor imitation posture
                ref_pose = cls._generate_canonical_reference_pose()

            sim = compute_pose_similarity(c_pose, ref_pose)
            similarities.append(sim)

        if not similarities:
            mean_sim = 0.0
            consistency = 0.0
            completion_proxy = 0.0
            latency = 0.0
        else:
            mean_sim = float(np.mean(similarities))
            # Lower variance in similarity = higher movement consistency
            consistency = float(np.clip(1.0 - np.std(similarities) * 2.0, 0.0, 1.0))
            completion_proxy = float(np.sum(np.array(similarities) > 0.6) / len(similarities))
            
            # First frame index reaching peak similarity > 0.65
            peak_indices = np.where(np.array(similarities) > 0.65)[0]
            latency = float(peak_indices[0] * frame_time_step) if len(peak_indices) > 0 else float(len(similarities) * frame_time_step)

        features = [
            {
                "feature_name": "pose_similarity",
                "value": round(mean_sim, 3),
                "unit": "score",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.85
            },
            {
                "feature_name": "movement_consistency",
                "value": round(consistency, 3),
                "unit": "score",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.85
            },
            {
                "feature_name": "movement_completion_proxy",
                "value": round(completion_proxy, 3),
                "unit": "ratio",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.85
            },
            {
                "feature_name": "response_latency",
                "value": round(latency, 2),
                "unit": "seconds",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.80
            }
        ]

        return {
            "pose_similarity": round(mean_sim, 3),
            "movement_consistency": round(consistency, 3),
            "movement_completion_proxy": round(completion_proxy, 3),
            "response_latency_sec": round(latency, 2),
            "features_list": features
        }

    @staticmethod
    def _generate_canonical_reference_pose() -> List[Dict[str, float]]:
        """Generate normalized 33 MediaPipe pose keypoints for canonical arms-raised imitation reference."""
        landmarks = []
        for i in range(33):
            landmarks.append({"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9})
        # Left shoulder (11), Right shoulder (12)
        landmarks[11] = {"x": 0.4, "y": 0.4, "z": 0.0, "visibility": 0.95}
        landmarks[12] = {"x": 0.6, "y": 0.4, "z": 0.0, "visibility": 0.95}
        # Left elbow (13), Right elbow (14)
        landmarks[13] = {"x": 0.35, "y": 0.3, "z": 0.0, "visibility": 0.95}
        landmarks[14] = {"x": 0.65, "y": 0.3, "z": 0.0, "visibility": 0.95}
        # Left wrist (15), Right wrist (16)
        landmarks[15] = {"x": 0.3, "y": 0.2, "z": 0.0, "visibility": 0.95}
        landmarks[16] = {"x": 0.7, "y": 0.2, "z": 0.0, "visibility": 0.95}
        # Left hip (23), Right hip (24)
        landmarks[23] = {"x": 0.42, "y": 0.7, "z": 0.0, "visibility": 0.95}
        landmarks[24] = {"x": 0.58, "y": 0.7, "z": 0.0, "visibility": 0.95}
        return landmarks
