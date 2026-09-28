from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.repositories.seo_repository import SEORepository
from app.models.domain_schemas import (
    SearchQueryCreate,
    SearchQueryUpdate,
    SearchQueryResponse,
    WebsiteCreate,
    WebsiteUpdate,
    WebsiteResponse,
    RankingHistoryCreate,
    RankingHistoryResponse,
    SEOOptimizationCreate,
    SEOOptimizationUpdate,
    SEOOptimizationResponse,
    CompetitorHistoryCreate,
    CompetitorHistoryResponse,
    OutcomeCreate,
    OutcomeUpdate,
    OutcomeResponse,
    ContentCitationCreate,
    ContentCitationUpdate,
    ContentCitationResponse,
    UserInteractionCreate,
    UserInteractionUpdate,
    UserInteractionResponse,
)

router = APIRouter(prefix="/entities", tags=["Entities CRUD"])
repo = SEORepository()


# ==========================================
# 1. Search Query Endpoints
# ==========================================
@router.post("/search-queries", response_model=SearchQueryResponse, status_code=status.HTTP_201_CREATED)
def create_search_query(payload: SearchQueryCreate):
    return repo.create_search_query(payload)


@router.get("/search-queries", response_model=List[SearchQueryResponse])
def list_search_queries(limit: int = Query(50, ge=1, le=200)):
    return repo.list_search_queries(limit=limit)


@router.get("/search-queries/{query_id}", response_model=SearchQueryResponse)
def get_search_query(query_id: str):
    res = repo.get_search_query(query_id)
    if not res:
        raise HTTPException(status_code=404, detail="Search query not found")
    return res


@router.patch("/search-queries/{query_id}", response_model=SearchQueryResponse)
def update_search_query(query_id: str, payload: SearchQueryUpdate):
    res = repo.update_search_query(query_id, payload)
    if not res:
        raise HTTPException(status_code=404, detail="Search query not found")
    return res


# ==========================================
# 2. Website Endpoints
# ==========================================
@router.post("/websites", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
def create_website(payload: WebsiteCreate):
    return repo.create_website(payload)


@router.get("/websites", response_model=List[WebsiteResponse])
def list_websites():
    return repo.list_websites()


@router.get("/websites/{website_id}", response_model=WebsiteResponse)
def get_website(website_id: str):
    res = repo.get_website(website_id)
    if not res:
        raise HTTPException(status_code=404, detail="Website not found")
    return res


@router.patch("/websites/{website_id}", response_model=WebsiteResponse)
def update_website(website_id: str, payload: WebsiteUpdate):
    res = repo.update_website(website_id, payload)
    if not res:
        raise HTTPException(status_code=404, detail="Website not found")
    return res


# ==========================================
# 3. Ranking History Endpoints
# ==========================================
@router.post("/ranking-history", response_model=RankingHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_ranking_entry(payload: RankingHistoryCreate):
    return repo.create_ranking_entry(payload)


@router.get("/ranking-history", response_model=List[RankingHistoryResponse])
def list_ranking_history(website_id: str = Query(...), keyword: Optional[str] = None):
    return repo.list_ranking_history(website_id=website_id, keyword=keyword)


# ==========================================
# 4. SEO Optimization Endpoints
# ==========================================
@router.post("/seo-optimizations", response_model=SEOOptimizationResponse, status_code=status.HTTP_201_CREATED)
def create_optimization(payload: SEOOptimizationCreate):
    return repo.create_optimization(payload)


@router.get("/seo-optimizations", response_model=List[SEOOptimizationResponse])
def list_optimizations(website_id: str = Query(...)):
    return repo.list_optimizations(website_id=website_id)


@router.get("/seo-optimizations/{opt_id}", response_model=SEOOptimizationResponse)
def get_optimization(opt_id: str):
    res = repo.get_optimization(opt_id)
    if not res:
        raise HTTPException(status_code=404, detail="Optimization not found")
    return res


@router.patch("/seo-optimizations/{opt_id}", response_model=SEOOptimizationResponse)
def update_optimization(opt_id: str, payload: SEOOptimizationUpdate):
    res = repo.update_optimization(opt_id, payload)
    if not res:
        raise HTTPException(status_code=404, detail="Optimization not found")
    return res


# ==========================================
# 5. Competitor History Endpoints
# ==========================================
@router.post("/competitor-history", response_model=CompetitorHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_competitor_history(payload: CompetitorHistoryCreate):
    return repo.create_competitor_history(payload)


@router.get("/competitor-history", response_model=List[CompetitorHistoryResponse])
def list_competitor_history(competitor_website_id: Optional[str] = None, keyword: Optional[str] = None):
    return repo.list_competitor_history(competitor_website_id=competitor_website_id, keyword=keyword)


# ==========================================
# 6. Outcome (Causal Attribution) Endpoints
# ==========================================
@router.post("/outcomes", response_model=OutcomeResponse, status_code=status.HTTP_201_CREATED)
def create_outcome(payload: OutcomeCreate):
    return repo.create_outcome(payload)


@router.get("/outcomes", response_model=List[OutcomeResponse])
def list_outcomes(website_id: Optional[str] = None):
    return repo.list_outcomes(website_id=website_id)


@router.get("/outcomes/{outcome_id}", response_model=OutcomeResponse)
def get_outcome(outcome_id: str):
    res = repo.get_outcome(outcome_id)
    if not res:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return res


@router.patch("/outcomes/{outcome_id}", response_model=OutcomeResponse)
def update_outcome(outcome_id: str, payload: OutcomeUpdate):
    res = repo.update_outcome(outcome_id, payload)
    if not res:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return res


# ==========================================
# 7. Content / Citation Endpoints
# ==========================================
@router.post("/citations", response_model=ContentCitationResponse, status_code=status.HTTP_201_CREATED)
def create_citation(payload: ContentCitationCreate):
    return repo.create_citation(payload)


@router.get("/citations", response_model=List[ContentCitationResponse])
def list_citations(website_id: Optional[str] = None, only_used: bool = True):
    return repo.list_citations(website_id=website_id, only_used=only_used)


@router.get("/citations/{citation_id}", response_model=ContentCitationResponse)
def get_citation(citation_id: str):
    res = repo.get_citation(citation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Citation not found")
    return res


@router.patch("/citations/{citation_id}", response_model=ContentCitationResponse)
def update_citation(citation_id: str, payload: ContentCitationUpdate):
    res = repo.update_citation(citation_id, payload)
    if not res:
        raise HTTPException(status_code=404, detail="Citation not found")
    return res


# ==========================================
# 8. User Interaction Endpoints
# ==========================================
@router.post("/user-interactions", response_model=UserInteractionResponse, status_code=status.HTTP_201_CREATED)
def create_user_interaction(payload: UserInteractionCreate):
    return repo.create_user_interaction(payload)


@router.get("/user-interactions", response_model=List[UserInteractionResponse])
def list_user_interactions(query_text: Optional[str] = None, website_id: Optional[str] = None):
    return repo.list_user_interactions(query_text=query_text, website_id=website_id)


@router.get("/user-interactions/{interaction_id}", response_model=UserInteractionResponse)
def get_user_interaction(interaction_id: str):
    res = repo.get_user_interaction(interaction_id)
    if not res:
        raise HTTPException(status_code=404, detail="User interaction not found")
    return res


@router.patch("/user-interactions/{interaction_id}", response_model=UserInteractionResponse)
def update_user_interaction(interaction_id: str, payload: UserInteractionUpdate):
    res = repo.update_user_interaction(interaction_id, payload)
    if not res:
        raise HTTPException(status_code=404, detail="User interaction not found")
    return res
