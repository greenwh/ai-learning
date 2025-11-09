"""
Integration tests with simulated users
Tests the complete learning flow
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base, User, Module, LearningProfile
from backend.learning_engine.style_engine import StyleEngine
from backend.learning_engine.content_delivery import ContentDeliveryEngine
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
def test_module(test_db):
    """Create a test module"""
    module = Module(
        module_id="test-module-1",
        domain="Finance",
        subject="Stock Market Investing",
        topic="Fundamental Analysis",
        title="Understanding P/E Ratio",
        description="Learn what P/E ratio means and how to use it",
        learning_objectives=["Understand P/E ratio", "Apply it to stock analysis"],
        difficulty_level=2,
        estimated_time=15,
        content_config={}
    )
    test_db.add(module)
    test_db.commit()
    return module


class SimulatedUser:
    """
    Simulates a user with specific learning preferences
    """
    def __init__(self, name: str, best_modality: str, effectiveness: dict):
        self.name = name
        self.best_modality = best_modality
        self.effectiveness = effectiveness

    def simulate_session_outcome(self, modality: str) -> dict:
        """
        Simulate how well a session goes with a given modality

        Returns engagement and comprehension scores
        """
        import random

        base_effectiveness = self.effectiveness.get(modality, 0.5)

        # Add some randomness (±10%)
        noise = random.gauss(0, 0.1)

        engagement = max(0.1, min(1.0, base_effectiveness + noise))
        comprehension = max(0.1, min(1.0, base_effectiveness + noise))

        return {
            "engagement_score": engagement,
            "comprehension_score": comprehension
        }


def create_simulated_users():
    """Create different user personas for testing"""
    return [
        SimulatedUser(
            name="Visual Learner",
            best_modality=LearningModality.VISUAL.value,
            effectiveness={
                LearningModality.VISUAL.value: 0.9,
                LearningModality.NARRATIVE.value: 0.6,
                LearningModality.INTERACTIVE.value: 0.7,
                LearningModality.SOCRATIC.value: 0.5
            }
        ),
        SimulatedUser(
            name="Interactive Learner",
            best_modality=LearningModality.INTERACTIVE.value,
            effectiveness={
                LearningModality.VISUAL.value: 0.6,
                LearningModality.NARRATIVE.value: 0.5,
                LearningModality.INTERACTIVE.value: 0.95,
                LearningModality.SOCRATIC.value: 0.7
            }
        ),
        SimulatedUser(
            name="Story Lover",
            best_modality=LearningModality.NARRATIVE.value,
            effectiveness={
                LearningModality.VISUAL.value: 0.5,
                LearningModality.NARRATIVE.value: 0.9,
                LearningModality.INTERACTIVE.value: 0.6,
                LearningModality.SOCRATIC.value: 0.6
            }
        )
    ]


def test_system_discovers_user_preference(test_db, test_module):
    """
    Test that the system correctly discovers a user's learning preference
    over multiple sessions
    """
    simulated_user = SimulatedUser(
        name="Test User",
        best_modality=LearningModality.INTERACTIVE.value,
        effectiveness={
            LearningModality.VISUAL.value: 0.5,
            LearningModality.NARRATIVE.value: 0.55,
            LearningModality.INTERACTIVE.value: 0.9,
            LearningModality.SOCRATIC.value: 0.6
        }
    )

    # Create user in database
    user = User(
        user_id="discovery-test-user",
        username=simulated_user.name,
        password_hash="fake"
    )
    test_db.add(user)
    test_db.commit()

    engine = StyleEngine(test_db)

    # Simulate 25 learning sessions
    modality_history = []

    for session_num in range(25):
        # Select modality
        modality, reason = engine.select_modality(user.user_id)
        modality_history.append(modality.value)

        # Simulate session outcome
        outcome = simulated_user.simulate_session_outcome(modality.value)

        # Create session record
        from backend.database.models import LearningSession
        session = LearningSession(
            session_id=f"session-{session_num}",
            user_id=user.user_id,
            module_id=test_module.module_id,
            modality_used=modality.value
        )
        test_db.add(session)
        test_db.commit()

        # Update learning profile
        engine.update_learning_profile(
            user_id=user.user_id,
            session_id=session.session_id,
            modality=modality,
            engagement_score=outcome["engagement_score"],
            comprehension_score=outcome["comprehension_score"]
        )

    # After 25 sessions, check if system learned the preference
    profile = test_db.query(LearningProfile).filter(
        LearningProfile.user_id == user.user_id
    ).first()

    # Get effectiveness scores
    prefs = profile.modality_preferences
    interactive_score = prefs[LearningModality.INTERACTIVE.value]['effectiveness_score']

    # Interactive should have highest effectiveness
    all_scores = {k: v['effectiveness_score'] for k, v in prefs.items()}
    max_modality = max(all_scores, key=all_scores.get)

    assert max_modality == LearningModality.INTERACTIVE.value, \
        f"System should have learned INTERACTIVE is best, but chose {max_modality}"

    # Check last 10 selections favor interactive
    last_10 = modality_history[-10:]
    interactive_count = last_10.count(LearningModality.INTERACTIVE.value)

    assert interactive_count >= 6, \
        f"Last 10 selections should favor INTERACTIVE, got {interactive_count}/10"

    print(f"✓ System correctly discovered preference: {max_modality}")
    print(f"  Effectiveness score: {interactive_score*100:.0f}%")
    print(f"  Last 10 selections: {interactive_count}/10 interactive")


def test_multiple_user_personas(test_db, test_module):
    """
    Test system with multiple different user personas
    """
    users = create_simulated_users()
    engine = StyleEngine(test_db)

    results = []

    for sim_user in users:
        # Create database user
        user = User(
            user_id=f"user-{sim_user.name.replace(' ', '-')}",
            username=sim_user.name,
            password_hash="fake"
        )
        test_db.add(user)
        test_db.commit()

        # Run 20 sessions
        for session_num in range(20):
            modality, _ = engine.select_modality(user.user_id)
            outcome = sim_user.simulate_session_outcome(modality.value)

            from backend.database.models import LearningSession
            session = LearningSession(
                session_id=f"{user.user_id}-session-{session_num}",
                user_id=user.user_id,
                module_id=test_module.module_id,
                modality_used=modality.value
            )
            test_db.add(session)
            test_db.commit()

            engine.update_learning_profile(
                user_id=user.user_id,
                session_id=session.session_id,
                modality=modality,
                engagement_score=outcome["engagement_score"],
                comprehension_score=outcome["comprehension_score"]
            )

        # Check learned preference
        profile = test_db.query(LearningProfile).filter(
            LearningProfile.user_id == user.user_id
        ).first()

        prefs = profile.modality_preferences
        all_scores = {k: v['effectiveness_score'] for k, v in prefs.items()}
        learned_best = max(all_scores, key=all_scores.get)

        results.append({
            "user": sim_user.name,
            "true_best": sim_user.best_modality,
            "learned_best": learned_best,
            "score": all_scores[learned_best]
        })

    # Print results
    print("\nMulti-User Test Results:")
    print("-" * 60)
    for result in results:
        match = "✓" if result["true_best"] == result["learned_best"] else "✗"
        print(f"{match} {result['user']}")
        print(f"  True preference: {result['true_best']}")
        print(f"  Learned preference: {result['learned_best']}")
        print(f"  Effectiveness: {result['score']*100:.0f}%")

    # At least 2 out of 3 should be correct
    correct = sum(1 for r in results if r["true_best"] == r["learned_best"])
    assert correct >= 2, \
        f"System should correctly identify at least 2/3 preferences, got {correct}/3"


def test_exploration_continues_after_convergence(test_db, test_module):
    """
    Test that system continues exploring even after finding best modality
    """
    user = User(
        user_id="exploration-test",
        username="explorer",
        password_hash="fake"
    )
    test_db.add(user)

    # Create profile with strong preference
    profile = LearningProfile(
        user_id=user.user_id,
        modality_preferences={
            LearningModality.NARRATIVE.value: {
                "effectiveness_score": 0.95,
                "sessions_count": 100,
                "avg_retention": 0.95,
                "avg_engagement": 0.95
            },
            LearningModality.INTERACTIVE.value: {
                "effectiveness_score": 0.6,
                "sessions_count": 20,
                "avg_retention": 0.6,
                "avg_engagement": 0.6
            },
            LearningModality.SOCRATIC.value: {
                "effectiveness_score": 0.55,
                "sessions_count": 15,
                "avg_retention": 0.55,
                "avg_engagement": 0.55
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

    engine = StyleEngine(test_db)

    # Run 100 selections
    selections = []
    for _ in range(100):
        modality, _ = engine.select_modality(user.user_id)
        selections.append(modality.value)

    # Count non-narrative selections
    non_narrative = [s for s in selections if s != LearningModality.NARRATIVE.value]
    exploration_rate = len(non_narrative) / 100

    # Should explore at least 10% of the time
    assert exploration_rate >= 0.10, \
        f"Should explore at least 10% of time, only explored {exploration_rate*100:.0f}%"

    # Should explore all modalities at least once
    unique_modalities = set(selections)
    assert len(unique_modalities) >= 3, \
        "Should explore at least 3 different modalities even with strong preference"

    print(f"✓ Exploration rate: {exploration_rate*100:.0f}%")
    print(f"  Unique modalities tried: {len(unique_modalities)}/4")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
