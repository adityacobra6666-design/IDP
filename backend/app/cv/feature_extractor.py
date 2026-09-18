import numpy as np
from typing import Dict, Any, List, Optional
from app.cv.features import compute_pose_similarity, normalize_pose_landmarks

class FeatureExtractor:
    """
    Modular Feature Extraction Engine for NeuroTrack AI.
    Extracts Core CV features (face/pose visibility, head orientation stability, movement magnitude)
    and Task-Specific Behavioral features (Joint Attention attention proxy & Motor Imitation pose similarity).
    """

    @classmethod
    def extract_all_features(
        cls,
        task_code: str,
        meta: Dict[str, Any],
        qa_result: Dict[str, Any],
        joint_evaluations: List[Dict[str, Any]],
        child_poses: List[List[Dict[str, float]]],
        fps: float
    ) -> Dict[str, Any]:
        """
        Main entrypoint extracting Core CV features + Task Specific Features.
        Returns dict containing:
        - `all_features_list`: List of feature dicts for DB persistence.
        - `joint_summary`: Dict or None
        - `imitation_summary`: Dict or None
        """
        all_features = []
        frame_time_step = 1.0 / max(1.0, fps)
        total_frames = max(1, len(joint_evaluations))

        # ----------------------------------------------------
        # 1. CORE CV FEATURES (Computed for ALL recordings)
        # ----------------------------------------------------
        face_ratio = qa_result.get("face_visibility_ratio", 0.0)
        pose_ratio = qa_result.get("pose_visibility_ratio", 0.0)
        face_valid = face_ratio >= 0.25
        pose_valid = pose_ratio >= 0.25

        # Feature 1: Face Visibility Ratio
        all_features.append({
            "feature_name": "face_visibility_ratio",
            "value": round(face_ratio, 3),
            "unit": "ratio",
            "source": "MediaPipe Face",
            "valid": face_valid,
            "confidence": 0.95 if face_valid else 0.4
        })

        # Feature 2: Pose Visibility Ratio
        all_features.append({
            "feature_name": "pose_visibility_ratio",
            "value": round(pose_ratio, 3),
            "unit": "ratio",
            "source": "MediaPipe Pose",
            "valid": pose_valid,
            "confidence": 0.95 if pose_valid else 0.4
        })

        # Feature 3: Head Orientation Stability (Yaw variance)
        yaws = [ev.get("yaw_degrees", 0.0) for ev in joint_evaluations if ev.get("confidence", 0) > 0]
        if yaws and face_valid:
            yaw_std = float(np.std(yaws))
            orientation_stability = float(np.clip(1.0 - (yaw_std / 45.0), 0.0, 1.0))
        else:
            orientation_stability = 0.0

        all_features.append({
            "feature_name": "head_orientation_stability",
            "value": round(orientation_stability, 3),
            "unit": "score",
            "source": "video_cv",
            "valid": face_valid,
            "confidence": 0.85 if face_valid else 0.0
        })

        # Feature 4 & 5: Body Movement Magnitude & Trajectory Consistency
        valid_poses = [p for p in child_poses if len(p) >= 24]
        if len(valid_poses) >= 2 and pose_valid:
            displacements = []
            for i in range(1, len(valid_poses)):
                norm_p1 = normalize_pose_landmarks(valid_poses[i-1])
                norm_p2 = normalize_pose_landmarks(valid_poses[i])
                if norm_p1.size > 0 and norm_p2.size > 0:
                    disp = float(np.mean(np.linalg.norm(norm_p2[11:25] - norm_p1[11:25], axis=1)))
                    displacements.append(disp)

            mov_magnitude = float(np.mean(displacements)) if displacements else 0.0
            mov_consistency = float(np.clip(1.0 - np.std(displacements) * 3.0, 0.0, 1.0)) if displacements else 0.0
        else:
            mov_magnitude = 0.0
            mov_consistency = 0.0

        all_features.append({
            "feature_name": "movement_magnitude",
            "value": round(mov_magnitude, 4),
            "unit": "normalized_dist",
            "source": "MediaPipe Pose",
            "valid": pose_valid,
            "confidence": 0.85 if pose_valid else 0.0
        })

        all_features.append({
            "feature_name": "movement_consistency",
            "value": round(mov_consistency, 3),
            "unit": "score",
            "source": "MediaPipe Pose",
            "valid": pose_valid,
            "confidence": 0.85 if pose_valid else 0.0
        })

        # ----------------------------------------------------
        # 2. TASK-SPECIFIC FEATURES
        # ----------------------------------------------------
        joint_summary = None
        imitation_summary = None

        if task_code == "joint_attention":
            oriented_count = 0
            first_orientation_idx = None
            max_fixation_frames = 0
            current_fixation_frames = 0
            gaze_shifts = 0
            previous_zone = None

            for idx, ev in enumerate(joint_evaluations):
                is_oriented = ev.get("oriented_to_target", False)
                current_zone = ev.get("target_zone", "NONE")

                if is_oriented:
                    oriented_count += 1
                    if first_orientation_idx is None:
                        first_orientation_idx = idx

                    current_fixation_frames += 1
                    if current_fixation_frames > max_fixation_frames:
                        max_fixation_frames = current_fixation_frames
                else:
                    current_fixation_frames = 0

                if previous_zone and previous_zone != current_zone and current_zone != "NONE":
                    gaze_shifts += 1

                previous_zone = current_zone

            orientation_ratio = round(oriented_count / total_frames, 3)
            orientation_latency = round(first_orientation_idx * frame_time_step, 2) if first_orientation_idx is not None else round(total_frames * frame_time_step, 2)
            max_fixation_sec = round(max_fixation_frames * frame_time_step, 2)

            joint_summary = {
                "target_orientation_ratio": orientation_ratio,
                "orientation_latency_sec": orientation_latency,
                "fixation_duration_sec": max_fixation_sec,
                "gaze_shift_count": gaze_shifts
            }

            all_features.extend([
                {
                    "feature_name": "target_orientation_ratio",
                    "value": orientation_ratio,
                    "unit": "ratio",
                    "source": "video_cv",
                    "valid": face_valid,
                    "confidence": 0.9 if face_valid else 0.2
                },
                {
                    "feature_name": "orientation_latency",
                    "value": orientation_latency,
                    "unit": "seconds",
                    "source": "video_cv",
                    "valid": face_valid,
                    "confidence": 0.85 if face_valid else 0.2
                },
                {
                    "feature_name": "fixation_duration",
                    "value": max_fixation_sec,
                    "unit": "seconds",
                    "source": "video_cv",
                    "valid": face_valid,
                    "confidence": 0.9 if face_valid else 0.2
                },
                {
                    "feature_name": "gaze_shift_count",
                    "value": float(gaze_shifts),
                    "unit": "count",
                    "source": "video_cv",
                    "valid": face_valid,
                    "confidence": 0.85 if face_valid else 0.2
                }
            ])

        elif task_code == "imitation":
            similarities = []
            canonical_ref = cls._generate_canonical_reference_pose()

            for c_pose in child_poses:
                if c_pose and len(c_pose) >= 24:
                    sim = compute_pose_similarity(c_pose, canonical_ref)
                    similarities.append(sim)

            if not similarities or not pose_valid:
                mean_sim = 0.0
                im_consistency = 0.0
                completion_proxy = 0.0
                latency = 0.0
            else:
                mean_sim = float(np.mean(similarities))
                im_consistency = float(np.clip(1.0 - np.std(similarities) * 2.0, 0.0, 1.0))
                completion_proxy = float(np.sum(np.array(similarities) > 0.6) / len(similarities))
                peak_indices = np.where(np.array(similarities) > 0.65)[0]
                latency = float(peak_indices[0] * frame_time_step) if len(peak_indices) > 0 else float(len(similarities) * frame_time_step)

            imitation_summary = {
                "pose_similarity": round(mean_sim, 3),
                "movement_consistency": round(im_consistency, 3),
                "movement_completion_proxy": round(completion_proxy, 3),
                "response_latency_sec": round(latency, 2)
            }

            all_features.extend([
                {
                    "feature_name": "pose_similarity",
                    "value": round(mean_sim, 3),
                    "unit": "score",
                    "source": "video_cv",
                    "valid": pose_valid,
                    "confidence": 0.85 if pose_valid else 0.2
                },
                {
                    "feature_name": "movement_completion_proxy",
                    "value": round(completion_proxy, 3),
                    "unit": "ratio",
                    "source": "video_cv",
                    "valid": pose_valid,
                    "confidence": 0.85 if pose_valid else 0.2
                },
                {
                    "feature_name": "response_latency",
                    "value": round(latency, 2),
                    "unit": "seconds",
                    "source": "video_cv",
                    "valid": pose_valid,
                    "confidence": 0.80 if pose_valid else 0.2
                }
            ])

        return {
            "all_features_list": all_features,
            "joint_summary": joint_summary,
            "imitation_summary": imitation_summary
        }

    @staticmethod
    def _generate_canonical_reference_pose() -> List[Dict[str, float]]:
        landmarks = []
        for i in range(33):
            landmarks.append({"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9})
        landmarks[11] = {"x": 0.4, "y": 0.4, "z": 0.0, "visibility": 0.95}
        landmarks[12] = {"x": 0.6, "y": 0.4, "z": 0.0, "visibility": 0.95}
        landmarks[13] = {"x": 0.35, "y": 0.3, "z": 0.0, "visibility": 0.95}
        landmarks[14] = {"x": 0.65, "y": 0.3, "z": 0.0, "visibility": 0.95}
        landmarks[15] = {"x": 0.3, "y": 0.2, "z": 0.0, "visibility": 0.95}
        landmarks[16] = {"x": 0.7, "y": 0.2, "z": 0.0, "visibility": 0.95}
        landmarks[23] = {"x": 0.42, "y": 0.7, "z": 0.0, "visibility": 0.95}
        landmarks[24] = {"x": 0.58, "y": 0.7, "z": 0.0, "visibility": 0.95}
        return landmarks
