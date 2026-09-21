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

def init_db_schema():
    """Ensure tables exist, apply column additions if missing, and backfill profile_number."""
    from sqlalchemy import inspect, text
    Base.metadata.create_all(bind=engine)
    try:
        inspector = inspect(engine)
        if "children" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("children")]
            if "profile_number" not in columns:
                logger.info("Adding missing profile_number column to children table...")
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE children ADD COLUMN profile_number INTEGER;"))
            
            # Backfill any null profile_number records
            with engine.begin() as conn:
                rows = conn.execute(text("SELECT id FROM children WHERE profile_number IS NULL ORDER BY created_at ASC;")).fetchall()
                if rows:
                    max_res = conn.execute(text("SELECT MAX(profile_number) FROM children WHERE profile_number IS NOT NULL;")).fetchone()
                    current_num = (max_res[0] if max_res and max_res[0] is not None else 0)
                    for row in rows:
                        current_num += 1
                        conn.execute(text("UPDATE children SET profile_number = :num WHERE id = :cid;"), {"num": current_num, "cid": row[0]})
                    logger.info(f"Backfilled {len(rows)} child records with sequential profile numbers.")
    except Exception as e:
        logger.warning(f"Schema migration check error: {e}")

