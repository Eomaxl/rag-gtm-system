""" Pydantic models for API Validation """

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union
from .core import PersonaType
from datetime import datetime, UTC
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

class QueryResponse(BaseModel):
    """Response model with confidence scoring and validation"""
    answer: str = Field(..., min_length=1, description="Generated answer text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the answer")
    sources: List[Dict[str,Any]] = Field(..., description="Source documents used for the answer")
    persona_context: str = Field(...,description="Persona-specific context applied")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now(UTC), description="Response timestamp")

    @field_validator('answer')
    @classmethod
    def validate_answer_quality(cls, v:str) -> str:
        """ Validate answer quality and content """
        if not v.strip():
            raise ValueError("Answer cannot be empty")
        
        # Check for minimum answer length for quality
        if len(v.strip()) < 10:
            raise ValueError("Answer is too short - minimum 10 characters required")
        
        # Check for maximum reasonable length
        if len(v) > 10000:
            raise ValueError("Answer is too long - maximum 10000 characters allowed")
        
        return v.strip()
    
    @field_validator('sources')
    @classmethod
    def validate_sources_structure(cls, v: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        """ Validate source documents structure """
        if not isinstance(v, list):
            raise ValueError("Sources must be a list")
        
        required_score_fields = {'id','title','relevance_score'}

        for i, source in enumerate(v):
            if not isinstance(source, dict):
                raise ValueError(f"Source {i} must be a dictionary")
            
            # Check required fields
            missing_fields = required_score_fields - set(source.keys())
            if missing_fields:
                raise ValueError(f"Source {i} missing required fields: {missing_fields}")
            
            # Validate relevant score
            if 'relevance_score' in source:
                score = source['relevance_score']
                if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                    raise ValueError(f"Source {i} relevance_score must be between 0.0 and 1.0")
        
        return v
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence_reasonableness(cls, v: float)-> float:
        """ Validate confidence score reasonableness """
        # Very low confidence might indicate a problem
        if v < 0.1:
            # In a real system, this might trigger additional validation or warnings
            pass

        return v
    
    @model_validator(mode='after')
    def validate_response_consistency(self) -> 'QueryResponse' :
        """ Validate overall response consistency """
        # Check that confidence aligns with source quality
        if self.sources:
            avg_relevance = sum(s.get('relevance_score',0.0) for s in self.sources) / len(self.sources)

            # Confidence shouldn't be much higher than average source relevance
            if self.confidence > avg_relevance + 0.3:
                # In production, this might log a warning or adjust confidence
                pass

        # Validate processing time reasonableness
        if self.processing_time_ms > 30000: # 30 seconds
            # log warning for very slow responses
            pass

        return self
