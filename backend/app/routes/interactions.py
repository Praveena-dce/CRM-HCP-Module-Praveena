from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db, Interaction, Base, engine
from app.schemas import (
    InteractionCreate, InteractionUpdate, InteractionResponse,
    ChatRequest, ChatResponse
)
from app.services import extract_data_from_text

router = APIRouter(prefix="/api/interactions", tags=["interactions"])

Base.metadata.create_all(bind=engine)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    extracted = extract_data_from_text(request.message)
    
    try:
        interaction = Interaction(**extracted)
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        interaction_id = interaction.id
        response_msg = f"Interaction logged successfully! Details for '{extracted['hcp_name'] or 'HCP'}' have been saved."
    except Exception as e:
        db.rollback()
        response_msg = f"Error saving: {str(e)}"
        interaction_id = None
    
    return ChatResponse(
        response=response_msg,
        extracted_data=extracted,
        interaction_id=interaction_id
    )


@router.get("", response_model=List[InteractionResponse])
async def get_interactions(limit: int = 50, db: Session = Depends(get_db)):
    interactions = db.query(Interaction).order_by(Interaction.id.desc()).limit(limit).all()
    return interactions


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.post("", response_model=InteractionResponse)
async def create_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    db_interaction = Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(interaction_id: int, interaction: InteractionUpdate, db: Session = Depends(get_db)):
    db_interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    for key, value in interaction.dict().items():
        setattr(db_interaction, key, value)
    
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@router.delete("/{interaction_id}")
async def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    db_interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    db.delete(db_interaction)
    db.commit()
    return {"message": "Interaction deleted successfully"}
