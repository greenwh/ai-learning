"""
Smart Recommendations Engine
Suggests what to learn next based on user's style, progress, and interests
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from backend.database.models import (
    Module, ModuleProgress, LearningProfile, LearningSession,
    ConceptMastery, User
)


class RecommendationEngine:
    """
    Generates personalized recommendations for what to learn next
    """

    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized learning recommendations

        Args:
            user_id: User ID
            limit: Maximum number of recommendations

        Returns:
            List of recommended modules/topics with reasons
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return []

        profile = self.db.query(LearningProfile).filter(
            LearningProfile.user_id == user_id
        ).first()

        # Get user's learning history
        completed_modules = self._get_completed_modules(user_id)
        in_progress_modules = self._get_in_progress_modules(user_id)
        weak_concepts = self._get_weak_concepts(user_id)

        recommendations = []

        # 1. Continue in-progress modules
        for module_id in in_progress_modules[:2]:
            module = self.db.query(Module).filter(
                Module.module_id == module_id
            ).first()
            if module:
                recommendations.append({
                    "type": "continue",
                    "module_id": module.module_id,
                    "title": module.title,
                    "reason": "You're making progress - let's finish this!",
                    "priority": "high",
                    "estimated_time": module.estimated_time
                })

        # 2. Review weak concepts
        if weak_concepts:
            recommendations.append({
                "type": "review",
                "concepts": weak_concepts[:3],
                "reason": "Quick review to strengthen retention",
                "priority": "medium",
                "estimated_time": 10
            })

        # 3. Next logical modules (based on prerequisites)
        next_modules = self._get_next_logical_modules(user_id, completed_modules)
        for module in next_modules[:2]:
            recommendations.append({
                "type": "new",
                "module_id": module.module_id,
                "title": module.title,
                "reason": f"Natural progression from {self._get_prerequisite_title(module, completed_modules)}",
                "priority": "high",
                "estimated_time": module.estimated_time
            })

        # 4. Popular in same domain
        if completed_modules or in_progress_modules:
            popular = self._get_popular_in_domain(user_id)
            if popular:
                recommendations.append({
                    "type": "explore",
                    "module_id": popular.module_id,
                    "title": popular.title,
                    "reason": "Popular topic in your learning domain",
                    "priority": "low",
                    "estimated_time": popular.estimated_time
                })

        # 5. Fill knowledge gaps
        gaps = self._identify_knowledge_gaps(user_id)
        if gaps:
            recommendations.append({
                "type": "fill_gap",
                "topic": gaps[0]["topic"],
                "reason": f"Strengthen your foundation in {gaps[0]['area']}",
                "priority": "medium",
                "estimated_time": 15
            })

        return recommendations[:limit]

    def _get_completed_modules(self, user_id: str) -> List[str]:
        """Get list of completed module IDs"""
        progress = self.db.query(ModuleProgress).filter(
            ModuleProgress.user_id == user_id,
            ModuleProgress.status.in_(["completed", "mastered"])
        ).all()

        return [p.module_id for p in progress]

    def _get_in_progress_modules(self, user_id: str) -> List[str]:
        """Get list of in-progress module IDs"""
        progress = self.db.query(ModuleProgress).filter(
            ModuleProgress.user_id == user_id,
            ModuleProgress.status == "in_progress"
        ).all()

        return [p.module_id for p in progress]

    def _get_weak_concepts(self, user_id: str) -> List[str]:
        """Get concepts that need review"""
        concepts = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
            ConceptMastery.mastery_level < 0.7
        ).limit(5).all()

        return [c.concept_id for c in concepts]

    def _get_next_logical_modules(
        self,
        user_id: str,
        completed: List[str]
    ) -> List[Module]:
        """Find modules whose prerequisites are met"""
        all_modules = self.db.query(Module).all()
        next_modules = []

        for module in all_modules:
            if module.module_id in completed:
                continue

            # Check if prerequisites are met
            prereqs = module.prerequisites or []
            if all(p in completed for p in prereqs):
                next_modules.append(module)

        # Sort by difficulty
        return sorted(next_modules, key=lambda m: m.difficulty_level)[:3]

    def _get_prerequisite_title(self, module: Module, completed: List[str]) -> str:
        """Get title of the prerequisite module"""
        if not module.prerequisites or not module.prerequisites:
            return "your previous learning"

        prereq_id = module.prerequisites[0]
        prereq = self.db.query(Module).filter(
            Module.module_id == prereq_id
        ).first()

        return prereq.title if prereq else "your previous learning"

    def _get_popular_in_domain(self, user_id: str) -> Optional[Module]:
        """Get popular module in user's domain"""
        # Get user's most common domain
        sessions = self.db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).all()

        if not sessions:
            return None

        # Find domain they study most
        domains = {}
        for session in sessions:
            module = self.db.query(Module).filter(
                Module.module_id == session.module_id
            ).first()
            if module:
                domain = module.domain
                domains[domain] = domains.get(domain, 0) + 1

        if not domains:
            return None

        most_common_domain = max(domains.items(), key=lambda x: x[1])[0]

        # Get a module in that domain they haven't done
        completed = self._get_completed_modules(user_id)
        in_progress = self._get_in_progress_modules(user_id)
        excluded = set(completed + in_progress)

        modules = self.db.query(Module).filter(
            Module.domain == most_common_domain
        ).all()

        available = [m for m in modules if m.module_id not in excluded]
        return random.choice(available) if available else None

    def _identify_knowledge_gaps(self, user_id: str) -> List[Dict[str, str]]:
        """Identify gaps in user's knowledge"""
        # Get concepts with low mastery
        weak_concepts = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
            ConceptMastery.mastery_level < 0.6
        ).all()

        if not weak_concepts:
            return []

        # Group by area (simplified - would use more sophisticated categorization)
        gaps = []
        for concept in weak_concepts[:3]:
            gaps.append({
                "topic": concept.concept_id,
                "area": concept.concept_id.split('_')[0] if '_' in concept.concept_id else "core concepts",
                "mastery": concept.mastery_level
            })

        return gaps

    def get_learning_streak(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate user's learning streak

        Args:
            user_id: User ID

        Returns:
            Streak information
        """
        sessions = self.db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.completed_at != None
        ).order_by(
            LearningSession.completed_at.desc()
        ).all()

        if not sessions:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "total_days": 0,
                "last_active": None
            }

        # Calculate current streak
        current_streak = 0
        today = datetime.utcnow().date()
        check_date = today

        session_dates = set(s.completed_at.date() for s in sessions)

        # Count backwards from today
        while check_date in session_dates or (today - check_date).days == 0:
            if check_date in session_dates:
                current_streak += 1
            check_date -= timedelta(days=1)
            if current_streak == 0 and check_date < today - timedelta(days=1):
                break

        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        prev_date = None

        for date in sorted(session_dates):
            if prev_date is None or (date - prev_date).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
            prev_date = date

        return {
            "current_streak": current_streak,
            "longest_streak": max(longest_streak, current_streak),
            "total_days": len(session_dates),
            "last_active": sessions[0].completed_at.isoformat() if sessions else None,
            "streak_status": self._get_streak_status(current_streak)
        }

    def _get_streak_status(self, streak: int) -> str:
        """Get motivational message for streak"""
        if streak == 0:
            return "Start your streak today!"
        elif streak == 1:
            return "Great start! Come back tomorrow to continue."
        elif streak < 7:
            return f"{streak} days strong! Keep it up!"
        elif streak < 30:
            return f"Amazing {streak}-day streak! You're on fire! 🔥"
        else:
            return f"Incredible {streak}-day streak! You're a learning machine! 🚀"

    def get_achievement_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Get progress towards achievements/milestones

        Args:
            user_id: User ID

        Returns:
            Achievement progress
        """
        sessions = self.db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.completed_at != None
        ).all()

        completed_modules = len(self._get_completed_modules(user_id))
        total_time = sum(s.duration or 0 for s in sessions)

        achievements = {
            "sessions": {
                "current": len(sessions),
                "milestones": [
                    {"target": 1, "label": "First Session", "unlocked": len(sessions) >= 1},
                    {"target": 10, "label": "Getting Started", "unlocked": len(sessions) >= 10},
                    {"target": 25, "label": "Committed Learner", "unlocked": len(sessions) >= 25},
                    {"target": 50, "label": "Dedicated Student", "unlocked": len(sessions) >= 50},
                    {"target": 100, "label": "Century Club", "unlocked": len(sessions) >= 100},
                ]
            },
            "modules": {
                "current": completed_modules,
                "milestones": [
                    {"target": 1, "label": "First Module", "unlocked": completed_modules >= 1},
                    {"target": 5, "label": "Knowledge Seeker", "unlocked": completed_modules >= 5},
                    {"target": 10, "label": "Scholar", "unlocked": completed_modules >= 10},
                    {"target": 25, "label": "Expert Learner", "unlocked": completed_modules >= 25},
                ]
            },
            "time": {
                "current": total_time,
                "milestones": [
                    {"target": 60, "label": "First Hour", "unlocked": total_time >= 60},
                    {"target": 300, "label": "5 Hours", "unlocked": total_time >= 300},
                    {"target": 600, "label": "10 Hours", "unlocked": total_time >= 600},
                    {"target": 1200, "label": "20 Hours", "unlocked": total_time >= 1200},
                ]
            }
        }

        return achievements

    def get_next_session_suggestion(self, user_id: str) -> Dict[str, Any]:
        """
        Get a specific suggestion for the next learning session

        Args:
            user_id: User ID

        Returns:
            Session suggestion
        """
        # Get recent activity
        recent_sessions = self.db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).order_by(
            LearningSession.created_at.desc()
        ).limit(3).all()

        if not recent_sessions:
            return {
                "suggestion": "Start with a beginner topic in your area of interest",
                "type": "new_user",
                "estimated_time": 15
            }

        # Check when they last learned
        last_session = recent_sessions[0]
        hours_since = (datetime.utcnow() - last_session.created_at).total_seconds() / 3600

        # If been a while, suggest review
        if hours_since > 48:
            return {
                "suggestion": "Welcome back! Let's review what you learned before continuing.",
                "type": "review",
                "estimated_time": 10
            }

        # Check if they have in-progress modules
        in_progress = self._get_in_progress_modules(user_id)
        if in_progress:
            module = self.db.query(Module).filter(
                Module.module_id == in_progress[0]
            ).first()
            return {
                "suggestion": f"Continue with: {module.title if module else 'your current module'}",
                "type": "continue",
                "module_id": in_progress[0],
                "estimated_time": module.estimated_time if module else 15
            }

        # Suggest new topic
        recommendations = self.get_recommendations(user_id, limit=1)
        if recommendations:
            rec = recommendations[0]
            return {
                "suggestion": rec.get("title", rec.get("topic", "Try something new")),
                "type": rec["type"],
                "reason": rec["reason"],
                "estimated_time": rec["estimated_time"]
            }

        return {
            "suggestion": "Explore a new topic that interests you",
            "type": "explore",
            "estimated_time": 15
        }
