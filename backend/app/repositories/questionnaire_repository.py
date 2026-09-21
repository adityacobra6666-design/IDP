from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.entities import ParentQuestionnaire
from app.schemas.questionnaire import ParentQuestionnaireCreate, ParentQuestionnaireUpdate

class QuestionnaireRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_child_id(self, child_id: str) -> Optional[ParentQuestionnaire]:
        return self.db.query(ParentQuestionnaire).filter(ParentQuestionnaire.child_id == child_id).first()

    def save_or_update(self, child_id: str, data: ParentQuestionnaireCreate) -> ParentQuestionnaire:
        existing = self.get_by_child_id(child_id)
        
        dev_dict = data.developmental_context.model_dump() if data.developmental_context else None
        comm_dict = data.communication.model_dump() if data.communication else None
        social_dict = data.social_interaction.model_dump() if data.social_interaction else None
        attn_dict = data.attention_engagement.model_dump() if data.attention_engagement else None
        imit_dict = data.imitation_play.model_dump() if data.imitation_play else None

        if existing:
            existing.developmental_context = dev_dict
            existing.communication = comm_dict
            existing.social_interaction = social_dict
            existing.attention_engagement = attn_dict
            existing.imitation_play = imit_dict
            existing.sensory_context = data.sensory_context
            existing.parent_observations = data.parent_observations
            existing.session_context = data.session_context
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            q_obj = ParentQuestionnaire(
                child_id=child_id,
                developmental_context=dev_dict,
                communication=comm_dict,
                social_interaction=social_dict,
                attention_engagement=attn_dict,
                imitation_play=imit_dict,
                sensory_context=data.sensory_context,
                parent_observations=data.parent_observations,
                session_context=data.session_context
            )
            self.db.add(q_obj)
            self.db.commit()
            self.db.refresh(q_obj)
            return q_obj
