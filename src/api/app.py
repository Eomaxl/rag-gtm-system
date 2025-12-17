""" Fast API Application setup with dependency injection"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from src.api.dependencies import get_embedding_service, get_vector_store, get_query_processor
from src.api.routes import health, documents, queries


# Configuration Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """ Application lifespan management"""
    logger.info("Starting RAG System application")

    # Startup logic here
    yield

    # Shutdown logic here
    logger.info("Shutting down RAG system application")

def create_app() -> FastAPI:
    """ Create and configure FastAPI application"""

    app = FastAPI(
        title="RAG system for GTM strategies",
        description="A production-ready RAG system",
        version="0.1.0",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(queries.router, prefix="/api/v1/queries", tags=["queries"])

    return app

# Create the application instance
app = create_app()