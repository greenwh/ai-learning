#!/usr/bin/env python3
"""
CLI tool for backing up and restoring learning data

Usage:
    python backup_cli.py backup              # Full database backup
    python backup_cli.py export-modules      # Export all modules
    python backup_cli.py export-profile USER_ID  # Export user profile
    python backup_cli.py import-modules FILE  # Import modules
    python backup_cli.py import-profile FILE USER_ID  # Import profile
    python backup_cli.py restore FILE        # Restore database
    python backup_cli.py list                # List all backups
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils.backup import BackupManager


def main():
    parser = argparse.ArgumentParser(
        description="Backup and restore learning data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create full database backup
  python backup_cli.py backup

  # Create named backup
  python backup_cli.py backup --name my_backup

  # Export all modules
  python backup_cli.py export-modules

  # Export specific modules
  python backup_cli.py export-modules --ids module1 module2

  # Export user profile
  python backup_cli.py export-profile user123

  # Import modules (skip existing)
  python backup_cli.py import-modules modules_export.json

  # Import modules (overwrite existing)
  python backup_cli.py import-modules modules_export.json --overwrite

  # Import user profile
  python backup_cli.py import-profile profile_john.json user123

  # Restore from backup
  python backup_cli.py restore full_backup_20240101.db

  # List all backups
  python backup_cli.py list
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create full database backup')
    backup_parser.add_argument('--name', help='Backup name (default: auto-generated)')

    # Export modules command
    export_modules_parser = subparsers.add_parser('export-modules', help='Export modules to JSON')
    export_modules_parser.add_argument('--ids', nargs='+', help='Module IDs to export (default: all)')
    export_modules_parser.add_argument('--name', help='Export file name')

    # Export profile command
    export_profile_parser = subparsers.add_parser('export-profile', help='Export user profile')
    export_profile_parser.add_argument('user_id', help='User ID to export')
    export_profile_parser.add_argument('--name', help='Export file name')

    # Import modules command
    import_modules_parser = subparsers.add_parser('import-modules', help='Import modules from JSON')
    import_modules_parser.add_argument('file', help='Path to modules JSON file')
    import_modules_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing modules')

    # Import profile command
    import_profile_parser = subparsers.add_parser('import-profile', help='Import user profile')
    import_profile_parser.add_argument('file', help='Path to profile JSON file')
    import_profile_parser.add_argument('user_id', help='Target user ID')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore database from backup')
    restore_parser.add_argument('file', help='Path to backup file')

    # List command
    subparsers.add_parser('list', help='List all backups')

    # Complete export command
    complete_parser = subparsers.add_parser('complete-export', help='Create complete export package')
    complete_parser.add_argument('user_id', help='User ID to export')
    complete_parser.add_argument('--name', help='Export package name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = BackupManager()

    try:
        if args.command == 'backup':
            print("📦 Creating full database backup...")
            path = manager.create_full_backup(args.name)
            print(f"\n✅ Success! Backup saved to:\n   {path}")

        elif args.command == 'export-modules':
            print("📚 Exporting modules...")
            path = manager.export_modules(
                module_ids=args.ids,
                export_name=args.name
            )
            print(f"\n✅ Success! Modules exported to:\n   {path}")

        elif args.command == 'export-profile':
            print(f"👤 Exporting profile for user: {args.user_id}")
            path = manager.export_user_profile(
                user_id=args.user_id,
                export_name=args.name
            )
            print(f"\n✅ Success! Profile exported to:\n   {path}")

        elif args.command == 'import-modules':
            print(f"📥 Importing modules from: {args.file}")
            stats = manager.import_modules(
                import_path=Path(args.file),
                overwrite=args.overwrite
            )
            print(f"\n✅ Import complete!")
            print(f"   Total: {stats['total']}")
            print(f"   Imported: {stats['imported']}")
            print(f"   Updated: {stats['updated']}")
            print(f"   Skipped: {stats['skipped']}")
            if stats['errors']:
                print(f"   Errors: {len(stats['errors'])}")
                for error in stats['errors']:
                    print(f"     - {error}")

        elif args.command == 'import-profile':
            print(f"📥 Importing profile to user: {args.user_id}")
            stats = manager.import_user_profile(
                import_path=Path(args.file),
                new_user_id=args.user_id
            )
            print(f"\n✅ Import complete!")
            print(f"   Profile imported: {stats['profile_imported']}")
            print(f"   Progress records: {stats['progress_records']}")
            print(f"   Concepts: {stats['concepts_imported']}")
            if stats['errors']:
                print(f"   Errors: {len(stats['errors'])}")
                for error in stats['errors']:
                    print(f"     - {error}")

        elif args.command == 'restore':
            print(f"⚠️  Restoring database from: {args.file}")
            print("   This will replace your current database!")
            response = input("   Continue? (yes/no): ")
            if response.lower() == 'yes':
                manager.restore_from_backup(Path(args.file))
                print(f"\n✅ Database restored successfully!")
            else:
                print("   Cancelled.")

        elif args.command == 'complete-export':
            print(f"📦 Creating complete export for user: {args.user_id}")
            path = manager.create_complete_export(
                user_id=args.user_id,
                export_name=args.name
            )
            print(f"\n✅ Success! Complete export created:\n   {path}")

        elif args.command == 'list':
            print("📋 Available backups:\n")
            backups = manager.list_backups()
            if not backups:
                print("   No backups found.")
            else:
                for backup in backups:
                    print(f"   📄 {backup['name']}")
                    print(f"      Type: {backup['type']}")
                    print(f"      Size: {backup['size_mb']} MB")
                    print(f"      Created: {backup['created']}")
                    print(f"      Path: {backup['path']}")
                    print()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
