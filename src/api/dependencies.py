""" Dependency injection for FastAPI """

from typing import Annotated
from fastapi import Depends

from src.services.protocols import EmbeddingProvider, VectorStore, QueryProcessor

class MockEmbeddingService:
    """ Mock embedding service for initial setup """

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        # Return mock embeddings
        return [[0.1] * 1536 for _ in documents]
    
    async def embed_query(self,query : str) -> list[float]:
        # return mock embedding
        return [0.1] * 1536
    
class MockVectorStore:
    """ Mock vector store for initial setup """

    async def add_documents(self, documents) -> None:
        pass

    async def similarity_search(self, query_embedding: list[float], k: int):
        return []
    
class MockQueryProcessor:
    """ Mock query processor for initial setup """

    async def process_query(self, context) -> str:
        return "Mock response"
    
async def get_embedding_service()-> EmbeddingProvider:
    """Get embedding service instance """
    return MockEmbeddingService()

async def get_vector_service() -> VectorStore:
    """ Get vector store instance """
    return MockVectorStore()

async def get_query_processor() -> QueryProcessor:
    """Get query processor instance"""
    return MockQueryProcessor()

# Type aliases for dependency injection
EmbeddingServiceProvider = Annotated[EmbeddingProvider, Depends(get_embedding_service)]
VectorStoreDep = Annotated[VectorStore, Depends(get_vector_service)]
QueryProcessorDep = Annotated[QueryProcessor, Depends(get_embedding_service)]