import os
import cv2
from pathlib import Path
from typing import Dict, Any, Generator, Tuple
from app.core.config import settings
from app.core.exceptions import VideoProcessingException

class VideoService:
    ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

    @classmethod
    def validate_video_file(cls, file_path: Path) -> Dict[str, Any]:
        """Validate format, size, and readability of uploaded video file."""
        if not file_path.exists():
            raise VideoProcessingException(f"Video file not found at {file_path}")

        ext = file_path.suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise VideoProcessingException(f"Unsupported video extension '{ext}'. Supported formats: {cls.ALLOWED_EXTENSIONS}")

        file_size_bytes = file_path.stat().st_size
        if file_size_bytes == 0:
            raise VideoProcessingException("Uploaded video file is zero bytes (empty file)")

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size_bytes > max_bytes:
            raise VideoProcessingException(f"File size ({file_size_bytes / (1024*1024):.1f}MB) exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB")

        cap = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            raise VideoProcessingException("Could not open or decode video stream with OpenCV")

        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
            raise VideoProcessingException("Invalid video metadata (zero frames, FPS, or resolution)")

        duration_sec = frame_count / fps

        return {
            "file_size_bytes": file_size_bytes,
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration_seconds": round(duration_sec, 2)
        }

    @classmethod
    def extract_sampled_frames(cls, file_path: Path, max_samples: int = 150) -> Generator[Tuple[int, float, cv2.Mat], None, None]:
        """
        Intelligently sample video frames to optimize processing speed and memory footprint.
        Yields (frame_idx, timestamp_sec, frame_bgr).
        """
        cap = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        step = max(1, total_frames // max_samples)
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            if frame_idx % step == 0:
                timestamp = frame_idx / fps
                yield (frame_idx, round(timestamp, 2), frame)

            frame_idx += 1

        cap.release()
