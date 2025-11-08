"""
Learning session routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.learning_engine import ContentDeliveryEngine
from backend.api.models import (
    SessionStart, SessionComplete, EngagementSignalCreate,
    LessonContentResponse
)

router = APIRouter()


@router.post("/start", response_model=LessonContentResponse)
async def start_session(
    session_data: SessionStart,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Start a new learning session
    Generates content adapted to user's learning style
    """
    engine = ContentDeliveryEngine(db)

    try:
        result = await engine.generate_lesson_content(
            user_id=user_id,
            module_id=session_data.module_id,
            force_modality=session_data.force_modality
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")


@router.post("/{session_id}/engagement")
async def record_engagement(
    session_id: str,
    signal: EngagementSignalCreate,
    db: Session = Depends(get_db)
):
    """
    Record an engagement signal during a learning session
    """
    engine = ContentDeliveryEngine(db)

    engine.record_engagement_signal(
        session_id=session_id,
        signal_type=signal.signal_type,
        signal_value=signal.signal_value,
        context=signal.context
    )

    return {"status": "recorded", "session_id": session_id}


@router.post("/{session_id}/complete")
async def complete_session(
    session_id: str,
    completion_data: SessionComplete,
    db: Session = Depends(get_db)
):
    """
    Mark a session as complete
    Updates learning profile based on performance
    """
    engine = ContentDeliveryEngine(db)

    engine.complete_session(
        session_id=session_id,
        comprehension_score=completion_data.comprehension_score,
        engagement_score=completion_data.engagement_score
    )

    return {
        "status": "completed",
        "session_id": session_id,
        "comprehension_score": completion_data.comprehension_score,
        "engagement_score": completion_data.engagement_score
    }
