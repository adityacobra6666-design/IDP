from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import Task
from app.schemas.task import TaskCreate

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_code(self, code: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.code == code).first()

    def get_all(self) -> List[Task]:
        return self.db.query(Task).all()

    def seed_default_tasks(self):
        """Seed standardized task definitions if not already present."""
        defaults = [
            {
                "code": "joint_attention",
                "name": "Standardized Joint Attention Task",
                "description": "Assesses attention-following and gaze proxy toward standardized visual/auditory stimulus targets.",
                "category": "joint_attention"
            },
            {
                "code": "imitation",
                "name": "Standardized Motor Imitation Task",
                "description": "Assesses physical posture and movement imitation similarity relative to a reference examiner posture sequence.",
                "category": "imitation"
            }
        ]
        for task_data in defaults:
            existing = self.get_by_code(task_data["code"])
            if not existing:
                task = Task(
                    code=task_data["code"],
                    name=task_data["name"],
                    description=task_data["description"],
                    category=task_data["category"]
                )
                self.db.add(task)
        self.db.commit()
