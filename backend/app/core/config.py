import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "NeuroTrack AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    
    # Storage settings
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    PROCESSED_DIR: Path = BASE_DIR / "processed"
    MAX_UPLOAD_SIZE_MB: int = 100
    
    # Database Settings
    # Default to PostgreSQL, with SQLite fallback if postgres driver/url fails during local testing
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://neurotrack:neurotrack123@localhost:5432/neurotrack")
    SQLITE_FALLBACK_URL: str = f"sqlite:///{BASE_DIR}/neurotrack.db"
    
    # Quality Gate Thresholds
    MIN_RESOLUTION_WIDTH: int = 480
    MIN_RESOLUTION_HEIGHT: int = 360
    MIN_FPS: float = 10.0
    MIN_DURATION_SEC: float = 1.0
    MIN_BLUR_SCORE: float = 40.0  # Laplacian variance threshold
    MIN_FACE_VISIBILITY: float = 0.25  # Minimum ratio of frames with face detected
    MIN_POSE_VISIBILITY: float = 0.25  # Minimum ratio of frames with pose landmarks
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
