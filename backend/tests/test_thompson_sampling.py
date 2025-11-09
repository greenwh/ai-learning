"""
Tests for Thompson Sampling algorithm in StyleEngine
"""
import pytest
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base, User, LearningProfile, LearningSession
from backend.learning_engine.style_engine import StyleEngine
from backend.ai.content_templates import LearningModality


@pytest.fixture
def test_db():
    """Create in-memory test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    user = User(
        user_id="test-user-123",
        username="testuser",
        password_hash="fake_hash"
    )
    test_db.add(user)
    test_db.commit()
    return user


def test_new_user_random_selection(test_db, test_user):
    """Test that new users get random modality selection"""
    engine = StyleEngine(test_db)

    # Run selection 20 times for new user
    selections = []
    for _ in range(20):
        modality, reason = engine.select_modality(test_user.user_id)
        selections.append(modality.value)

    # Should see variety (at least 2 different modalities)
    unique_selections = set(selections)
    assert len(unique_selections) >= 2, \
        f"New user should get variety, only got: {unique_selections}"
    assert "Initial exploration" in reason


def test_thompson_sampling_convergence(test_db, test_user):
    """Test that Thompson Sampling converges to best modality"""
    engine = StyleEngine(test_db)

    # Create learning profile
    profile = LearningProfile(
        user_id=test_user.user_id,
        modality_preferences={},
        cognitive_patterns={}
    )
    test_db.add(profile)
    test_db.commit()

    # Simulate 30 sessions where INTERACTIVE is clearly best
    for i in range(30):
        modality, _ = engine.select_modality(test_user.user_id)

        # Create session
        session = LearningSession(
            session_id=f"session-{i}",
            user_id=test_user.user_id,
            module_id="test-module",
            modality_used=modality.value
        )
        test_db.add(session)
        test_db.commit()

        # Simulate results: interactive is best (90% effective)
        # other modalities are mediocre (50% effective)
        if modality.value == LearningModality.INTERACTIVE.value:
            engagement = 0.9
            comprehension = 0.9
        else:
            engagement = 0.5
            comprehension = 0.5

        engine.update_learning_profile(
            user_id=test_user.user_id,
            session_id=session.session_id,
            modality=modality,
            engagement_score=engagement,
            comprehension_score=comprehension
        )

    # After 30 sessions, should strongly prefer INTERACTIVE
    # Run 100 selections and count
    selections = []
    for _ in range(100):
        modality, _ = engine.select_modality(test_user.user_id)
        selections.append(modality.value)

    interactive_count = selections.count(LearningModality.INTERACTIVE.value)

    # Should select interactive >60% of time (allows for exploration)
    assert interactive_count > 60, \
        f"Should prefer interactive modality, but selected {interactive_count}/100 times"

    # Should still explore others occasionally
    unique_selections = set(selections)
    assert len(unique_selections) >= 2, \
        "Should still explore other modalities occasionally"


def test_exploration_vs_exploitation(test_db, test_user):
    """Test that exploration still happens with strong preference"""
    engine = StyleEngine(test_db)

    # Create profile with strong preference for NARRATIVE
    profile = LearningProfile(
        user_id=test_user.user_id,
        modality_preferences={
            LearningModality.NARRATIVE.value: {
                "effectiveness_score": 0.95,
                "sessions_count": 50,
                "avg_retention": 0.95,
                "avg_engagement": 0.95
            },
            LearningModality.INTERACTIVE.value: {
                "effectiveness_score": 0.5,
                "sessions_count": 10,
                "avg_retention": 0.5,
                "avg_engagement": 0.5
            },
            LearningModality.SOCRATIC.value: {
                "effectiveness_score": 0.5,
                "sessions_count": 10,
                "avg_retention": 0.5,
                "avg_engagement": 0.5
            },
            LearningModality.VISUAL.value: {
                "effectiveness_score": 0.5,
                "sessions_count": 10,
                "avg_retention": 0.5,
                "avg_engagement": 0.5
            }
        },
        cognitive_patterns={}
    )
    test_db.add(profile)
    test_db.commit()

    # Run 100 selections
    selections = []
    for _ in range(100):
        modality, _ = engine.select_modality(test_user.user_id)
        selections.append(modality.value)

    # Should mostly select NARRATIVE but still explore
    narrative_count = selections.count(LearningModality.NARRATIVE.value)

    # Should prefer narrative but not exclusively
    assert 70 < narrative_count < 95, \
        f"Expected 70-95 narrative selections, got {narrative_count}"

    # Should explore other modalities
    other_count = 100 - narrative_count
    assert other_count > 5, \
        "Should still explore other modalities at least 5% of time"


def test_effectiveness_calculation(test_db, test_user):
    """Test that effectiveness score is calculated correctly"""
    engine = StyleEngine(test_db)

    profile = LearningProfile(
        user_id=test_user.user_id,
        modality_preferences={},
        cognitive_patterns={}
    )
    test_db.add(profile)
    test_db.commit()

    # Create session
    session = LearningSession(
        session_id="test-session",
        user_id=test_user.user_id,
        module_id="test-module",
        modality_used=LearningModality.NARRATIVE.value
    )
    test_db.add(session)
    test_db.commit()

    # Update with known scores
    engine.update_learning_profile(
        user_id=test_user.user_id,
        session_id=session.session_id,
        modality=LearningModality.NARRATIVE,
        engagement_score=0.8,
        comprehension_score=0.9,
        retention_score=0.85
    )

    # Check profile was updated
    profile = test_db.query(LearningProfile).filter(
        LearningProfile.user_id == test_user.user_id
    ).first()

    narrative_stats = profile.modality_preferences[LearningModality.NARRATIVE.value]

    # With retention: effectiveness = retention*0.5 + comprehension*0.3 + engagement*0.2
    # = 0.85*0.5 + 0.9*0.3 + 0.8*0.2 = 0.425 + 0.27 + 0.16 = 0.855
    expected_effectiveness = 0.855
    actual_effectiveness = narrative_stats['effectiveness_score']

    assert abs(actual_effectiveness - expected_effectiveness) < 0.01, \
        f"Expected effectiveness {expected_effectiveness}, got {actual_effectiveness}"


def test_all_modalities_initialized(test_db, test_user):
    """Test that all modalities are initialized with default values"""
    engine = StyleEngine(test_db)

    profile = LearningProfile(
        user_id=test_user.user_id,
        modality_preferences={},
        cognitive_patterns={}
    )
    test_db.add(profile)
    test_db.commit()

    # Trigger profile initialization via session
    session = LearningSession(
        session_id="init-session",
        user_id=test_user.user_id,
        module_id="test-module",
        modality_used=LearningModality.NARRATIVE.value
    )
    test_db.add(session)
    test_db.commit()

    engine.update_learning_profile(
        user_id=test_user.user_id,
        session_id=session.session_id,
        modality=LearningModality.NARRATIVE,
        engagement_score=0.7,
        comprehension_score=0.8
    )

    # Check all modalities exist
    profile = test_db.query(LearningProfile).filter(
        LearningProfile.user_id == test_user.user_id
    ).first()

    for modality in LearningModality:
        assert modality.value in profile.modality_preferences, \
            f"Modality {modality.value} not initialized"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
