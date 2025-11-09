#!/usr/bin/env python3
"""
Database Fix Script
Ensures database exists and is properly initialized
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import DATABASE_FILE, init_db, SessionLocal, engine
from database.models import User, Module, UserSettings
from sqlalchemy import inspect

# Try to import bcrypt, use simple hash if not available
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    import hashlib


def check_and_create_database():
    """Check if database exists and create if needed"""
    print("Checking database status...")

    if not DATABASE_FILE.exists():
        print(f"✗ Database not found at: {DATABASE_FILE}")
        print("Creating database...")
        DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
        init_db()
        print(f"✓ Database created at: {DATABASE_FILE}")
        return True
    else:
        print(f"✓ Database exists at: {DATABASE_FILE}")
        return False


def check_tables():
    """Check if all tables exist"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = [
        'users', 'learning_profiles', 'modules', 'module_progress',
        'learning_sessions', 'engagement_signals', 'retention_tests',
        'user_settings', 'concept_mastery', 'chat_messages'
    ]

    missing_tables = [t for t in required_tables if t not in tables]

    if missing_tables:
        print(f"✗ Missing tables: {', '.join(missing_tables)}")
        print("Recreating all tables...")
        init_db()
        print("✓ Tables created")
        return True
    else:
        print(f"✓ All {len(required_tables)} required tables exist")
        return False


def create_test_user():
    """Create a test user if none exists"""
    db = SessionLocal()

    try:
        user_count = db.query(User).count()

        if user_count == 0:
            print("\nNo users found. Creating test user...")

            # Create test user
            password = "password123"

            # Hash password (use bcrypt if available, otherwise simple hash)
            if HAS_BCRYPT:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            else:
                # Simple fallback hash for testing (not secure for production!)
                password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                print("  Note: Using simple hash (bcrypt not available)")

            test_user = User(
                user_id="test-user-001",
                username="testuser",
                email="test@example.com",
                password_hash=password_hash
            )

            db.add(test_user)
            db.commit()

            print(f"✓ Test user created:")
            print(f"  Username: testuser")
            print(f"  Password: {password}")
            print(f"  User ID: {test_user.user_id}")

            return test_user
        else:
            print(f"\n✓ Database has {user_count} user(s)")
            return None

    finally:
        db.close()


def create_sample_modules():
    """Create sample modules if none exist"""
    db = SessionLocal()

    try:
        module_count = db.query(Module).count()

        if module_count == 0:
            print("\nNo modules found. Creating sample modules...")

            sample_modules = [
                {
                    "module_id": "stock-fundamentals-101",
                    "domain": "Finance",
                    "subject": "Stock Market Investing",
                    "topic": "Fundamental Analysis",
                    "title": "Stock Market Fundamentals 101",
                    "description": "Learn the basics of stock market analysis",
                    "learning_objectives": [
                        "Understand what stocks represent",
                        "Learn basic financial metrics",
                        "Analyze company fundamentals"
                    ],
                    "difficulty_level": 1,
                    "estimated_time": 20,
                    "content_config": {}
                },
                {
                    "module_id": "pe-ratio-deep-dive",
                    "domain": "Finance",
                    "subject": "Stock Market Investing",
                    "topic": "Valuation Metrics",
                    "title": "Understanding P/E Ratio",
                    "description": "Deep dive into Price-to-Earnings ratio",
                    "learning_objectives": [
                        "Calculate P/E ratio",
                        "Interpret P/E values",
                        "Compare companies using P/E"
                    ],
                    "difficulty_level": 2,
                    "estimated_time": 15,
                    "content_config": {}
                },
                {
                    "module_id": "balance-sheet-basics",
                    "domain": "Finance",
                    "subject": "Financial Statements",
                    "topic": "Balance Sheets",
                    "title": "Reading Balance Sheets",
                    "description": "Learn to read and analyze balance sheets",
                    "learning_objectives": [
                        "Understand balance sheet structure",
                        "Identify key line items",
                        "Assess financial health"
                    ],
                    "difficulty_level": 2,
                    "estimated_time": 25,
                    "content_config": {}
                }
            ]

            for module_data in sample_modules:
                module = Module(**module_data)
                db.add(module)

            db.commit()

            print(f"✓ Created {len(sample_modules)} sample modules")
        else:
            print(f"\n✓ Database has {module_count} module(s)")

    finally:
        db.close()


def main():
    """Run all database fixes"""
    print("=" * 60)
    print("DATABASE FIX SCRIPT")
    print("=" * 60)
    print()

    # Step 1: Check and create database
    db_created = check_and_create_database()

    # Step 2: Check tables
    tables_created = check_tables()

    # Step 3: Create test data if needed
    test_user = create_test_user()
    create_sample_modules()

    print()
    print("=" * 60)
    print("DATABASE STATUS")
    print("=" * 60)
    print(f"Database file: {DATABASE_FILE}")
    print(f"Database size: {DATABASE_FILE.stat().st_size / 1024:.2f} KB")

    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        module_count = db.query(Module).count()

        print(f"Users: {user_count}")
        print(f"Modules: {module_count}")
    finally:
        db.close()

    print()
    print("✓ Database is ready to use!")
    print()

    if test_user:
        print("To test the system, you can use:")
        print("  Username: testuser")
        print("  Password: password123")
        print()


if __name__ == "__main__":
    main()
