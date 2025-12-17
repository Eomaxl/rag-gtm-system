""" Query processing endpoints """

from fastapi import APIRouter, HTTPException
from src.models.api import QueryRequest, QueryResponse
from src.api.dependencies import QueryProcessorDep
import time

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    query_processor: QueryProcessorDep = None
):
    """Process a query with persona context"""
    try:
        start_time = time.time()
        # This is a placeholder - actual implementation will be in later phase
        response_text = f"Mock response for query: '{request.query}' with persona: {request.persona}"
        processing_time = int((time.time() - start_time) * 1000)

        return QueryResponse(
            answer=response_text,
            confidence=0.85,
            sources=[],
            persona_context=f"Response tailored for {request.persona}",
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query : {str(e)}")
    


