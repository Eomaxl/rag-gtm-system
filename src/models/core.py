""" Core data models with memory optimization """

from typing import Protocol, Optional, AsyncIterator, Dict, Any, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

@dataclass(slots=True)
class Document:
    """Memory optimized document representation"""
    id: str
    content: str
    metadata: Dict[str,Any]
    embedding: Optional[List[float]] = None

@dataclass(slots=True)
class QueryContext:
    """Query context with persona information"""
    query: str
    persona_id: str
    filter: Dict[str, Any]
    max_results: int = 10

class PersonaType(str, Enum):
    """Enumeration of supported personas """
    ENTERPRISE_BUYER = "enterprise_buyer"
    SMB_DECISION_MAKER = "smb_decision_maker"
    TECHNICAL_EVALUATOR = "technical_evaluator"
    PROCUREMENT_SPECIALIST = "procurement_specialist"

@dataclass(slots=True, frozen=True)
class EmbeddingCacheKey:
    """Immutable cache key for embedding"""
    content_hash: str
    model_version: str
    
    def __post__init(self):
        # Validate cache key format
        if not self.content_hash or not self.model_version:
            raise ValueError("Cache key components cannot be empty")

class DocumentChunk:
    """Memory-optimized document chunk with __slots__"""
    __slots__ = ('chunk_id', 'content', 'start_pos', 'end_pos', 'embedding')

    def __init__(self, chunk_id: str, content: str, start_pos: int, end_pos: int):
        self.chunk_id = chunk_id
        self.content = content
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.embedding: Optional[List[float]] = None

class ChunkIterator:
    """Iterator for lazy chunk processing"""

    def __init__(self, document:str, chunk_size: int= 1000):
        self.document = document
        self.chunk_size = chunk_size
        self.position = 0
    
    def __iter__(self):
        return self
    
    def __next__(self) -> DocumentChunk:
        if self.position >= len(self.document):
            raise StopIteration
        
        start = self.position
        end = min(start + self.chunk_size, len(self.document))
        chunk = DocumentChunk(
            chunk_id=f"chunk_{start}_{end}",
            content=self.document[start:end],
            start_pos=start,
            end_pos=end
        )
        self.position = end
        return chunk