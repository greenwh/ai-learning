"""
User Settings API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
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
    google_model: str = "gemini-2.0-flash-exp"

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

    # Learning Preferences
    default_modality: Optional[str] = None
    session_reminders: Optional[bool] = None
    spaced_repetition_enabled: Optional[bool] = None

    # UI Preferences
    theme: Optional[str] = None
    language: Optional[str] = None


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
            google_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
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
        default_modality=settings.default_modality,
        session_reminders=settings.session_reminders,
        spaced_repetition_enabled=settings.spaced_repetition_enabled,
        theme=settings.theme,
        language=settings.language,
        updated_at=settings.updated_at
    )
