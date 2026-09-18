import cv2
import mediapipe as mp
from fastapi import APIRouter
from app.cv.face import FaceDetector
from app.cv.pose import PoseDetector
from app.core.logging import logger

router = APIRouter(prefix="/system", tags=["System & CV Status"])

@router.get("/cv-status")
def cv_status_check():
    """Diagnostic endpoint checking OpenCV and MediaPipe status and versioning."""
    face_ok = False
    pose_ok = False
    
    try:
        fd = FaceDetector()
        face_ok = True
        fd.close()
    except Exception as e:
        logger.error(f"FaceDetector check failed: {e}")

    try:
        pd = PoseDetector()
        pose_ok = True
        pd.close()
    except Exception as e:
        logger.error(f"PoseDetector check failed: {e}")

    mp_version = getattr(mp, '__version__', 'unknown')
    has_solutions = hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh')
    has_tasks = hasattr(mp, 'tasks') and hasattr(mp.tasks, 'vision')

    return {
        "status": "healthy" if (face_ok and pose_ok) else "degraded",
        "opencv": {
            "available": True,
            "version": cv2.__version__
        },
        "mediapipe": {
            "available": True,
            "version": mp_version,
            "solutions_api": has_solutions,
            "tasks_api": has_tasks,
            "face_processing": face_ok,
            "pose_processing": pose_ok
        }
    }
