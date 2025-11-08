"""
Content Delivery Engine
Generates and delivers personalized learning content
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database.models import (
    Module, ModuleProgress, LearningSession,
    EngagementSignal, UserSettings
)
from backend.ai import (
    ai_provider_manager, TaskType, get_content_template,
    LearningModality, AIProvider
)
from backend.learning_engine.style_engine import StyleEngine


class ContentDeliveryEngine:
    """
    Dynamically generates and delivers content optimized for user's learning style
    """

    def __init__(self, db: Session):
        self.db = db
        self.style_engine = StyleEngine(db)

    async def generate_lesson_content(
        self,
        user_id: str,
        module_id: str,
        force_modality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate lesson content adapted to user's learning style

        Args:
            user_id: User ID
            module_id: Module to generate content for
            force_modality: Optional - force a specific modality (for testing)

        Returns:
            Dictionary with generated content and metadata
        """
        # Get module information
        module = self.db.query(Module).filter(Module.module_id == module_id).first()
        if not module:
            raise ValueError(f"Module {module_id} not found")

        # Select modality
        if force_modality:
            modality = LearningModality(force_modality)
            selection_reason = f"Forced modality: {force_modality}"
        else:
            modality, selection_reason = self.style_engine.select_modality(user_id)

        # Get user context
        user_context = await self._get_user_context(user_id, module_id)

        # Generate content using AI
        system_prompt = get_content_template(
            modality.value,
            module.title,
            ", ".join(module.learning_objectives),
            user_context
        )

        # Create user prompt
        user_prompt = self._create_user_prompt(module, user_context)

        # Get user's preferred provider from settings
        user_settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()

        preferred_provider = None
        if user_settings and user_settings.preferred_provider:
            try:
                preferred_provider = AIProvider(user_settings.preferred_provider)
            except ValueError:
                pass  # Invalid provider value, will use default

        # Select AI provider and generate
        provider = ai_provider_manager.select_provider(
            TaskType.CONTENT_GENERATION,
            user_preference=preferred_provider
        )
        content = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2000,
            temperature=0.7
        )

        # Create learning session record
        session = LearningSession(
            user_id=user_id,
            module_id=module_id,
            modality_used=modality.value,
            session_context={
                "modality": modality.value,
                "selection_reason": selection_reason,
                "learning_objectives": module.learning_objectives,
                "user_context": user_context,
                "generated_content": content  # Store generated content for tutor context
            }
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return {
            "session_id": session.session_id,
            "content": content,
            "modality": modality.value,
            "selection_reason": selection_reason,
            "module": {
                "id": module.module_id,
                "title": module.title,
                "objectives": module.learning_objectives,
                "estimated_time": module.estimated_time
            }
        }

    async def _get_user_context(
        self,
        user_id: str,
        module_id: str
    ) -> Dict[str, Any]:
        """Get user's current knowledge level and preferences"""
        # Get progress on this module
        progress = self.db.query(ModuleProgress).filter(
            ModuleProgress.user_id == user_id,
            ModuleProgress.module_id == module_id
        ).first()

        # Get user's learning insights
        insights = self.style_engine.get_learning_insights(user_id)

        # Determine knowledge level (1-5)
        if progress:
            knowledge_level = min(5, max(1, int(progress.mastery_score * 5) + 1))
        else:
            knowledge_level = 1  # Beginner

        return {
            "knowledge_level": knowledge_level,
            "interests": ["finance", "investing", "Warren Buffett"],  # TODO: Make dynamic
            "learning_style": insights.get("status", "discovery"),
            "preferences": insights.get("cognitive_patterns", {})
        }

    def _create_user_prompt(
        self,
        module: Module,
        user_context: Dict[str, Any]
    ) -> str:
        """Create the user prompt for content generation"""
        return f"""Generate a lesson for: {module.title}

Description: {module.description}

Learning Objectives:
{chr(10).join(f"- {obj}" for obj in module.learning_objectives)}

User's Knowledge Level: {user_context['knowledge_level']}/5

Focus on making this practical, engaging, and perfectly suited to their learning style."""

    def record_engagement_signal(
        self,
        session_id: str,
        signal_type: str,
        signal_value: float,
        context: Optional[Dict] = None
    ) -> None:
        """
        Record an engagement signal during a learning session

        Args:
            session_id: Learning session ID
            signal_type: Type of signal (time_on_task, question_asked, etc.)
            signal_value: Numeric value of signal
            context: Additional context
        """
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).first()

        if not session:
            return

        signal = EngagementSignal(
            user_id=session.user_id,
            session_id=session_id,
            signal_type=signal_type,
            signal_value=signal_value,
            context=context or {}
        )

        self.db.add(signal)

        # Update session metrics
        if signal_type == "question_asked":
            session.questions_asked = (session.questions_asked or 0) + 1
        elif signal_type == "time_on_task":
            session.duration = int(signal_value)

        self.db.commit()

    def complete_session(
        self,
        session_id: str,
        comprehension_score: float,
        engagement_score: float
    ) -> None:
        """
        Mark a session as complete and update learning profile

        Args:
            session_id: Session ID
            comprehension_score: How well user understood (0-1)
            engagement_score: How engaged user was (0-1)
        """
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).first()

        if not session:
            return

        # Update session
        session.completed_at = datetime.utcnow()
        session.comprehension_score = comprehension_score
        session.engagement_score = engagement_score

        # Calculate duration if not set
        if not session.duration and session.created_at:
            duration_seconds = (datetime.utcnow() - session.created_at).total_seconds()
            session.duration = int(duration_seconds / 60)  # Convert to minutes

        # Update learning style profile
        modality = LearningModality(session.modality_used)
        self.style_engine.update_learning_profile(
            user_id=session.user_id,
            session_id=session_id,
            modality=modality,
            engagement_score=engagement_score,
            comprehension_score=comprehension_score
        )

        # Update module progress
        self._update_module_progress(
            session.user_id,
            session.module_id,
            comprehension_score
        )

        self.db.commit()

    def _update_module_progress(
        self,
        user_id: str,
        module_id: str,
        comprehension_score: float
    ) -> None:
        """Update user's progress on a module"""
        progress = self.db.query(ModuleProgress).filter(
            ModuleProgress.user_id == user_id,
            ModuleProgress.module_id == module_id
        ).first()

        if not progress:
            progress = ModuleProgress(
                user_id=user_id,
                module_id=module_id,
                status="in_progress",
                started_at=datetime.utcnow()
            )
            self.db.add(progress)

        # Update mastery score (weighted average)
        if progress.mastery_score:
            progress.mastery_score = (progress.mastery_score * 0.7) + (comprehension_score * 0.3)
        else:
            progress.mastery_score = comprehension_score

        # Update status based on mastery
        if progress.mastery_score >= 0.9:
            progress.status = "mastered"
            progress.completed_at = datetime.utcnow()
        elif progress.mastery_score >= 0.7:
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
        else:
            progress.status = "in_progress"

        # Update completion percentage
        progress.completion_percentage = min(1.0, progress.mastery_score + 0.1)
