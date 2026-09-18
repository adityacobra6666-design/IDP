# NeuroTrack AI

> **Full Title**: NeuroTrack AI: A Confidence-Aware Multimodal and Longitudinal System for Personalized Behavioral Monitoring and Intervention-Response Assessment in Children with Autism Spectrum Disorder  
> **Student**: Aditya Kumar (Reg No: 25BCE1368)  
> **Institution**: VIT Chennai  
> **Project Type**: B.Tech Innovative Design Project (IDP) — Review-II Prototype (~20% Completion Target)

---

## 📌 Important Positioning Statement

NeuroTrack AI is an **AI-assisted behavioral monitoring and assessment-support research prototype**.  
It objectively quantifies observable behavioral traits from standardized task recordings to support longitudinal tracking.

**NeuroTrack AI is NOT:**
- An autism diagnosis engine
- A medical diagnosis system
- A hospital management system
- A generic ASD yes/no classifier
- A replacement for trained clinicians

---

## 🚀 Key Features Implemented in Review-II Prototype

1. **Modular FastAPI Backend**: Clean architecture separating Routers, Services, Repositories, Schemas, CV Modules, and ORM Entities.
2. **PostgreSQL Relational Schema**: Normalized tables for `Child`, `Session`, `Task`, `Recording`, `QualityAssessment`, `BehavioralFeatures`, `ModelOutput`.
3. **Transparent Input Quality Gate**: Evaluates Laplacian variance blur score, resolution, FPS, face visibility ratio, and pose visibility ratio.
4. **MediaPipe + OpenCV Processing**: Face detection/mesh, head pose orientation estimation, body keypoint extraction, and annotated overlay frame generation.
5. **Hero Feature Prototypes**:
   - **Joint Attention**: Target orientation ratio, orientation latency, fixation duration, gaze shift count.
   - **Motor Imitation**: Posture normalization, upper-body pose similarity score, movement consistency.
6. **Confidence-Aware Layer**: Evaluates evidence quality (`HIGH`, `MEDIUM`, `LOW`, `REASSESSMENT_REQUIRED`).
7. **React + Vite Dashboard**: Modern, glassmorphic research UI consuming real backend REST APIs.
8. **Containerization & Testing**: Docker Compose setup and `pytest` automated test suite.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, Pydantic, SQLAlchemy, OpenCV, MediaPipe, NumPy, SciPy, Scikit-learn
- **Frontend**: React 18, Vite, Lucide Icons, Vanilla CSS
- **Database**: PostgreSQL 15 (with SQLite local test fallback)
- **Containerization**: Docker, Docker Compose, Nginx

---

## 💻 How to Run Locally

### Option 1: Quick Local Execution (Without Docker)

1. **Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

### Option 2: Docker Compose (Full Stack)

```bash
docker compose up --build
```
Access the application at `http://localhost:3000` and Swagger API docs at `http://localhost:8000/docs`.

---

## 🧪 Running Automated Tests

```bash
cd backend
PYTHONPATH=. venv/bin/pytest tests
```

---

## 📄 Documentation

- [Architecture Specification](docs/architecture.md)
- [REST API Reference](docs/api.md)
- [Extracted Feature Dictionary](docs/feature_dictionary.md)
- [Review-II Prototype Scope](docs/prototype_scope.md)
- [Review-II Demo Walkthrough](docs/review_ii_demo.md)
