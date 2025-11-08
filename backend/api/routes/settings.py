"""
User Settings API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os

from backend.database import get_db
from backend.database.models import UserSettings

router = APIRouter()


class SettingsResponse(BaseModel):
    # AI Provider Settings
    preferred_provider: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    google_api_key: Optional[str] = None
    google_model: str = "gemini-2.0-flash"
    xai_api_key: Optional[str] = None
    xai_model: str = "grok-3"

    # Learning Preferences
    default_modality: Optional[str] = None
    session_reminders: bool = True
    spaced_repetition_enabled: bool = True

    # UI Preferences
    theme: str = "light"
    language: str = "en"

    updated_at: Optional[datetime] = None


class SettingsUpdate(BaseModel):
    # AI Provider Settings
    preferred_provider: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    anthropic_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    google_api_key: Optional[str] = None
    google_model: Optional[str] = None
    xai_api_key: Optional[str] = None
    xai_model: Optional[str] = None

    # Learning Preferences
    default_modality: Optional[str] = None
    session_reminders: Optional[bool] = None
    spaced_repetition_enabled: Optional[bool] = None

    # UI Preferences
    theme: Optional[str] = None
    language: Optional[str] = None


class AvailableModelsResponse(BaseModel):
    anthropic: List[str]
    openai: List[str]
    google: List[str]
    xai: List[str]


@router.get("/available-models", response_model=AvailableModelsResponse)
async def get_available_models():
    """
    Get available AI models from environment variables
    """
    def parse_models(env_var: str, default: str) -> List[str]:
        models_str = os.getenv(env_var, default)
        return [m.strip() for m in models_str.split(',') if m.strip()]

    return AvailableModelsResponse(
        anthropic=parse_models("ANTHROPIC_MODELS", "claude-sonnet-4-5-20250929,claude-opus-4-1-20250805,claude-haiku-4-5-20251001"),
        openai=parse_models("OPENAI_MODELS", "gpt-4o-mini,gpt-4o,o1,o1-mini"),
        google=parse_models("GEMINI_MODELS", "gemini-2.0-flash,gemini-2.5-pro,gemini-2.5-flash"),
        xai=parse_models("XAI_MODELS", "grok-3,grok-3-mini,grok-4-fast-reasoning")
    )


@router.get("/{user_id}", response_model=SettingsResponse)
async def get_settings(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user settings, populated with defaults from .env if not set
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    if not settings:
        # Create default settings from environment variables
        settings = UserSettings(
            user_id=user_id,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            google_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            xai_api_key=os.getenv("XAI_API_KEY"),
            xai_model=os.getenv("XAI_MODEL", "grok-3"),
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return SettingsResponse(
        preferred_provider=settings.preferred_provider,
        anthropic_api_key=settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"),
        anthropic_model=settings.anthropic_model,
        openai_api_key=settings.openai_api_key or os.getenv("OPENAI_API_KEY"),
        openai_model=settings.openai_model,
        google_api_key=settings.google_api_key or os.getenv("GOOGLE_API_KEY"),
        google_model=settings.google_model,
        xai_api_key=settings.xai_api_key or os.getenv("XAI_API_KEY"),
        xai_model=settings.xai_model,
        default_modality=settings.default_modality,
        session_reminders=settings.session_reminders,
        spaced_repetition_enabled=settings.spaced_repetition_enabled,
        theme=settings.theme,
        language=settings.language,
        updated_at=settings.updated_at
    )


@router.put("/{user_id}", response_model=SettingsResponse)
async def update_settings(
    user_id: str,
    updates: SettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user settings
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    if not settings:
        # Create new settings
        settings = UserSettings(user_id=user_id)
        db.add(settings)

    # Update fields that were provided
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)

    return SettingsResponse(
        preferred_provider=settings.preferred_provider,
        anthropic_api_key=settings.anthropic_api_key,
        anthropic_model=settings.anthropic_model,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        google_api_key=settings.google_api_key,
        google_model=settings.google_model,
        xai_api_key=settings.xai_api_key,
        xai_model=settings.xai_model,
        default_modality=settings.default_modality,
        session_reminders=settings.session_reminders,
        spaced_repetition_enabled=settings.spaced_repetition_enabled,
        theme=settings.theme,
        language=settings.language,
        updated_at=settings.updated_at
    )
