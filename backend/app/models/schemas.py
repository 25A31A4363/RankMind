from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ActionCategory(str, Enum):
    CONTENT_DEPTH = "content_depth"
    INTERACTIVE_UX = "interactive_ux"
    SCHEMA_MARKUP = "schema_markup"
    ONPAGE_STRUCTURE = "onpage_structure"
    FRESHNESS_UPDATE = "freshness_update"
    CREDIBILITY_CERTIFICATION = "credibility_certification"
    MULTIMEDIA_EXPANSION = "multimedia_expansion"


class AttributionVerdict(str, Enum):
    CONFIRMED_POSITIVE = "confirmed_positive"   # Significant rank improvement correlated with action
    NEUTRAL = "neutral"                         # No significant rank movement (ineffective)
    CONFIRMED_NEGATIVE = "confirmed_negative"   # Rank dropped following change
    CONFOUNDED = "confounded"                   # Competitor surge or algorithm update confounded the result


class EvidenceTier(str, Enum):
    HISTORICALLY_PROVEN = "historically_proven" # Grounded in past successful outcomes for this query
    COMPETITOR_TREND = "competitor_trend"       # Observed widespread adoption among top 3 rankers
    THEORETICAL_HYPOTHESIS = "theoretical_hypothesis" # Standard SEO thesis without local confirmation


class SERPItem(BaseModel):
    rank: int
    url: str
    domain: str
    title: str
    snippet: str
    word_count: int
    has_interactive_widget: bool
    has_video_preview: bool
    has_curriculum_table: bool
    schema_types: List[str] = Field(default_factory=list)
    last_updated: Optional[str] = None
    readability_score: float = Field(default=75.0, description="0 to 100")
    citation_density: float = Field(default=2.5, description="Citations / links per 1000 words")
    intent_match_score: float = Field(default=80.0, description="0 to 100 intent alignment")


class SERPSnapshot(BaseModel):
    id: str
    query: str
    timestamp: str
    cycle_index: int
    total_results_evaluated: int
    items: List[SERPItem]


class OptimizationAction(BaseModel):
    id: str
    query: str
    target_domain: str
    target_url: str
    timestamp: str
    category: ActionCategory
    title: str
    description: str
    hypothesis: str
    snapshot_before_id: str


class CompetitorDiff(BaseModel):
    id: str
    query: str
    domain: str
    cycle_from: int
    cycle_to: int
    rank_delta: int
    changes_detected: List[str]
    feature_shifts: Dict[str, Any] = Field(default_factory=dict)


class MemoryNode(BaseModel):
    id: str
    query: str
    target_domain: str
    action_id: str
    action_category: ActionCategory
    action_title: str
    date_applied: str
    date_evaluated: str
    latency_days: int
    rank_before: int
    rank_after: int
    rank_delta: int                             # e.g., +4 means moved from #7 to #3
    verdict: AttributionVerdict
    confidence_score: float                     # 0.0 to 1.0
    agent_distilled_lesson: str


class RecommendationItem(BaseModel):
    id: str
    title: str
    category: ActionCategory
    evidence_tier: EvidenceTier
    rationale: str
    expected_impact: str
    historical_precedent: Optional[str] = None
    priority: int                               # 1 (Highest) to 4 (Lowest)


class AuditReport(BaseModel):
    query: str
    target_domain: str
    current_snapshot: SERPSnapshot
    current_rank: Optional[int]
    historical_peak_rank: Optional[int]
    net_velocity_30d: int                       # Rank delta over last 30 days
    
    # Clearly distinct perspectives:
    current_observations: List[str]
    historical_memory: List[MemoryNode]
    observed_outcomes_summary: str
    prescriptive_recommendations: List[RecommendationItem]
