import numpy as np
from typing import Dict, Any, List

class GazeTargetTracker:
    """
    Attention & Head-Orientation Proxy Tracker for Standardized Joint Attention Tasks.
    Estimates child focus direction relative to standardized visual/auditory stimulus targets.
    """
    def __init__(self):
        # Default target zone in normalized camera coordinates: Right target (x > 0.6), Left target (x < 0.4), Center (0.4-0.6)
        self.targets = {
            "TARGET_LEFT": {"x_min": 0.0, "x_max": 0.4, "yaw_threshold": -15.0},
            "TARGET_RIGHT": {"x_min": 0.6, "x_max": 1.0, "yaw_threshold": 15.0},
            "TARGET_CENTER": {"x_min": 0.4, "x_max": 0.6, "yaw_threshold": 0.0}
        }

    def evaluate_frame_attention(self, face_data: Dict[str, Any], active_target: str = "TARGET_RIGHT") -> Dict[str, Any]:
        """
        Evaluate frame-level attention proxy toward the active task stimulus target.
        """
        if not face_data.get("detected"):
            return {"oriented_to_target": False, "target_zone": "NONE", "confidence": 0.0}

        yaw = face_data.get("yaw", 0.0)
        landmarks = face_data.get("landmarks", [])

        # Nose tip horizontal position as secondary check
        nose_x = landmarks[1]["x"] if (landmarks and len(landmarks) > 1) else 0.5

        oriented = False
        target_info = self.targets.get(active_target, self.targets["TARGET_RIGHT"])

        if active_target == "TARGET_RIGHT":
            oriented = (yaw >= target_info["yaw_threshold"]) or (nose_x > 0.55)
        elif active_target == "TARGET_LEFT":
            oriented = (yaw <= target_info["yaw_threshold"]) or (nose_x < 0.45)
        else: # CENTER
            oriented = abs(yaw) < 15.0

        current_zone = "CENTER"
        if yaw > 12.0 or nose_x > 0.6:
            current_zone = "RIGHT"
        elif yaw < -12.0 or nose_x < 0.4:
            current_zone = "LEFT"

        return {
            "oriented_to_target": oriented,
            "target_zone": current_zone,
            "yaw_degrees": yaw,
            "confidence": 0.85 if face_data.get("detected") else 0.0
        }
