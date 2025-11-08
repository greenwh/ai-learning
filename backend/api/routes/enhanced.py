"""
Enhanced Learning Features API
Spaced repetition, recommendations, streaks, and achievements
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.database import get_db
from backend.learning_engine import SpacedRepetitionEngine, RecommendationEngine

router = APIRouter()


class RetentionAnswer(BaseModel):
    answer: str


class RetentionEvaluation(BaseModel):
    recall_accuracy: float
    confidence_level: float
    application_ability: float
    feedback: str
    passed: bool
    reschedule: bool


# Spaced Repetition Endpoints

@router.get("/{user_id}/retention/due")
async def get_due_retention_tests(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all retention tests that are due for review
    """
    engine = SpacedRepetitionEngine(db)

    try:
        tests = await engine.get_due_tests(user_id)
        return {
            "count": len(tests),
            "tests": tests
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tests: {str(e)}")


@router.post("/retention/{test_id}/answer", response_model=RetentionEvaluation)
async def answer_retention_test(
    test_id: str,
    answer: RetentionAnswer,
    db: Session = Depends(get_db)
):
    """
    Submit answer to a retention test
    """
    engine = SpacedRepetitionEngine(db)

    try:
        result = await engine.evaluate_retention_response(test_id, answer.answer)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")


@router.get("/{user_id}/retention/stats")
async def get_retention_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get retention statistics for a user
    """
    engine = SpacedRepetitionEngine(db)

    try:
        stats = engine.get_retention_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/{user_id}/review/{concept_id}")
async def get_concept_review(
    user_id: str,
    concept_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a quick review session for a specific concept
    """
    engine = SpacedRepetitionEngine(db)

    try:
        review = await engine.get_review_session(user_id, concept_id)
        return review
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating review: {str(e)}")


# Recommendations Endpoints

@router.get("/{user_id}/recommendations")
async def get_recommendations(
    user_id: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get personalized learning recommendations
    """
    engine = RecommendationEngine(db)

    try:
        recommendations = engine.get_recommendations(user_id, limit)
        return {
            "count": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


@router.get("/{user_id}/next-session")
async def get_next_session_suggestion(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get suggestion for what to do in the next learning session
    """
    engine = RecommendationEngine(db)

    try:
        suggestion = engine.get_next_session_suggestion(user_id)
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestion: {str(e)}")


@router.get("/{user_id}/streak")
async def get_learning_streak(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user's learning streak information
    """
    engine = RecommendationEngine(db)

    try:
        streak = engine.get_learning_streak(user_id)
        return streak
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting streak: {str(e)}")


@router.get("/{user_id}/achievements")
async def get_achievements(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user's achievement progress
    """
    engine = RecommendationEngine(db)

    try:
        achievements = engine.get_achievement_progress(user_id)
        return achievements
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting achievements: {str(e)}")


# Schedule retention tests after session completion
@router.post("/sessions/{session_id}/schedule-retention")
async def schedule_retention_tests(
    session_id: str,
    concepts: List[str],
    db: Session = Depends(get_db)
):
    """
    Schedule retention tests for concepts learned in a session

    Args:
        session_id: Learning session ID
        concepts: List of concept IDs that were learned

    Returns:
        Number of tests scheduled
    """
    engine = SpacedRepetitionEngine(db)

    try:
        tests = engine.schedule_retention_tests(session_id, concepts)
        return {
            "scheduled": len(tests),
            "intervals": ["24 hours", "3 days", "7 days", "14 days", "30 days"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling tests: {str(e)}")
