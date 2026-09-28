from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BaselineAnalysisRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Target search query or keyword")
    website_id: Optional[str] = Field(None, description="ID of a website from the database")
    url: Optional[str] = Field(None, description="URL of the website if analyzing ad-hoc")
    custom_title: Optional[str] = Field(None, description="Optional custom page title")
    custom_meta_description: Optional[str] = Field(None, description="Optional custom meta description")
    custom_content: Optional[str] = Field(None, description="Optional raw text content or page copy")


class TitleAnalysis(BaseModel):
    title_text: str
    char_length: int
    optimal_length_range: str = "50-60 chars"
    is_length_optimal: bool
    contains_target_keyword: bool
    keyword_position: str  # "front", "middle", "end", "missing"
    has_power_words_or_year: bool
    title_status: str  # "optimal", "needs_optimization", "critical_issue"


class MetaDescriptionAnalysis(BaseModel):
    description_text: str
    char_length: int
    optimal_length_range: str = "120-160 chars"
    is_length_optimal: bool
    contains_target_keyword: bool
    has_call_to_action: bool
    truncation_risk: bool
    meta_status: str


class HeadingStructureAnalysis(BaseModel):
    h1_text: Optional[str] = None
    h1_count: int
    h1_contains_keyword: bool
    h2_count: int
    h3_count: int
    has_logical_hierarchy: bool
    scan_friendliness_score: float  # 0-100


class ContentCompleteness(BaseModel):
    word_count: int
    intent_benchmark_word_count: int
    completeness_percentage: float
    estimated_read_time_minutes: int
    readability_score: float  # 0-100
    reading_ease_level: str  # "Easy", "Standard", "Complex"


class KeywordTopicCoverage(BaseModel):
    target_keyword: str
    keyword_density_percentage: float
    keyword_prominence_score: float  # 0-100
    subtopics_detected: List[str]
    subtopics_missing: List[str]
    topic_coverage_score: float  # 0-100


class InternalContentStructure(BaseModel):
    has_comparison_table: bool
    has_curriculum_or_syllabus: bool
    has_table_of_contents: bool
    bullet_list_count: int
    scannability_rating: str  # "High", "Medium", "Low"


class UserExperienceObservations(BaseModel):
    has_interactive_widget: bool
    interactive_widget_type: Optional[str] = None
    has_video_preview: bool
    estimated_dwell_impact: str  # "High", "Moderate", "Low"
    ux_engagement_score: float  # 0-100


class TechnicalSEOObservations(BaseModel):
    canonical_specified: bool
    schema_types_present: List[str]
    missing_high_value_schemas: List[str]
    rich_snippet_readiness: str  # "Ready", "Partial", "Missing"


class CurrentObservations(BaseModel):
    search_intent_detected: str  # "informational", "commercial", "transactional", "navigational"
    intent_match_score: float  # 0-100
    title: TitleAnalysis
    meta_description: MetaDescriptionAnalysis
    headings: HeadingStructureAnalysis
    content_completeness: ContentCompleteness
    keyword_coverage: KeywordTopicCoverage
    internal_structure: InternalContentStructure
    user_experience: UserExperienceObservations
    technical_seo: TechnicalSEOObservations


class ProblemItem(BaseModel):
    id: str
    severity: str  # "high", "medium", "low"
    category: str  # "content", "technical", "ux", "metadata"
    problem: str
    impact: str


class OpportunityItem(BaseModel):
    id: str
    impact_potential: str  # "high", "medium", "low"
    category: str
    opportunity: str
    rationale: str


class RecommendedActionItem(BaseModel):
    id: str
    priority: int  # 1 (Highest) to 5 (Lowest)
    category: str
    action_title: str
    implementation_guide: str
    expected_benefit: str


class BaselineAnalysisResult(BaseModel):
    analysis_id: str
    timestamp: str
    query: str
    target_keyword: str
    target_domain: str
    target_url: str
    
    # Explicit differentiation & baseline flags:
    hindsight_memory_applied: bool = Field(default=False, description="Always False in Baseline Analyzer")
    data_source_type: str = Field(default="synthetic_database", description="synthetic_database | ad_hoc_input | scraped")
    disclaimer: str = Field(
        default="BASELINE STATIC SEO ANALYZER (v1.0 - Zero Hindsight Memory). Evaluates isolated on-page signals. Does NOT use historical ranking memory or competitor causal outcomes.",
        description="Disclaimer stating this is a memory-free static baseline analyzer."
    )
    
    # 4 Mandatory Structured Sections:
    current_observations: CurrentObservations
    problems: List[ProblemItem]
    opportunities: List[OpportunityItem]
    recommended_actions: List[RecommendedActionItem]
    
    # Machine-readable summary for LLM prompt ingestion:
    llm_prompt_summary: str

    model_config = ConfigDict(from_attributes=True)
