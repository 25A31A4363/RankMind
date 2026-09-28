from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryUnderstanding(BaseModel):
    raw_query: str
    topic: str
    intent: str
    user_goal: str
    entities: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    time_requirement: Optional[str] = None
    audience_level: str = "General"  # Beginner, Student, Intermediate, Advanced, General
    price_preference: str = "Any"    # Free, Freemium, Paid, Any
    price_constraint: Optional[str] = None
    resource_type_preference: str = "General Resource"
    explicit_requirements: List[str] = Field(default_factory=list)


class ResourceClassification(BaseModel):
    resource_type: str  # Tutorial, Documentation, Reference, Article, Guide, Course, Recipe, Review, Comparison, News, Official Website, Forum / Discussion, Video, Research / Paper, Product Information, Other
    access_type: str    # FREE, FREE DOCUMENTATION, FREE TUTORIAL, FREEMIUM, PAID, UNKNOWN
    access_evidence: str


class FactorEvaluation(BaseModel):
    relevance_score: int
    relevance_evidence: str
    quality_score: int
    quality_evidence: str
    completeness_score: int
    completeness_evidence: str
    authority_score: int
    authority_evidence: str
    popularity_score: Optional[int] = None
    popularity_label: str = "Data unavailable"
    freshness_score: Optional[int] = None
    freshness_label: str = "Data unavailable"
    accessibility_score: int
    accessibility_evidence: str
    free_availability_score: Optional[int] = None
    free_availability_label: str = "Data unavailable"
    historical_performance_score: Optional[int] = None
    historical_label: str = "Data unavailable"
    user_interaction_boost: int = 0
    hindsight_memory_boost: int = 0
    missing_data_disclaimers: List[str] = Field(default_factory=list)


class WhyThisPosition(BaseModel):
    summary: str
    positive_signals: List[str] = Field(default_factory=list)
    data_limitations: List[str] = Field(default_factory=list)


class RankedResource(BaseModel):
    rankmind_position: int
    search_position: Optional[int] = None
    domain: str
    title: str
    url: str
    snippet: str
    classification: ResourceClassification
    rankmind_score: int
    factors: FactorEvaluation
    key_points: List[str] = Field(default_factory=list)
    key_points_source: str = "Key points based on available metadata"
    highlighted_content: List[str] = Field(default_factory=list)
    why_this_position: WhyThisPosition
    historical_progression: List[Dict[str, Any]] = Field(default_factory=list)
    hindsight_insight: Optional[str] = None
    word_count: int = 0
    has_interactive_widget: bool = False
    has_video_preview: bool = False
    has_curriculum_table: bool = False
    schema_types: List[str] = Field(default_factory=list)


class WebsiteIntelligenceResponse(BaseModel):
    query: str
    query_understanding: QueryUnderstanding
    source_label: str = "Based on RankMind's available dataset"
    is_live_web: bool = False
    total_candidates_found: int
    total_after_relevance_filter: int
    insufficient_results: bool = False
    message: Optional[str] = None
    recalled_hindsight_memories: List[Dict[str, Any]] = Field(default_factory=list)
    results: List[RankedResource] = Field(default_factory=list)


class UserInteractionRequest(BaseModel):
    query: str
    domain: str
    url: str
    rankmind_position: int
    interaction_type: str = "open_website"  # open_website, select_website, rate_useful, rate_not_useful
    details: Optional[Dict[str, Any]] = None


class UserInteractionResponse(BaseModel):
    status: str
    message: str
    memory_id: Optional[str] = None
    retained_content: Optional[str] = None
