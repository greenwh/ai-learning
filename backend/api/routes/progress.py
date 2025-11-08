"""
Progress tracking routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.database.models import ModuleProgress, LearningSession
from backend.learning_engine import StyleEngine
from backend.api.models import ProgressOverview, ModuleProgressResponse

router = APIRouter()


@router.get("/{user_id}/overview", response_model=ProgressOverview)
async def get_progress_overview(user_id: str, db: Session = Depends(get_db)):
    """
    Get overall progress overview for a user
    """
    # Get all module progress
    progress_records = db.query(ModuleProgress).filter(
        ModuleProgress.user_id == user_id
    ).all()

    # Get all sessions
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == user_id
    ).all()

    # Calculate totals
    modules_in_progress = len([p for p in progress_records if p.status == "in_progress"])
    modules_completed = len([p for p in progress_records if p.status == "completed"])
    modules_mastered = len([p for p in progress_records if p.status == "mastered"])
    total_time_spent = sum(p.time_spent or 0 for p in progress_records)

    # Get learning insights
    style_engine = StyleEngine(db)
    learning_insights = style_engine.get_learning_insights(user_id)

    return ProgressOverview(
        user_id=user_id,
        total_sessions=len(sessions),
        modules_in_progress=modules_in_progress,
        modules_completed=modules_completed,
        modules_mastered=modules_mastered,
        total_time_spent=total_time_spent,
        learning_insights=learning_insights
    )


@router.get("/{user_id}/modules", response_model=List[ModuleProgressResponse])
async def get_user_modules(user_id: str, db: Session = Depends(get_db)):
    """
    Get all module progress for a user
    """
    progress_records = db.query(ModuleProgress).filter(
        ModuleProgress.user_id == user_id
    ).all()

    return progress_records


@router.get("/{user_id}/modules/{module_id}", response_model=ModuleProgressResponse)
async def get_module_progress(
    user_id: str,
    module_id: str,
    db: Session = Depends(get_db)
):
    """
    Get progress for a specific module
    """
    progress = db.query(ModuleProgress).filter(
        ModuleProgress.user_id == user_id,
        ModuleProgress.module_id == module_id
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    return progress
