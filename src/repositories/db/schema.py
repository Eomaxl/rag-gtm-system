SCHEMA_SQL = """
-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(255) PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on metadata for faster queries
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING GIN (metadata);

-- Create index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents (created_at);

-- Query history table
CREATE TABLE IF NOT EXISTS query_history (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    persona_id VARCHAR(100),
    response TEXT,
    confidence FLOAT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on persona_id for analytics
CREATE INDEX IF NOT EXISTS idx_query_history_persona ON query_history (persona_id);

-- Create index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON query_history (created_at);

-- Embeddings cache table
CREATE TABLE IF NOT EXISTS embeddings_cache (
    content_hash VARCHAR(64) PRIMARY KEY,
    model_version VARCHAR(50) NOT NULL,
    embedding FLOAT[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 1
);

-- Create index on model_version
CREATE INDEX IF NOT EXISTS idx_embeddings_cache_model ON embeddings_cache (model_version);

-- Create index on accessed_at for cache eviction
CREATE INDEX IF NOT EXISTS idx_embeddings_cache_accessed ON embeddings_cache (accessed_at);
"""
