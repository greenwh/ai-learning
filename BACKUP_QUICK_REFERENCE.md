# Backup Quick Reference

## 🚀 Most Common Commands

### Daily Routine

```bash
# Before learning - create backup
cd backend && source venv/bin/activate
python backup_cli.py backup --name daily

# After learning - export profile
python backup_cli.py export-profile YOUR_USER_ID
```

### Export Your Data

```bash
# Export all modules you created
python backup_cli.py export-modules

# Export your learning profile
python backup_cli.py export-profile YOUR_USER_ID

# Export everything (database + modules + profile)
python backup_cli.py complete-export YOUR_USER_ID
```

### Import/Restore

```bash
# Import modules from file
python backup_cli.py import-modules modules_export.json

# Import and overwrite existing modules
python backup_cli.py import-modules modules_export.json --overwrite

# Import profile
python backup_cli.py import-profile profile_export.json YOUR_USER_ID

# Restore full database
python backup_cli.py restore backup_file.db
```

### List & View

```bash
# List all available backups
python backup_cli.py list
```

## 📂 Backup Location

All backups saved to:
```
/home/user/Placeholder3/backend/backups/
```

## 🔄 Moving to New Computer

**Old computer:**
```bash
python backup_cli.py complete-export YOUR_USER_ID --name migration
# Copy the .zip file to new computer
```

**New computer:**
```bash
# Extract and import
unzip migration.zip
python backup_cli.py restore database.db
python backup_cli.py import-modules modules_export.json
python backup_cli.py import-profile profile_USER.json NEW_USER_ID
```

## 🎯 Quick Workflows

### Before Experimenting
```bash
python backup_cli.py backup --name before_experiment
```

### Share Custom Modules
```bash
python backup_cli.py export-modules --name my_modules
# Share the JSON file
```

### Monthly Archive
```bash
python backup_cli.py export-profile YOUR_USER_ID --name archive_$(date +%b_%Y)
```

## 🆘 Emergency Restore

If something goes wrong:

```bash
# List backups
python backup_cli.py list

# Find the most recent backup
# Restore it
python backup_cli.py restore BACKUP_FILE.db
```

## 📝 Get Your User ID

Check the logs when you log in, or:

```bash
sqlite3 backend/data/learning_system.db "SELECT user_id, username FROM users;"
```

## 🌐 Using the Web UI

API endpoint for exports (when backend running):
- Create backup: `POST http://localhost:8000/api/backup/database/backup`
- List backups: `GET http://localhost:8000/api/backup/database/backups`
- Download: `GET http://localhost:8000/api/backup/download/{filename}`

## 📖 Full Documentation

For complete guide, see: **BACKUP_GUIDE.md**
