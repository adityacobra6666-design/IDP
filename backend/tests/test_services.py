import numpy as np
from app.services.quality_service import QualityService
from app.services.joint_attention_service import JointAttentionService
from app.services.imitation_service import ImitationService
from app.cv.features import calculate_blur_score, compute_pose_similarity

def test_calculate_blur_score():
    # Synthetic sharp image with high variance gradient
    sharp_img = np.zeros((100, 100, 3), dtype=np.uint8)
    sharp_img[:, :50] = 255
    blur_score = calculate_blur_score(sharp_img)
    assert blur_score > 100.0

def test_quality_service_evaluation():
    meta = {
        "width": 1280,
        "height": 720,
        "fps": 30.0,
        "duration_seconds": 10.0
    }
    blur_scores = [120.0, 150.0, 130.0]
    qa = QualityService.evaluate_quality(
        meta=meta,
        sampled_blur_scores=blur_scores,
        face_detected_count=80,
        pose_detected_count=80,
        total_sampled_frames=100
    )
    assert qa["status"] == "VALID"
    assert qa["overall_score"] >= 70.0
    assert len(qa["reasons"]) == 0

def test_joint_attention_service():
    frame_evals = [
        {"oriented_to_target": True, "target_zone": "RIGHT"},
        {"oriented_to_target": True, "target_zone": "RIGHT"},
        {"oriented_to_target": False, "target_zone": "CENTER"},
        {"oriented_to_target": True, "target_zone": "RIGHT"}
    ]
    res = JointAttentionService.analyze_joint_attention(frame_evals, fps=30.0)
    assert res["target_orientation_ratio"] == 0.75
    assert res["gaze_shift_count"] == 2
    assert len(res["features_list"]) == 4

def test_imitation_service():
    ref_pose = ImitationService._generate_canonical_reference_pose()
    sim = compute_pose_similarity(ref_pose, ref_pose)
    assert abs(sim - 1.0) < 1e-3

    res = ImitationService.analyze_imitation([ref_pose, ref_pose], fps=30.0)
    assert res["pose_similarity"] > 0.95
    assert len(res["features_list"]) == 4
