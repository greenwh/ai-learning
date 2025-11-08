"""
Main FastAPI application for AI-Based Personalized Learning System
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.database import init_db, get_db
from backend.learning_engine import (
    StyleEngine, ContentDeliveryEngine, TutorEngine
)
from backend.api.routes import auth, sessions, content, chat, progress
from backend.api import models as api_models

# Initialize FastAPI app
app = FastAPI(
    title="AI Personalized Learning System",
    description="Discovers how you learn best and teaches you accordingly",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:1420", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print("✅ AI Personalized Learning System ready!")


# Health check
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Personalized Learning System",
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Learning Sessions"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Tutor Chat"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
