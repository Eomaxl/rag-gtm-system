""" Protocol definitions for service interfaces """

from typing import Protocol, List, AsyncIterator
from src.models.core import Document, QueryContext

class EmbeddingProvider(Protocol):
    """ Protocol for embedding service """

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """ Generate embeddings for a list of documents """
        ...

    async def embed_query(self, query:str) -> List[float]:
        """ Generate embedding for a single query"""
        ...

class VectorStore(Protocol):
    """ Protocol for vector storage backends """

    async def add_documents(self, documents:List[Document]) -> None:
        """ Add documents with embedding to the vector store """
        ...

    async def similarity_search(self, query_embedding: List[float], k: int) -> List[Document]:
        """ Perform similarity search and return top k documents"""
        ...

class QueryProcessor(Protocol):
    """ Protocol for query processing engines"""

    async def process_query(self, context: QueryContext) -> str:
        """Process a query with context and return response """
        ...

class DocumentProcessor(Protocol):
    """ Protocol for document processing services """

    async def process_documents_stream(self, documents: AsyncIterator[str]) -> AsyncIterator[Document]:
        """ Process documents in streaming fashion """
        ...