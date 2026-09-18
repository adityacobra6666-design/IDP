# NeuroTrack AI — REST API Documentation

Base URL: `http://localhost:8000/api`

## Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health and version check |
| `POST` | `/api/children` | Register a child profile record |
| `GET` | `/api/children` | List registered child profiles |
| `GET` | `/api/children/{id}` | Get single child profile by ID |
| `GET` | `/api/tasks` | List standardized task catalog |
| `GET` | `/api/tasks/{id}` | Get task details by ID |
| `POST` | `/api/sessions` | Create a behavioral session |
| `GET` | `/api/sessions` | List sessions |
| `GET` | `/api/sessions/{id}` | Get session details |
| `POST` | `/api/sessions/{id}/recording` | Upload video recording for a session |
| `POST` | `/api/sessions/{id}/analyze` | Trigger video analysis pipeline |
| `GET` | `/api/sessions/{id}/quality` | Get Quality Gate evaluation |
| `GET` | `/api/sessions/{id}/features` | Get extracted feature dictionary |
| `GET` | `/api/sessions/{id}/results` | Get complete structured report |

## Interactive Swagger OpenAPI Docs
FastAPI auto-generates interactive Swagger documentation at: `http://localhost:8000/docs`.
