from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ==========================================
# Enums
# ==========================================

class SearchIntent(str, Enum):
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"


class OptimizationType(str, Enum):
    CONTENT_DEPTH = "content_depth"
    INTERACTIVE_UX = "interactive_ux"
    SCHEMA_MARKUP = "schema_markup"
    ONPAGE_STRUCTURE = "onpage_structure"
    FRESHNESS_UPDATE = "freshness_update"
    CREDIBILITY_CERTIFICATION = "credibility_certification"
    MULTIMEDIA_EXPANSION = "multimedia_expansion"
    TECHNICAL_SPEED = "technical_speed"


class CitationType(str, Enum):
    AUTHORITATIVE_REFERENCE = "authoritative_reference"
    DATASET_SOURCE = "dataset_source"
    COMPETITOR_REFERENCE = "competitor_reference"
    INDUSTRY_STUDY = "industry_study"


# ==========================================
# 1. Search Query Schemas
# ==========================================

class SearchQueryBase(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Full search query")
    target_keyword: str = Field(..., min_length=2, max_length=255, description="Primary targeted keyword")
    search_intent: SearchIntent = Field(default=SearchIntent.INFORMATIONAL)
    location: Optional[str] = Field(default="Global", max_length=100)


def utc_now():
    return datetime.now(timezone.utc)


class SearchQueryCreate(SearchQueryBase):
    date: Optional[datetime] = Field(default_factory=utc_now)


class SearchQueryUpdate(BaseModel):
    query: Optional[str] = Field(None, min_length=2, max_length=500)
    target_keyword: Optional[str] = Field(None, min_length=2, max_length=255)
    search_intent: Optional[SearchIntent] = None
    location: Optional[str] = None


class SearchQueryResponse(SearchQueryBase):
    id: str
    date: datetime
    results_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. Website Schemas
# ==========================================

class WebsiteBase(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255, description="Domain name (e.g. learnpythonhub.io)")
    title: str = Field(..., min_length=2, max_length=500, description="Page / Site title")
    url: str = Field(..., min_length=5, max_length=1000, description="Full canonical URL")
    content_topic: str = Field(default="General", max_length=255)
    seo_observations: Dict[str, Any] = Field(default_factory=dict, description="Word count, schema types, interactive widgets, etc.")


class WebsiteCreate(WebsiteBase):
    id: Optional[str] = None


class WebsiteUpdate(BaseModel):
    domain: Optional[str] = Field(None, min_length=3, max_length=255)
    title: Optional[str] = Field(None, min_length=2, max_length=500)
    url: Optional[str] = Field(None, min_length=5, max_length=1000)
    content_topic: Optional[str] = None
    seo_observations: Optional[Dict[str, Any]] = None


class WebsiteResponse(WebsiteBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 3. Ranking History Schemas
# ==========================================

class RankingHistoryBase(BaseModel):
    website_id: str
    search_query_id: Optional[str] = None
    keyword: str = Field(..., min_length=2, max_length=255)
    position: int = Field(..., ge=1, le=100, description="Current rank position (1 to 100)")
    previous_position: Optional[int] = Field(None, ge=1, le=100, description="Previous rank position")
    change_in_position: int = Field(default=0, description="Positive = rank gained, negative = rank dropped")

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Position must be at least 1")
        return v


class RankingHistoryCreate(RankingHistoryBase):
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class RankingHistoryResponse(RankingHistoryBase):
    id: str
    domain: Optional[str] = None
    date: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 4. SEO Optimization Schemas
# ==========================================

class SEOOptimizationBase(BaseModel):
    website_id: str
    optimization_type: OptimizationType
    description: str = Field(..., min_length=5, description="Detailed description of changes made")
    reason_for_optimization: str = Field(..., min_length=5, description="Why this optimization was selected")
    expected_effect: str = Field(..., min_length=3, description="Expected ranking / CTR impact")
    observed_effect: Optional[str] = Field(None, description="Actual outcome observed after evaluation")


class SEOOptimizationCreate(SEOOptimizationBase):
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class SEOOptimizationUpdate(BaseModel):
    description: Optional[str] = None
    reason_for_optimization: Optional[str] = None
    expected_effect: Optional[str] = None
    observed_effect: Optional[str] = None


class SEOOptimizationResponse(SEOOptimizationBase):
    id: str
    domain: Optional[str] = None
    date: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 5. Competitor History Schemas
# ==========================================

class CompetitorHistoryBase(BaseModel):
    competitor_website_id: str
    keyword: str = Field(..., min_length=2, max_length=255)
    content_changes: List[str] = Field(default_factory=list, description="Content additions/removals")
    feature_changes: List[str] = Field(default_factory=list, description="Interactive/media feature shifts")
    ranking_changes: Dict[str, Any] = Field(default_factory=dict, description="Rank deltas e.g. before/after")
    notable_seo_changes: List[str] = Field(default_factory=list, description="Schema, canonical, or title changes")


class CompetitorHistoryCreate(CompetitorHistoryBase):
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class CompetitorHistoryResponse(CompetitorHistoryBase):
    id: str
    competitor_domain: Optional[str] = None
    date: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 6. Outcome Schemas
# ==========================================

class OutcomeBase(BaseModel):
    website_id: str
    optimization_id: str
    previous_ranking: int = Field(..., ge=1, le=100)
    new_ranking: int = Field(..., ge=1, le=100)
    observed_change: str = Field(..., min_length=2, description="e.g. +5 positions (#8 to #3)")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    uncertainty_factors: List[str] = Field(default_factory=list, description="Confounders / uncertainty factors")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class OutcomeCreate(OutcomeBase):
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class OutcomeUpdate(BaseModel):
    previous_ranking: Optional[int] = Field(None, ge=1, le=100)
    new_ranking: Optional[int] = Field(None, ge=1, le=100)
    observed_change: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    uncertainty_factors: Optional[List[str]] = None


class OutcomeResponse(OutcomeBase):
    id: str
    domain: Optional[str] = None
    optimization_type: Optional[str] = None
    date: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 7. Content/Citation Information Schemas
# ==========================================

class ContentCitationBase(BaseModel):
    website_id: Optional[str] = None
    search_query_id: Optional[str] = None
    source_title: str = Field(..., min_length=2, max_length=500)
    source_url: str = Field(..., min_length=5, max_length=1000)
    citation_snippet: Optional[str] = None
    citation_type: CitationType = Field(default=CitationType.AUTHORITATIVE_REFERENCE)
    is_used_by_app: bool = Field(default=True)
    citation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata for citations")


class ContentCitationCreate(ContentCitationBase):
    pass


class ContentCitationUpdate(BaseModel):
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    citation_snippet: Optional[str] = None
    citation_type: Optional[CitationType] = None
    is_used_by_app: Optional[bool] = None
    citation_metadata: Optional[Dict[str, Any]] = None


class ContentCitationResponse(ContentCitationBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 8. User Interaction Schemas
# ==========================================

class UserInteractionBase(BaseModel):
    search_query_id: Optional[str] = None
    query_text: str = Field(..., min_length=2, max_length=500)
    selected_website_id: Optional[str] = None
    question_asked: Optional[str] = None
    recommendation_requested: Optional[str] = None
    recommendation_provided: Optional[str] = None
    feedback: Dict[str, Any] = Field(default_factory=dict, description="User rating, thumbs up/down, notes")


class UserInteractionCreate(UserInteractionBase):
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class UserInteractionUpdate(BaseModel):
    feedback: Optional[Dict[str, Any]] = None
    recommendation_provided: Optional[str] = None


class UserInteractionResponse(UserInteractionBase):
    id: str
    selected_domain: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
