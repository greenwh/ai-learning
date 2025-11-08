"""
AI Tutor Engine
Provides conversational interface for learning and Q&A
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database.models import (
    LearningSession, ChatMessage, Module, LearningProfile
)
from backend.ai import ai_provider_manager, TaskType


class TutorEngine:
    """
    Conversational AI tutor with context awareness
    """

    def __init__(self, db: Session):
        self.db = db

    async def chat(
        self,
        session_id: str,
        user_message: str
    ) -> str:
        """
        Process user message and generate tutor response

        Args:
            session_id: Learning session ID
            user_message: User's message

        Returns:
            AI tutor's response
        """
        # Get session context
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).first()

        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Get conversation history
        conversation_history = self._get_conversation_history(session_id)

        # Build context-aware system prompt
        system_prompt = self._build_tutor_prompt(session)

        # Record user message
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=user_message
        )
        self.db.add(user_msg)
        self.db.commit()

        # Generate AI response
        provider = ai_provider_manager.select_provider(TaskType.TUTOR_RESPONSE)

        # Prepare conversation history for AI
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history
        ]
        messages.append({"role": "user", "content": user_message})

        response_text = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_message,
            max_tokens=500,
            temperature=0.7,
            conversation_history=messages[:-1]  # Don't include the current message twice
        )

        # Record AI response
        ai_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=response_text
        )
        self.db.add(ai_msg)

        # Update session metrics (question asked)
        session.questions_asked = (session.questions_asked or 0) + 1

        self.db.commit()

        return response_text

    def _get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ChatMessage]:
        """Get recent conversation history"""
        return self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(
            ChatMessage.timestamp.desc()
        ).limit(limit).all()[::-1]  # Reverse to chronological order

    def _build_tutor_prompt(self, session: LearningSession) -> str:
        """Build context-aware system prompt for the tutor"""
        # Get module information
        module = self.db.query(Module).filter(
            Module.module_id == session.module_id
        ).first()

        # Get user's learning profile
        profile = self.db.query(LearningProfile).filter(
            LearningProfile.user_id == session.user_id
        ).first()

        # Get user preferences
        preferences = {}
        if profile and profile.cognitive_patterns:
            preferences = profile.cognitive_patterns

        # Get the generated lesson content from session
        lesson_content = ""
        if session.session_context and 'generated_content' in session.session_context:
            lesson_content = session.session_context['generated_content']
            # Truncate if too long (keep first 4000 chars for context)
            if len(lesson_content) > 4000:
                lesson_content = lesson_content[:4000] + "...\n\n[Content truncated for context window]"

        # Build system prompt
        prompt = f"""You are an expert tutor helping someone learn about {module.title if module else 'investing'}.

CURRENT LEARNING CONTEXT:
- Topic: {module.title if module else 'General finance concepts'}
- Learning Objectives: {', '.join(module.learning_objectives) if module else 'Understanding fundamentals'}
- Current Modality: {session.modality_used}

LESSON CONTENT THEY'RE VIEWING:
{lesson_content if lesson_content else "No specific lesson content available"}

STUDENT PROFILE:
- Learning Style: {session.modality_used}"""

        if preferences.get('learns_by_doing'):
            prompt += "\n- Learns best through hands-on practice and real examples"
        if preferences.get('asks_why_questions'):
            prompt += "\n- Tends to ask 'why' questions - values deep understanding"
        if preferences.get('needs_concrete_examples'):
            prompt += "\n- Benefits from concrete, real-world examples"

        prompt += """

YOUR ROLE:
1. Answer questions clearly and concisely
2. Relate answers to the current lesson context
3. Use examples that match their learning style
4. Encourage them to think deeper with follow-up questions
5. Check understanding without making it feel like a quiz
6. Be encouraging and patient

GUIDELINES:
- Keep responses conversational and friendly
- Aim for 2-4 paragraphs per response
- Use concrete examples from real companies when relevant
- If they're confused, try explaining a different way
- Celebrate insights and good questions
- Gently correct misconceptions without being negative

Remember: You're a supportive tutor, not just an answer machine. Help them truly understand, not just memorize."""

        return prompt

    async def generate_comprehension_check(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Generate a casual comprehension check question

        Args:
            session_id: Learning session ID

        Returns:
            Dictionary with question and acceptable answer types
        """
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).first()

        if not session:
            raise ValueError(f"Session {session_id} not found")

        module = self.db.query(Module).filter(
            Module.module_id == session.module_id
        ).first()

        # Build prompt for generating a comprehension check
        system_prompt = f"""You are creating a casual comprehension check for a lesson on {module.title if module else 'finance'}.

This should NOT feel like a test. Make it conversational, like you're just checking if they got the main idea.

Create a question that:
1. Checks understanding of a key concept
2. Feels natural and conversational
3. Can be answered in their own words
4. Has multiple acceptable answer types

Format your response as a natural question, like:
"So, if you were explaining this to a friend, how would you describe...?"
"What do you think is the main reason why...?"
"If you saw [scenario], what might that tell you?"

Keep it casual and encouraging."""

        user_prompt = f"""Generate a comprehension check question for a lesson on: {module.title if module else 'stock fundamentals'}

The lesson objectives were:
{chr(10).join(f"- {obj}" for obj in (module.learning_objectives if module else ['Understanding basics']))}

Generate one conversational question that checks if they understood the core concept."""

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        question = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=150,
            temperature=0.8
        )

        return {
            "question": question.strip(),
            "session_id": session_id,
            "type": "conversational"
        }

    async def evaluate_comprehension_response(
        self,
        session_id: str,
        user_response: str
    ) -> Dict[str, Any]:
        """
        Evaluate user's response to comprehension check

        Args:
            session_id: Session ID
            user_response: User's answer

        Returns:
            Evaluation results with feedback
        """
        session = self.db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).first()

        module = self.db.query(Module).filter(
            Module.module_id == session.module_id
        ).first()

        # Build evaluation prompt
        system_prompt = f"""You are evaluating a student's understanding of {module.title if module else 'finance concepts'}.

Learning objectives were:
{chr(10).join(f"- {obj}" for obj in (module.learning_objectives if module else ['Understanding basics']))}

Your task:
1. Evaluate if they understood the core concept (0-1 score)
2. Provide encouraging feedback
3. Gently correct any misconceptions
4. Suggest what to review if needed

Be supportive and constructive. Focus on what they got right, then help with what they missed.

Respond in this format:
SCORE: [0.0 to 1.0]
FEEDBACK: [Your encouraging feedback and corrections]"""

        user_prompt = f"""The student's answer was:

"{user_response}"

Evaluate their understanding."""

        provider = ai_provider_manager.select_provider(TaskType.QUICK_QA)
        evaluation = await ai_provider_manager.generate_content(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=300,
            temperature=0.6
        )

        # Parse response
        score = 0.7  # Default
        feedback = evaluation

        if "SCORE:" in evaluation:
            parts = evaluation.split("FEEDBACK:", 1)
            if len(parts) == 2:
                try:
                    score_text = parts[0].replace("SCORE:", "").strip()
                    score = float(score_text)
                    feedback = parts[1].strip()
                except:
                    pass

        return {
            "score": score,
            "feedback": feedback,
            "passed": score >= 0.6
        }
