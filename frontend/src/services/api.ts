import {
  AuditReport,
  SERPSnapshot,
  MemoryNode,
  OptimizationActionInput,
  MemoryAugmentedAnalysisResponse,
  WebsiteEventTimeline,
  LearningHistoryResponse,
  BeforeAfterComparisonResponse,
  UserFeedbackInput,
  HindsightMemoryItem,
} from '../types';

const API_BASE = '/api/v1';

// ----------------------------------------------------------------------------
// 1. Audit & Snapshot APIs (Legacy & Baseline)
// ----------------------------------------------------------------------------

export async function fetchAuditReport(query: string, targetDomain: string): Promise<AuditReport> {
  const params = new URLSearchParams({ query, target_domain: targetDomain });
  const res = await fetch(`${API_BASE}/audit?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to load audit report: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchSnapshots(query: string): Promise<SERPSnapshot[]> {
  const params = new URLSearchParams({ query });
  const res = await fetch(`${API_BASE}/snapshots?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to load snapshots: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchAttributions(query: string): Promise<MemoryNode[]> {
  const params = new URLSearchParams({ query });
  const res = await fetch(`${API_BASE}/attributions?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to load memory nodes: ${res.statusText}`);
  }
  return res.json();
}

export async function logOptimizationAction(action: OptimizationActionInput) {
  const res = await fetch(`${API_BASE}/actions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action),
  });
  if (!res.ok) {
    throw new Error(`Failed to log action: ${res.statusText}`);
  }
  return res.json();
}

export async function resetDemoState() {
  const res = await fetch(`${API_BASE}/reset-demo`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to reset demo: ${res.statusText}`);
  }
  return res.json();
}

// ----------------------------------------------------------------------------
// 2. Hindsight Memory & Reasoning APIs
// ----------------------------------------------------------------------------

export async function fetchMemoryAnalysis(
  query: string,
  targetDomain?: string,
  userRequest?: string,
  currentPosition?: number
): Promise<MemoryAugmentedAnalysisResponse> {
  const payload: Record<string, any> = {
    query,
    provider: 'local',
    max_memories: 6,
  };
  if (targetDomain) {
    payload.url = `https://${targetDomain}/courses`;
  }
  if (userRequest) {
    payload.user_request = userRequest;
  }
  if (currentPosition !== undefined) {
    payload.current_position = currentPosition;
  }

  const res = await fetch(`${API_BASE}/hindsight/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Analysis failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchRecalledMemories(
  query: string,
  targetDomain?: string,
  maxMemories: number = 6
): Promise<{ memories: HindsightMemoryItem[]; total_recalled: number }> {
  const params = new URLSearchParams({ query, max_memories: String(maxMemories) });
  if (targetDomain) params.append('domain', targetDomain);

  const res = await fetch(`${API_BASE}/hindsight/recall?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to recall memories: ${res.statusText}`);
  }
  return res.json();
}

// ----------------------------------------------------------------------------
// 3. Complete SEO Learning Loop APIs
// ----------------------------------------------------------------------------

export async function fetchWebsiteTimeline(
  website: string,
  keyword?: string
): Promise<WebsiteEventTimeline> {
  const params = new URLSearchParams({ website });
  if (keyword) params.append('keyword', keyword);

  const res = await fetch(`${API_BASE}/learning-loop/timeline?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to load timeline: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchLearningHistory(website: string): Promise<LearningHistoryResponse> {
  const params = new URLSearchParams({ website });
  const res = await fetch(`${API_BASE}/learning-loop/history?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to load learning history: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchBeforeAfterComparison(
  website: string,
  query: string
): Promise<BeforeAfterComparisonResponse> {
  const params = new URLSearchParams({ website, query });
  const res = await fetch(`${API_BASE}/learning-loop/before-after?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to load Before/After comparison: ${res.statusText}`);
  }
  return res.json();
}

export async function recordOptimizationAction(action: {
  website: string;
  keyword: string;
  optimization_type: string;
  title: string;
  description: string;
  reason?: string;
  expected_effect?: string;
}) {
  const res = await fetch(`${API_BASE}/learning-loop/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Action recording failed: ${res.statusText}`);
  }
  return res.json();
}

export async function recordMeasuredOutcome(measurement: {
  website: string;
  keyword: string;
  action_id?: string;
  optimization_title: string;
  optimization_type: string;
  previous_ranking: number;
  new_ranking: number;
  time_period_days?: number;
  confidence?: number;
}) {
  const res = await fetch(`${API_BASE}/learning-loop/measure`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(measurement),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Measurement failed: ${res.statusText}`);
  }
  return res.json();
}

// ----------------------------------------------------------------------------
// 4. User Feedback Submission (Feeds into Hindsight Memory Quality Layer)
// ----------------------------------------------------------------------------

export async function submitUserFeedback(feedback: UserFeedbackInput) {
  // Feed into Hindsight Event Quality Gatekeeper as recommendation_decision / user_feedback
  const payload = {
    event_type: 'recommendation_decision',
    website: feedback.website_domain,
    keyword: feedback.search_query,
    details: {
      recommendation_id: feedback.recommendation_id,
      recommendation_title: feedback.recommendation_title,
      decision: feedback.decision,
      is_useful: feedback.is_useful,
      user_explanation: feedback.explanation,
    },
  };

  const res = await fetch(`${API_BASE}/hindsight/process-event`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Feedback submission failed: ${res.statusText}`);
  }
  return res.json();
}

// ----------------------------------------------------------------------------
// 5. Entity Information APIs (Websites, Rankings, Competitors)
// ----------------------------------------------------------------------------

export async function fetchAllWebsites(): Promise<Array<{ id: string; domain: string; title: string; url: string; content_topic: string }>> {
  const res = await fetch(`${API_BASE}/entities/websites`);
  if (!res.ok) {
    throw new Error(`Failed to list websites: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCompetitorHistory(keyword?: string): Promise<any[]> {
  const params = keyword ? `?keyword=${encodeURIComponent(keyword)}` : '';
  const res = await fetch(`${API_BASE}/entities/competitor-history${params}`);
  if (!res.ok) {
    return [];
  }
  return res.json();
}

export async function fetchWebsiteDetails(websiteId: string, keyword?: string): Promise<any> {
  const [siteRes, ranksRes, optsRes, outsRes, comps] = await Promise.all([
    fetch(`${API_BASE}/entities/websites/${websiteId}`),
    fetch(`${API_BASE}/entities/ranking-history?website_id=${websiteId}`),
    fetch(`${API_BASE}/entities/seo-optimizations?website_id=${websiteId}`),
    fetch(`${API_BASE}/entities/outcomes?website_id=${websiteId}`),
    fetchCompetitorHistory(keyword),
  ]);

  const website = siteRes.ok ? await siteRes.json() : null;
  const rankings = ranksRes.ok ? await ranksRes.json() : [];
  const optimizations = optsRes.ok ? await optsRes.json() : [];
  const outcomes = outsRes.ok ? await outsRes.json() : [];

  return { website, rankings, optimizations, outcomes, competitors: comps };
}

// ----------------------------------------------------------------------------
// 6. General-Purpose Website Intelligence & Hindsight Search APIs
// ----------------------------------------------------------------------------

export async function executeIntelligenceSearch(query: string): Promise<any> {
  const res = await fetch(`${API_BASE}/intelligence/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Intelligence search failed: ${res.statusText}`);
  }
  return res.json();
}

export async function recordWebsiteInteraction(interaction: {
  query: string;
  domain: string;
  url: string;
  rankmind_position: number;
  interaction_type: 'open_website' | 'select_website' | 'rate_useful' | 'rate_not_useful';
  details?: Record<string, any>;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/intelligence/interact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(interaction),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Interaction recording failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchQueryUnderstanding(query: string): Promise<any> {
  const params = new URLSearchParams({ query });
  const res = await fetch(`${API_BASE}/intelligence/understand?${params}`);
  if (!res.ok) {
    throw new Error(`Failed to analyze query: ${res.statusText}`);
  }
  return res.json();
}

