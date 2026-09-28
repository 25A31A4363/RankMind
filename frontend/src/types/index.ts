export type ActionCategory =
  | 'content_depth'
  | 'interactive_ux'
  | 'schema_markup'
  | 'onpage_structure'
  | 'freshness_update'
  | 'credibility_certification'
  | 'multimedia_expansion';

export type AttributionVerdict =
  | 'confirmed_positive'
  | 'neutral'
  | 'confirmed_negative'
  | 'confounded';

export type EvidenceTier =
  | 'historically_proven'
  | 'competitor_trend'
  | 'theoretical_hypothesis';

export interface SERPItem {
  rank: number;
  search_position?: number;
  url: string;
  domain: string;
  title: string;
  snippet?: string;
  word_count: number;
  has_interactive_widget: boolean;
  has_video_preview: boolean;
  has_curriculum_table: boolean;
  schema_types: string[];
  last_updated?: string;
  readability_score: number;
  citation_density: number;
  intent_match_score: number;
  historical_movement?: string; // e.g. "+5", "-1", "0"
  confidence_label?: string;

  // General-Purpose Website Intelligence & Evaluation fields
  classification?: {
    resource_type: string;
    access_type: string;
    access_evidence: string;
  };
  resource_type?: string;
  access_type?: string;
  access_evidence?: string;
  rankmind_score?: number;
  factor_breakdown?: {
    relevance_score: number;
    relevance_evidence?: string;
    quality_score: number;
    quality_evidence?: string;
    completeness_score: number;
    completeness_evidence?: string;
    authority_score: number;
    authority_evidence?: string;
    popularity_score?: number | null;
    popularity_label?: string;
    freshness_score?: number | null;
    freshness_label?: string;
    accessibility_score: number;
    accessibility_evidence?: string;
    free_availability_score?: number | null;
    free_availability_label?: string;
    historical_performance_score?: number | null;
    historical_label?: string;
    user_interaction_boost?: number;
    hindsight_memory_boost?: number;
    missing_data_disclaimers?: string[];
  };
  key_points?: string[];
  key_points_source?: string;
  highlighted_content?: string[];
  why_this_position?: {
    summary: string;
    positive_signals: string[];
    data_limitations: string[];
  };
  hindsight_insight?: string;
}

export interface QueryUnderstanding {
  raw_query: string;
  topic: string;
  intent: string;
  user_goal: string;
  entities: string[];
  location?: string | null;
  time_requirement?: string | null;
  audience_level: string;
  price_preference: string;
  price_constraint?: string | null;
  resource_type_preference: string;
  explicit_requirements: string[];
}

export interface WebsiteIntelligenceResponse {
  query: string;
  query_understanding: QueryUnderstanding;
  source_label: string;
  is_live_web: boolean;
  total_candidates_found: number;
  total_after_relevance_filter: number;
  insufficient_results: boolean;
  message?: string | null;
  recalled_hindsight_memories: any[];
  results: SERPItem[];
}

export interface SERPSnapshot {
  id: string;
  query: string;
  timestamp: string;
  cycle_index: number;
  total_results_evaluated: number;
  items: SERPItem[];
}

export interface MemoryNode {
  id: string;
  query: string;
  target_domain: string;
  action_id: string;
  action_category: ActionCategory;
  action_title: string;
  date_applied: string;
  date_evaluated: string;
  latency_days: number;
  rank_before: number;
  rank_after: number;
  rank_delta: number;
  verdict: AttributionVerdict;
  confidence_score: number;
  agent_distilled_lesson: string;
}

export interface RecommendationItem {
  id: string;
  title: string;
  category: ActionCategory;
  evidence_tier: EvidenceTier;
  rationale: string;
  expected_impact: string;
  historical_precedent?: string;
  priority: number;
}

export interface AuditReport {
  query: string;
  target_domain: string;
  current_snapshot: SERPSnapshot;
  current_rank: number | null;
  historical_peak_rank: number | null;
  net_velocity_30d: number;
  current_observations: string[];
  historical_memory: MemoryNode[];
  observed_outcomes_summary: string;
  prescriptive_recommendations: RecommendationItem[];
}

export interface OptimizationActionInput {
  query: string;
  target_domain: string;
  target_url: string;
  category: ActionCategory;
  title: string;
  description: string;
  hypothesis: string;
}

// ----------------------------------------------------------------------------
// Hindsight Memory & Learning Loop Types
// ----------------------------------------------------------------------------

export interface WhyAmISeeingThis {
  current_observation: string;
  recalled_memory: string;
  connection_between_them: string;
  recommendation: string;
  observational_caveat: string;
}

export interface ContextAwareRecommendation {
  id: string;
  priority: number;
  title: string;
  category: string;
  reasoning: string;
  expected_direction_of_improvement: string;
  implementation_steps: string[];
  why_am_i_seeing_this: WhyAmISeeingThis;
}

export interface HindsightMemoryItem {
  id: string;
  bank_id: string;
  category: string;
  content: string;
  target_keyword: string;
  target_domain?: string;
  timestamp: string;
  relevance_score?: number;
  why_relevant?: string;
  metadata?: Record<string, any>;
  tags?: string[];
}

export interface MemoryAugmentedAnalysisResponse {
  analysis_id: string;
  timestamp: string;
  query: string;
  user_request: string;
  target_domain: string;
  hindsight_memory_applied: boolean;
  provider_used: string;
  reasoning_context_assembled: Record<string, any>;
  recalled_memories: HindsightMemoryItem[];
  memory_impact_analysis: Array<{
    recalled_memory_id: string;
    memory_type: string;
    core_learning: string;
    influence_on_recommendations: string;
  }>;
  suppressed_tactics: string[];
  current_information: Record<string, any>;
  current_competitor_information: Array<Record<string, any>>;
  observed_data?: Record<string, any>;
  ai_interpretation_with_memory: {
    seo_diagnosis: string;
    intent_fit_assessment: string;
    main_weaknesses: Array<{
      weakness: string;
      category: string;
      severity: string;
      evidence: string;
    }>;
  };
  context_aware_recommendations: ContextAwareRecommendation[];
  baseline_vs_hindsight_contrast: string;
}

export interface LearningLoopEventItem {
  id: string;
  step_number: number;
  stage: string;
  timestamp: string;
  website: string;
  keyword: string;
  title: string;
  description: string;
  state_snapshot: Record<string, any>;
  details: Record<string, any>;
}

export interface WebsiteEventTimeline {
  website: string;
  keyword: string;
  current_position: number;
  total_events: number;
  timeline: LearningLoopEventItem[];
}

export interface LearningHistoryItem {
  cycle_id: string;
  cycle_name: string;
  website: string;
  keyword: string;
  timestamp: string;
  previous_state: {
    ranking: number;
    word_count?: number;
    interactive_widget?: boolean;
    video_preview?: boolean;
    schema_types?: string[];
    summary?: string;
  };
  action: {
    optimization_type: string;
    title: string;
    description: string;
    reason: string;
    expected_effect: string;
    timestamp: string;
  };
  later_observed_state: {
    ranking: number;
    ranking_delta: number;
    latency_days: number;
    observed_result: string;
    timestamp: string;
  };
  memory_created: {
    memory_id: string;
    category: string;
    content: string;
    verdict: string;
    confidence: number;
    observational_caveat: string;
  };
  future_recommendation_influenced_by_memory: string;
}

export interface LearningHistoryResponse {
  website: string;
  keyword: string;
  total_cycles: number;
  items: LearningHistoryItem[];
}

export interface BeforeAfterComparisonResponse {
  website: string;
  keyword: string;
  demonstration_thesis: string;
  before_memory: {
    mode: string;
    memory_applied: boolean;
    seo_diagnosis: string;
    intent_fit_assessment?: string;
    recommendations: Array<{
      id: string;
      title: string;
      category: string;
      reasoning: string;
      expected_direction_of_improvement?: string;
    }>;
    suppressed_tactics: string[];
    limitations: string;
  };
  after_memory: {
    mode: string;
    memory_applied: boolean;
    recalled_memories_count: number;
    seo_diagnosis: string;
    intent_fit_assessment?: string;
    suppressed_tactics: string[];
    recommendations: Array<{
      id: string;
      title: string;
      category: string;
      reasoning: string;
      expected_direction_of_improvement?: string;
      why_am_i_seeing_this: WhyAmISeeingThis;
    }>;
    strategic_advantage: string;
  };
  key_differences_matrix: Array<{
    dimension: string;
    before_memory: string;
    after_memory: string;
  }>;
}

export interface UserFeedbackInput {
  search_query: string;
  website_domain: string;
  recommendation_id?: string;
  recommendation_title: string;
  decision: 'accepted' | 'rejected';
  is_useful: boolean;
  explanation: string;
}
