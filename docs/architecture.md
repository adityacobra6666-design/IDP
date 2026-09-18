# NeuroTrack AI — Architecture Specification

## Overview

NeuroTrack AI is structured as a confidence-aware, backend-first, modular micro-architecture for personalized behavioral monitoring and intervention-response assessment in children with Autism Spectrum Disorder (ASD).

```
 ┌─────────────────────────────────────────────────────────┐
 │                   React + Vite Dashboard                │
 └────────────────────────────┬────────────────────────────┘
                              │ REST APIs (JSON / Form)
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │                 FastAPI Backend Service                 │
 │  ┌───────────────────────────────────────────────────┐  │
 │  │ API Routers (Health, Children, Sessions, Results) │  │
 │  └─────────────────────────┬─────────────────────────┘  │
 │                            ▼                            │
 │  ┌───────────────────────────────────────────────────┐  │
 │  │ Service Layer (Video, Quality, JointAttn, Immit.) │  │
 │  └──────┬──────────────────┬──────────────────┬──────┘  │
 │         │                  │                  │         │
 │         ▼                  ▼                  ▼         │
 │   ┌───────────┐      ┌───────────┐      ┌───────────┐   │
 │   │ OpenCV +  │      │ SQLALchemy│      │ File Storage│  │
 │   │ MediaPipe │      │ ORM Repos │      │ Uploads/  │   │
 │   │ CV Engine │      │ (Postgres)│      │ Processed │   │
 │   └───────────┘      └───────────┘      └───────────┘   │
 └─────────────────────────────────────────────────────────┘
```

## Layer Definitions

1. **API Router Layer (`app/api/routes/`)**:
   Enforces RESTful contract with Pydantic request/response schemas. Returns structured HTTP responses without exposing raw internal stack traces.

2. **Domain Service Layer (`app/services/`)**:
   Coordinates business logic, file decoding, frame sampling, Quality Gate execution, task feature extraction engines, and confidence level evaluation.

3. **Computer Vision Processing Layer (`app/cv/`)**:
   - `face.py`: MediaPipe Face Mesh + OpenCV Haar Cascade fallback for face visibility ratio and head orientation estimation (yaw/pitch).
   - `pose.py`: MediaPipe Pose for 33 body joint landmark detection and skeleton overlay rendering.
   - `gaze.py`: Attention-to-target proxy relative to task stimulus regions.
   - `features.py`: Laplacian variance image sharpness calculation, posture normalization, and Euclidean/Cosine similarity.

4. **Repository Layer (`app/repositories/`)**:
   Encapsulates all database CRUD logic using SQLAlchemy ORM. Supports PostgreSQL in production and Docker, with graceful SQLite fallback for local test suites.

5. **Database Storage (`app/models/entities.py`)**:
   Relational model hierarchy: `Child` -> `Session` -> `Task` -> `Recording` -> `QualityAssessment` -> `BehavioralFeatures` -> `ModelOutput`.
