from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class VRContext(BaseModel):
    target_object_id: Optional[str] = None
    target_object_name: Optional[str] = None
    step_id: Optional[str] = None
    progress: Optional[float] = None
    scenario_state: Optional[Dict[str, Any]] = None


class AskRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    user_profile: str = "default"
    mode: str = "Decouverte"  # "Decouverte" | "Jeu"
    vr_context: VRContext = VRContext()


class Citation(BaseModel):
    source_file: Optional[str] = None
    equipment_name: Optional[str] = None
    validated_by: Optional[str] = None
    last_reviewed_date: Optional[str] = None
    chunk_id: Optional[str] = None


class AskResponse(BaseModel):
    assistant_text: str
    intent: str
    confidence: str
    citations: List[Citation] = []
