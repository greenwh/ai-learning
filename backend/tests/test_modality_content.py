"""
Tests for modality content generation and diversity
"""
import pytest
from backend.ai.content_templates import (
    ContentTemplates, LearningModality, get_content_template
)


def test_all_modalities_have_templates():
    """Test that all modalities have template implementations"""
    for modality in LearningModality:
        template = ContentTemplates.get_system_prompt(
            modality=modality,
            concept="Test Concept",
            learning_objective="Understand the concept",
            user_context={"knowledge_level": 3, "interests": ["test"]}
        )

        assert template is not None, f"No template for {modality.value}"
        assert len(template) > 100, f"Template for {modality.value} is too short"


def test_narrative_template_structure():
    """Test that narrative template has story elements"""
    template = ContentTemplates.get_system_prompt(
        modality=LearningModality.NARRATIVE,
        concept="P/E Ratio",
        learning_objective="Calculate and interpret P/E ratio",
        user_context={"knowledge_level": 2, "interests": ["investing"]}
    )

    # Should mention story-related keywords
    keywords = ["story", "scenario", "example", "narrative", "protagonist"]
    assert any(keyword.lower() in template.lower() for keyword in keywords), \
        "Narrative template should mention story/narrative elements"

    # Should NOT emphasize interaction heavily
    assert template.count("interact") < template.count("story"), \
        "Narrative template should emphasize story over interaction"


def test_interactive_template_structure():
    """Test that interactive template has hands-on elements"""
    template = ContentTemplates.get_system_prompt(
        modality=LearningModality.INTERACTIVE,
        concept="Stock Valuation",
        learning_objective="Evaluate stocks using fundamentals",
        user_context={"knowledge_level": 3, "interests": ["stocks"]}
    )

    # Should mention interactive keywords
    keywords = ["interactive", "hands-on", "decision", "exercise", "practice"]
    assert any(keyword.lower() in template.lower() for keyword in keywords), \
        "Interactive template should mention interactive elements"

    # Should mention user making decisions
    assert "decision" in template.lower() or "choice" in template.lower(), \
        "Interactive template should involve user decisions"


def test_socratic_template_structure():
    """Test that Socratic template has dialogue elements"""
    template = ContentTemplates.get_system_prompt(
        modality=LearningModality.SOCRATIC,
        concept="Market Efficiency",
        learning_objective="Understand efficient market hypothesis",
        user_context={"knowledge_level": 4, "interests": ["economics"]}
    )

    # Should mention dialogue/question keywords
    keywords = ["question", "dialogue", "conversation", "discover", "socratic"]
    assert any(keyword.lower() in template.lower() for keyword in keywords), \
        "Socratic template should mention dialogue elements"


def test_visual_template_structure():
    """Test that visual template has visualization elements"""
    template = ContentTemplates.get_system_prompt(
        modality=LearningModality.VISUAL,
        concept="Financial Ratios",
        learning_objective="Compare financial ratios visually",
        user_context={"knowledge_level": 2, "interests": ["charts"]}
    )

    # Should mention visual keywords
    keywords = ["visual", "diagram", "chart", "picture", "image", "see", "view"]
    assert any(keyword.lower() in template.lower() for keyword in keywords), \
        "Visual template should mention visualization elements"

    # Should mention describing visuals
    assert "describ" in template.lower() or "imagine" in template.lower(), \
        "Visual template should describe visual elements"


def test_templates_are_different():
    """Test that different modalities produce different templates"""
    concept = "Stock Market Basics"
    objective = "Understand how stock markets work"
    context = {"knowledge_level": 2, "interests": ["finance"]}

    templates = {}
    for modality in LearningModality:
        templates[modality] = ContentTemplates.get_system_prompt(
            modality=modality,
            concept=concept,
            learning_objective=objective,
            user_context=context
        )

    # Each template should be unique
    template_texts = list(templates.values())
    unique_templates = set(template_texts)

    assert len(unique_templates) == len(LearningModality), \
        "All modality templates should be different"

    # Check specific differences
    narrative = templates[LearningModality.NARRATIVE]
    interactive = templates[LearningModality.INTERACTIVE]
    socratic = templates[LearningModality.SOCRATIC]
    visual = templates[LearningModality.VISUAL]

    # Narrative should focus on story
    assert narrative.lower().count("story") > interactive.lower().count("story"), \
        "Narrative should mention 'story' more than Interactive"

    # Interactive should focus on doing
    assert interactive.lower().count("decision") > narrative.lower().count("decision"), \
        "Interactive should mention 'decision' more than Narrative"

    # Visual should focus on visuals
    assert visual.lower().count("visual") > narrative.lower().count("visual"), \
        "Visual should mention 'visual' more than Narrative"


def test_template_adapts_to_knowledge_level():
    """Test that templates adapt based on knowledge level"""
    concept = "Investment Strategy"
    objective = "Develop investment strategy"

    beginner_template = ContentTemplates.get_system_prompt(
        modality=LearningModality.NARRATIVE,
        concept=concept,
        learning_objective=objective,
        user_context={"knowledge_level": 1, "interests": []}
    )

    expert_template = ContentTemplates.get_system_prompt(
        modality=LearningModality.NARRATIVE,
        concept=concept,
        learning_objective=objective,
        user_context={"knowledge_level": 5, "interests": []}
    )

    # Both should mention the knowledge level
    assert "1/5" in beginner_template or "beginner" in beginner_template.lower()
    assert "5/5" in expert_template or "expert" in expert_template.lower()

    # Should not be identical
    assert beginner_template != expert_template


def test_helper_function():
    """Test the helper function works correctly"""
    template = get_content_template(
        modality="narrative_story",
        concept="Test",
        learning_objective="Test objective",
        user_context={"knowledge_level": 2}
    )

    assert template is not None
    assert len(template) > 100


def test_visual_content_distinctiveness():
    """
    IMPORTANT TEST: Ensure visual modality produces distinctly visual content
    This addresses the user's complaint about not seeing visual content
    """
    visual_template = ContentTemplates.get_system_prompt(
        modality=LearningModality.VISUAL,
        concept="Company Financial Structure",
        learning_objective="Understand how companies are structured financially",
        user_context={"knowledge_level": 3, "interests": ["business"]}
    )

    narrative_template = ContentTemplates.get_system_prompt(
        modality=LearningModality.NARRATIVE,
        concept="Company Financial Structure",
        learning_objective="Understand how companies are structured financially",
        user_context={"knowledge_level": 3, "interests": ["business"]}
    )

    # Visual template should heavily emphasize visual descriptions
    visual_keywords = [
        "diagram", "chart", "visual", "picture", "image", "see",
        "imagine", "visualiz", "draw", "flowchart", "graph"
    ]

    visual_count = sum(
        visual_template.lower().count(keyword) for keyword in visual_keywords
    )
    narrative_count = sum(
        narrative_template.lower().count(keyword) for keyword in visual_keywords
    )

    assert visual_count > narrative_count * 2, \
        f"Visual template should have >2x more visual keywords than narrative. " \
        f"Visual: {visual_count}, Narrative: {narrative_count}"

    print(f"✓ Visual template has {visual_count} visual keywords")
    print(f"  Narrative template has {narrative_count} visual keywords")
    print(f"  Ratio: {visual_count/max(narrative_count, 1):.1f}x more visual")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
