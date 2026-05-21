from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .config import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hcp_name = Column(String(255), nullable=False)
    interaction_type = Column(String(50), default="Meeting")
    date = Column(String(50), nullable=False)
    time = Column(String(50), nullable=False)
    attendees = Column(Text, default="")
    topics_discussed = Column(Text, default="")
    summary = Column(Text, default="")
    materials_shared = Column(Text, default="")
    samples_distributed = Column(Text, default="")
    sentiment = Column(String(50), default="Neutral")
    outcomes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
