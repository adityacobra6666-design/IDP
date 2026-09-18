import cv2
import numpy as np
from typing import List, Dict, Tuple, Any

def calculate_blur_score(frame: np.ndarray) -> float:
    """Calculate image sharpness/blur score using Variance of Laplacian."""
    if frame is None or frame.size == 0:
        return 0.0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(variance)

def normalize_pose_landmarks(landmarks: List[Dict[str, float]]) -> np.ndarray:
    """
    Normalize 2D/3D pose landmarks for position/scale invariance.
    Translates origin to mid-hip point and scales by torso distance (mid-hip to mid-shoulder).
    """
    if not landmarks or len(landmarks) < 24:
        return np.array([])
    
    coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
    
    # MediaPipe pose landmark indices:
    # 11: left shoulder, 12: right shoulder
    # 23: left hip, 24: right hip
    left_hip = coords[23]
    right_hip = coords[24]
    left_shoulder = coords[11]
    right_shoulder = coords[12]
    
    mid_hip = (left_hip + right_hip) / 2.0
    mid_shoulder = (left_shoulder + right_shoulder) / 2.0
    
    # Translate to mid-hip origin
    normalized_coords = coords - mid_hip
    
    # Scale factor based on torso length
    torso_length = np.linalg.norm(mid_shoulder - mid_hip)
    if torso_length > 1e-4:
        normalized_coords = normalized_coords / torso_length
        
    return normalized_coords

def compute_pose_similarity(landmarks_a: List[Dict[str, float]], landmarks_b: List[Dict[str, float]]) -> float:
    """
    Compute cosine/Euclidean similarity between two pose landmark sets.
    Returns a normalized similarity score between 0.0 and 1.0 (1.0 = identical pose).
    """
    norm_a = normalize_pose_landmarks(landmarks_a)
    norm_b = normalize_pose_landmarks(landmarks_b)
    
    if norm_a.size == 0 or norm_b.size == 0:
        return 0.0
    
    # Compute mean Euclidean distance across upper body keypoints (indices 11-24)
    upper_body_indices = list(range(11, 25))
    diffs = norm_a[upper_body_indices] - norm_b[upper_body_indices]
    dist = np.mean(np.linalg.norm(diffs, axis=1))
    
    # Convert distance to similarity score in [0.0, 1.0] using exponential decay
    similarity = np.exp(-1.5 * dist)
    return float(np.clip(similarity, 0.0, 1.0))
