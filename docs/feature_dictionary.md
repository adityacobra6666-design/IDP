# NeuroTrack AI — Extracted Behavioral Feature Dictionary

Every feature produced by the NeuroTrack AI computer vision pipeline conforms to a standardized schema containing:
`feature_name`, `value`, `unit`, `source`, `valid`, `confidence`.

---

## 1. Joint Attention Task Features

| Feature Name | Unit | Formula / Methodology | Source |
| :--- | :--- | :--- | :--- |
| `target_orientation_ratio` | ratio (0.0-1.0) | `frames_oriented_to_target / total_sampled_frames` based on head yaw orientation & facial landmarks | `video_cv` |
| `orientation_latency` | seconds | Time delta from recording start to first frame matching target head orientation threshold | `video_cv` |
| `fixation_duration` | seconds | Longest continuous duration of frames maintaining target focus | `video_cv` |
| `gaze_shift_count` | count | Total count of orientation zone transitions (Left <-> Center <-> Right) | `video_cv` |

---

## 2. Motor Imitation Task Features

| Feature Name | Unit | Formula / Methodology | Source |
| :--- | :--- | :--- | :--- |
| `pose_similarity` | score (0.0-1.0) | Mean upper-body landmark similarity score computed via `exp(-1.5 * Euclidean_dist)` on normalized keypoints | `video_cv` |
| `movement_consistency` | score (0.0-1.0) | Movement stability proxy calculated as `1.0 - std(similarity_scores)` | `video_cv` |
| `movement_completion_proxy` | ratio (0.0-1.0) | Ratio of sampled frames achieving pose similarity > 0.6 | `video_cv` |
| `response_latency` | seconds | Time delta to first peak similarity frame index | `video_cv` |
