from fastapi import APIRouter, HTTPException, Query, status
from typing import Dict, Any

from app.models.intelligence_schemas import (
    WebsiteIntelligenceResponse,
    UserInteractionRequest,
    UserInteractionResponse,
    QueryUnderstanding,
)
from app.services.general_intelligence_engine import (
    general_intelligence_engine,
    QueryUnderstandingEngine,
)

router = APIRouter(prefix="/api/v1/intelligence", tags=["General-Purpose Website Intelligence"])


@router.post(
    "/search",
    response_model=WebsiteIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Search, analyze, recall Hindsight memory, and rank resources for any query",
)
def search_intelligence(payload: Dict[str, Any]) -> WebsiteIntelligenceResponse:
    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty.",
        )
    try:
        response = general_intelligence_engine.process_query(query)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligence pipeline error: {str(e)}",
        )


@router.post(
    "/interact",
    response_model=UserInteractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Record user interaction (open website, select, rate) and retain into Hindsight",
)
def record_interaction(payload: UserInteractionRequest) -> UserInteractionResponse:
    try:
        mem_id, content = general_intelligence_engine.retain_user_interaction(
            query=payload.query,
            domain=payload.domain,
            url=payload.url,
            rankmind_position=payload.rankmind_position,
            interaction_type=payload.interaction_type,
            details=payload.details,
        )
        return UserInteractionResponse(
            status="success",
            message=f"Interaction successfully recorded and retained in Hindsight memory.",
            memory_id=mem_id,
            retained_content=content,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hindsight retention error: {str(e)}",
        )


@router.get(
    "/understand",
    response_model=QueryUnderstanding,
    status_code=status.HTTP_200_OK,
    summary="Directly inspect query understanding output for any query",
)
def inspect_query_understanding(query: str = Query(..., description="Search query to analyze")) -> QueryUnderstanding:
    return QueryUnderstandingEngine.analyze(query)
