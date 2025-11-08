"""
Dynamic subject creation and knowledge assessment routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.database import get_db
from backend.learning_engine import DynamicSubjectEngine

router = APIRouter()


class SubjectRequest(BaseModel):
    subject: str


class AssessmentMessage(BaseModel):
    message: str


class AssessmentContinue(BaseModel):
    subject: str
    conversation_history: List[Dict[str, str]]


class AssessmentResponse(BaseModel):
    status: str  # "in_progress" or "complete"
    question: Optional[str] = None
    questions_asked: Optional[int] = None
    assessment_complete: bool
    # Only present when complete:
    knowledge_level: Optional[int] = None
    summary: Optional[str] = None
    gaps: Optional[List[str]] = None
    starting_point: Optional[str] = None
    learning_objectives: Optional[List[str]] = None


class CreateModuleRequest(BaseModel):
    subject: str
    assessment: Dict[str, Any]


@router.post("/assess/start", response_model=AssessmentResponse)
async def start_assessment(
    request: SubjectRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Start knowledge assessment for a new subject

    User says: "I want to learn about stock fundamentals"
    System responds with first assessment question
    """
    engine = DynamicSubjectEngine(db)

    try:
        result = await engine.assess_knowledge(
            user_id=user_id,
            subject=request.subject,
            conversation_history=None
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting assessment: {str(e)}")


@router.post("/assess/continue", response_model=AssessmentResponse)
async def continue_assessment(
    request: AssessmentContinue,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Continue knowledge assessment with user's answer

    Takes conversation history and returns next question or completion
    """
    engine = DynamicSubjectEngine(db)

    try:
        result = await engine.assess_knowledge(
            user_id=user_id,
            subject=request.subject,
            conversation_history=request.conversation_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error continuing assessment: {str(e)}")


@router.post("/create-module")
async def create_dynamic_module(
    request: CreateModuleRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Create a learning module dynamically from assessment results

    After assessment is complete, this generates the actual module
    """
    engine = DynamicSubjectEngine(db)

    try:
        module = await engine.create_dynamic_module(
            user_id=user_id,
            subject=request.subject,
            assessment=request.assessment
        )

        return {
            "module_id": module.module_id,
            "title": module.title,
            "description": module.description,
            "learning_objectives": module.learning_objectives,
            "difficulty_level": module.difficulty_level,
            "estimated_time": module.estimated_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating module: {str(e)}")
