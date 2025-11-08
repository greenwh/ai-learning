"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Authentication
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


# Learning Sessions
class SessionStart(BaseModel):
    module_id: str
    force_modality: Optional[str] = None


class SessionComplete(BaseModel):
    comprehension_score: float = Field(ge=0.0, le=1.0)
    engagement_score: float = Field(ge=0.0, le=1.0)


class EngagementSignalCreate(BaseModel):
    signal_type: str
    signal_value: float
    context: Optional[Dict[str, Any]] = None


# Content
class ModuleCreate(BaseModel):
    domain: str
    subject: str
    topic: str
    title: str
    description: str
    prerequisites: List[str] = []
    learning_objectives: List[str]
    difficulty_level: int = Field(ge=1, le=5)
    estimated_time: int  # minutes
    content_config: Dict[str, Any]


class ModuleResponse(BaseModel):
    module_id: str
    domain: str
    subject: str
    topic: str
    title: str
    description: str
    prerequisites: List[str]
    learning_objectives: List[str]
    difficulty_level: int
    estimated_time: int
    created_at: datetime
    version: str

    class Config:
        from_attributes = True


class LessonContentResponse(BaseModel):
    session_id: str
    content: str
    modality: str
    selection_reason: str
    module: Dict[str, Any]


# Chat
class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime


class ComprehensionCheckResponse(BaseModel):
    question: str
    session_id: str
    type: str


class ComprehensionAnswer(BaseModel):
    answer: str


class ComprehensionEvaluation(BaseModel):
    score: float
    feedback: str
    passed: bool


# Progress
class ProgressOverview(BaseModel):
    user_id: str
    total_sessions: int
    modules_in_progress: int
    modules_completed: int
    modules_mastered: int
    total_time_spent: int  # minutes
    learning_insights: Dict[str, Any]


class ModuleProgressResponse(BaseModel):
    progress_id: str
    module_id: str
    status: str
    completion_percentage: float
    mastery_score: float
    time_spent: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
