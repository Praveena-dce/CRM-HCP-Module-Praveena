from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import json
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crm.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InteractionDB(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hcp_name = Column(String(255), nullable=False)
    interaction_type = Column(String(50), default="Meeting")
    date = Column(String(50), nullable=False)
    time = Column(String(50), nullable=False)
    attendees = Column(String(500), default="")
    topics_discussed = Column(String(1000), default="")
    materials_shared = Column(String(500), default="")
    samples_distributed = Column(String(500), default="")
    sentiment = Column(String(50), default="Neutral")
    outcomes = Column(String(1000), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-First CRM HCP Module")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="gemma2-9b-it", temperature=0, api_key=GROQ_API_KEY)

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict]] = []
    interaction_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    extracted_data: Dict[str, Any]
    interaction_id: Optional[int]
    interaction: Optional[Dict[str, Any]] = None

class InteractionBase(BaseModel):
    hcp_name: str
    interaction_type: Optional[str] = 'Meeting'
    date: str
    time: str
    attendees: Optional[str] = ''
    topics_discussed: Optional[str] = ''
    materials_shared: Optional[str] = ''
    samples_distributed: Optional[str] = ''
    sentiment: Optional[str] = 'Neutral'
    outcomes: Optional[str] = ''

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^[:]\s*', '', text)
    return text

def extract_hcp_name(text: str) -> str | None:
    text_lower = text.lower()
    edit_keywords = ['attendees', 'materials', 'samples', 'sentiment', 'outcomes', 'topics', 'date', 'time', 'interaction']
    if any(keyword in text_lower for keyword in edit_keywords) and ('met' not in text_lower and 'dr.' not in text_lower and 'doctor' not in text_lower):
        return None
    
    forbidden = [
        'today', 'yesterday', 'met', 'the', 'and', 'with', 'discussed', 'shared', 'i', 'we', 'product', 'time', 
        'date', 'attendees', 'materials', 'samples', 'outcomes', 'sentiment', 'interaction', 'hcp', 'name', 'is', 
        'dr', 'doctor', 'at', 'in', 'on', 'for', 'to', 'from', 'it', 'was', 'were', 'are', 'is', 'schedule', 
        'follow', 'up', 'not', 'a', 'an', 'visit', 'call', 'email', 'meeting', 'positive', 'negative', 'neutral', 
        'that', 'this', 'these', 'those', 'but', 'or', 'nor', 'so', 'yet', 'for', 'and', 'nor', 'but', 'or', 
        'yet', 'so', 'ug', 'am', 'pm', 'its', 'it\'s', 'change', 'update', 'edit', 'instead', 'swap', 'replace',
        'drug', 'drugs', 'unit', 'units', 'brochure', 'brochures', 'sheet', 'sheets', 'safety', 'data',
        'distributed'
    ]
    
    patterns = [
        r'(?:dr\.?|doctor)\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)',
        r'met\s+(?:with\s+)?([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = clean_text(match.group(1))
            name = re.sub(r'\s+(?:at|in|on|for|to|from|with|and|the|a|an|it|was|were|are|is)$', '', name, flags=re.IGNORECASE)
            if name.lower() not in forbidden and len(name) > 2:
                return name
    
    words = text.split()
    for word in words:
        word = clean_text(word)
        if word and len(word) > 2 and word[0].isupper() and word.isalpha():
            if word.lower() not in forbidden:
                return word
    
    return None

def extract_time(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'it\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)'
    edit_match = re.search(edit_pattern, text, re.IGNORECASE)
    if edit_match:
        time_str = clean_text(edit_match.group(1))
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            return time_obj.strftime("%H:%M")
        except:
            try:
                time_obj = datetime.strptime(time_str, "%I:%M%p")
                return time_obj.strftime("%H:%M")
            except:
                pass
    
    at_pattern = r'at\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)'
    at_match = re.search(at_pattern, text, re.IGNORECASE)
    if at_match:
        time_str = clean_text(at_match.group(1))
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            return time_obj.strftime("%H:%M")
        except:
            try:
                time_obj = datetime.strptime(time_str, "%I:%M%p")
                return time_obj.strftime("%H:%M")
            except:
                pass
    
    any_pattern = r'(\d{1,2}:\d{2}\s*(?:am|pm)?)'
    any_match = re.search(any_pattern, text, re.IGNORECASE)
    if any_match:
        time_str = clean_text(any_match.group(1))
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            return time_obj.strftime("%H:%M")
        except:
            try:
                time_obj = datetime.strptime(time_str, "%I:%M%p")
                return time_obj.strftime("%H:%M")
            except:
                pass
    return None

def extract_interaction_type(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'it\s+(?:was|is)\s+(meeting|call|email|visit)'
    edit_match = re.search(edit_pattern, text_lower)
    if edit_match:
        type_str = clean_text(edit_match.group(1))
        if type_str:
            return type_str.capitalize()
    
    if 'call' in text_lower:
        return 'Call'
    elif 'email' in text_lower:
        return 'Email'
    elif 'visit' in text_lower:
        return 'Visit'
    elif 'meeting' in text_lower:
        return 'Meeting'
    return None

def extract_attendees(text: str) -> str | None:
    text_lower = text.lower()
    
    has_attendees = 'attendees' in text_lower
    has_standalone_its = bool(re.search(r'\bits\b', text_lower))
    
    if has_attendees and has_standalone_its:
        matches = list(re.finditer(r'\bits\b', text, re.IGNORECASE))
        if matches:
            last_match = matches[-1]
            attendees = clean_text(text[last_match.end():])
            if attendees:
                attendees = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|we|it|materials|samples|sentiment|outcomes|topics|discussed)$', '', attendees, flags=re.IGNORECASE)
                if attendees:
                    return attendees
    
    patterns = [
        r'attendees?\s*(?:name\s+|were\s+|was\s+|are\s+|is\s+)?(.*?)(?:\.\s+|\s+(?:materials|samples|sentiment|outcomes|topics|discussed|we))',
        r'attendees?\s*(?:name\s+|were\s+|was\s+|are\s+|is\s+)?(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            attendees = clean_text(match.group(1))
            if attendees:
                attendees = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|we|it|materials|samples|sentiment|outcomes|topics|discussed)$', '', attendees, flags=re.IGNORECASE)
                if attendees:
                    return attendees
    return None

def extract_topics(text: str, existing_value: str = None) -> str | None:
    patterns = [
        r'(?:change|update|edit)\s+(?:the\s+)?topics?\s+(?:discussed\s+)?(?:to|:)?\s*(.+)',
        r'(?:topics?\s+discussed\s*:?\s*)(.+)',
        r'(?:we\s+)?discussed\s+(.+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            topics = clean_text(match.group(1))

            # stop next field labels
            topics = re.split(
                r'\b(?:materials\s+shared|samples\s+distributed|sentiment|outcomes|attendees)\b',
                topics,
                flags=re.IGNORECASE
            )[0].strip()

            # FIX 1
            # only new treatment guidelines
            # -> treatment guidelines

            only_match = re.search(
                r'only\s+new\s+(.*)',
                topics,
                re.IGNORECASE
            )

            if only_match:
                topics = clean_text(only_match.group(1))

            # FIX 2
            # discussed PPT
            # -> PPT

            discussed_match = re.search(
                r'discussed\s+(.*)',
                topics,
                re.IGNORECASE
            )

            if discussed_match:
                topics = clean_text(discussed_match.group(1))

            return topics

    return None

def extract_materials(text: str, existing_value: str = None) -> str | None:
    patterns = [
        r'(?:change|update|edit)\s+(?:the\s+)?materials?\s+(?:shared\s+)?(?:to|:)?\s*(.+)',
        r'(?:materials?\s+shared\s*:?\s*)(.+)',
        r'(?:shared\s+)(.+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            materials = clean_text(match.group(1))

            # stop at next field names
            materials = re.split(
                r'\b(?:samples\s+distributed|sentiment|outcomes|topics\s+discussed|attendees)\b',
                materials,
                flags=re.IGNORECASE
            )[0].strip()

            # CUSTOM FIX
            # "only Product brochure not safety data sheet"
            # -> keep only "Product brochure"

            not_match = re.search(
                r'only\s+(.*?)\s+not\s+',
                materials,
                re.IGNORECASE
            )

            if not_match:
                materials = clean_text(not_match.group(1))

            return materials

    return None


def extract_outcomes(text: str, existing_value: str = None) -> str | None:
    text_lower = text.lower()
    
    # Handle edit commands - specifically for the "not 2 weeks its Schedule follow-up in 3 weeks" pattern
    edit_patterns = [
        r'(?:change|update|edit)\s+(?:the\s+)?outcomes?\s+(?:to|:)?\s*(.*?)(?:\.\s+|\s+(?:and|topics|materials|samples|sentiment|attendees|$))',
        r'(?:outcomes?\s+(?:should be|is|are|:)?\s+)(.*?)(?:\.\s+|\s+(?:topics|materials|samples|sentiment|attendees|$))',
        r'(?:new\s+)?outcomes?\s*:?\s*(.*?)(?:\.\s+|\s+(?:topics|materials|samples|sentiment|attendees|$))',
        # Special pattern for the exact format in your image
        r'(?:outcomes?\s+-\s+)(.*?)(?:\s+(?:topics|materials|samples|sentiment|attendees|$))'
    ]
    
    for pattern in edit_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            outcomes = clean_text(match.group(1))
            if outcomes and len(outcomes) > 0 and outcomes.lower() not in ['it', 'its', 'the', 'this', 'that']:
                outcomes = re.sub(r'\s+(?:and|topics|materials|samples|sentiment|attendees)$', '', outcomes, flags=re.IGNORECASE)
                return outcomes
    
    # Look for "Outcomes:" pattern
    outcomes_pattern = r'(?:outcomes?\s*:?\s*)(.*?)(?:\.\s+|\s+(?:topics|materials|samples|sentiment|attendees|$))'
    match = re.search(outcomes_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        outcomes = clean_text(match.group(1))
        if outcomes and len(outcomes) > 0:
            outcomes = re.sub(r'\s+(?:and|topics|materials|samples|sentiment|attendees)$', '', outcomes, flags=re.IGNORECASE)
            return outcomes
    
    return None

def extract_samples(text: str) -> str | None:
    text_lower = text.lower()
    
    # Look for "Samples Distributed:" pattern
    samples_pattern = r'(?:samples?\s+distributed\s*:?\s*)(.*?)(?:\.\s+|\s+(?:materials|sentiment|outcomes|topics|attendees|$))'
    match = re.search(samples_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        samples = clean_text(match.group(1))
        if samples and len(samples) > 0:
            return samples
    
    # Keep existing patterns
    is_edit_message = 'not' in text_lower or 'change to' in text_lower or 'instead' in text_lower
    
    has_samples_key = 'samples' in text_lower or 'sample' in text_lower
    has_drug_unit = any(keyword in text_lower for keyword in ['unit', 'units', 'drug', 'vial', 'vials'])
    
    if is_edit_message and (has_samples_key or has_drug_unit):
        change_patterns = [
            r'change to\s+(\d+\s+units?.*)',
            r'change to\s+(.*?drug.*)',
            r'change to\s+(.*)'
        ]
        for pattern in change_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                samples = clean_text(match.group(1))
                if samples and any(keyword in samples.lower() for keyword in ['unit', 'units', 'drug', 'sample', 'samples', 'vial', 'vials']):
                    samples = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|sentiment|outcomes|topics|attendees|materials|distributed)$', '', samples, flags=re.IGNORECASE)
                    if samples:
                        return samples
        
        its_patterns = [
            r'its\s+(\d+\s+units?.*)',
            r'its\s+(.*?drug.*)',
            r'its\s+(.*)'
        ]
        for pattern in its_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                samples = clean_text(match.group(1))
                if samples and any(keyword in samples.lower() for keyword in ['unit', 'units', 'drug', 'sample', 'samples', 'vial', 'vials']):
                    samples = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|sentiment|outcomes|topics|attendees|materials|distributed)$', '', samples, flags=re.IGNORECASE)
                    if samples:
                        return samples
    
    patterns = [
        r'samples?\s*distributed\s*:\s*(.*?)(?:\.\s+|\s+(?:sentiment|outcomes|topics|attendees|materials))',
        r'samples?\s*distributed\s*(?:is|are|were|was)?\s*(.*?)(?:\.\s+|\s+(?:sentiment|outcomes|topics|attendees|materials))',
        r'samples?\s*distributed\s*(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            samples = clean_text(match.group(1))
            if samples and any(keyword in samples.lower() for keyword in ['unit', 'units', 'drug', 'sample', 'samples', 'vial', 'vials']):
                samples = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|sentiment|outcomes|topics|attendees|materials|distributed)$', '', samples, flags=re.IGNORECASE)
                if samples:
                    return samples
    return None

def extract_attendees(text: str) -> str | None:
    text_lower = text.lower()
    
    # Look for "Attendees:" pattern
    attendees_pattern = r'(?:attendees?\s*:?\s*)(.*?)(?:\.\s+|\s+(?:materials|samples|sentiment|outcomes|topics|$))'
    match = re.search(attendees_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        attendees = clean_text(match.group(1))
        if attendees and len(attendees) > 0:
            return attendees
    
    # Keep existing patterns
    has_attendees = 'attendees' in text_lower
    has_standalone_its = bool(re.search(r'\bits\b', text_lower))
    
    if has_attendees and has_standalone_its:
        matches = list(re.finditer(r'\bits\b', text, re.IGNORECASE))
        if matches:
            last_match = matches[-1]
            attendees = clean_text(text[last_match.end():])
            if attendees:
                attendees = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|we|it|materials|samples|sentiment|outcomes|topics|discussed)$', '', attendees, flags=re.IGNORECASE)
                if attendees:
                    return attendees
    
    patterns = [
        r'attendees?\s*(?:name\s+|were\s+|was\s+|are\s+|is\s+)?(.*?)(?:\.\s+|\s+(?:materials|samples|sentiment|outcomes|topics|discussed|we))',
        r'attendees?\s*(?:name\s+|were\s+|was\s+|are\s+|is\s+)?(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            attendees = clean_text(match.group(1))
            if attendees:
                attendees = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|we|it|materials|samples|sentiment|outcomes|topics|discussed)$', '', attendees, flags=re.IGNORECASE)
                if attendees:
                    return attendees
    return None

def extract_sentiment(text: str) -> str | None:
    text_lower = text.lower()
    
    # Look for "Sentiment:" pattern
    sentiment_pattern = r'(?:sentiment\s*:?\s*)(positive|negative|neutral)'
    match = re.search(sentiment_pattern, text_lower)
    if match:
        return match.group(1).capitalize()
    
    # Keep existing patterns
    edit_pattern = r'sentiment\s+(?:was|is)?\s*(positive|negative|neutral)'
    edit_match = re.search(edit_pattern, text_lower)
    if edit_match:
        sentiment_str = clean_text(edit_match.group(1))
        if sentiment_str:
            return sentiment_str.capitalize()
    
    positive = ['positive', 'good', 'great', 'excellent', 'happy', 'pleased', 'interested', 'favorable', 'liked']
    negative = ['negative', 'bad', 'poor', 'unhappy', 'concerned', 'worried', 'disappointed', 'difficult', 'issue']
    
    if any(word in text_lower for word in positive):
        return 'Positive'
    elif any(word in text_lower for word in negative):
        return 'Negative'
    elif 'neutral' in text_lower:
        return 'Neutral'
    return None


def extract_date(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'date\s+(?:was|is)?\s*(today|yesterday)'
    edit_match = re.search(edit_pattern, text_lower)
    if edit_match:
        date_str = clean_text(edit_match.group(1))
        if date_str == 'yesterday':
            return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_str == 'today':
            return datetime.now().strftime("%Y-%m-%d")
    
    if 'yesterday' in text_lower:
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif 'today' in text_lower:
        return datetime.now().strftime("%Y-%m-%d")
    return None

def extract_data_from_text(text: str) -> dict:
    data = {}
    hcp_name = extract_hcp_name(text)
    if hcp_name is not None:
        data["hcp_name"] = hcp_name
    interaction_type = extract_interaction_type(text)
    if interaction_type is not None:
        data["interaction_type"] = interaction_type
    date = extract_date(text)
    if date is not None:
        data["date"] = date
    time = extract_time(text)
    if time is not None:
        data["time"] = time
    attendees = extract_attendees(text)
    if attendees is not None:
        data["attendees"] = attendees
    topics = extract_topics(text)
    if topics is not None:
        data["topics_discussed"] = topics
    materials = extract_materials(text)
    if materials is not None:
        data["materials_shared"] = materials
    samples = extract_samples(text)
    if samples is not None:
        data["samples_distributed"] = samples
    sentiment = extract_sentiment(text)
    if sentiment is not None:
        data["sentiment"] = sentiment
    outcomes = extract_outcomes(text)
    if outcomes is not None:
        data["outcomes"] = outcomes
    return data

@app.post("/api/interactions/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    db = SessionLocal()
    extracted = extract_data_from_text(request.message)
    interaction_id = request.interaction_id
    final_interaction = None
    
    # Check if this is an edit command
    is_edit_command = any(keyword in request.message.lower() for keyword in ['change', 'update', 'edit', 'instead of', 'replace'])
    
    if interaction_id and is_edit_command:
        db_interaction = db.query(InteractionDB).filter(InteractionDB.id == interaction_id).first()
        if db_interaction:
            updated_fields = []
            
            # For each field, check if we have new value
            if "topics_discussed" in extracted and extracted["topics_discussed"]:
                old_value = db_interaction.topics_discussed
                db_interaction.topics_discussed = extracted["topics_discussed"]
                updated_fields.append(f"Topics Discussed: '{old_value}' → '{extracted['topics_discussed']}'")
            
            if "materials_shared" in extracted and extracted["materials_shared"]:
                old_value = db_interaction.materials_shared
                db_interaction.materials_shared = extracted["materials_shared"]
                updated_fields.append(f"Materials Shared: '{old_value}' → '{extracted['materials_shared']}'")
            
            if "outcomes" in extracted and extracted["outcomes"]:
                old_value = db_interaction.outcomes
                db_interaction.outcomes = extracted["outcomes"]
                updated_fields.append(f"Outcomes: '{old_value}' → '{extracted['outcomes']}'")
            
            # Also handle other fields
            for key, value in extracted.items():
                if key not in ["topics_discussed", "materials_shared", "outcomes"] and value:
                    setattr(db_interaction, key, value)
                    updated_fields.append(key)
            
            db.commit()
            db.refresh(db_interaction)
            final_interaction = db_interaction
            interaction_id = final_interaction.id
            
            # Create response message
            if updated_fields:
                response_text = f"Updated successfully! Changes made to: {', '.join(updated_fields[:3])}"
                if len(updated_fields) > 3:
                    response_text += f" and {len(updated_fields)-3} other field(s)"
            else:
                response_text = "Interaction updated successfully!"
        else:
            response_text = "Interaction not found. Please create a new interaction first."
    
    elif interaction_id:
        # Normal update without explicit edit command
        db_interaction = db.query(InteractionDB).filter(InteractionDB.id == interaction_id).first()
        if db_interaction:
            for key, value in extracted.items():
                if value:
                    setattr(db_interaction, key, value)
            db.commit()
            db.refresh(db_interaction)
            final_interaction = db_interaction
            interaction_id = final_interaction.id
            response_text = f"Interaction details updated for {db_interaction.hcp_name}"
        else:
            response_text = "Interaction not found"
    
    else:
        # Create new interaction
        if "hcp_name" in extracted and extracted.get("hcp_name"):
            db_interaction = InteractionDB(
                hcp_name=extracted.get("hcp_name", "Unknown HCP"),
                interaction_type=extracted.get("interaction_type", "Meeting"),
                date=extracted.get("date", datetime.now().strftime("%Y-%m-%d")),
                time=extracted.get("time", ""),
                attendees=extracted.get("attendees", ""),
                topics_discussed=extracted.get("topics_discussed", ""),
                materials_shared=extracted.get("materials_shared", ""),
                samples_distributed=extracted.get("samples_distributed", ""),
                sentiment=extracted.get("sentiment", "Neutral"),
                outcomes=extracted.get("outcomes", "")
            )
            db.add(db_interaction)
            db.commit()
            db.refresh(db_interaction)
            interaction_id = db_interaction.id
            final_interaction = db_interaction
            response_text = f"New interaction created for {extracted['hcp_name']}"
        else:
            response_text = "Please provide HCP name to create an interaction"
    
    db.close()
    
    interaction_dict = None
    if final_interaction:
        interaction_dict = {
            "id": final_interaction.id,
            "hcp_name": final_interaction.hcp_name,
            "interaction_type": final_interaction.interaction_type,
            "date": final_interaction.date,
            "time": final_interaction.time,
            "attendees": final_interaction.attendees,
            "topics_discussed": final_interaction.topics_discussed,
            "materials_shared": final_interaction.materials_shared,
            "samples_distributed": final_interaction.samples_distributed,
            "sentiment": final_interaction.sentiment,
            "outcomes": final_interaction.outcomes,
            "created_at": final_interaction.created_at.isoformat()
        }
    
    return ChatResponse(
        response=response_text,
        extracted_data=extracted,
        interaction_id=interaction_id,
        interaction=interaction_dict
    )

@app.get("/api/interactions", response_model=List[Interaction])
def get_interactions():
    db = SessionLocal()
    interactions = db.query(InteractionDB).order_by(InteractionDB.created_at.desc()).all()
    db.close()
    return interactions

@app.get("/api/interactions/{interaction_id}", response_model=Interaction)
def get_interaction(interaction_id: int):
    db = SessionLocal()
    interaction = db.query(InteractionDB).filter(InteractionDB.id == interaction_id).first()
    db.close()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction

@app.post("/api/interactions", response_model=Interaction)
def create_interaction(interaction: InteractionCreate):
    db = SessionLocal()
    db_interaction = InteractionDB(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    db.close()
    return db_interaction

@app.put("/api/interactions/{interaction_id}", response_model=Interaction)
def update_interaction(interaction_id: int, interaction: InteractionUpdate):
    db = SessionLocal()
    db_interaction = db.query(InteractionDB).filter(InteractionDB.id == interaction_id).first()
    if not db_interaction:
        db.close()
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    update_data = interaction.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_interaction, key, value)
    
    db.commit()
    db.refresh(db_interaction)
    db.close()
    return db_interaction

@app.delete("/api/interactions/{interaction_id}")
def delete_interaction(interaction_id: int):
    db = SessionLocal()
    db_interaction = db.query(InteractionDB).filter(InteractionDB.id == interaction_id).first()
    if not db_interaction:
        db.close()
        raise HTTPException(status_code=404, detail="Interaction not found")
    db.delete(db_interaction)
    db.commit()
    db.close()
    return {"message": "Interaction deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("AI-First CRM HCP Module Backend")
    print("=" * 50)
    print("Server: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Database: MySQL (crm_hcp_db)")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
