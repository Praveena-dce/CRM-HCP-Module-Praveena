from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class InteractionBase(BaseModel):
    hcp_name: str
    interaction_type: Optional[str] = "Meeting"
    date: str
    time: str
    attendees: Optional[str] = ""
    topics_discussed: Optional[str] = ""
    summary: Optional[str] = ""
    materials_shared: Optional[str] = ""
    samples_distributed: Optional[str] = ""
    sentiment: Optional[str] = "Neutral"
    outcomes: Optional[str] = ""


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(InteractionBase):
    pass


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict]] = []


class ChatResponse(BaseModel):
    response: str
    extracted_data: Dict[str, Any]
    interaction_id: Optional[int]
