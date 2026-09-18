from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from app.core.config import settings

logger = logging.getLogger("neurotrack.database")

Base = declarative_base()

def get_engine():
    """Attempt PostgreSQL connection; fallback to SQLite for local execution if needed."""
    try:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            logger.info(f"Connected to PostgreSQL database: {settings.DATABASE_URL.split('@')[-1]}")
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Using SQLite fallback: {settings.SQLITE_FALLBACK_URL}")
        engine = create_engine(settings.SQLITE_FALLBACK_URL, connect_args={"check_same_thread": False})
        return engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
