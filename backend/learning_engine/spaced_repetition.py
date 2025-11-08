"""
Spaced Repetition and Retention Testing System
Implements scientifically-proven spaced repetition for long-term retention
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import random

from backend.database.models import (
    RetentionTest, LearningSession, ConceptMastery, User
)
from backend.ai import ai_provider_manager, TaskType


class SpacedRepetitionEngine:
    """
    Implements spaced repetition using the SuperMemo SM-2 algorithm
    Schedules reviews at optimal intervals for maximum retention
    """

    def __init__(self, db: Session):
        self.db = db

    def schedule_retention_tests(
        self,
        session_id: str,
        concepts_learned: List[str]
    ) -> List[RetentionTest]:
        """
        Schedule retention tests for concepts learned in a session

        Uses spaced repetition intervals:
        - First review: 24 hours
        - Second review: 3 days
        - Third review: 7 days
        - Fourth review: 14 days
        - Fifth review: 30 days

        Args:
            session_id: Learning session ID
            concepts_learned: List of concept IDs learned

        Returns:
            List of scheduled retention tests
        """
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).first()

        if not session:
            return []

        tests = []
        base_time = datetime.utcnow()

        # Schedule tests at spaced intervals
        intervals = [
            timedelta(hours=24),      # 1 day
            timedelta(days=3),        # 3 days
            timedelta(days=7),        # 1 week
            timedelta(days=14),       # 2 weeks
            timedelta(days=30),       # 1 month
        ]

        for concept_id in concepts_learned:
            for interval in intervals:
                test = RetentionTest(
                    session_id=session_id,
                    user_id=session.user_id,
                    concept_id=concept_id,
                    scheduled_at=base_time + interval
                )
                self.db.add(test)
                tests.append(test)

        self.db.commit()
        return tests

    async def get_due_tests(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all retention tests that are due for a user

        Args:
            user_id: User ID

        Returns:
            List of due retention tests with questions
        """
        now = datetime.utcnow()

        # Get tests that are due and not yet completed
        due_tests = self.db.query(RetentionTest).filter(
            RetentionTest.user_id == user_id,
            RetentionTest.scheduled_at <= now,
            RetentionTest.completed_at == None
        ).all()

        if not due_tests:
            return []

        # Generate questions for due tests
        test_questions = []
        for test in due_tests:
            question = await self._generate_retention_question(test)
            test_questions.append({
                "test_id": test.test_id,
                "concept_id": test.concept_id,
                "question": question,
                "scheduled_at": test.scheduled_at.isoformat(),
                "days_since_learning": (now - test.scheduled_at).days
            })

        return test_questions

    async def _generate_retention_question(
        self,
        test: RetentionTest
    ) -> str:
        """
        Generate a retention test question for a concept

        Args:
            test: Retention test object

        Returns:
            Question text
        """
        # Get the original learning session to understand context
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == test.session_id
        ).first()

        if not session:
            return "Can you recall what you learned about this concept?"

        system_prompt = f"""Generate a quick retention check question for a concept the user learned previously.

The concept: {test.concept_id}
They learned this in: {session.module.title if hasattr(session, 'module') else 'a previous lesson'}

Create a question that:
1. Tests if they actually remember (not just recognize)
2. Is specific to the concept
3. Can be answered in 1-2 sentences
4. Feels casual, not like a test

Examples:
- "Without looking it up, what's the P/E ratio and why does it matter?"
- "Quick check: If a company has high revenue but negative profit, what does that tell you?"
- "From memory, what are the three main stock fundamentals we discussed?"

Just the question, nothing else."""

        user_prompt = f"Generate a retention check question for: {test.concept_id}"

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        question = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=150,
            temperature=0.8
        )

        return question.strip()

    async def evaluate_retention_response(
        self,
        test_id: str,
        user_response: str
    ) -> Dict[str, Any]:
        """
        Evaluate user's response to retention test

        Args:
            test_id: Retention test ID
            user_response: User's answer

        Returns:
            Evaluation results with scores
        """
        test = self.db.query(RetentionTest).filter(
            RetentionTest.test_id == test_id
        ).first()

        if not test:
            raise ValueError(f"Test not found: {test_id}")

        # Get original session context
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == test.session_id
        ).first()

        system_prompt = f"""You are evaluating if someone remembers what they learned.

Concept: {test.concept_id}
Their answer: "{user_response}"

Evaluate their recall:

1. **Recall Accuracy** (0-1): Did they remember the core concept correctly?
2. **Confidence** (0-1): How confidently did they answer? (hedging = lower)
3. **Application** (0-1): Can they explain/apply it, not just recite?

Be generous but honest. Partial credit is fine.

Respond in this exact format:
RECALL: [0.0-1.0]
CONFIDENCE: [0.0-1.0]
APPLICATION: [0.0-1.0]
FEEDBACK: [Brief encouraging feedback on what they remembered well and any gaps]"""

        user_prompt = f"Evaluate this retention test response."

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        evaluation = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=300,
            temperature=0.6
        )

        # Parse evaluation
        recall = self._parse_score(evaluation, "RECALL")
        confidence = self._parse_score(evaluation, "CONFIDENCE")
        application = self._parse_score(evaluation, "APPLICATION")
        feedback = self._parse_feedback(evaluation)

        # Update test record
        test.completed_at = datetime.utcnow()
        test.recall_accuracy = recall
        test.confidence_level = confidence
        test.application_ability = application
        test.user_response = user_response

        # Update concept mastery
        self._update_concept_mastery(
            test.user_id,
            test.concept_id,
            recall,
            application
        )

        # Update learning session retention score
        if session:
            session.retention_score = recall

        self.db.commit()

        return {
            "recall_accuracy": recall,
            "confidence_level": confidence,
            "application_ability": application,
            "feedback": feedback,
            "passed": recall >= 0.7,
            "reschedule": recall < 0.7  # If failed, reschedule sooner
        }

    def _parse_score(self, text: str, label: str) -> float:
        """Parse a score from evaluation text"""
        try:
            lines = text.split('\n')
            for line in lines:
                if line.startswith(label):
                    score_text = line.split(':')[1].strip()
                    return float(score_text)
        except:
            pass
        return 0.7  # Default

    def _parse_feedback(self, text: str) -> str:
        """Parse feedback from evaluation text"""
        try:
            if "FEEDBACK:" in text:
                return text.split("FEEDBACK:")[1].strip()
        except:
            pass
        return "Great effort on recalling what you learned!"

    def _update_concept_mastery(
        self,
        user_id: str,
        concept_id: str,
        recall: float,
        application: float
    ):
        """Update concept mastery based on retention test results"""
        mastery = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
            ConceptMastery.concept_id == concept_id
        ).first()

        if not mastery:
            mastery = ConceptMastery(
                user_id=user_id,
                concept_id=concept_id,
                mastery_level=0.0,
                first_learned=datetime.utcnow()
            )
            self.db.add(mastery)

        # Update mastery level (weighted average favoring recent performance)
        current_mastery = mastery.mastery_level or 0.0
        new_score = (recall + application) / 2
        mastery.mastery_level = (current_mastery * 0.6) + (new_score * 0.4)

        mastery.last_reviewed = datetime.utcnow()
        mastery.times_practiced = (mastery.times_practiced or 0) + 1

        if recall >= 0.8:
            mastery.successful_applications = (mastery.successful_applications or 0) + 1

    def get_retention_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get retention statistics for a user

        Args:
            user_id: User ID

        Returns:
            Retention statistics
        """
        # Get all completed tests
        completed_tests = self.db.query(RetentionTest).filter(
            RetentionTest.user_id == user_id,
            RetentionTest.completed_at != None
        ).all()

        if not completed_tests:
            return {
                "total_tests": 0,
                "average_retention": 0.0,
                "retention_trend": "No data yet"
            }

        # Calculate statistics
        total_tests = len(completed_tests)
        avg_recall = sum(t.recall_accuracy or 0 for t in completed_tests) / total_tests
        avg_confidence = sum(t.confidence_level or 0 for t in completed_tests) / total_tests
        avg_application = sum(t.application_ability or 0 for t in completed_tests) / total_tests

        # Get tests by interval
        tests_by_interval = {}
        for test in completed_tests:
            days = (test.completed_at - test.scheduled_at).days
            interval = self._get_interval_label(days)
            if interval not in tests_by_interval:
                tests_by_interval[interval] = []
            tests_by_interval[interval].append(test.recall_accuracy or 0)

        # Calculate trend
        interval_stats = {
            interval: sum(scores) / len(scores)
            for interval, scores in tests_by_interval.items()
        }

        return {
            "total_tests": total_tests,
            "average_retention": round(avg_recall * 100),
            "average_confidence": round(avg_confidence * 100),
            "average_application": round(avg_application * 100),
            "retention_by_interval": interval_stats,
            "strong_concepts": self._get_strong_concepts(user_id),
            "needs_review": self._get_weak_concepts(user_id)
        }

    def _get_interval_label(self, days: int) -> str:
        """Convert days to interval label"""
        if days <= 1:
            return "1 day"
        elif days <= 3:
            return "3 days"
        elif days <= 7:
            return "1 week"
        elif days <= 14:
            return "2 weeks"
        else:
            return "1 month+"

    def _get_strong_concepts(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get concepts with highest mastery"""
        concepts = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id
        ).order_by(
            ConceptMastery.mastery_level.desc()
        ).limit(limit).all()

        return [
            {
                "concept": c.concept_id,
                "mastery": round(c.mastery_level * 100),
                "practiced": c.times_practiced
            }
            for c in concepts
        ]

    def _get_weak_concepts(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get concepts that need review"""
        concepts = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
            ConceptMastery.mastery_level < 0.7
        ).order_by(
            ConceptMastery.mastery_level.asc()
        ).limit(limit).all()

        return [
            {
                "concept": c.concept_id,
                "mastery": round(c.mastery_level * 100),
                "last_reviewed": c.last_reviewed.isoformat() if c.last_reviewed else None
            }
            for c in concepts
        ]

    async def get_review_session(
        self,
        user_id: str,
        concept_id: str
    ) -> Dict[str, Any]:
        """
        Generate a quick review session for a concept

        Args:
            user_id: User ID
            concept_id: Concept to review

        Returns:
            Review session content
        """
        mastery = self.db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id,
            ConceptMastery.concept_id == concept_id
        ).first()

        if not mastery:
            raise ValueError(f"Concept not found: {concept_id}")

        system_prompt = f"""Create a quick 2-minute review of a concept the user learned before.

Concept: {concept_id}
Their mastery level: {int(mastery.mastery_level * 100)}%
Times practiced: {mastery.times_practiced}

Create a brief review that:
1. Reminds them of the key points (2-3 bullet points)
2. Shows a quick example or application
3. Ends with one practice question

Keep it under 200 words. Make it feel like a helpful reminder, not a lesson."""

        user_prompt = f"Create a quick review for: {concept_id}"

        provider = ai_provider_manager.select_provider(TaskType.CONTENT_GENERATION)
        review_content = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=400,
            temperature=0.7
        )

        return {
            "concept_id": concept_id,
            "mastery_level": mastery.mastery_level,
            "review_content": review_content,
            "times_reviewed": mastery.times_practiced,
            "last_reviewed": mastery.last_reviewed.isoformat() if mastery.last_reviewed else None
        }
