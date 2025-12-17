""" Health Check endpoints """

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, UTC

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC)
        version="0.1.0"
    )

@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check for kubernetes"""
    return HealthResponse(
        status="ready",
        timestamp=datetime.now(UTC),
        version="0.1.0"
    )