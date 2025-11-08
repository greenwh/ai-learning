"""
Backup and Export API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path

from backend.database import get_db
from backend.utils.backup import BackupManager

router = APIRouter()


class BackupResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    size_mb: Optional[float] = None


class BackupInfo(BaseModel):
    name: str
    path: str
    size_mb: float
    created: str
    type: str


class ModuleExportRequest(BaseModel):
    module_ids: Optional[List[str]] = None
    export_name: Optional[str] = None


class ModuleImportRequest(BaseModel):
    overwrite: bool = False


class ImportStats(BaseModel):
    total: int
    imported: int
    updated: int
    skipped: int
    errors: List[str]


class ProfileImportStats(BaseModel):
    profile_imported: bool
    progress_records: int
    concepts_imported: int
    errors: List[str]


@router.post("/database/backup", response_model=BackupResponse)
async def create_database_backup(
    backup_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create a full database backup
    """
    try:
        manager = BackupManager()
        backup_path = manager.create_full_backup(backup_name)

        return BackupResponse(
            success=True,
            message=f"Database backup created successfully",
            file_path=str(backup_path),
            size_mb=round(backup_path.stat().st_size / (1024 * 1024), 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.get("/database/backups", response_model=List[BackupInfo])
async def list_backups():
    """
    List all available backups
    """
    try:
        manager = BackupManager()
        backups = manager.list_backups()
        return backups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing backups: {str(e)}")


@router.post("/modules/export", response_model=BackupResponse)
async def export_modules(
    request: ModuleExportRequest,
    db: Session = Depends(get_db)
):
    """
    Export modules to JSON file
    """
    try:
        manager = BackupManager()
        export_path = manager.export_modules(
            module_ids=request.module_ids,
            export_name=request.export_name
        )

        return BackupResponse(
            success=True,
            message=f"Modules exported successfully",
            file_path=str(export_path),
            size_mb=round(export_path.stat().st_size / (1024 * 1024), 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/modules/import", response_model=ImportStats)
async def import_modules(
    file_path: str,
    overwrite: bool = False,
    db: Session = Depends(get_db)
):
    """
    Import modules from JSON file
    """
    try:
        manager = BackupManager()
        stats = manager.import_modules(
            import_path=Path(file_path),
            overwrite=overwrite
        )
        return stats
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Import file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/profile/export", response_model=BackupResponse)
async def export_profile(
    user_id: str,
    export_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Export user's learning profile
    """
    try:
        manager = BackupManager()
        export_path = manager.export_user_profile(
            user_id=user_id,
            export_name=export_name
        )

        return BackupResponse(
            success=True,
            message=f"Profile exported successfully",
            file_path=str(export_path),
            size_mb=round(export_path.stat().st_size / (1024 * 1024), 2)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/profile/import", response_model=ProfileImportStats)
async def import_profile(
    file_path: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Import user's learning profile
    """
    try:
        manager = BackupManager()
        stats = manager.import_user_profile(
            import_path=Path(file_path),
            new_user_id=user_id
        )
        return stats
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Import file not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/complete/export", response_model=BackupResponse)
async def create_complete_export(
    user_id: str,
    export_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create a complete export package (database + modules + profile)
    """
    try:
        manager = BackupManager()
        export_path = manager.create_complete_export(
            user_id=user_id,
            export_name=export_name
        )

        return BackupResponse(
            success=True,
            message=f"Complete export created successfully",
            file_path=str(export_path),
            size_mb=round(export_path.stat().st_size / (1024 * 1024), 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/download/{file_name}")
async def download_backup(file_name: str):
    """
    Download a backup file
    """
    manager = BackupManager()
    file_path = manager.backup_dir / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type='application/octet-stream'
    )
