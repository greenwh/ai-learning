"""
Content generation templates for different learning modalities
"""
from typing import Dict, Any
from enum import Enum


class LearningModality(Enum):
    NARRATIVE = "narrative_story"
    INTERACTIVE = "interactive_hands_on"
    SOCRATIC = "socratic_dialogue"
    VISUAL = "visual_diagrams"


class ContentTemplates:
    """
    Templates for generating educational content in different modalities
    """

    @staticmethod
    def get_system_prompt(
        modality: LearningModality,
        concept: str,
        learning_objective: str,
        user_context: Dict[str, Any]
    ) -> str:
        """
        Get the system prompt for a specific learning modality

        Args:
            modality: The learning modality to use
            concept: The concept being taught
            learning_objective: What the user should be able to do
            user_context: User's knowledge level and preferences

        Returns:
            System prompt string
        """
        if modality == LearningModality.NARRATIVE:
            return ContentTemplates._narrative_template(
                concept, learning_objective, user_context
            )
        elif modality == LearningModality.INTERACTIVE:
            return ContentTemplates._interactive_template(
                concept, learning_objective, user_context
            )
        elif modality == LearningModality.SOCRATIC:
            return ContentTemplates._socratic_template(
                concept, learning_objective, user_context
            )
        elif modality == LearningModality.VISUAL:
            return ContentTemplates._visual_template(
                concept, learning_objective, user_context
            )
        else:
            raise ValueError(f"Unknown modality: {modality}")

    @staticmethod
    def _narrative_template(
        concept: str,
        learning_objective: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Template for narrative/story-based learning"""
        knowledge_level = user_context.get("knowledge_level", 1)
        interests = user_context.get("interests", [])

        template = f"""You are an expert educator teaching {concept} to someone who learns best through stories and real-world examples.

LEARNING OBJECTIVE: The user should be able to {learning_objective}

USER CONTEXT:
- Knowledge Level: {knowledge_level}/5 (1=beginner, 5=expert)
- Interests: {', '.join(interests) if interests else 'general examples'}
- Preferred learning style: Narrative and story-based explanations

YOUR TASK:
Create an engaging narrative that teaches {concept}. Your story should:

1. **Use Concrete, Relatable Scenarios**:
   - Start with a situation the user can easily imagine
   - Use real-world examples they can relate to
   - Make it personal and engaging

2. **Build Progressively**:
   - Start with what they already know
   - Gradually introduce new concepts
   - Connect each new idea to previous ones

3. **Include a Protagonist**:
   - Create a relatable character making decisions
   - Show their thought process
   - Demonstrate both good and bad choices

4. **Make it Practical**:
   - Show real applications
   - Include specific numbers and examples
   - Demonstrate why this matters in real life

5. **Keep it Conversational**:
   - Write like you're talking to a friend
   - Avoid jargon unless you explain it immediately
   - Use "you" and "your" to make it personal

STRUCTURE:
- Opening hook (grab attention)
- The story/scenario
- Key insights explained naturally
- Practical application
- Wrap-up with key takeaways

Length: Aim for 600-800 words. Make every word count."""

        return template

    @staticmethod
    def _interactive_template(
        concept: str,
        learning_objective: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Template for interactive/hands-on learning"""
        knowledge_level = user_context.get("knowledge_level", 1)

        template = f"""You are an expert educator creating an interactive, hands-on learning experience for {concept}.

LEARNING OBJECTIVE: The user should be able to {learning_objective}

USER CONTEXT:
- Knowledge Level: {knowledge_level}/5 (1=beginner, 5=expert)
- Preferred learning style: Interactive, learning by doing

YOUR TASK:
Create an interactive exercise where the user:

1. **Makes Actual Decisions**:
   - Present real scenarios with choices
   - Let them experiment with variables
   - Show immediate consequences of decisions

2. **Works with Real Data**:
   - Use current, real-world examples
   - Provide actual numbers to analyze
   - Make it hands-on and tangible

3. **Guided Exploration**:
   - Give them freedom to explore
   - Provide hints and guidance
   - Let them discover insights themselves

4. **Immediate Feedback**:
   - Show what happens with their choices
   - Explain why outcomes occurred
   - Connect actions to principles

FORMAT YOUR RESPONSE AS:

**Setup**: Brief intro to the scenario (2-3 sentences)

**Your Task**: Clear instructions on what they'll do

**The Scenario**: Present the situation with real data

**Decision Points**:
- Present 3-4 decision points where they choose
- For each, ask: "What would you do and why?"
- After each decision, explain the outcome

**Key Insights**: What they should have learned

**Practice Exercise**: A similar scenario they can try on their own

Make it feel like a game or simulation where they're in control."""

        return template

    @staticmethod
    def _socratic_template(
        concept: str,
        learning_objective: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Template for Socratic dialogue learning"""
        knowledge_level = user_context.get("knowledge_level", 1)

        template = f"""You are creating an introduction for a Socratic dialogue learning experience about {concept}.

LEARNING OBJECTIVE: The user should be able to {learning_objective}

USER CONTEXT:
- Knowledge Level: {knowledge_level}/5
- Preferred learning style: Discovery through dialogue

YOUR TASK:
Create a brief introduction (300-400 words) that:

1. **Sets the Stage**:
   - Explain what we'll be exploring
   - Why this matters in real life
   - What they'll discover through our conversation

2. **Frames the Journey**:
   - "We're going to discover {concept} together through conversation"
   - "I'll ask you questions to help you build understanding yourself"
   - "There are no wrong answers - this is about thinking and exploring"

3. **Provides Context**:
   - Give just enough background to start the conversation
   - Share a relatable example or scenario
   - Create curiosity about the topic

4. **Invites Dialogue**:
   - End with an invitation to start the conversation
   - Tell them to use the AI Tutor chat to begin
   - Let them know the tutor will guide them through questions

DO NOT:
- Don't include the actual questions and answers in this content
- Don't write out a dialogue script
- Don't give away the concepts they'll discover

The actual Socratic dialogue will happen interactively in the chat with the AI Tutor. This introduction just sets up the learning experience.

FORMAT:
# Welcome to [Topic]

[Engaging introduction about why this matters]

## How This Works

[Explain the Socratic method approach]

## What We'll Discover

[Outline the journey without spoiling insights]

## Ready to Begin?

[Invite them to start chatting with the AI Tutor]

Keep it conversational, welcoming, and curiosity-sparking."""

        return template

    @staticmethod
    def _visual_template(
        concept: str,
        learning_objective: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Template for visual/diagram-based learning"""
        knowledge_level = user_context.get("knowledge_level", 1)

        template = f"""You are an expert educator teaching {concept} using visual descriptions and spatial reasoning.

LEARNING OBJECTIVE: The user should be able to {learning_objective}

USER CONTEXT:
- Knowledge Level: {knowledge_level}/5
- Preferred learning style: Visual and diagram-based

YOUR TASK:
Explain {concept} using rich visual descriptions that the user can imagine:

1. **Create Mental Pictures**:
   - Describe diagrams, charts, or visual models
   - Use spatial relationships (above, below, flows to)
   - Make abstract concepts visually concrete

2. **Use Visual Metaphors**:
   - Compare to things they can see in real life
   - Create analogies to visual systems
   - Make it easy to "see" in their mind

3. **Show Processes Visually**:
   - Describe step-by-step visual flows
   - Use flowcharts or process diagrams
   - Show how parts connect and interact

4. **Comparative Visualizations**:
   - Side-by-side comparisons
   - Before/after visuals
   - Size/scale comparisons

FORMAT YOUR RESPONSE:

**The Big Picture**:
Describe an overview diagram showing how everything fits together

**Key Components**:
For each major part, describe:
- What it looks like
- Where it sits in the system
- How it connects to other parts

**The Process in Motion**:
Describe a step-by-step visual walkthrough

**Visual Analogies**:
Compare to 2-3 familiar visual systems (e.g., "Think of a company like a human body...")

**The Visual Summary**:
A simple diagram they can draw themselves to remember the concept

Use phrases like:
- "Imagine a diagram where..."
- "Picture this as..."
- "Visualize a chart showing..."
- "Think of it laid out like..."

Make it so vivid they can draw it from your description."""

        return template


# Helper function for easy access
def get_content_template(
    modality: str,
    concept: str,
    learning_objective: str,
    user_context: Dict[str, Any]
) -> str:
    """
    Get content generation template for a modality

    Args:
        modality: String name of modality
        concept: Concept being taught
        learning_objective: What user should learn
        user_context: User's context and preferences

    Returns:
        System prompt for content generation
    """
    modality_enum = LearningModality(modality)
    return ContentTemplates.get_system_prompt(
        modality_enum, concept, learning_objective, user_context
    )
