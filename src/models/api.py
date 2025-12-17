""" Pydantic models for API Validation """

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .core import PersonaType

class QueryRequest(BaseModel):
    """Pydantic model for API Requests"""
    query: str = Field(..., min_length=1, max_length=1000)
    persona: PersonaType
    filters: Optional[Dict[str,Any]] = None
    max_results: int = Field(default=10, ge=1,le=50)

    model_config = {"use_enum_values": True}

class QueryRequest(BaseModel):
    """Pydantic model for API Response"""
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: List[Dict[str,Any]]
    persona_context: str
    processing_time_ms: int