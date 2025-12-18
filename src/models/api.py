""" Pydantic models for API Validation """

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union
from .core import PersonaType
from datetime import datetime
import re
from .core import PersonaType

class QueryRequest(BaseModel):
    """Pydantic model for API Requests with business logic validation"""
    query: str = Field(..., min_length=1, max_length=1000, description="User query text")
    persona: PersonaType = Field(..., description="Persona type context-aware responses")
    filters: Optional[Dict[str,Any]] = Field(None, description="Optional filters for document retrieval")
    max_results: int = Field(default=10, ge=1,le=50, description="Maximum number of results to return")

    model_config = {"use_enum_values": True}

    @field_validator('query')
    @classmethod
    def validate_query_content(cls, v: str) -> str:
        """ Validate query content for business logic constraints """
        # Remove excessive whitespace
        cleaned_query = re.sub(r'\s+',' ', v.strip())

        if not cleaned_query:
            raise ValueError("Query cannot be empty or only whitespace")
        
        # Check for minimum meanginful content
        if len(cleaned_query.split()) < 2:
            raise ValueError("Query must contain at least 2 words for meaningful results")
        
        # Check for potentially harmful content ( basic SQL injection patterns)
        sql_patterns = [
            r'\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)\b',
            r'[;\'"\\]',
            r'--',
            r'/\*.*\*/'
        ]

        for pattern in sql_patterns:
            if re.search(pattern, cleaned_query, re.IGNORECASE):
                raise ValueError("Query contains potentially harmful content")
        
        return cleaned_query
    
    @field_validator('filter')
    @classmethod
    def validate_filters(cls, v:Optional[Dict[str, Any]]) -> Optional[Dict[str,Any]]:
        """ Validate filter structure and content """
        if v is None:
            return v

        if not isinstance(v,dict):
            raise ValueError("Filters must be a dictionary")

        # Limit filter complexity
        if len(v) > 10:
            raise ValueError("Too many filters specified (maximum 10)")
        
        # Validate filter keys and values
        allowed_filter_keys = {
            'category','source','date_range','author','tags','document_type','priority','status','region','language'
        }

        for key,value in v.items():
            if not isinstance(key,str):
                raise ValueError("Filter keys must be strings")
            
            if key not in allowed_filter_keys:
                raise ValueError(f"Invalid filter key: {key}. Allowed keys: {allowed_filter_keys}")
            
            # validate specific filter types
            if key == 'date_range' and isinstance(value, dict):
                # Basic date validation would go here
                pass
            elif key == 'tags' and isinstance(value,list):
                if len(value) > 20:
                    raise ValueError("Too many tags specified (maximum 20)")
        return v

    @model_validator(mode='after')
    def validate_persona_query_compatibility(self) -> 'QueryRequest':
        """ Validate that query is appropriate for the selected persona """
        persona_keywords = {
            PersonaType.ENTERPRISE_BUYER: ['enterprise', 'scale', 'roi', 'budget','procurement'],
            PersonaType.SMB_DECISION_MAKER: ['small business',' cost-effective','simple','quick'],
            PersonaType.TECHNICAL_EVALUATOR: ['technical','integration','api','security','performance'],
            PersonaType.PROCUREMENT_SPECIALIST: ['vendor','contract','complaince','terms','pricing']
        }

        # This is a soft validation - we don't enforce it strictly but could log warnings
        query_lower = self.query.lower()
        persona_keys = persona_keywords.get(self.persona,[])

        # For now, we just validate that the combination is reasonable
        # In a real system, this might trigger different processing paths

        return self

class QueryRequest(BaseModel):
    """Pydantic model for API Response"""
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: List[Dict[str,Any]]
    persona_context: str
    processing_time_ms: int