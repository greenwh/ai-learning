"""
Database migration script to add xAI settings columns
Run this to update existing databases with new xai_api_key and xai_model columns
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from backend.database.connection import DATABASE_FILE, engine, init_db
import os


def migrate_add_xai_columns():
    """Add xai_api_key and xai_model columns to user_settings table if they don't exist"""

    # Check if database file exists
    if not DATABASE_FILE.exists():
        print(f"Database doesn't exist yet at {DATABASE_FILE}")
        print("Creating new database with all columns...")
        init_db()
        print("✓ Database created successfully with all columns including xAI support")
        return

    print(f"Found existing database at {DATABASE_FILE}")

    # Check if user_settings table exists
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'user_settings' not in tables:
        print("user_settings table doesn't exist yet")
        print("Creating all tables...")
        init_db()
        print("✓ Tables created successfully")
        return

    # Check existing columns
    columns = [col['name'] for col in inspector.get_columns('user_settings')]
    print(f"Existing columns in user_settings: {columns}")

    # Add missing columns
    migrations = []
    if 'xai_api_key' not in columns:
        migrations.append("ALTER TABLE user_settings ADD COLUMN xai_api_key VARCHAR")
        print("  + Will add xai_api_key column")

    if 'xai_model' not in columns:
        migrations.append("ALTER TABLE user_settings ADD COLUMN xai_model VARCHAR DEFAULT 'grok-3'")
        print("  + Will add xai_model column")

    if not migrations:
        print("✓ All columns already exist - no migration needed")
        return

    # Execute migrations
    print("\nApplying migrations...")
    with engine.connect() as conn:
        for migration_sql in migrations:
            print(f"  Executing: {migration_sql}")
            conn.execute(text(migration_sql))
            conn.commit()

    print("✓ Migration completed successfully!")

    # Verify
    inspector = inspect(engine)
    new_columns = [col['name'] for col in inspector.get_columns('user_settings')]
    print(f"\nUpdated columns: {new_columns}")


if __name__ == "__main__":
    try:
        migrate_add_xai_columns()
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
