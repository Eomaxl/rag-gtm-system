""" Async PostgreSQL operations with connection pooling """

import asyncio
import logging
from typing import Optional, List, Dict, Any, AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime

import asyncpg
from asyncpg import Pool, Connection

from src.models.exceptions import RAGSystemError

logger = logging.getLogger(__name__)

class DatabaseError(RAGSystemError):
    """ Errors from database operations"""
    pass

class DatabaseConnectionError(DatabaseError):
    """ Database connection errors """
    pass

class DatabaseQueryError(DatabaseError):
    """ Database query execution errors """
    pass

@dataclass(frozen=True)
class DatabaseConfig:
    """ Configuration for database connection pool """
    host: str = "localhost"
    port: int = 5432
    database: str = "rag_system"
    user: str = "postgres"
    password: str = ""
    min_pool_size: int = 10
    max_pool_size: int = 50
    max_queries: int = 50000 # Max queries per connection before recycling
    max_inactive_connection_lifetime: float = 300.0 # 5 minutes
    command_timeout: float = 60.0 # Query timeout in seconds

    @classmethod
    def from_url(cls, url:str) -> "DatabaseConfig":
        """ Create config from database url"""
        # Simple url parsing (in production, use urllib.parse)
        # Format: postgresql://user:password@host:port/database
        if not url.startswith("postgresql://"):
            raise ValueError("Invalid database URL format")
        
        # This is a simplified parser - in production use proper URL parsing
        return cls()
    
class AsyncDatabase:
    """
    Async PostgreSQL database client with connection pooling.

    Demonstrates:
    - Connection pooling for performance
    - Async context managers for resource management
    - Proper connection lifecycle management
    - Transaction support
    - Query timeout handling
    - Connection health checks
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool: Optional[Pool] = None
        self._closed = False

    async def __aenter__(self):
        """ Async context manager entry """
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """ Async context manager exit with proper cleanup """
        await self.close()
        return False
    
    async def connect(self):
        """ Create connection pool """
        if self._pool is not None:
            logger.warning("Database pool already created")
            return
        
        try:
            self_pool = await asyncpg.create_pool(
                host = self.config.host,
                port= self.config.port,
                database = self.config.database,
                user = self.config.user,
                password = self.config.password,
                min_size=self.config.min_pool_size,
                max_size=self.config.max_pool_size,
                max_queries=self.config.max_queries,
                max_inactive_connection_lifetime=self.config.max_inactive_connection_lifetime,
                command_timeout=self.config.command_timeout
            )

            self._closed = False
            logger.info(f"Database pool created : {self.config.min_pool_size} - {self.config.max_pool_size} connections")

            # Initialize schema if needed
            await self._initialize_schema()
        
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to create database pool: {str(e)}") from e
        
    async def close(self):
        """Close connection pool and cleanup resources"""
        if self._closed:
            return

        if self._pool is not None:
            await self._pool.close()
            self._pool = None

        self._closed = True
        logger.info("Database pool closed and resources cleaned up")

    def _ensure_pool(self):
        """Ensure pool is initialized"""
        if self._pool is None or self._closed:
            raise DatabaseError("Database not connected. Use async context manager or call connect()")

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[Connection]:
        """
        Acquire a connection from a pool.

        Usage:
            async with db.acquire() as conn:
                result = await conn.fetch("SELECT * FROM documents")
        """
        self._ensure_pool()

        async with self._pool_acquire() as connection:
            yield connection
           
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[Connection]:
           """ 
           Acquire a connection and start a transaction 
           Usage : 
                async with db.transaction() as conn:
                    await conn.execute("INSERT INTO Documents ....")
                    await conn.execute("UPDATE metadata ...")
                    # Automatically commits on success, rolls back on exception
           """
           self._ensure_pool()

           async with self._pool_acquire() as connection:
               async with connection.transaction():
                   yield connection

    async def execute(
            self,
            query:str,
            *args,
            timeout: Optional[float] = None
    ) -> str:
        """
        Execute a query that doesn't return rows (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query
            *args: Query parameters
            timeout: Override default timeout
        
        Returns:
            Status string from database
        """
        self._ensure_pool()

        try:
            async with self._pool.acquire() as conn:
                return await conn.execute(query, *args, timeout = timeout)
        except asyncpg.QueryCanceledError as e:
            raise DatabaseQueryError(f"Query timeout: {str(e)}")
        except Exception as e:
            raise DatabaseQueryError(f"Query execution failed: {str(e)}") from e
        
    async def fetch(
            self,
            query: str,
            *args,
            timeout: Optional[float] = None 
    ) ->List[Dict[str, Any]]:
        """
        Fetch all rows from a query.

        Args:
            query: SQL query
            *args: Query parameters
            timeout: Override default timeout

        Returns:
            List of rows as dictionaries
        """
        self._ensure_pool()

        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *args, timeout=timeout)
                return [dict(row) for row in rows]
        except asyncpg.QueryCanceledError as e:
            raise DatabaseQueryError(f"Query timeout : {str(e)}") from e
        except Exception as e:
            raise DatabaseQueryError(f"Query execution failed: {str(e)}") from e
        
    async def fetchrow(
            self,
            query: str,
            *args,
            timeout: Optional[float] = None
    ) -> Optional[Dict[str,any]]:
        """ 
        Fetch a single row from a query.
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Override default timeout

        Returns:
            Single row as dictionary or None
        """
        self._ensure_pool()

        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(query, *args, timeout= timeout)
            return dict(row) if row else None
        except asyncpg.QueryCanceledError as e:
            raise DatabaseQueryError(f"Query timeout: {str(e)}") from e
        except Exception as e:
            raise DatabaseQueryError(f"Query execution failed: {str(e)}") from e
        

    async def fetchval(
            self,
            query: str,
            *args,
            column: int = 0,
            timeout: Optional[float] = None
    ) -> Any:
        """
        Fetch a single value from a query.

        Args:
            query: SQL Query
            *args: Query parameters
            column: Column index to return
            timeout: Override default timeout
        
        Returns:
            Single Value
        """
        self._ensure_pool()

        try:
            async with self._pool.acquire() as conn:
                return await conn.fetchval(query, *args, column=column, timeout=timeout)
        except asyncpg.QueryCanceledError as e:
            raise DatabaseQueryError(f"Query timeout: {str(e)}") from e
        except Exception as e:
            raise DatabaseQueryError(f"Query execution failed: {str(e)}") from e

    async def executemany(
        self,
        query: str,
        args: List[tuple],
        timeout: Optional[float] = None
    ) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Useful for batch inserts.
        
        Args:
            query: SQL query
            args: List of parameter tuples
            timeout: Override default timeout
        """
        self._ensure_pool()
        
        try:
            async with self._pool.acquire() as conn:
                await conn.executemany(query, args, timeout=timeout)
        except asyncpg.QueryCanceledError as e:
            raise DatabaseQueryError(f"Query timeout: {str(e)}") from e
        except Exception as e:
            raise DatabaseQueryError(f"Batch execution failed: {str(e)}") from e
    
    async def health_check(self) -> bool:
        """
        Check database connection health.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            self._ensure_pool()
            result = await self.fetchval("SELECT 1")
            return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
        
    async def get_pool_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.
        
        Returns:
            Dictionary with pool statistics
        """
        self._ensure_pool()
        
        return {
            "size": self._pool.get_size(),
            "free_size": self._pool.get_idle_size(),
            "min_size": self._pool.get_min_size(),
            "max_size": self._pool.get_max_size(),
        }
    
# Repository classes for specific entities

class DocumentRepository:
    """ Repository for document operations """
    
    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def create(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any],
        embedding_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """ Create a new document """
        query = """
        INSERT INTO documents (id, content, metadata, embedding_id)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """
        return await self.db.fetchrow(query, doc_id, content, metadata, embedding_id)
    
    async def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """ Get a document by ID """
        query = "SELECT * FROM documents WHERE id = $1"
        return await self.db.fetchrow(query, doc_id)
    
    async def list(
        self,
        limit: int = 100,
        offset: int = 0      
    ) -> List[Dict[str, Any]]:
        """List documents with pagination"""
        query = """
        SELECT * FROM documents
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
        """
        return await self.db.fetch(query,limit,offset)
    
    async def update(
            self,
            doc_id: str,
            content: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """ Update a document """
        if content is not None:
            query = """
            UPDATE documents
            SET content=$2, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING *
            """
            return await self.db.fetchrow(query, doc_id, content)
        elif metadata is not None:
            query = """
            UPDATE documents
            SET metadata = $2, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING *
            """
            return await self.db.fetchrow(query, doc_id, metadata)
        
    async def delete(self, doc_id: str) -> bool:
        """ Delete a document """
        query = "DELETE FROM documents WHERE id = $1"
        result = await self.db.execute(query, doc_id)
        return "DELETE 1" in result
    
    async def count(self) -> int:
        """ Count total documents """
        query = "SELECT COUNT(*) FROM documents"
        return await self.db.fetchval(query)
    
class QueryHistoryRepository:
    """ Repository for query history operations """

    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def create(
        self,
        query: str,
        persona_id: str,
        response: str,
        confidence: float,
        processing_time_ms: int
    ) -> Dict[str, Any]:
        """ Record a query in history """
        sql = """
        INSERT INTO query_history (query, persona_id, response, confidence, processing_time_ms)
        VALUES ( $1, $2, $3, $4 , $5)
        RETURNING *
        """
        return await self.db.fetch(sql, query, persona_id, response, confidence, processing_time_ms)
    
    async def get_recent(
        self,
        persona_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """ Get recent queries """
        if persona_id :
            sql = """
            SELECT * FROM query_history
            WHERE person_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """
            return await self.db.fetch(sql, persona_id, limit)
        else:
            sql = """
            SELECT * FROM query_history
            ORDER BY created_at DESC
            LIMIT BY $1
            """
            return await self.db.fetch(sql, limit)
        
    async def get_stats(self, persona_id: Optional[str] = None) -> Dict[str, Any]:
        """ Get query statistics """
        if persona_id:
            sql = """
            
            """
        