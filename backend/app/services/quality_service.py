import numpy as np
from typing import Dict, Any, List
from app.core.config import settings
from app.cv.features import calculate_blur_score

class QualityService:
    @classmethod
    def evaluate_quality(
        cls,
        meta: Dict[str, Any],
        sampled_blur_scores: List[float],
        face_detected_count: int,
        pose_detected_count: int,
        total_sampled_frames: int
    ) -> Dict[str, Any]:
        """
        Evaluate video recording quality based on resolution, blur, and subject visibility.
        """
        reasons = []
        status = "VALID"

        # 1. Resolution Check
        res_ok = (meta["width"] >= settings.MIN_RESOLUTION_WIDTH) and (meta["height"] >= settings.MIN_RESOLUTION_HEIGHT)
        if not res_ok:
            reasons.append(f"Resolution ({meta['width']}x{meta['height']}) is below minimum threshold ({settings.MIN_RESOLUTION_WIDTH}x{settings.MIN_RESOLUTION_HEIGHT})")

        # 2. FPS Check
        fps_ok = meta["fps"] >= settings.MIN_FPS
        if not fps_ok:
            reasons.append(f"Frame rate ({meta['fps']} FPS) is below minimum threshold ({settings.MIN_FPS} FPS)")

        # 3. Duration Check
        duration_ok = meta["duration_seconds"] >= settings.MIN_DURATION_SEC
        if not duration_ok:
            reasons.append(f"Recording duration ({meta['duration_seconds']}s) is too short (min {settings.MIN_DURATION_SEC}s)")

        # 4. Blur Score (Mean Laplacian Variance)
        avg_blur = float(np.mean(sampled_blur_scores)) if sampled_blur_scores else 0.0
        blur_ok = avg_blur >= settings.MIN_BLUR_SCORE
        if not blur_ok:
            reasons.append(f"Video sharpness/blur score ({avg_blur:.1f}) is below threshold ({settings.MIN_BLUR_SCORE})")

        # 5. Face Visibility Ratio
        face_ratio = (face_detected_count / total_sampled_frames) if total_sampled_frames > 0 else 0.0
        face_ok = face_ratio >= settings.MIN_FACE_VISIBILITY
        if not face_ok:
            reasons.append(f"Face visibility ratio ({face_ratio*100:.1f}%) is below minimum threshold ({settings.MIN_FACE_VISIBILITY*100:.0f}%)")

        # 6. Pose Visibility Ratio
        pose_ratio = (pose_detected_count / total_sampled_frames) if total_sampled_frames > 0 else 0.0
        pose_ok = pose_ratio >= settings.MIN_POSE_VISIBILITY
        if not pose_ok:
            reasons.append(f"Body pose landmark visibility ratio ({pose_ratio*100:.1f}%) is below threshold ({settings.MIN_POSE_VISIBILITY*100:.0f}%)")

        # Determine overall decision
        if not (res_ok and fps_ok and duration_ok and blur_ok and (face_ok or pose_ok)):
            status = "REASSESSMENT_REQUIRED"

        # Calculate overall quality score (0.0 - 100.0)
        res_factor = 1.0 if res_ok else 0.5
        blur_factor = min(1.0, avg_blur / (settings.MIN_BLUR_SCORE * 1.5))
        vis_factor = (face_ratio + pose_ratio) / 2.0

        overall_score = round(100.0 * (0.3 * res_factor + 0.35 * blur_factor + 0.35 * vis_factor), 1)

        return {
            "overall_score": overall_score,
            "resolution_ok": res_ok,
            "blur_score": round(avg_blur, 2),
            "face_visibility_ratio": round(face_ratio, 3),
            "pose_visibility_ratio": round(pose_ratio, 3),
            "status": status,
            "reasons": reasons
        }
