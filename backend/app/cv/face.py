import os
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from typing import Dict, Any, List

CV_DATA_DIR = Path(__file__).resolve().parent / "data"

class FaceDetector:
    def __init__(self):
        self.use_solutions = hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh')
        
        if self.use_solutions:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.face_cascade = None
            self.eye_cascade = None
        else:
            self.face_mesh = None
            # Locate Haar Cascade XML files
            cascade_face_path = CV_DATA_DIR / "haarcascade_frontalface_default.xml"
            cascade_eye_path = CV_DATA_DIR / "haarcascade_eye.xml"
            
            if not cascade_face_path.exists():
                cascade_face_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
            if not cascade_eye_path.exists():
                cascade_eye_path = Path(cv2.data.haarcascades) / "haarcascade_eye.xml"

            self.face_cascade = cv2.CascadeClassifier(str(cascade_face_path))
            self.eye_cascade = cv2.CascadeClassifier(str(cascade_eye_path))

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a single BGR frame for face presence and head pose orientation proxy.
        """
        if frame is None or frame.size == 0:
            return {"detected": False, "landmarks": [], "yaw": 0.0, "pitch": 0.0, "roll": 0.0}

        h, w, c = frame.shape

        if self.use_solutions and self.face_mesh:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                landmarks_list = []
                for lm in face_landmarks.landmark:
                    landmarks_list.append({"x": lm.x, "y": lm.y, "z": lm.z})

                # Calculate head pose proxy (yaw, pitch)
                nose_tip = np.array([face_landmarks.landmark[1].x * w, face_landmarks.landmark[1].y * h, face_landmarks.landmark[1].z * w])
                chin = np.array([face_landmarks.landmark[152].x * w, face_landmarks.landmark[152].y * h, face_landmarks.landmark[152].z * w])
                left_eye = np.array([face_landmarks.landmark[33].x * w, face_landmarks.landmark[33].y * h, face_landmarks.landmark[33].z * w])
                right_eye = np.array([face_landmarks.landmark[263].x * w, face_landmarks.landmark[263].y * h, face_landmarks.landmark[263].z * w])

                eye_center = (left_eye + right_eye) / 2.0
                eye_vector = right_eye - left_eye
                yaw = float(np.arctan2(nose_tip[0] - eye_center[0], eye_vector[0] + 1e-5) * 180.0 / np.pi)
                pitch = float(np.arctan2(nose_tip[1] - chin[1], nose_tip[2] - chin[2] + 1e-5) * 180.0 / np.pi)

                return {
                    "detected": True,
                    "landmarks": landmarks_list,
                    "yaw": round(yaw, 2),
                    "pitch": round(pitch, 2),
                    "roll": 0.0
                }

        # OpenCV Haar Cascade Processing Fallback
        if self.face_cascade and not self.face_cascade.empty():
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))

            if len(faces) > 0:
                # Pick largest detected face
                fx, fy, fw, fh = max(faces, key=lambda b: b[2] * b[3])
                
                # Generate standard 468 facial landmark topology points
                landmarks_list = []
                for i in range(468):
                    landmarks_list.append({"x": float((fx + fw/2)/w), "y": float((fy + fh/2)/h), "z": 0.0})

                # Key landmark indices (matching MediaPipe Face Mesh index topology):
                # Index 1: Nose tip
                landmarks_list[1] = {"x": float((fx + fw/2)/w), "y": float((fy + fh*0.55)/h), "z": 0.0}
                # Index 33: Left eye
                landmarks_list[33] = {"x": float((fx + fw*0.3)/w), "y": float((fy + fh*0.35)/h), "z": 0.0}
                # Index 263: Right eye
                landmarks_list[263] = {"x": float((fx + fw*0.7)/w), "y": float((fy + fh*0.35)/h), "z": 0.0}
                # Index 152: Chin
                landmarks_list[152] = {"x": float((fx + fw/2)/w), "y": float((fy + fh*0.95)/h), "z": 0.0}

                # Estimate yaw based on eye symmetry within face ROI if eye cascade is loaded
                yaw = 0.0
                if self.eye_cascade and not self.eye_cascade.empty():
                    roi_gray = gray[fy:fy+fh, fx:fx+fw]
                    eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    if len(eyes) >= 2:
                        sorted_eyes = sorted(eyes, key=lambda e: e[0])
                        e1_cx = sorted_eyes[0][0] + sorted_eyes[0][2]/2
                        e2_cx = sorted_eyes[1][0] + sorted_eyes[1][2]/2
                        eye_mid = (e1_cx + e2_cx) / 2
                        yaw = float((eye_mid - (fw / 2)) / (fw / 2) * 30.0)

                return {
                    "detected": True,
                    "landmarks": landmarks_list,
                    "yaw": round(yaw, 2),
                    "pitch": 0.0,
                    "roll": 0.0
                }

        return {"detected": False, "landmarks": [], "yaw": 0.0, "pitch": 0.0, "roll": 0.0}

    def draw_landmarks(self, frame: np.ndarray, face_data: Dict[str, Any]) -> np.ndarray:
        """Draw facial features and orientation vector on frame."""
        if not face_data.get("detected"):
            return frame

        annotated = frame.copy()
        landmarks = face_data.get("landmarks", [])
        h, w, _ = frame.shape

        if landmarks and len(landmarks) > 263:
            for idx in [1, 33, 263, 152]:
                pt = landmarks[idx]
                cx, cy = int(pt["x"] * w), int(pt["y"] * h)
                cv2.circle(annotated, (cx, cy), 4, (0, 255, 0), -1)

            # Draw nose tip orientation vector
            nose = landmarks[1]
            nx, ny = int(nose["x"] * w), int(nose["y"] * h)
            yaw = face_data.get("yaw", 0.0)
            dx = int(yaw * 1.5)
            cv2.arrowedLine(annotated, (nx, ny), (nx + dx, ny - 15), (255, 242, 0), 2)

        return annotated

    def close(self):
        if self.use_solutions and self.face_mesh:
            try:
                self.face_mesh.close()
            except Exception:
                pass
