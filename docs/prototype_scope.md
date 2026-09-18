# NeuroTrack AI — Review-II Prototype Scope & Boundaries

## Implemented in Review-II Prototype (~20% Vertical Slice)

- [x] Full REST API backend built with FastAPI, SQLAlchemy, Pydantic, and OpenAPI.
- [x] PostgreSQL relational database tables (`Child`, `Session`, `Task`, `Recording`, `QualityAssessment`, `BehavioralFeatures`, `ModelOutput`).
- [x] Video recording upload, size/format validation, and intelligent frame sampling.
- [x] Input Quality Gate evaluating resolution, FPS, Laplacian variance blur score, face visibility ratio, and pose visibility ratio.
- [x] MediaPipe Face Mesh & OpenCV Haar Cascade face detection and head orientation estimation.
- [x] MediaPipe Pose keypoint extraction and skeleton overlay rendering.
- [x] Joint Attention feature engine (target orientation ratio, orientation latency, fixation duration, gaze shifts).
- [x] Motor Imitation feature engine (posture normalization, upper-body pose similarity, movement consistency).
- [x] Transparent evidence quality & confidence scoring (`HIGH`, `MEDIUM`, `LOW`, `REASSESSMENT_REQUIRED`).
- [x] Professional React + Vite research dashboard consuming backend REST endpoints live.
- [x] Containerization via Docker & Docker Compose.
- [x] Pytest automated test suite.

---

## Planned Future Work (Remaining Scope)

- Advanced multi-camera 3D gaze estimation.
- Longitudinal personal baseline estimation engine.
- Persistent change-point Bayesian detection across multi-month session histories.
- Audio vocalization and speech prosody analysis integration.
- Clinical validation studies with partner centers.
