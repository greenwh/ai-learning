"""
AI Tutor Chat routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend.learning_engine import TutorEngine
from backend.api.models import (
    ChatMessage, ChatResponse,
    ComprehensionCheckResponse, ComprehensionAnswer,
    ComprehensionEvaluation
)

router = APIRouter()


@router.post("/{session_id}/message", response_model=ChatResponse)
async def send_message(
    session_id: str,
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI tutor
    """
    engine = TutorEngine(db)

    try:
        response = await engine.chat(
            session_id=session_id,
            user_message=message.message
        )

        return ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/{session_id}/comprehension-check", response_model=ComprehensionCheckResponse)
async def get_comprehension_check(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate a casual comprehension check question
    """
    engine = TutorEngine(db)

    try:
        result = await engine.generate_comprehension_check(session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating check: {str(e)}")


@router.post("/{session_id}/comprehension-check", response_model=ComprehensionEvaluation)
async def evaluate_comprehension(
    session_id: str,
    answer: ComprehensionAnswer,
    db: Session = Depends(get_db)
):
    """
    Evaluate user's answer to comprehension check
    """
    engine = TutorEngine(db)

    try:
        result = await engine.evaluate_comprehension_response(
            session_id=session_id,
            user_response=answer.answer
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating response: {str(e)}")
