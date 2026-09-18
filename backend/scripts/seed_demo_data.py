import sys
from pathlib import Path

# Add backend directory to sys.path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.models.database import engine, Base, SessionLocal
from app.models.entities import Child
from app.repositories.child_repository import ChildRepository
from app.repositories.task_repository import TaskRepository
from app.core.logging import logger

def seed_demo_data(db: Session) -> dict:
    """
    Idempotent database seeding script.
    Seeds default tasks and a synthetic demo child profile if none exist.
    """
    # 1. Seed Tasks
    task_repo = TaskRepository(db)
    task_repo.seed_default_tasks()

    # 2. Seed Demo Child
    child_repo = ChildRepository(db)
    demo_child = child_repo.get_by_external_id("DEMO-001")
    
    if not demo_child:
        logger.info("Seeding initial synthetic demo child profile: DEMO-001...")
        demo_child = Child(
            external_id="DEMO-001",
            age_months=36,
            gender="Male",
            notes="Synthetic demo child profile for IDP Review-II prototype monitoring."
        )
        db.add(demo_child)
        db.commit()
        db.refresh(demo_child)
        logger.info(f"Successfully seeded demo child: {demo_child.external_id} (ID: {demo_child.id})")
    else:
        logger.info(f"Demo child {demo_child.external_id} already exists in database.")

    return {"status": "success", "demo_child_id": demo_child.id}

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        res = seed_demo_data(session)
        print(f"Seed script completed: {res}")
