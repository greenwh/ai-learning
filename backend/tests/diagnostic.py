#!/usr/bin/env python3
"""
Diagnostic script to check database state and system health
Run this to debug issues with the learning system
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import DATABASE_FILE, engine, init_db, SessionLocal
from database.models import (
    User, LearningProfile, Module, ModuleProgress,
    LearningSession, EngagementSignal
)
from learning_engine.style_engine import StyleEngine
from ai.content_templates import LearningModality
import json


def check_database_exists():
    """Check if database file exists"""
    print("=" * 60)
    print("DATABASE FILE CHECK")
    print("=" * 60)

    if DATABASE_FILE.exists():
        print(f"✓ Database exists: {DATABASE_FILE}")
        print(f"  Size: {DATABASE_FILE.stat().st_size / 1024:.2f} KB")
        return True
    else:
        print(f"✗ Database does NOT exist: {DATABASE_FILE}")
        print(f"  Expected location: {DATABASE_FILE}")
        return False


def check_tables():
    """Check if all required tables exist"""
    print("\n" + "=" * 60)
    print("DATABASE TABLES CHECK")
    print("=" * 60)

    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = [
        'users', 'learning_profiles', 'modules', 'module_progress',
        'learning_sessions', 'engagement_signals', 'retention_tests',
        'user_settings'
    ]

    for table in required_tables:
        if table in tables:
            print(f"✓ Table '{table}' exists")
        else:
            print(f"✗ Table '{table}' MISSING")

    return len(tables) > 0


def check_user_data():
    """Check user data and learning profiles"""
    print("\n" + "=" * 60)
    print("USER DATA CHECK")
    print("=" * 60)

    db = SessionLocal()

    try:
        users = db.query(User).all()
        print(f"Total users: {len(users)}")

        if users:
            for user in users[:5]:  # Show first 5 users
                print(f"\nUser: {user.username} (ID: {user.user_id[:8]}...)")

                # Check learning profile
                profile = db.query(LearningProfile).filter(
                    LearningProfile.user_id == user.user_id
                ).first()

                if profile:
                    print("  ✓ Has learning profile")

                    if profile.modality_preferences:
                        print("  Modality Preferences:")
                        for modality, stats in profile.modality_preferences.items():
                            effectiveness = stats.get('effectiveness_score', 0)
                            sessions = stats.get('sessions_count', 0)
                            print(f"    - {modality}: {effectiveness*100:.0f}% effective ({sessions} sessions)")
                    else:
                        print("  ⚠ No modality preferences set")

                    if profile.cognitive_patterns:
                        print("  Cognitive Patterns:")
                        for key, value in profile.cognitive_patterns.items():
                            print(f"    - {key}: {value}")
                else:
                    print("  ✗ No learning profile")

                # Check sessions
                sessions = db.query(LearningSession).filter(
                    LearningSession.user_id == user.user_id
                ).count()
                print(f"  Sessions completed: {sessions}")

                # Check module progress
                progress = db.query(ModuleProgress).filter(
                    ModuleProgress.user_id == user.user_id
                ).all()

                if progress:
                    completed = sum(1 for p in progress if p.status == 'completed')
                    in_progress = sum(1 for p in progress if p.status == 'in_progress')
                    print(f"  Modules: {completed} completed, {in_progress} in progress")
        else:
            print("No users found in database")

    finally:
        db.close()


def check_modules():
    """Check available modules"""
    print("\n" + "=" * 60)
    print("MODULES CHECK")
    print("=" * 60)

    db = SessionLocal()

    try:
        modules = db.query(Module).all()
        print(f"Total modules: {len(modules)}")

        if modules:
            for module in modules[:5]:  # Show first 5
                print(f"\n  - {module.title}")
                print(f"    Domain: {module.domain}")
                print(f"    Difficulty: {module.difficulty_level}/5")
                print(f"    Estimated time: {module.estimated_time} min")
        else:
            print("⚠ No modules found in database")

    finally:
        db.close()


def check_recent_sessions():
    """Check recent learning sessions"""
    print("\n" + "=" * 60)
    print("RECENT SESSIONS CHECK")
    print("=" * 60)

    db = SessionLocal()

    try:
        sessions = db.query(LearningSession).order_by(
            LearningSession.created_at.desc()
        ).limit(10).all()

        print(f"Total sessions in database: {db.query(LearningSession).count()}")

        if sessions:
            print(f"\nShowing last {len(sessions)} sessions:\n")

            modality_counts = {}
            for session in sessions:
                modality_counts[session.modality_used] = \
                    modality_counts.get(session.modality_used, 0) + 1

                status = "✓" if session.completed_at else "○"
                print(f"{status} Session {session.session_id[:8]}...")
                print(f"  Modality: {session.modality_used}")
                print(f"  Engagement: {session.engagement_score or 'N/A'}")
                print(f"  Comprehension: {session.comprehension_score or 'N/A'}")
                print(f"  Duration: {session.duration or 'N/A'} min")
                print()

            print("Modality distribution in recent sessions:")
            for modality, count in modality_counts.items():
                print(f"  - {modality}: {count}/{len(sessions)} ({count/len(sessions)*100:.0f}%)")
        else:
            print("No sessions found in database")

    finally:
        db.close()


def test_thompson_sampling():
    """Test Thompson Sampling selection"""
    print("\n" + "=" * 60)
    print("THOMPSON SAMPLING TEST")
    print("=" * 60)

    db = SessionLocal()

    try:
        users = db.query(User).all()

        if not users:
            print("No users to test")
            return

        user = users[0]
        print(f"Testing with user: {user.username}")

        engine = StyleEngine(db)

        # Run 20 selections and see distribution
        selections = []
        reasons = []

        for i in range(20):
            modality, reason = engine.select_modality(user.user_id)
            selections.append(modality.value)
            if i == 0:
                reasons.append(reason)

        print(f"\nSelection reason: {reasons[0]}")
        print(f"\nModality distribution over 20 selections:")

        for modality in LearningModality:
            count = selections.count(modality.value)
            print(f"  - {modality.value}: {count}/20 ({count/20*100:.0f}%)")

        # Check if we're getting diversity
        unique_modalities = set(selections)
        if len(unique_modalities) == 1:
            print("\n⚠ WARNING: Only one modality being selected!")
            print("  This suggests Thompson Sampling may not be working correctly")
        elif len(unique_modalities) >= 3:
            print(f"\n✓ Good diversity: {len(unique_modalities)} different modalities selected")
        else:
            print(f"\n○ Moderate diversity: {len(unique_modalities)} different modalities selected")

    finally:
        db.close()


def initialize_database():
    """Initialize database if it doesn't exist"""
    print("\n" + "=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    if not DATABASE_FILE.exists():
        print("Initializing database...")
        init_db()
        print(f"✓ Database created at: {DATABASE_FILE}")
    else:
        print("Database already exists")


def main():
    """Run all diagnostic checks"""
    print("\n" + "=" * 60)
    print("AI LEARNING SYSTEM DIAGNOSTICS")
    print("=" * 60)
    print()

    # Check if database exists
    db_exists = check_database_exists()

    if not db_exists:
        print("\n⚠ Database does not exist!")
        response = input("Would you like to initialize it? (y/n): ")
        if response.lower() == 'y':
            initialize_database()
            db_exists = True
        else:
            print("Cannot proceed without database. Exiting.")
            return

    # Check tables
    if db_exists:
        has_tables = check_tables()

        if not has_tables:
            print("\n⚠ Database exists but has no tables!")
            print("This usually means init_db() was never called.")
            response = input("Initialize tables now? (y/n): ")
            if response.lower() == 'y':
                init_db()

    # Check data
    check_user_data()
    check_modules()
    check_recent_sessions()

    # Test Thompson Sampling
    test_thompson_sampling()

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
