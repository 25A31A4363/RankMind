from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class MemoryCategory(str, Enum):
    RANKING_HISTORY = "ranking_history"
    OPTIMIZATION_HISTORY = "optimization_history"
    COMPETITOR_HISTORY = "competitor_history"
    OUTCOME_HISTORY = "outcome_history"


class RetentionDecisionEnum(str, Enum):
    REMEMBER = "REMEMBER"
    DO_NOT_REMEMBER = "DO NOT REMEMBER"


class NormalizedMemoryRepresentation(BaseModel):
    """Normalized memory representation containing all required contextual fields:
    event, website, keyword, date, context, action, result, confidence/uncertainty.
    """
    event: str = Field(..., description="Event type: ranking_change | optimization_performed | outcome_observed | competitor_change")
    website: str = Field(..., description="Target website domain or competitor identifier")
    keyword: str = Field(..., description="Target search query or keyword")
    date: str = Field(..., description="ISO 8601 timestamp of the event")
    context: str = Field(..., description="Rich background context (SERP position, intent, market environment)")
    action: str = Field(..., description="Specific optimization, action taken, or competitor change")
    result: str = Field(..., description="Observed empirical ranking movement or SERP impact")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence level in the observation")
    uncertainty_factors: List[str] = Field(default_factory=list, description="Confounders, seasonality, or missing data")
    language_discipline_note: str = Field(
        default="Correlational observation: 'After this change, the observed ranking moved from X to Y' - no definitive causality asserted."
    )


class RawSEOEvent(BaseModel):
    """Raw incoming SEO event submitted to the event-processing layer."""
    event_type: str = Field(
        ...,
        description="ranking_change | optimization_performed | outcome_observed | competitor_change | recommendation_decision | user_feedback"
    )
    website: str
    keyword: str
    date: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class RetentionDecisionResult(BaseModel):
    """Output from the memory-quality layer deciding REMEMBER vs DO NOT REMEMBER."""
    decision: RetentionDecisionEnum
    reason: str = Field(..., description="Explanation of why this event was remembered or ignored")
    importance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    event_type: str
    website: str
    keyword: str
    deduplication_fingerprint: str
    normalized_memory: Optional[NormalizedMemoryRepresentation] = None
    retained_memory_item: Optional[HindsightMemoryItem] = None


class RetentionDecisionLogItem(BaseModel):
    id: str
    timestamp: str
    bank_id: str
    event_type: str
    website: str
    keyword: str
    decision: str
    reason: str
    importance_score: float
    fingerprint: str
    content_snippet: Optional[str] = None
    normalized_data: Dict[str, Any] = Field(default_factory=dict)


class HindsightMemoryItem(BaseModel):
    id: str
    bank_id: str
    category: MemoryCategory
    content: str
    target_keyword: str
    target_domain: Optional[str] = None
    timestamp: str
    relevance_score: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    why_relevant: Optional[str] = Field(default=None, description="Explanation of why this memory was recalled")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class HindsightRetainRequest(BaseModel):
    bank_id: Optional[str] = "rankmind-seo"
    category: MemoryCategory
    content: str = Field(..., min_length=5)
    target_keyword: str
    target_domain: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class HindsightRecallRequest(BaseModel):
    bank_id: Optional[str] = "rankmind-seo"
    query: str
    target_domain: Optional[str] = None
    categories: Optional[List[MemoryCategory]] = None
    max_tokens: Optional[int] = 4096
    max_memories: Optional[int] = 6


class HindsightRecallResponse(BaseModel):
    bank_id: str
    query: str
    target_domain: Optional[str] = None
    total_recalled: int
    memories: List[HindsightMemoryItem]
    relevance_summary: str
    audit_log_id: str


class RetentionLogItem(BaseModel):
    id: str
    timestamp: str
    bank_id: str
    category: MemoryCategory
    target_keyword: str
    target_domain: Optional[str] = None
    content_snippet: str
    tags: List[str]


class RecallLogItem(BaseModel):
    id: str
    timestamp: str
    bank_id: str
    query: str
    target_domain: Optional[str] = None
    recalled_count: int
    recalled_memory_ids: List[str]
    why_relevant_summary: str


class WhyAmISeeingThis(BaseModel):
    """Transparent explanation linking current observation and recalled memory to recommendation."""
    current_observation: str = Field(..., description="Factual signal or ranking observed on current website")
    recalled_memory: str = Field(..., description="Exact historical memory fact or outcome retrieved from Hindsight")
    connection_between_them: str = Field(..., description="Strategic rationale connecting the historical outcome to current situation")
    recommendation: str = Field(..., description="Prescribed context-aware action")
    observational_caveat: str = Field(
        default="Historical relationship is observational and not guaranteed; external SERP algorithm shifts remain confounding variables.",
        description="Explicit caution that past correlation does not guarantee future results"
    )


class ContextAwareRecommendation(BaseModel):
    """Enriched recommendation with transparent 'Why am I seeing this recommendation?' section."""
    id: str
    priority: int
    title: str
    category: str
    reasoning: str
    expected_direction_of_improvement: str
    implementation_steps: List[str] = Field(default_factory=list)
    why_am_i_seeing_this: WhyAmISeeingThis


class MemoryAugmentedAnalysisRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    website_id: Optional[str] = None
    url: Optional[str] = None
    user_request: Optional[str] = Field(
        default=None,
        description="Optional custom user goal or prompt (e.g., 'How to improve ranking from #8?')"
    )
    current_position: Optional[int] = Field(default=None, description="Optional override for current ranking position")
    provider: Optional[str] = "auto"
    api_key: Optional[str] = None
    max_memories: Optional[int] = 6


class MemoryImpactItem(BaseModel):
    recalled_memory_id: str
    memory_type: str
    core_learning: str
    influence_on_recommendations: str


class MemoryAugmentedAnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    query: str
    user_request: str
    target_domain: str
    hindsight_memory_applied: bool = True
    provider_used: str
    
    # 4-Layer Reasoning Context Assembled
    reasoning_context_assembled: Dict[str, Any] = Field(
        default_factory=dict,
        description="The 4 assembled layers: CURRENT INFORMATION + RELEVANT HISTORICAL MEMORY + CURRENT COMPETITOR INFORMATION + USER REQUEST"
    )

    # Recalled Hindsight Context
    recalled_memories: List[HindsightMemoryItem]
    memory_impact_analysis: List[MemoryImpactItem]
    suppressed_tactics: List[str] = Field(
        default_factory=list,
        description="Standard generic tactics explicitly suppressed because past Hindsight memory proved them ineffective"
    )

    # 4 Core Structured Layers:
    current_information: Dict[str, Any]
    current_competitor_information: List[Dict[str, Any]] = Field(default_factory=list)
    observed_data: Optional[Dict[str, Any]] = None
    ai_interpretation_with_memory: Dict[str, Any]
    context_aware_recommendations: List[ContextAwareRecommendation]
    
    # Comparison Against Static Baseline
    baseline_vs_hindsight_contrast: str

    model_config = ConfigDict(from_attributes=True)
