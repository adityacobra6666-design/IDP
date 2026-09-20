from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import NeuroTrackException
from app.models.database import engine, Base, SessionLocal
from app.api.routes import health, children, tasks, sessions, results, system
from app.repositories.task_repository import TaskRepository

# Auto-create DB tables schema
Base.metadata.create_all(bind=engine)

# Seed standard task definitions catalog ONLY (Joint Attention & Imitation task types definition)
with SessionLocal() as db:
    task_repo = TaskRepository(db)
    task_repo.seed_default_tasks()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="NeuroTrack AI: Confidence-Aware Multimodal & Longitudinal Behavioral Monitoring Research Prototype API",
    openapi_url="/api/openapi.json",
    docs_url="/docs"
)

# Configure CORS for development origins
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mount for processed annotated frames and videos
app.mount("/processed", StaticFiles(directory=str(settings.PROCESSED_DIR)), name="processed")

# Global Exception Handlers
@app.exception_handler(NeuroTrackException)
async def neurotrack_exception_handler(request: Request, exc: NeuroTrackException):
    logger.error(f"Domain Exception on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "details": exc.details}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "FAILED",
            "error_code": "INTERNAL_SERVER_ERROR",
            "detail": f"Internal processing error: {str(exc)}"
        }
    )

# Include API Routers
app.include_router(health.router)
app.include_router(system.router, prefix=settings.API_V1_STR)
app.include_router(children.router, prefix=settings.API_V1_STR)
app.include_router(tasks.router, prefix=settings.API_V1_STR)
app.include_router(sessions.router, prefix=settings.API_V1_STR)
app.include_router(results.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
