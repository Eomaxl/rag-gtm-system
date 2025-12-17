""" Configuration management for RAG System """

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """ Applications with environment variable support """

    # Application
    app_name: str = Field(default= "RAG System", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="info", env="LOG_LEVEL")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")

    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")

    # Vector Database
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    pinecone_index_name: Optional[str] = Field(default="rag-documents", env="PINECONE_INDEX_NAME")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Rate-Limiting Configuration
    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_burst_size: int = Field(default= 10, env="RATE_LIMIT_BURST_SIZE")

    # Security
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")

    # Kafka 
    kafka_bootstrap_servers: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_topic_documents: str = Field(default="document-processing", env="KAFKA_TOPIC_DOCUMENTS")
    kafka_topic_queries: str = Field(default="query-processing", env="KAFKA_TOPIC_QUERIES")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="text-embedding-ada-002", env="OPENAI_MODEL")

    model_config = {
        "env_file":".env",
        "env_file_encoding":"utf-8"
    }

#Global setting instance
settings = Settings()