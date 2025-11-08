"""
Database models for the AI-Based Personalized Learning System
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON,
    ForeignKey, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False)
    email = Column(String)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    encryption_key_hash = Column(String)
    sync_enabled = Column(Boolean, default=False)

    # Relationships
    learning_profile = relationship("LearningProfile", back_populates="user", uselist=False)
    progress = relationship("ModuleProgress", back_populates="user")
    sessions = relationship("LearningSession", back_populates="user")
    concept_mastery = relationship("ConceptMastery", back_populates="user")
    engagement_signals = relationship("EngagementSignal", back_populates="user")


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    user_id = Column(String, ForeignKey("users.user_id"), primary_key=True)
    modality_preferences = Column(JSON, nullable=False, default=dict)
    # Structure: {
    #   "narrative_story": {"effectiveness_score": 0.85, "sessions_count": 12, ...},
    #   "interactive_hands_on": {...},
    #   "socratic_dialogue": {...},
    #   "visual_diagrams": {...}
    # }
    cognitive_patterns = Column(JSON, nullable=False, default=dict)
    # Structure: {
    #   "prefers_big_picture_first": true,
    #   "learns_by_doing": true,
    #   "optimal_session_length": 15,
    #   "best_time_of_day": "evening"
    # }
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="learning_profile")


class Module(Base):
    __tablename__ = "modules"

    module_id = Column(String, primary_key=True, default=generate_uuid)
    domain = Column(String, nullable=False)  # e.g., "Finance"
    subject = Column(String, nullable=False)  # e.g., "Stock Market Investing"
    topic = Column(String, nullable=False)  # e.g., "Fundamental Analysis"
    title = Column(String, nullable=False)
    description = Column(Text)
    prerequisites = Column(JSON, default=list)  # Array of module_ids
    learning_objectives = Column(JSON, default=list)
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    estimated_time = Column(Integer)  # minutes
    content_config = Column(JSON, nullable=False)
    # Structure: Full content configuration with variants for each modality
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(String, default="1.0")

    # Relationships
    progress = relationship("ModuleProgress", back_populates="module")
    sessions = relationship("LearningSession", back_populates="module")


class ModuleProgress(Base):
    __tablename__ = "module_progress"

    progress_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    module_id = Column(String, ForeignKey("modules.module_id"), nullable=False)
    status = Column(String, default="not_started")  # not_started, in_progress, completed, mastered
    current_lesson = Column(String)
    completion_percentage = Column(Float, default=0.0)
    mastery_score = Column(Float, default=0.0)  # 0-1 based on retention and application
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    time_spent = Column(Integer, default=0)  # minutes

    # Relationships
    user = relationship("User", back_populates="progress")
    module = relationship("Module", back_populates="progress")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    session_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    module_id = Column(String, ForeignKey("modules.module_id"), nullable=False)
    modality_used = Column(String, nullable=False)  # narrative, interactive, socratic, visual
    duration = Column(Integer, default=0)  # minutes
    engagement_score = Column(Float)  # 0-1
    questions_asked = Column(Integer, default=0)
    comprehension_score = Column(Float)  # 0-1
    retention_score = Column(Float)  # 0-1, filled in after 24hr test
    session_context = Column(JSON)  # Full context snapshot
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="sessions")
    module = relationship("Module", back_populates="sessions")
    engagement_signals = relationship("EngagementSignal", back_populates="session")
    chat_messages = relationship("ChatMessage", back_populates="session")


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    user_id = Column(String, ForeignKey("users.user_id"), primary_key=True)
    concept_id = Column(String, primary_key=True)
    mastery_level = Column(Float, default=0.0)  # 0-1
    first_learned = Column(DateTime)
    last_reviewed = Column(DateTime)
    times_practiced = Column(Integer, default=0)
    successful_applications = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="concept_mastery")


class EngagementSignal(Base):
    __tablename__ = "engagement_signals"

    signal_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    session_id = Column(String, ForeignKey("learning_sessions.session_id"), nullable=False)
    signal_type = Column(String, nullable=False)  # question_asked, scrolled_back, time_on_concept, etc.
    signal_value = Column(Float)
    context = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="engagement_signals")
    session = relationship("LearningSession", back_populates="engagement_signals")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("learning_sessions.session_id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("LearningSession", back_populates="chat_messages")


class RetentionTest(Base):
    __tablename__ = "retention_tests"

    test_id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("learning_sessions.session_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    concept_id = Column(String, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)  # 24 hours after learning
    completed_at = Column(DateTime)
    recall_accuracy = Column(Float)  # 0-1
    confidence_level = Column(Float)  # 0-1
    application_ability = Column(Float)  # 0-1
    user_response = Column(Text)

    # No explicit relationships defined to keep it lightweight


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(String, ForeignKey("users.user_id"), primary_key=True)

    # AI Provider Settings
    preferred_provider = Column(String)  # anthropic, openai, google, xai
    anthropic_api_key = Column(String)  # Encrypted
    anthropic_model = Column(String, default="claude-sonnet-4-5-20250929")
    openai_api_key = Column(String)  # Encrypted
    openai_model = Column(String, default="gpt-4o-mini")
    google_api_key = Column(String)  # Encrypted
    google_model = Column(String, default="gemini-2.0-flash")
    xai_api_key = Column(String)  # Encrypted
    xai_model = Column(String, default="grok-3")

    # Learning Preferences
    default_modality = Column(String)  # narrative_story, interactive_hands_on, etc.
    session_reminders = Column(Boolean, default=True)
    spaced_repetition_enabled = Column(Boolean, default=True)

    # UI Preferences
    theme = Column(String, default="light")  # light, dark
    language = Column(String, default="en")

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User")
