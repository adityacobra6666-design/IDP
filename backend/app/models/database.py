from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from app.core.config import settings

logger = logging.getLogger("neurotrack.database")

Base = declarative_base()

def get_engine():
    """Create the configured database engine with a bounded PostgreSQL fallback."""
    if settings.DATABASE_URL.startswith("sqlite"):
        logger.info(f"Using SQLite database: {settings.DATABASE_URL}")
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3},
        )
        # Test connection
        with engine.connect() as conn:
            logger.info(f"Connected to database: {settings.DATABASE_URL.split('@')[-1]}")
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
