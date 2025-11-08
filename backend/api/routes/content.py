"""
Content management routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.database.models import Module
from backend.api.models import ModuleCreate, ModuleResponse

router = APIRouter()


@router.post("/modules", response_model=ModuleResponse)
async def create_module(
    module_data: ModuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new learning module
    """
    module = Module(
        domain=module_data.domain,
        subject=module_data.subject,
        topic=module_data.topic,
        title=module_data.title,
        description=module_data.description,
        prerequisites=module_data.prerequisites,
        learning_objectives=module_data.learning_objectives,
        difficulty_level=module_data.difficulty_level,
        estimated_time=module_data.estimated_time,
        content_config=module_data.content_config
    )

    db.add(module)
    db.commit()
    db.refresh(module)

    return module


@router.get("/modules", response_model=List[ModuleResponse])
async def list_modules(
    domain: str = None,
    subject: str = None,
    db: Session = Depends(get_db)
):
    """
    List available modules, optionally filtered by domain/subject
    """
    query = db.query(Module)

    if domain:
        query = query.filter(Module.domain == domain)
    if subject:
        query = query.filter(Module.subject == subject)

    modules = query.all()
    return modules


@router.get("/modules/{module_id}", response_model=ModuleResponse)
async def get_module(module_id: str, db: Session = Depends(get_db)):
    """
    Get a specific module by ID
    """
    module = db.query(Module).filter(Module.module_id == module_id).first()

    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    return module
