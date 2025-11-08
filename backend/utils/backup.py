"""
Backup and Export/Import Utilities
Handles database backups, module exports, and data migration
"""
import json
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import zipfile
import io

from backend.database.models import (
    Module, User, LearningProfile, ModuleProgress,
    LearningSession, ConceptMastery, EngagementSignal,
    ChatMessage, RetentionTest
)
from backend.database.connection import DATABASE_FILE, SessionLocal


class BackupManager:
    """
    Manages backup, export, and import operations
    """

    def __init__(self, backup_dir: Path = None):
        self.backup_dir = backup_dir or Path(__file__).parent.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def create_full_backup(self, backup_name: Optional[str] = None) -> Path:
        """
        Create a complete backup of the database

        Returns:
            Path to the backup file
        """
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"full_backup_{timestamp}"

        backup_path = self.backup_dir / f"{backup_name}.db"

        # Copy the SQLite database file
        shutil.copy2(DATABASE_FILE, backup_path)

        print(f"✅ Full backup created: {backup_path}")
        return backup_path

    def restore_from_backup(self, backup_path: Path) -> bool:
        """
        Restore database from a backup file

        Args:
            backup_path: Path to backup file

        Returns:
            True if successful
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Create a safety backup of current database
        safety_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if DATABASE_FILE.exists():
            shutil.copy2(DATABASE_FILE, safety_backup)
            print(f"💾 Safety backup created: {safety_backup}")

        # Restore from backup
        shutil.copy2(backup_path, DATABASE_FILE)
        print(f"✅ Database restored from: {backup_path}")
        return True

    def export_modules(
        self,
        module_ids: Optional[List[str]] = None,
        export_name: Optional[str] = None
    ) -> Path:
        """
        Export modules to JSON file

        Args:
            module_ids: List of module IDs to export (None = all modules)
            export_name: Name for the export file

        Returns:
            Path to the export file
        """
        db = SessionLocal()

        try:
            # Query modules
            query = db.query(Module)
            if module_ids:
                query = query.filter(Module.module_id.in_(module_ids))

            modules = query.all()

            if not modules:
                raise ValueError("No modules found to export")

            # Convert to dictionaries
            modules_data = []
            for module in modules:
                modules_data.append({
                    "module_id": module.module_id,
                    "domain": module.domain,
                    "subject": module.subject,
                    "topic": module.topic,
                    "title": module.title,
                    "description": module.description,
                    "prerequisites": module.prerequisites,
                    "learning_objectives": module.learning_objectives,
                    "difficulty_level": module.difficulty_level,
                    "estimated_time": module.estimated_time,
                    "content_config": module.content_config,
                    "version": module.version,
                    "created_at": module.created_at.isoformat() if module.created_at else None
                })

            # Create export file
            if not export_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_name = f"modules_export_{timestamp}"

            export_path = self.backup_dir / f"{export_name}.json"

            with open(export_path, 'w') as f:
                json.dump({
                    "export_date": datetime.now().isoformat(),
                    "module_count": len(modules_data),
                    "modules": modules_data
                }, f, indent=2)

            print(f"✅ Exported {len(modules_data)} module(s) to: {export_path}")
            return export_path

        finally:
            db.close()

    def import_modules(
        self,
        import_path: Path,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import modules from JSON file

        Args:
            import_path: Path to JSON export file
            overwrite: Whether to overwrite existing modules

        Returns:
            Dictionary with import statistics
        """
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")

        with open(import_path, 'r') as f:
            data = json.load(f)

        modules_data = data.get("modules", [])
        if not modules_data:
            raise ValueError("No modules found in import file")

        db = SessionLocal()
        stats = {
            "total": len(modules_data),
            "imported": 0,
            "skipped": 0,
            "updated": 0,
            "errors": []
        }

        try:
            for module_data in modules_data:
                try:
                    # Check if module exists
                    existing = db.query(Module).filter(
                        Module.module_id == module_data["module_id"]
                    ).first()

                    if existing and not overwrite:
                        stats["skipped"] += 1
                        print(f"⏭️  Skipped existing module: {module_data['title']}")
                        continue

                    if existing and overwrite:
                        # Update existing module
                        for key, value in module_data.items():
                            if key != "module_id" and hasattr(existing, key):
                                setattr(existing, key, value)
                        stats["updated"] += 1
                        print(f"🔄 Updated module: {module_data['title']}")
                    else:
                        # Create new module
                        # Remove created_at as it will be set automatically
                        module_data.pop("created_at", None)
                        module = Module(**module_data)
                        db.add(module)
                        stats["imported"] += 1
                        print(f"✅ Imported module: {module_data['title']}")

                    db.commit()

                except Exception as e:
                    db.rollback()
                    error_msg = f"Error importing {module_data.get('title', 'unknown')}: {str(e)}"
                    stats["errors"].append(error_msg)
                    print(f"❌ {error_msg}")

            return stats

        finally:
            db.close()

    def export_user_profile(
        self,
        user_id: str,
        export_name: Optional[str] = None
    ) -> Path:
        """
        Export a user's learning profile and progress

        Args:
            user_id: User ID to export
            export_name: Name for the export file

        Returns:
            Path to the export file
        """
        db = SessionLocal()

        try:
            # Get user data
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Get learning profile
            profile = db.query(LearningProfile).filter(
                LearningProfile.user_id == user_id
            ).first()

            # Get module progress
            progress_records = db.query(ModuleProgress).filter(
                ModuleProgress.user_id == user_id
            ).all()

            # Get concept mastery
            concepts = db.query(ConceptMastery).filter(
                ConceptMastery.user_id == user_id
            ).all()

            # Build export data
            export_data = {
                "export_date": datetime.now().isoformat(),
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                },
                "learning_profile": {
                    "modality_preferences": profile.modality_preferences if profile else {},
                    "cognitive_patterns": profile.cognitive_patterns if profile else {},
                    "updated_at": profile.updated_at.isoformat() if profile and profile.updated_at else None
                } if profile else None,
                "module_progress": [
                    {
                        "module_id": p.module_id,
                        "status": p.status,
                        "completion_percentage": p.completion_percentage,
                        "mastery_score": p.mastery_score,
                        "time_spent": p.time_spent,
                        "started_at": p.started_at.isoformat() if p.started_at else None,
                        "completed_at": p.completed_at.isoformat() if p.completed_at else None
                    }
                    for p in progress_records
                ],
                "concept_mastery": [
                    {
                        "concept_id": c.concept_id,
                        "mastery_level": c.mastery_level,
                        "times_practiced": c.times_practiced,
                        "successful_applications": c.successful_applications
                    }
                    for c in concepts
                ]
            }

            # Create export file
            if not export_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_name = f"profile_{user.username}_{timestamp}"

            export_path = self.backup_dir / f"{export_name}.json"

            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(f"✅ Exported profile for {user.username} to: {export_path}")
            return export_path

        finally:
            db.close()

    def import_user_profile(
        self,
        import_path: Path,
        new_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import a user's learning profile

        Args:
            import_path: Path to profile export file
            new_user_id: Optional new user ID (for migrating to different account)

        Returns:
            Dictionary with import statistics
        """
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")

        with open(import_path, 'r') as f:
            data = json.load(f)

        db = SessionLocal()
        stats = {
            "profile_imported": False,
            "progress_records": 0,
            "concepts_imported": 0,
            "errors": []
        }

        try:
            user_id = new_user_id or data["user"]["user_id"]

            # Check if user exists
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise ValueError(f"Target user not found: {user_id}")

            # Import learning profile
            if data.get("learning_profile"):
                profile_data = data["learning_profile"]
                profile = db.query(LearningProfile).filter(
                    LearningProfile.user_id == user_id
                ).first()

                if profile:
                    profile.modality_preferences = profile_data["modality_preferences"]
                    profile.cognitive_patterns = profile_data["cognitive_patterns"]
                else:
                    profile = LearningProfile(
                        user_id=user_id,
                        modality_preferences=profile_data["modality_preferences"],
                        cognitive_patterns=profile_data["cognitive_patterns"]
                    )
                    db.add(profile)

                stats["profile_imported"] = True
                print(f"✅ Imported learning profile")

            # Import module progress
            for progress_data in data.get("module_progress", []):
                try:
                    existing = db.query(ModuleProgress).filter(
                        ModuleProgress.user_id == user_id,
                        ModuleProgress.module_id == progress_data["module_id"]
                    ).first()

                    if existing:
                        # Update existing
                        for key, value in progress_data.items():
                            if key != "module_id" and hasattr(existing, key):
                                setattr(existing, key, value)
                    else:
                        # Create new
                        progress = ModuleProgress(
                            user_id=user_id,
                            **progress_data
                        )
                        db.add(progress)

                    stats["progress_records"] += 1
                except Exception as e:
                    stats["errors"].append(f"Error importing progress: {str(e)}")

            # Import concept mastery
            for concept_data in data.get("concept_mastery", []):
                try:
                    existing = db.query(ConceptMastery).filter(
                        ConceptMastery.user_id == user_id,
                        ConceptMastery.concept_id == concept_data["concept_id"]
                    ).first()

                    if existing:
                        for key, value in concept_data.items():
                            if key != "concept_id" and hasattr(existing, key):
                                setattr(existing, key, value)
                    else:
                        concept = ConceptMastery(
                            user_id=user_id,
                            **concept_data
                        )
                        db.add(concept)

                    stats["concepts_imported"] += 1
                except Exception as e:
                    stats["errors"].append(f"Error importing concept: {str(e)}")

            db.commit()
            print(f"✅ Profile import complete")
            return stats

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def create_complete_export(
        self,
        user_id: str,
        export_name: Optional[str] = None
    ) -> Path:
        """
        Create a complete export package (database + modules + profile)

        Args:
            user_id: User ID to export
            export_name: Name for the export package

        Returns:
            Path to the ZIP file
        """
        if not export_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_name = f"complete_export_{timestamp}"

        # Create temporary directory for exports
        temp_dir = self.backup_dir / f"temp_{export_name}"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Export database
            db_backup = temp_dir / "database.db"
            shutil.copy2(DATABASE_FILE, db_backup)

            # Export all modules
            modules_path = self.export_modules(
                export_name=str(temp_dir / "modules")
            )

            # Export user profile
            profile_path = self.export_user_profile(
                user_id=user_id,
                export_name=str(temp_dir / "profile")
            )

            # Create ZIP file
            zip_path = self.backup_dir / f"{export_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in temp_dir.rglob('*'):
                    if file.is_file():
                        zipf.write(file, file.relative_to(temp_dir))

            print(f"✅ Complete export created: {zip_path}")
            return zip_path

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups

        Returns:
            List of backup information
        """
        backups = []

        for file in self.backup_dir.glob("*"):
            if file.is_file():
                backups.append({
                    "name": file.name,
                    "path": str(file),
                    "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    "type": self._detect_backup_type(file)
                })

        return sorted(backups, key=lambda x: x["created"], reverse=True)

    def _detect_backup_type(self, file: Path) -> str:
        """Detect the type of backup file"""
        name = file.name.lower()

        if name.endswith('.db'):
            if 'full_backup' in name:
                return "Full Database Backup"
            return "Database File"
        elif name.endswith('.json'):
            if 'modules' in name:
                return "Module Export"
            elif 'profile' in name:
                return "User Profile Export"
            return "JSON Export"
        elif name.endswith('.zip'):
            return "Complete Export Package"
        else:
            return "Unknown"


# Convenience functions
def backup_database(name: Optional[str] = None) -> Path:
    """Quick function to backup database"""
    manager = BackupManager()
    return manager.create_full_backup(name)


def export_all_modules(name: Optional[str] = None) -> Path:
    """Quick function to export all modules"""
    manager = BackupManager()
    return manager.export_modules(export_name=name)


def export_my_profile(user_id: str, name: Optional[str] = None) -> Path:
    """Quick function to export user profile"""
    manager = BackupManager()
    return manager.export_user_profile(user_id, name)
