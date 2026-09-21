from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class DevelopmentalContext(BaseModel):
    school_setting: Optional[str] = Field(None, description="Current school or learning setting")
    primary_communication: Optional[str] = Field(None, description="Primary mode of communication: Verbal, Limited verbal, Non-verbal, Alternative/AAC, Other")
    home_languages: Optional[str] = Field(None, description="Languages commonly used at home")

class CommunicationContext(BaseModel):
    communicate_needs: Optional[str] = Field(None, description="Can child communicate basic needs: Always, Often, Sometimes, Rarely")
    communication_mode: Optional[str] = Field(None, description="Usual communication method: Speech, Gestures, Pointing, AAC/device, Other")

class SocialInteractionContext(BaseModel):
    initiate_interaction: Optional[str] = Field(None, description="Frequency of initiating interaction: Frequently, Sometimes, Rarely, Not sure")
    respond_name: Optional[str] = Field(None, description="Response when name called: Consistently, Often, Sometimes, Rarely, Not sure")

class AttentionEngagementContext(BaseModel):
    engagement_ability: Optional[str] = Field(None, description="Ability to stay engaged: Short, Moderate, Long, Variable")
    shift_attention: Optional[str] = Field(None, description="Shifts attention between people/objects: Frequently, Sometimes, Rarely, Not sure")

class ImitationPlayContext(BaseModel):
    imitate_actions: Optional[str] = Field(None, description="Imitates simple actions: Frequently, Sometimes, Rarely, Not sure")
    play_style: Optional[str] = Field(None, description="Preferred play style: Social, Solitary, Parallel, Mixed, Not sure")

class ParentQuestionnaireBase(BaseModel):
    developmental_context: Optional[DevelopmentalContext] = None
    communication: Optional[CommunicationContext] = None
    social_interaction: Optional[SocialInteractionContext] = None
    attention_engagement: Optional[AttentionEngagementContext] = None
    imitation_play: Optional[ImitationPlayContext] = None
    sensory_context: Optional[List[str]] = Field(default_factory=list, description="Uncomfortable situations: Loud sounds, Bright lights, Crowded environments, Certain textures, Unexpected changes, None known, Not sure")
    parent_observations: Optional[str] = Field(None, description="Free-text parent observations")
    session_context: Optional[str] = Field(None, description="Context for assessment: Typical day, Tired, Excited, Unwell, Unusual environment, Other")

class ParentQuestionnaireCreate(ParentQuestionnaireBase):
    pass

class ParentQuestionnaireUpdate(ParentQuestionnaireBase):
    pass

class ParentQuestionnaireResponse(ParentQuestionnaireBase):
    id: str
    child_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
