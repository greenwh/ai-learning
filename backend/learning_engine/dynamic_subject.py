"""
Dynamic Subject Creation and Knowledge Assessment
Allows users to learn about ANY topic without pre-loaded modules
"""
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import json

from backend.database.models import Module, User, LearningProfile
from backend.ai import ai_provider_manager, TaskType


class DynamicSubjectEngine:
    """
    Creates learning content dynamically for any subject
    Assesses prior knowledge through conversation
    """

    def __init__(self, db: Session):
        self.db = db

    async def assess_knowledge(
        self,
        user_id: str,
        subject: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Conduct conversational knowledge assessment

        Args:
            user_id: User ID
            subject: What they want to learn about
            conversation_history: Previous Q&A if continuing assessment

        Returns:
            Dictionary with assessment results or next question
        """
        if not conversation_history:
            # First interaction - get the opening question
            return await self._start_assessment(subject)

        # Continue assessment based on answers
        return await self._continue_assessment(subject, conversation_history)

    async def _start_assessment(self, subject: str) -> Dict[str, Any]:
        """Start the knowledge assessment with opening question"""

        system_prompt = f"""You are assessing someone's current knowledge about: {subject}

Your goal: Quickly understand what they already know through 3-4 natural questions.

GUIDELINES:
1. Start broad: "What do you already know about {subject}?"
2. Based on their answer, ask 1-2 targeted questions to gauge depth
3. Be conversational and encouraging
4. Don't make it feel like a test - make it feel like a chat

After 3-4 questions, you'll have enough to assess their level.

For the FIRST question, respond with ONLY the question text - no introduction, no explanation.
Make it warm and conversational."""

        user_prompt = f"""Generate the opening question to assess knowledge about: {subject}

Just the question, nothing else."""

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        question = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=150,
            temperature=0.8
        )

        return {
            "status": "in_progress",
            "question": question.strip(),
            "questions_asked": 1,
            "assessment_complete": False
        }

    async def _continue_assessment(
        self,
        subject: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Continue assessment or complete it"""

        questions_asked = len([m for m in conversation_history if m['role'] == 'assistant'])

        # After 3 questions, complete the assessment
        if questions_asked >= 3:
            return await self._complete_assessment(subject, conversation_history)

        # Generate next question based on their answers
        system_prompt = f"""You are assessing someone's knowledge about: {subject}

You've asked {questions_asked} question(s) so far. Review their answers and:

1. If they know very little: Ask a basic conceptual question
2. If they know some: Ask about practical application
3. If they know a lot: Ask about nuances or edge cases

Keep it conversational. You need {3 - questions_asked} more question(s) before completing the assessment.

Respond with ONLY the next question - no introduction."""

        user_prompt = "Based on the conversation so far, generate the next assessment question."

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        question = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=150,
            temperature=0.8,
            conversation_history=conversation_history
        )

        return {
            "status": "in_progress",
            "question": question.strip(),
            "questions_asked": questions_asked + 1,
            "assessment_complete": False
        }

    async def _complete_assessment(
        self,
        subject: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Complete the assessment and determine knowledge level"""

        system_prompt = f"""You are completing a knowledge assessment about: {subject}

Review the conversation and determine:

1. **Knowledge Level** (1-5):
   - 1 = Complete beginner, never heard of it
   - 2 = Heard of it, knows very basics
   - 3 = Moderate understanding, some experience
   - 4 = Strong understanding, practical experience
   - 5 = Expert level knowledge

2. **Specific Gaps**: What don't they know yet?

3. **Starting Point**: Where should their learning begin?

4. **Learning Objectives**: What should they learn first? (3-5 specific objectives)

Respond in this exact JSON format:
{{
  "knowledge_level": 1-5,
  "summary": "Brief summary of what they know",
  "gaps": ["Gap 1", "Gap 2", "Gap 3"],
  "starting_point": "Where to begin their learning",
  "learning_objectives": ["Objective 1", "Objective 2", "Objective 3"]
}}

ONLY output valid JSON, nothing else."""

        user_prompt = "Complete the assessment based on the conversation."

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        assessment_json = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=500,
            temperature=0.6,
            conversation_history=conversation_history
        )

        # Parse the JSON response
        try:
            # Clean up the response in case there's extra text
            json_start = assessment_json.find('{')
            json_end = assessment_json.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                assessment_json = assessment_json[json_start:json_end]

            assessment = json.loads(assessment_json)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            assessment = {
                "knowledge_level": 2,
                "summary": "Assessed based on conversation",
                "gaps": ["Core concepts", "Practical application"],
                "starting_point": "Begin with fundamentals",
                "learning_objectives": [
                    f"Understand basic concepts of {subject}",
                    f"Learn practical applications of {subject}",
                    f"Develop working knowledge of {subject}"
                ]
            }

        return {
            "status": "complete",
            "assessment_complete": True,
            "knowledge_level": assessment.get("knowledge_level", 2),
            "summary": assessment.get("summary", ""),
            "gaps": assessment.get("gaps", []),
            "starting_point": assessment.get("starting_point", ""),
            "learning_objectives": assessment.get("learning_objectives", [])
        }

    async def create_dynamic_module(
        self,
        user_id: str,
        subject: str,
        assessment: Dict[str, Any]
    ) -> Module:
        """
        Create a learning module dynamically based on subject and assessment

        Args:
            user_id: User ID
            subject: What they want to learn
            assessment: Results from knowledge assessment

        Returns:
            Created Module object
        """
        # Determine domain and breakdown from subject
        domain_info = await self._classify_subject(subject)

        # Create the module
        module = Module(
            domain=domain_info["domain"],
            subject=domain_info["subject"],
            topic=subject,
            title=self._generate_title(subject, assessment["knowledge_level"]),
            description=self._generate_description(subject, assessment),
            prerequisites=[],  # Dynamic modules have no prerequisites
            learning_objectives=assessment["learning_objectives"],
            difficulty_level=max(1, assessment["knowledge_level"]),
            estimated_time=15,  # Default to 15 minutes
            content_config={
                "dynamic": True,
                "user_id": user_id,
                "subject": subject,
                "knowledge_level": assessment["knowledge_level"],
                "assessment_summary": assessment["summary"],
                "modalities": {
                    "narrative_story": {"enabled": True},
                    "interactive_hands_on": {"enabled": True},
                    "socratic_dialogue": {"enabled": True},
                    "visual_diagrams": {"enabled": True}
                }
            }
        )

        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)

        return module

    async def _classify_subject(self, subject: str) -> Dict[str, str]:
        """Use AI to classify the subject into domain/subject/topic"""

        system_prompt = """Classify a learning subject into categories.

Respond in this exact JSON format:
{
  "domain": "Broad category (Finance, Science, Arts, Technology, etc.)",
  "subject": "Specific subject area"
}

Examples:
- "stock fundamentals" → {"domain": "Finance", "subject": "Stock Market Investing"}
- "photosynthesis" → {"domain": "Science", "subject": "Biology"}
- "React hooks" → {"domain": "Technology", "subject": "Web Development"}

ONLY output valid JSON."""

        user_prompt = f"Classify this subject: {subject}"

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        response = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=100,
            temperature=0.3
        )

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                response = response[json_start:json_end]

            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback
            return {
                "domain": "General Knowledge",
                "subject": subject.title()
            }

    def _generate_title(self, subject: str, knowledge_level: int) -> str:
        """Generate a module title"""
        level_labels = {
            1: "Complete Beginner's Guide",
            2: "Introduction to",
            3: "Understanding",
            4: "Advanced",
            5: "Mastering"
        }

        label = level_labels.get(knowledge_level, "Introduction to")
        return f"{label} {subject.title()}"

    def _generate_description(self, subject: str, assessment: Dict[str, Any]) -> str:
        """Generate module description"""
        starting_point = assessment.get("starting_point", f"learn about {subject}")

        return (
            f"A personalized learning experience about {subject}. "
            f"Based on your current knowledge, we'll {starting_point}. "
            f"This content is dynamically generated just for you."
        )
