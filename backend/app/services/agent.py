import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import Interaction

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="gemma2-9b-it", temperature=0, api_key=GROQ_API_KEY)


@tool
def log_interaction(data: dict, db: Session) -> int:
    """Log a new interaction to the database"""
    interaction = Interaction(**data)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction.id


@tool
def edit_interaction(interaction_id: int, data: dict, db: Session) -> bool:
    """Edit an existing interaction in the database"""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return False
    for key, value in data.items():
        setattr(interaction, key, value)
    db.commit()
    return True


@tool
def get_interaction(interaction_id: int, db: Session) -> dict | None:
    """Get an interaction from the database by ID"""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return None
    return {
        "id": interaction.id,
        "hcp_name": interaction.hcp_name,
        "interaction_type": interaction.interaction_type,
        "date": interaction.date,
        "time": interaction.time,
        "attendees": interaction.attendees,
        "topics_discussed": interaction.topics_discussed,
        "summary": interaction.summary,
        "materials_shared": interaction.materials_shared,
        "samples_distributed": interaction.samples_distributed,
        "sentiment": interaction.sentiment,
        "outcomes": interaction.outcomes
    }


@tool
def delete_interaction(interaction_id: int, db: Session) -> bool:
    """Delete an interaction from the database"""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return False
    db.delete(interaction)
    db.commit()
    return True


@tool
def list_interactions(db: Session, limit: int = 50) -> list:
    """List recent interactions from the database"""
    interactions = db.query(Interaction).order_by(Interaction.id.desc()).limit(limit).all()
    return [
        {
            "id": i.id,
            "hcp_name": i.hcp_name,
            "interaction_type": i.interaction_type,
            "date": i.date,
            "time": i.time,
            "summary": i.summary
        } for i in interactions
    ]


def extract_data_from_text(text: str) -> dict:
    """Extract interaction data using LLM"""
    current_date = datetime.now()
    yesterday = current_date - timedelta(days=1)
    
    extraction_prompt = f"""
    Extract the following interaction data from the user's message. Return JSON only, no other text.
    If a field is not mentioned, use reasonable defaults.
    
    Fields:
    - hcp_name: Name of the Healthcare Professional (required)
    - interaction_type: One of: Meeting, Call, Email, Visit (default: Meeting)
    - date: Date in YYYY-MM-DD format (default: {current_date.strftime('%Y-%m-%d')})
    - time: Time in HH:MM AM/PM format (default: {current_date.strftime('%I:%M %p')})
    - attendees: Other people present (comma-separated, default: "")
    - topics_discussed: Topics covered (default: "")
    - summary: Brief summary of the interaction (default: user's message)
    - materials_shared: Materials shared (default: "")
    - samples_distributed: Samples distributed (default: "")
    - sentiment: One of: Positive, Neutral, Negative (default: Neutral)
    - outcomes: Outcomes or next steps (default: "")
    
    User message: {text}
    
    Today's date: {current_date.strftime('%Y-%m-%d')}
    Yesterday's date: {yesterday.strftime('%Y-%m-%d')}
    """
    
    response = llm.invoke(extraction_prompt)
    import json
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        extracted = json.loads(content)
        if not extracted.get("hcp_name"):
            extracted["hcp_name"] = "Unknown HCP"
        if not extracted.get("summary"):
            extracted["summary"] = text[:200] if len(text) > 200 else text
        return extracted
    except:
        return {
            "hcp_name": "Unknown HCP",
            "interaction_type": "Meeting",
            "date": current_date.strftime("%Y-%m-%d"),
            "time": current_date.strftime("%I:%M %p"),
            "attendees": "",
            "topics_discussed": "",
            "summary": text[:200] if len(text) > 200 else text,
            "materials_shared": "",
            "samples_distributed": "",
            "sentiment": "Neutral",
            "outcomes": ""
        }
