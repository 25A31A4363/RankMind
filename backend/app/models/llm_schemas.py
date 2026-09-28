from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class LLMAnalysisRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Target search query")
    website_id: Optional[str] = Field(None, description="Database website ID")
    url: Optional[str] = Field(None, description="Custom URL if testing ad-hoc")
    custom_title: Optional[str] = None
    custom_content: Optional[str] = None
    
    # LLM configuration
    provider: Optional[str] = Field(default="auto", description="auto | gemini | openai | local")
    api_key: Optional[str] = Field(default=None, description="Optional API key override (masked in response)")
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=1.0)


class ObservedDataSummary(BaseModel):
    target_query: str
    target_domain: str
    target_url: str
    search_intent_detected: str
    intent_match_score: float
    word_count: int
    title_text: str
    meta_description: str
    h1_text: Optional[str] = None
    h2_count: int
    has_interactive_widget: bool
    has_video_preview: bool
    has_comparison_table: bool
    schema_types_present: List[str]
    missing_schemas_detected: List[str]
    competitor_context_available: Optional[List[Dict[str, Any]]] = None


class WeaknessItem(BaseModel):
    weakness: str
    category: str  # content, technical, ux, metadata
    severity: str  # high, medium, low
    evidence: str


class AIInterpretation(BaseModel):
    seo_diagnosis: str = Field(..., description="High-level diagnosis of current search performance readiness")
    intent_fit_assessment: str = Field(..., description="Assessment of how well the page satisfies user query intent")
    main_weaknesses: List[WeaknessItem]
    evidence_sufficiency_rating: str = Field(default="Sufficient", description="Sufficient | Moderate | Insufficient")
    missing_evidence_or_questions: List[str] = Field(
        default_factory=list,
        description="Explicit questions or missing information when evidence is insufficient to make firm claims"
    )
    disclaimer: str = Field(
        default="AI interpretation derived purely from isolated on-page signals. No historical ranking timeline or causal memory was consulted.",
        description="Truth-discipline disclaimer"
    )


class LLMRecommendationItem(BaseModel):
    id: str
    priority: int
    title: str
    category: str
    reasoning: str = Field(..., description="Detailed heuristic rationale for this recommendation")
    expected_direction_of_improvement: str = Field(..., description="Expected direction (CTR, dwell, rich snippet) without inventing fake historical ranking metrics")
    implementation_steps: List[str]


class LLMAnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    provider_used: str
    query: str
    target_domain: str
    hindsight_memory_applied: bool = Field(default=False, description="Always False at this baseline stage")
    
    # 3 Mandatory Distinct Layers:
    observed_data: ObservedDataSummary
    ai_interpretation: AIInterpretation
    recommendations: List[LLMRecommendationItem]
    
    raw_prompt_sent: Optional[str] = None
    llm_tokens_used: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
