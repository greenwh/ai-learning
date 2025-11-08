# Backup & Export Guide

Complete guide for backing up, exporting, and importing your learning data.

## 🎯 Why Backup?

- **Protect your progress**: Don't lose weeks of learning data
- **Migrate between machines**: Move your profile to a new computer
- **Share modules**: Export custom modules to share with others
- **Experiment safely**: Try new features with a backup to fall back on
- **Archive old data**: Keep historical records of your learning journey

## 📦 What Can You Backup?

### 1. Full Database Backup
Complete copy of everything:
- All users
- All modules
- All learning sessions
- All progress data
- All learning profiles

**File**: `.db` (SQLite database)

### 2. Module Export
Individual or all modules:
- Module content and configuration
- Learning objectives
- Prerequisites
- Difficulty levels

**File**: `.json` (Human-readable)

### 3. User Profile Export
Your personal learning data:
- Learning style preferences (narrative, interactive, etc.)
- Cognitive patterns
- Module progress
- Concept mastery
- Performance metrics

**File**: `.json` (Human-readable)

### 4. Complete Export Package
Everything bundled together:
- Database backup
- All modules
- User profile

**File**: `.zip` (Compressed archive)

## 🛠️ Using the CLI Tool

### Location
```bash
cd /home/user/Placeholder3/backend
```

### Activate Virtual Environment
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Basic Commands

#### 1. Create Full Database Backup

```bash
python backup_cli.py backup
```

Output:
```
📦 Creating full database backup...
✅ Full backup created: /path/to/backups/full_backup_20240315_143022.db

✅ Success! Backup saved to:
   /path/to/backups/full_backup_20240315_143022.db
```

#### 2. Create Named Backup

```bash
python backup_cli.py backup --name before_experiment
```

Creates: `before_experiment.db`

#### 3. Export All Modules

```bash
python backup_cli.py export-modules
```

Output:
```
📚 Exporting modules...
✅ Exported 5 module(s) to: /path/to/backups/modules_export_20240315_143530.json
```

#### 4. Export Specific Modules

```bash
python backup_cli.py export-modules --ids module_id_1 module_id_2
```

#### 5. Export User Profile

```bash
python backup_cli.py export-profile USER_ID
```

Example:
```bash
python backup_cli.py export-profile abc123-def456
```

Output:
```
👤 Exporting profile for user: abc123-def456
✅ Exported profile for john_doe to: /path/to/backups/profile_john_doe_20240315.json
```

#### 6. Import Modules

```bash
python backup_cli.py import-modules modules_export.json
```

Output:
```
📥 Importing modules from: modules_export.json
✅ Imported module: Stock Fundamentals 101
✅ Imported module: Understanding P/E Ratio
⏭️  Skipped existing module: Warren Buffett's Strategy

✅ Import complete!
   Total: 5
   Imported: 3
   Updated: 0
   Skipped: 2
```

#### 7. Import Modules (Overwrite Existing)

```bash
python backup_cli.py import-modules modules_export.json --overwrite
```

Output:
```
📥 Importing modules from: modules_export.json
✅ Imported module: Stock Fundamentals 101
🔄 Updated module: Understanding P/E Ratio
✅ Imported module: Warren Buffett's Strategy

✅ Import complete!
   Total: 3
   Imported: 1
   Updated: 2
   Skipped: 0
```

#### 8. Import User Profile

```bash
python backup_cli.py import-profile profile_john.json USER_ID
```

Example:
```bash
python backup_cli.py import-profile profile_john_20240315.json abc123-def456
```

Output:
```
📥 Importing profile to user: abc123-def456
✅ Imported learning profile

✅ Import complete!
   Profile imported: True
   Progress records: 8
   Concepts: 15
```

#### 9. Restore Database from Backup

```bash
python backup_cli.py restore full_backup_20240315.db
```

Output:
```
⚠️  Restoring database from: full_backup_20240315.db
   This will replace your current database!
   Continue? (yes/no): yes

💾 Safety backup created: /path/to/backups/pre_restore_20240315_144522.db
✅ Database restored from: full_backup_20240315.db
```

#### 10. List All Backups

```bash
python backup_cli.py list
```

Output:
```
📋 Available backups:

   📄 full_backup_20240315_143022.db
      Type: Full Database Backup
      Size: 2.5 MB
      Created: 2024-03-15T14:30:22
      Path: /path/to/backups/full_backup_20240315_143022.db

   📄 modules_export_20240315_143530.json
      Type: Module Export
      Size: 0.15 MB
      Created: 2024-03-15T14:35:30
      Path: /path/to/backups/modules_export_20240315_143530.json

   📄 profile_john_doe_20240315.json
      Type: User Profile Export
      Size: 0.05 MB
      Created: 2024-03-15T14:38:15
      Path: /path/to/backups/profile_john_doe_20240315.json
```

#### 11. Create Complete Export Package

```bash
python backup_cli.py complete-export USER_ID
```

Example:
```bash
python backup_cli.py complete-export abc123-def456 --name my_complete_backup
```

Creates a ZIP file with:
- Database backup
- All modules
- User profile

## 🌐 Using the API

All backup operations are also available via REST API.

### API Endpoints

#### Create Database Backup

```bash
POST /api/backup/database/backup
```

Example:
```bash
curl -X POST http://localhost:8000/api/backup/database/backup
```

Response:
```json
{
  "success": true,
  "message": "Database backup created successfully",
  "file_path": "/path/to/backup.db",
  "size_mb": 2.5
}
```

#### List All Backups

```bash
GET /api/backup/database/backups
```

#### Export All Modules

```bash
POST /api/backup/modules/export
Content-Type: application/json

{
  "module_ids": null,
  "export_name": "my_modules"
}
```

#### Import Modules

```bash
POST /api/backup/modules/import?file_path=/path/to/modules.json&overwrite=false
```

#### Export User Profile

```bash
POST /api/backup/profile/export?user_id=USER_ID
```

#### Import User Profile

```bash
POST /api/backup/profile/import?file_path=/path/to/profile.json&user_id=USER_ID
```

#### Download Backup File

```bash
GET /api/backup/download/{file_name}
```

## 📂 Backup Storage Location

All backups are stored in:
```
/home/user/Placeholder3/backend/backups/
```

You can change this location by creating a custom `BackupManager`:

```python
from backend.utils.backup import BackupManager
from pathlib import Path

manager = BackupManager(backup_dir=Path("/your/custom/path"))
```

## 🔄 Common Workflows

### Workflow 1: Daily Backup Routine

```bash
# Every day before learning
python backup_cli.py backup --name daily_$(date +%Y%m%d)

# After learning
python backup_cli.py export-profile YOUR_USER_ID
```

### Workflow 2: Moving to New Computer

**On old computer:**
```bash
# Create complete export
python backup_cli.py complete-export YOUR_USER_ID --name migration_package

# Copy the ZIP file to new computer
```

**On new computer:**
```bash
# Setup the system first
cd /home/user/Placeholder3/backend
source venv/bin/activate

# Extract and restore
unzip migration_package.zip
python backup_cli.py restore database.db
python backup_cli.py import-modules modules_export.json --overwrite
python backup_cli.py import-profile profile_USER.json YOUR_NEW_USER_ID
```

### Workflow 3: Sharing Custom Modules

**Create modules:**
```bash
# Create and save your custom modules through the UI
```

**Export for sharing:**
```bash
# Export all modules
python backup_cli.py export-modules --name finance_modules

# Or export specific ones
python backup_cli.py export-modules --ids module1 module2 --name custom_modules

# Share the JSON file with others
```

**Someone else imports:**
```bash
python backup_cli.py import-modules custom_modules.json
```

### Workflow 4: Experimenting Safely

```bash
# Before experimenting
python backup_cli.py backup --name before_experiment

# Experiment with new features...

# If something goes wrong
python backup_cli.py restore before_experiment.db
```

### Workflow 5: Archiving Old Progress

```bash
# Export profile monthly
python backup_cli.py export-profile YOUR_USER_ID --name archive_march_2024

# Store in external backup
mv backups/archive_march_2024.json ~/Dropbox/learning_archives/
```

## 🎓 Understanding Export Files

### Module Export JSON Structure

```json
{
  "export_date": "2024-03-15T14:35:30",
  "module_count": 2,
  "modules": [
    {
      "module_id": "abc-123",
      "domain": "Finance",
      "subject": "Stock Market Investing",
      "topic": "Fundamental Analysis",
      "title": "Stock Fundamentals 101",
      "description": "Learn what stock fundamentals are...",
      "prerequisites": [],
      "learning_objectives": [
        "Explain what fundamentals are",
        "Identify key metrics"
      ],
      "difficulty_level": 1,
      "estimated_time": 15,
      "content_config": {...},
      "version": "1.0",
      "created_at": "2024-03-01T10:00:00"
    }
  ]
}
```

### Profile Export JSON Structure

```json
{
  "export_date": "2024-03-15T14:38:15",
  "user": {
    "user_id": "abc-123",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00"
  },
  "learning_profile": {
    "modality_preferences": {
      "narrative_story": {
        "effectiveness_score": 0.75,
        "sessions_count": 8
      },
      "interactive_hands_on": {
        "effectiveness_score": 0.92,
        "sessions_count": 12
      }
    },
    "cognitive_patterns": {
      "learns_by_doing": true,
      "optimal_session_length": 15
    }
  },
  "module_progress": [...],
  "concept_mastery": [...]
}
```

## 🔒 Security & Privacy

### What's Included in Backups

✅ **Included:**
- Learning progress
- Module content
- Performance metrics
- Learning style preferences

❌ **NOT Included (for privacy):**
- Password hashes (database backup only)
- Email addresses (can be removed from exports)
- Session tokens
- API keys

### Backup Safety

1. **Automatic Safety Backups**: When restoring, system creates a safety backup first
2. **Local Storage**: All backups stored locally, not in cloud
3. **Manual Control**: You decide when to backup and what to export
4. **Encrypted Options**: Can encrypt backup files (see advanced usage)

## 🚨 Troubleshooting

### "Backup file not found"

Check the backups directory:
```bash
ls -la backend/backups/
```

Ensure you're using the full filename including extension.

### "Module already exists" (during import)

Use `--overwrite` flag:
```bash
python backup_cli.py import-modules modules.json --overwrite
```

### "User not found" (during profile import)

Create the user first through the UI or check the user ID.

### "Permission denied"

Ensure the backups directory is writable:
```bash
chmod 755 backend/backups/
```

### "Database locked"

Close the backend server before restoring:
```bash
# Stop the server
# Then restore
python backup_cli.py restore backup.db
# Then start server again
```

## 📅 Recommended Backup Schedule

### Daily
- Quick profile export after learning sessions

### Weekly
- Full database backup
- Export custom modules if created any

### Monthly
- Complete export package
- Store in external backup (Dropbox, Google Drive, etc.)

### Before Major Changes
- Full database backup before:
  - System updates
  - Experimenting with new features
  - Importing external data

## 🎯 Best Practices

1. **Name Your Backups**: Use descriptive names
   - ✅ `before_update_v2.db`
   - ❌ `backup1.db`

2. **Regular Schedule**: Don't wait until data loss

3. **Multiple Locations**: Store important backups externally
   - Cloud storage (Dropbox, Google Drive)
   - External hard drive
   - USB stick

4. **Test Restores**: Periodically test that backups work

5. **Clean Old Backups**: Delete outdated backups to save space
   ```bash
   # Keep last 30 days
   find backend/backups/ -name "*.db" -mtime +30 -delete
   ```

6. **Document Module Changes**: When exporting modules, note what changed

## 🔧 Advanced Usage

### Automated Backups with Cron

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /home/user/Placeholder3/backend && source venv/bin/activate && python backup_cli.py backup --name daily_$(date +\%Y\%m\%d)
```

### Python Script for Custom Backups

```python
from backend.utils.backup import BackupManager

manager = BackupManager()

# Custom backup logic
backup_path = manager.create_full_backup("my_custom_backup")
print(f"Backup created: {backup_path}")

# Export specific modules
manager.export_modules(
    module_ids=["module1", "module2"],
    export_name="important_modules"
)
```

### Selective Import

```python
from backend.utils.backup import BackupManager
import json

manager = BackupManager()

# Load export file
with open("modules.json", 'r') as f:
    data = json.load(f)

# Import only finance modules
finance_modules = [
    m for m in data["modules"]
    if m["domain"] == "Finance"
]

# Save filtered export
with open("finance_only.json", 'w') as f:
    json.dump({"modules": finance_modules}, f)

# Import filtered modules
manager.import_modules("finance_only.json")
```

## 📊 Backup File Sizes

Typical file sizes:

- **Full Database**: 1-5 MB (grows with usage)
- **Module Export**: 10-100 KB per module
- **Profile Export**: 5-50 KB per user
- **Complete Package (ZIP)**: 2-10 MB

## ✅ Checklist: Complete Backup Strategy

- [ ] Daily profile exports
- [ ] Weekly full database backups
- [ ] Monthly complete export packages
- [ ] External backup storage configured
- [ ] Tested restore process at least once
- [ ] Automated backup script (optional)
- [ ] Old backup cleanup routine
- [ ] Documentation of custom modules

Your learning data is valuable - protect it! 🛡️
