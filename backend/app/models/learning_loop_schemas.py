from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class LearningLoopStage(str, Enum):
    SEARCH = "SEARCH"
    ANALYZE = "ANALYZE"
    RECALL = "RECALL"
    REASON = "REASON"
    RECOMMEND = "RECOMMEND"
    ACTION = "ACTION"
    MEASURE = "MEASURE"
    RETAIN = "RETAIN"
    LEARN = "LEARN"


class LearningLoopEventItem(BaseModel):
    """A single discrete step in the 9-stage SEO Learning Loop."""
    id: str
    step_number: int = Field(..., ge=1, le=9, description="Stage index 1 to 9 in the learning loop")
    stage: LearningLoopStage
    timestamp: str
    website: str
    keyword: str
    title: str
    description: str
    state_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Observed ranking or on-page state at this step")
    details: Dict[str, Any] = Field(default_factory=dict, description="Stage-specific payloads (queries, memories, attributions)")

    model_config = ConfigDict(from_attributes=True)


class WebsiteEventTimeline(BaseModel):
    """Explicit chronological and stage-by-stage event timeline for a website."""
    website: str
    keyword: str
    current_position: int
    total_events: int
    timeline: List[LearningLoopEventItem]

    model_config = ConfigDict(from_attributes=True)


class LearningHistoryItem(BaseModel):
    """A complete empirical learning cycle:
    Previous state -> Action -> Later observed state -> Memory created -> Future recommendation influenced.
    """
    cycle_id: str
    cycle_name: str
    website: str
    keyword: str
    timestamp: str
    
    # 1. Previous state
    previous_state: Dict[str, Any] = Field(
        ...,
        description="State before action (ranking, word count, widgets, schemas, description)"
    )

    # 2. Action
    action: Dict[str, Any] = Field(
        ...,
        description="Optimization action taken (type, title, description, reason, expected effect)"
    )

    # 3. Later observed state
    later_observed_state: Dict[str, Any] = Field(
        ...,
        description="Empirical ranking and telemetry observed after latency window (ranking, delta, latency_days, result)"
    )

    # 4. Memory created
    memory_created: Dict[str, Any] = Field(
        ...,
        description="Hindsight memory node stored (id, category, content, verdict, confidence, observational caveat)"
    )

    # 5. Future recommendation influenced by memory
    future_recommendation_influenced_by_memory: str = Field(
        ...,
        description="Specific strategic change in subsequent recommendations caused by this experience"
    )

    model_config = ConfigDict(from_attributes=True)


class LearningHistoryResponse(BaseModel):
    """Complete collection of learning history cycles for a website."""
    website: str
    keyword: str
    total_cycles: int
    items: List[LearningHistoryItem]

    model_config = ConfigDict(from_attributes=True)


class RecordActionRequest(BaseModel):
    """Input payload to record an optimization action (Step 6 of the loop)."""
    website: str = Field(..., description="Target website domain")
    keyword: str = Field(..., description="Target search query or keyword")
    optimization_type: str = Field(..., description="e.g., interactive_ux | structured_schema | content_depth | multimedia")
    title: str = Field(..., description="Short title of the optimization performed")
    description: str = Field(..., description="Detailed description of the change implemented")
    reason: Optional[str] = Field("Strategic on-page optimization", description="Why this action was taken")
    expected_effect: Optional[str] = Field("Improve search visibility and ranking", description="Anticipated effect")
    timestamp: Optional[str] = None


class RecordMeasureRequest(BaseModel):
    """Input payload to measure later observed ranking and close the loop (Steps 7 & 8)."""
    website: str = Field(..., description="Target website domain")
    keyword: str = Field(..., description="Target search query")
    action_id: Optional[str] = Field(None, description="Optional ID of the action being measured")
    optimization_title: str = Field(..., description="Title of the optimization being measured")
    optimization_type: str = Field(..., description="Category of the optimization")
    previous_ranking: int = Field(..., ge=1, description="Ranking before optimization")
    new_ranking: int = Field(..., ge=1, description="Later observed ranking")
    observed_result: Optional[str] = Field(None, description="e.g., 'Rank moved from #8 to #5 (+3 positions)'")
    time_period_days: Optional[int] = Field(14, ge=1, description="Evaluation window in days")
    confidence: Optional[float] = Field(0.90, ge=0.0, le=1.0, description="Confidence in correlation")
    uncertainty_factors: Optional[List[str]] = Field(default_factory=list, description="Confounding factors or algorithm volatility")
    timestamp: Optional[str] = None


class BeforeAfterComparisonResponse(BaseModel):
    """Visual Before/After comparison demonstrating generic heuristic advice vs institutional memory."""
    website: str
    keyword: str
    demonstration_thesis: str
    
    # BEFORE MEMORY: Generic SEO analysis
    before_memory: Dict[str, Any]
    
    # AFTER MEMORY: Historical context + personalized recommendation
    after_memory: Dict[str, Any]
    
    # Side-by-side contrast matrix
    key_differences_matrix: List[Dict[str, str]]

    model_config = ConfigDict(from_attributes=True)
