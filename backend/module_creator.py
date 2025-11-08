#!/usr/bin/env python3
"""
Module Creator - Easy tool for creating and managing learning modules

Usage:
    python module_creator.py create           # Interactive creation
    python module_creator.py import FILE.json # Import from JSON
    python module_creator.py export MODULE_ID # Export to JSON
    python module_creator.py list             # List all modules
    python module_creator.py template         # Generate blank template
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, init_db
from backend.database.models import Module


def create_interactive():
    """Create a module interactively through prompts"""
    print("\n🎓 Interactive Module Creator\n")
    print("Let's create a new learning module!\n")

    # Basic info
    domain = input("Domain (e.g., Finance, Science, Technology): ").strip()
    subject = input(f"Subject within {domain}: ").strip()
    topic = input(f"Specific topic within {subject}: ").strip()
    title = input("Module title: ").strip()
    description = input("Description (what will they learn?): ").strip()

    # Difficulty and time
    print("\nDifficulty level:")
    print("  1 - Complete beginner")
    print("  2 - Some basics helpful")
    print("  3 - Intermediate")
    print("  4 - Advanced")
    print("  5 - Expert")
    difficulty = int(input("Choose (1-5): ").strip())

    estimated_time = int(input("Estimated time in minutes: ").strip())

    # Learning objectives
    print("\nLearning objectives (one per line, empty line to finish):")
    objectives = []
    while True:
        obj = input(f"  Objective {len(objectives) + 1}: ").strip()
        if not obj:
            break
        objectives.append(obj)

    # Key concepts
    print("\nKey concepts to cover (one per line, empty line to finish):")
    concepts = []
    while True:
        concept = input(f"  Concept {len(concepts) + 1}: ").strip()
        if not concept:
            break
        concepts.append(concept)

    # Real-world examples
    print("\nReal-world examples (one per line, empty line to finish):")
    examples = []
    while True:
        example = input(f"  Example {len(examples) + 1}: ").strip()
        if not example:
            break
        examples.append(example)

    # Create module
    module = Module(
        domain=domain,
        subject=subject,
        topic=topic,
        title=title,
        description=description,
        prerequisites=[],
        learning_objectives=objectives,
        difficulty_level=difficulty,
        estimated_time=estimated_time,
        content_config={
            "modalities": {
                "narrative_story": {
                    "enabled": True,
                    "theme": "auto_generated"
                },
                "interactive_hands_on": {
                    "enabled": True,
                    "type": "practical_exercise"
                },
                "socratic_dialogue": {
                    "enabled": True,
                    "starting_question": f"What do you already know about {topic}?"
                },
                "visual_diagrams": {
                    "enabled": True,
                    "metaphor": "simple_visual"
                }
            },
            "key_concepts": concepts,
            "real_world_examples": examples
        },
        version="1.0"
    )

    # Save to database
    db = SessionLocal()
    try:
        db.add(module)
        db.commit()
        db.refresh(module)

        print(f"\n✅ Module created successfully!")
        print(f"   Module ID: {module.module_id}")
        print(f"   Title: {module.title}")
        print(f"\nYou can now use this module in the learning system!")

        # Optionally export to JSON
        export_choice = input("\nExport to JSON file? (y/n): ").strip().lower()
        if export_choice == 'y':
            export_module(module.module_id, db)

    except Exception as e:
        print(f"\n❌ Error creating module: {e}")
        db.rollback()
    finally:
        db.close()


def import_from_json(file_path: str):
    """Import a module from a JSON file"""
    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return

    try:
        with open(path, 'r') as f:
            data = json.load(f)

        # Validate required fields
        required = [
            'domain', 'subject', 'topic', 'title', 'description',
            'learning_objectives', 'difficulty_level', 'estimated_time',
            'content_config'
        ]

        missing = [field for field in required if field not in data]
        if missing:
            print(f"❌ Missing required fields: {', '.join(missing)}")
            return

        # Create module
        module = Module(
            domain=data['domain'],
            subject=data['subject'],
            topic=data['topic'],
            title=data['title'],
            description=data['description'],
            prerequisites=data.get('prerequisites', []),
            learning_objectives=data['learning_objectives'],
            difficulty_level=data['difficulty_level'],
            estimated_time=data['estimated_time'],
            content_config=data['content_config'],
            version=data.get('version', '1.0')
        )

        # Save to database
        db = SessionLocal()
        try:
            db.add(module)
            db.commit()
            db.refresh(module)

            print(f"\n✅ Module imported successfully!")
            print(f"   Module ID: {module.module_id}")
            print(f"   Title: {module.title}")
            print(f"   Domain: {module.domain} → {module.subject}")
            print(f"   Difficulty: Level {module.difficulty_level}")
            print(f"   Time: {module.estimated_time} minutes")
            print(f"   Objectives: {len(module.learning_objectives)}")

        except Exception as e:
            print(f"\n❌ Error importing module: {e}")
            db.rollback()
        finally:
            db.close()

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON file: {e}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")


def export_module(module_id: str, db_session=None):
    """Export a module to JSON"""
    db = db_session or SessionLocal()
    close_db = db_session is None

    try:
        module = db.query(Module).filter(Module.module_id == module_id).first()

        if not module:
            print(f"❌ Module not found: {module_id}")
            return

        # Create export data
        export_data = {
            "domain": module.domain,
            "subject": module.subject,
            "topic": module.topic,
            "title": module.title,
            "description": module.description,
            "prerequisites": module.prerequisites or [],
            "learning_objectives": module.learning_objectives,
            "difficulty_level": module.difficulty_level,
            "estimated_time": module.estimated_time,
            "content_config": module.content_config,
            "version": module.version
        }

        # Generate filename
        safe_title = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in module.title)
        safe_title = safe_title.replace(' ', '_').lower()
        filename = f"module_{safe_title}_{datetime.now().strftime('%Y%m%d')}.json"

        # Save to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n✅ Module exported to: {filename}")
        print(f"   Title: {module.title}")
        print(f"   You can now edit this file and re-import it!")

    except Exception as e:
        print(f"❌ Error exporting module: {e}")
    finally:
        if close_db:
            db.close()


def list_modules():
    """List all modules in the database"""
    db = SessionLocal()

    try:
        modules = db.query(Module).all()

        if not modules:
            print("\n📚 No modules found in the database.")
            print("   Create one with: python module_creator.py create")
            return

        print(f"\n📚 {len(modules)} Module(s) in Database:\n")

        for i, module in enumerate(modules, 1):
            print(f"{i}. {module.title}")
            print(f"   ID: {module.module_id}")
            print(f"   Domain: {module.domain} → {module.subject} → {module.topic}")
            print(f"   Level: {module.difficulty_level}/5 | Time: {module.estimated_time}min")
            print(f"   Objectives: {len(module.learning_objectives)}")
            if module.prerequisites:
                print(f"   Prerequisites: {len(module.prerequisites)} required")
            print()

    except Exception as e:
        print(f"❌ Error listing modules: {e}")
    finally:
        db.close()


def generate_template():
    """Generate a blank template JSON file"""
    template = {
        "domain": "Your Domain",
        "subject": "Your Subject",
        "topic": "Your Topic",
        "title": "Your Module Title",
        "description": "What will students learn from this module?",
        "prerequisites": [],
        "learning_objectives": [
            "Objective 1: Start with action verb",
            "Objective 2: Be specific and measurable",
            "Objective 3: Focus on outcomes"
        ],
        "difficulty_level": 1,
        "estimated_time": 15,
        "content_config": {
            "modalities": {
                "narrative_story": {
                    "enabled": True,
                    "theme": "Describe the narrative approach"
                },
                "interactive_hands_on": {
                    "enabled": True,
                    "type": "Type of interaction",
                    "data_source": "Where examples come from"
                },
                "socratic_dialogue": {
                    "enabled": True,
                    "starting_question": "What opening question gets them thinking?"
                },
                "visual_diagrams": {
                    "enabled": True,
                    "metaphor": "What visual analogy to use?"
                }
            },
            "key_concepts": [
                "concept_1",
                "concept_2",
                "concept_3"
            ],
            "real_world_examples": [
                "Example 1",
                "Example 2",
                "Example 3"
            ]
        },
        "version": "1.0"
    }

    filename = f"module_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"\n✅ Template created: {filename}")
    print("   Edit this file and import with: python module_creator.py import {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Create and manage learning modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a module interactively
  python module_creator.py create

  # Import a module from JSON
  python module_creator.py import my_module.json

  # Export a module to JSON
  python module_creator.py export MODULE_ID

  # List all modules
  python module_creator.py list

  # Generate a blank template
  python module_creator.py template
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create command
    subparsers.add_parser('create', help='Create module interactively')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import module from JSON')
    import_parser.add_argument('file', help='Path to JSON file')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export module to JSON')
    export_parser.add_argument('module_id', help='Module ID to export')

    # List command
    subparsers.add_parser('list', help='List all modules')

    # Template command
    subparsers.add_parser('template', help='Generate blank template')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize database
    init_db()

    # Execute command
    if args.command == 'create':
        create_interactive()

    elif args.command == 'import':
        import_from_json(args.file)

    elif args.command == 'export':
        export_module(args.module_id)

    elif args.command == 'list':
        list_modules()

    elif args.command == 'template':
        generate_template()


if __name__ == "__main__":
    main()
