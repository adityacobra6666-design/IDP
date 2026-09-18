import numpy as np
from typing import List, Dict, Any

class JointAttentionService:
    @classmethod
    def analyze_joint_attention(
        cls,
        frame_evaluations: List[Dict[str, Any]],
        fps: float
    ) -> Dict[str, Any]:
        """
        Analyze Joint Attention task metrics from sequential frame evaluations.
        """
        if not frame_evaluations:
            return {
                "target_orientation_ratio": 0.0,
                "orientation_latency_sec": 0.0,
                "fixation_duration_sec": 0.0,
                "gaze_shift_count": 0,
                "features_list": []
            }

        total_frames = len(frame_evaluations)
        frame_time_step = 1.0 / max(1.0, fps)

        oriented_count = 0
        first_orientation_idx = None
        max_fixation_frames = 0
        current_fixation_frames = 0
        gaze_shifts = 0
        previous_zone = None

        for idx, ev in enumerate(frame_evaluations):
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

            # Count gaze shifts
            if previous_zone and previous_zone != current_zone and current_zone != "NONE":
                gaze_shifts += 1

            previous_zone = current_zone

        orientation_ratio = round(oriented_count / total_frames, 3)
        
        # Latency calculation
        orientation_latency = round(first_orientation_idx * frame_time_step, 2) if first_orientation_idx is not None else round(total_frames * frame_time_step, 2)
        
        # Fixation duration
        max_fixation_sec = round(max_fixation_frames * frame_time_step, 2)

        # Standardized Behavioral Features List
        features = [
            {
                "feature_name": "target_orientation_ratio",
                "value": orientation_ratio,
                "unit": "ratio",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.9
            },
            {
                "feature_name": "orientation_latency",
                "value": orientation_latency,
                "unit": "seconds",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.85
            },
            {
                "feature_name": "fixation_duration",
                "value": max_fixation_sec,
                "unit": "seconds",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.9
            },
            {
                "feature_name": "gaze_shift_count",
                "value": float(gaze_shifts),
                "unit": "count",
                "source": "video_cv",
                "valid": True,
                "confidence": 0.85
            }
        ]

        return {
            "target_orientation_ratio": orientation_ratio,
            "orientation_latency_sec": orientation_latency,
            "fixation_duration_sec": max_fixation_sec,
            "gaze_shift_count": gaze_shifts,
            "features_list": features
        }
