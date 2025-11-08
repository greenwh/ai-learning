"""
Learning Style Discovery Engine
Uses multi-armed bandit algorithm to discover optimal teaching modalities
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database.models import LearningProfile, LearningSession, User
from backend.ai.content_templates import LearningModality


class StyleEngine:
    """
    Discovers and refines understanding of how a user learns best
    using Thompson Sampling (Bayesian multi-armed bandit)
    """

    def __init__(self, db: Session):
        self.db = db

    def select_modality(
        self,
        user_id: str,
        exploration_rate: float = 0.2
    ) -> Tuple[LearningModality, str]:
        """
        Select the best learning modality for the next session
        using Thompson Sampling

        Args:
            user_id: User ID
            exploration_rate: % of time to explore (try different methods)

        Returns:
            Tuple of (selected_modality, reason_for_selection)
        """
        # Get user's learning profile
        profile = self.db.query(LearningProfile).filter(
            LearningProfile.user_id == user_id
        ).first()

        if not profile or not profile.modality_preferences:
            # New user - random exploration
            modality = random.choice(list(LearningModality))
            return modality, "Initial exploration - discovering your learning style"

        prefs = profile.modality_preferences

        # Check if we should explore (try different methods)
        if random.random() < exploration_rate:
            # Explore: try modality with least data
            least_tried = min(
                prefs.items(),
                key=lambda x: x[1].get('sessions_count', 0)
            )
            modality = LearningModality(least_tried[0])
            return modality, "Exploring - trying different teaching methods to optimize your learning"

        # Exploit: use Thompson Sampling to select best modality
        samples = {}

        for modality_name, stats in prefs.items():
            successes = int(stats.get('sessions_count', 0) * stats.get('effectiveness_score', 0.5))
            failures = int(stats.get('sessions_count', 0) - successes)

            # Thompson Sampling: draw from Beta distribution
            # Beta(successes + 1, failures + 1)
            sample = np.random.beta(successes + 1, failures + 1)
            samples[modality_name] = sample

        # Select modality with highest sample
        best_modality_name = max(samples.items(), key=lambda x: x[1])[0]
        best_modality = LearningModality(best_modality_name)

        effectiveness = prefs[best_modality_name].get('effectiveness_score', 0.5)
        return best_modality, f"Using {best_modality_name} (your {int(effectiveness*100)}% effectiveness method)"

    def update_learning_profile(
        self,
        user_id: str,
        session_id: str,
        modality: LearningModality,
        engagement_score: float,
        comprehension_score: float,
        retention_score: Optional[float] = None
    ) -> None:
        """
        Update user's learning profile based on session performance

        Args:
            user_id: User ID
            session_id: Learning session ID
            modality: Modality used in session
            engagement_score: How engaged the user was (0-1)
            comprehension_score: How well they understood (0-1)
            retention_score: How well they retained info (0-1, optional)
        """
        profile = self.db.query(LearningProfile).filter(
            LearningProfile.user_id == user_id
        ).first()

        if not profile:
            # Create new profile
            profile = LearningProfile(
                user_id=user_id,
                modality_preferences={},
                cognitive_patterns={}
            )
            self.db.add(profile)

        # Initialize modality preferences if needed
        if not profile.modality_preferences:
            profile.modality_preferences = self._initialize_modality_preferences()

        # Get current stats for this modality
        modality_name = modality.value
        current_stats = profile.modality_preferences.get(modality_name, {
            "effectiveness_score": 0.5,
            "sessions_count": 0,
            "avg_retention": 0.5,
            "avg_engagement": 0.5,
            "last_updated": None
        })

        # Update stats with new session data
        sessions_count = current_stats['sessions_count']
        new_sessions_count = sessions_count + 1

        # Calculate effectiveness score (weighted average of metrics)
        if retention_score is not None:
            # If we have retention data, weight it heavily
            effectiveness = (
                retention_score * 0.5 +
                comprehension_score * 0.3 +
                engagement_score * 0.2
            )
        else:
            # Without retention, use comprehension and engagement
            effectiveness = (
                comprehension_score * 0.6 +
                engagement_score * 0.4
            )

        # Update running averages
        current_stats['effectiveness_score'] = (
            (current_stats['effectiveness_score'] * sessions_count + effectiveness) /
            new_sessions_count
        )
        current_stats['avg_engagement'] = (
            (current_stats['avg_engagement'] * sessions_count + engagement_score) /
            new_sessions_count
        )

        if retention_score is not None:
            current_retention = current_stats.get('avg_retention', 0.5)
            current_stats['avg_retention'] = (
                (current_retention * sessions_count + retention_score) /
                new_sessions_count
            )

        current_stats['sessions_count'] = new_sessions_count
        current_stats['last_updated'] = datetime.utcnow().isoformat()

        # Update profile
        profile.modality_preferences[modality_name] = current_stats
        profile.updated_at = datetime.utcnow()

        # Update cognitive patterns
        self._update_cognitive_patterns(profile, engagement_score, session_id)

        self.db.commit()

    def _initialize_modality_preferences(self) -> Dict:
        """Initialize modality preferences with default values"""
        return {
            modality.value: {
                "effectiveness_score": 0.5,
                "sessions_count": 0,
                "avg_retention": 0.5,
                "avg_engagement": 0.5,
                "last_updated": None
            }
            for modality in LearningModality
        }

    def _update_cognitive_patterns(
        self,
        profile: LearningProfile,
        engagement_score: float,
        session_id: str
    ) -> None:
        """
        Update cognitive patterns based on session data

        Analyzes patterns like:
        - Best time of day
        - Optimal session length
        - Question-asking behavior
        """
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).first()

        if not session:
            return

        if not profile.cognitive_patterns:
            profile.cognitive_patterns = {}

        patterns = profile.cognitive_patterns

        # Track optimal session length
        if session.duration:
            if engagement_score > 0.7:
                # Good engagement - this duration works
                current_optimal = patterns.get('optimal_session_length', session.duration)
                patterns['optimal_session_length'] = int(
                    (current_optimal + session.duration) / 2
                )

        # Track question-asking behavior
        if session.questions_asked > 0:
            patterns['asks_questions'] = True
            if session.questions_asked > 3:
                patterns['highly_curious'] = True

        # Track learning preferences based on modality success
        if engagement_score > 0.8:
            if session.modality_used == LearningModality.INTERACTIVE.value:
                patterns['learns_by_doing'] = True
            elif session.modality_used == LearningModality.NARRATIVE.value:
                patterns['prefers_stories'] = True
            elif session.modality_used == LearningModality.VISUAL.value:
                patterns['visual_learner'] = True
            elif session.modality_used == LearningModality.SOCRATIC.value:
                patterns['conceptual_thinker'] = True

        # Track time of day preference
        hour = session.created_at.hour
        time_of_day = self._get_time_period(hour)

        if engagement_score > 0.7:
            best_time = patterns.get('best_time_of_day', {})
            if isinstance(best_time, str):
                # Legacy format, convert to dict
                best_time = {best_time: 1}

            best_time[time_of_day] = best_time.get(time_of_day, 0) + 1
            patterns['best_time_of_day'] = max(best_time.items(), key=lambda x: x[1])[0]

        profile.cognitive_patterns = patterns

    def _get_time_period(self, hour: int) -> str:
        """Convert hour to time period"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def get_learning_insights(self, user_id: str) -> Dict:
        """
        Get insights about user's learning style

        Returns:
            Dictionary with learning insights and recommendations
        """
        profile = self.db.query(LearningProfile).filter(
            LearningProfile.user_id == user_id
        ).first()

        if not profile or not profile.modality_preferences:
            return {
                "status": "discovery",
                "message": "Still discovering your learning style",
                "sessions_needed": 3
            }

        prefs = profile.modality_preferences
        patterns = profile.cognitive_patterns or {}

        # Find best modalities
        sorted_modalities = sorted(
            prefs.items(),
            key=lambda x: x[1].get('effectiveness_score', 0),
            reverse=True
        )

        best_modalities = [
            {
                "modality": mod[0],
                "effectiveness": round(mod[1].get('effectiveness_score', 0) * 100),
                "retention": round(mod[1].get('avg_retention', 0) * 100),
                "sessions": mod[1].get('sessions_count', 0)
            }
            for mod in sorted_modalities[:2]
            if mod[1].get('sessions_count', 0) > 0
        ]

        # Find struggling modalities
        struggling = [
            mod[0]
            for mod in sorted_modalities
            if mod[1].get('effectiveness_score', 1) < 0.6
            and mod[1].get('sessions_count', 0) > 1
        ]

        # Build recommendations
        recommendations = []

        if patterns.get('optimal_session_length'):
            recommendations.append(
                f"Ideal session length: {patterns['optimal_session_length']} minutes"
            )

        if patterns.get('best_time_of_day'):
            recommendations.append(
                f"Best learning time: {patterns['best_time_of_day']}"
            )

        if patterns.get('learns_by_doing'):
            recommendations.append("You learn best by doing - we'll prioritize interactive exercises")

        if patterns.get('prefers_stories'):
            recommendations.append("You retain information better with real-world stories")

        return {
            "status": "discovered",
            "best_modalities": best_modalities,
            "struggling_with": struggling,
            "cognitive_patterns": patterns,
            "recommendations": recommendations,
            "total_sessions": sum(m[1].get('sessions_count', 0) for m in prefs.items())
        }
