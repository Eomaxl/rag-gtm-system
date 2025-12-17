""" Custom exception hierarchy for RAG system """

from typing import Optional
from datetime import datetime, UTC
import uuid

def generate_correlation_id() -> str:
    """Generate a unique correlation ID"""
    return str(uuid.uuid4())

class RAGSystemError(Exception):
    """Base exception for all RAG system errors """

    def __init__(self, message: str, correlation_id: Optional[str]= None):
        super().__init__(message)
        self.correlation_id = correlation_id or generate_correlation_id
        self.timestamp = datetime.now(UTC)

class DocumentProcessingError(RAGSystemError):
    """Errors during document processing"""
    pass

class EmbeddingServiceError(RAGSystemError):
    """Errors from embedding service"""
    pass

class QueryProcessingError(RAGSystemError):
    """Error during query processing"""
    pass

class InferenceTimeoutError(RAGSystemError):
    """Timeout during model inference"""
    pass

class RateLimitExceededError(RAGSystemError):
    """Rate limit exceeded"""

    def __init__(self, retry_after:int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after

class CircuitBreakerOpenError(RAGSystemError):
    """Circuit breaker is open"""
    pass