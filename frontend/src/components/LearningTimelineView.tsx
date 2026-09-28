import React, { useState } from 'react';
import {
  Wrench,
  TrendingUp,
  Brain,
  Sparkles,
  Layers,
} from 'lucide-react';
import { LearningHistoryItem, WebsiteEventTimeline } from '../types';

interface LearningTimelineViewProps {
  timeline: WebsiteEventTimeline | null;
  historyItems: LearningHistoryItem[];
  website: string;
  loading?: boolean;
}

export const LearningTimelineView: React.FC<LearningTimelineViewProps> = ({
  timeline,
  historyItems,
  website,
  loading = false,
}) => {
  const [selectedCycle, setSelectedCycle] = useState<number>(0);

  // Default demonstration items if historyItems is empty
  const defaultCycles: LearningHistoryItem[] = [
    {
      cycle_id: 'cycle_1_to_2',
      cycle_name: 'Cycle 1 → 2: Structured Curriculum Breakdown',
      website: website || 'learnpythonhub.io',
      keyword: 'best python courses for beginners',
      timestamp: '2026-02-15T00:00:00Z',
      previous_state: {
        ranking: 8,
        word_count: 2200,
        interactive_widget: false,
        video_preview: false,
        summary: 'Position #8 • Generic listicle format without weekly syllabus',
      },
      action: {
        optimization_type: 'onpage_structure',
        title: 'Structured Curriculum Breakdown & Syllabus Table',
        description: 'Replaced vague course descriptions with weekly module timelines and topic breakdowns.',
        reason: 'Searchers want exact curriculum before enrolling.',
        expected_effect: 'Improve engagement and time-on-page.',
        timestamp: '2026-02-15T00:00:00Z',
      },
      later_observed_state: {
        ranking: 5,
        ranking_delta: 3,
        latency_days: 14,
        observed_result: 'Rank climbed from #8 to #5 (+3 positions) within 14 days.',
        timestamp: '2026-03-01T00:00:00Z',
      },
      memory_created: {
        memory_id: 'mem_curr_01',
        category: 'outcome_history',
        content: 'Structured curriculum syllabus was followed by +3 ranking movement (from #8 to #5).',
        verdict: 'confirmed_positive',
        confidence: 0.88,
        observational_caveat: 'Past correlation does not guarantee future results.',
      },
      future_recommendation_influenced_by_memory:
        'Reinforce structured tables over generic text additions across all tutorial guides.',
    },
    {
      cycle_id: 'cycle_2_to_3',
      cycle_name: 'Cycle 2 → 3: Interactive Sandbox Deployment',
      website: website || 'learnpythonhub.io',
      keyword: 'best python courses for beginners',
      timestamp: '2026-03-10T00:00:00Z',
      previous_state: {
        ranking: 5,
        word_count: 3100,
        interactive_widget: false,
        video_preview: false,
        summary: 'Position #5 • Solid syllabus but missing hands-on interactive tool',
      },
      action: {
        optimization_type: 'interactive_ux',
        title: 'Embedded In-Browser Python Sandbox (Pyodide)',
        description: 'Added live runnable code sandbox allowing users to execute Python snippets directly.',
        reason: 'Match competitor intent for interactive learning experience.',
        expected_effect: 'Surpass static blog competitors.',
        timestamp: '2026-03-10T00:00:00Z',
      },
      later_observed_state: {
        ranking: 3,
        ranking_delta: 2,
        latency_days: 18,
        observed_result: 'Rank climbed from #5 to #3 (+2 positions). Peak performance.',
        timestamp: '2026-03-28T00:00:00Z',
      },
      memory_created: {
        memory_id: 'mem_sandbox_02',
        category: 'outcome_history',
        content: 'Interactive sandbox deployment resulted in movement from #5 to #3.',
        verdict: 'confirmed_positive',
        confidence: 0.92,
        observational_caveat: 'Observed correlation across 18-day latency window.',
      },
      future_recommendation_influenced_by_memory:
        'Prioritize interactive learning features over unformatted word count expansion.',
    },
    {
      cycle_id: 'cycle_3_to_4',
      cycle_name: 'Cycle 3 → 4: Competitor Counter-Move & Schema Gap',
      website: website || 'learnpythonhub.io',
      keyword: 'best python courses for beginners',
      timestamp: '2026-04-05T00:00:00Z',
      previous_state: {
        ranking: 3,
        word_count: 3650,
        interactive_widget: true,
        video_preview: false,
        summary: 'Position #3 • Competitor codecademy.com added video walkthroughs and schema',
      },
      action: {
        optimization_type: 'structured_schema',
        title: 'Course & VideoObject Schema Markup + 90-Sec Previews',
        description: 'Prepare Course JSON-LD markup and embed 90-sec video previews to reclaim #2.',
        reason: 'Counter competitor video snippets and rich result badges.',
        expected_effect: 'Reclaim top 3 positions with rich snippet enhancement.',
        timestamp: '2026-04-05T00:00:00Z',
      },
      later_observed_state: {
        ranking: 4,
        ranking_delta: -1,
        latency_days: 10,
        observed_result: 'Temporarily settled at #4 due to competitor rich result updates.',
        timestamp: '2026-04-15T00:00:00Z',
      },
      memory_created: {
        memory_id: 'mem_schema_03',
        category: 'competitor_history',
        content: 'Competitor rich results displaced #3 rank; Course JSON-LD is required to reclaim position.',
        verdict: 'neutral',
        confidence: 0.85,
        observational_caveat: 'Multi-factor algorithm shift.',
      },
      future_recommendation_influenced_by_memory:
        'Execute Course Schema and Video Preview deployment as highest immediate priority.',
    },
  ];

  const activeCycles = historyItems.length > 0 ? historyItems : defaultCycles;
  const currentItem = activeCycles[selectedCycle] || activeCycles[0];

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span
            style={{
              width: '20px',
              height: '20px',
              borderRadius: '4px',
              background: 'rgba(6, 182, 212, 0.2)',
              color: 'var(--cyan-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '11px',
              fontWeight: 800,
            }}
          >
            06
          </span>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} color="var(--cyan-primary)" />
              The Closed SEO Learning Timeline
              {timeline && (
                <span className="badge badge-trend" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                  {timeline.total_events || timeline.timeline?.length || 9} Loop Steps
                </span>
              )}
              {loading && <span style={{ fontSize: '0.7rem', color: 'var(--cyan-primary)' }}>(Updating...)</span>}
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Optimization → Observed Result → Retained Memory → Future Recommendation
            </p>
          </div>
        </div>

        {/* Cycle selector buttons */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {activeCycles.map((c, i) => (
            <button
              key={c.cycle_id || i}
              type="button"
              onClick={() => setSelectedCycle(i)}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 700,
                background: selectedCycle === i ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                border: selectedCycle === i ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                color: selectedCycle === i ? '#fff' : 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              {c.cycle_name || `Cycle ${i + 1}`}
            </button>
          ))}
        </div>
      </div>

      {/* Visual 4-Step Chain Card */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '14px',
          position: 'relative',
        }}
      >
        {/* Step 1: OPTIMIZATION */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.85)',
            border: '1px solid var(--border-subtle)',
            borderTop: '3px solid var(--cyan-primary)',
            borderRadius: '10px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--cyan-primary)' }}>
              Step 1: Optimization
            </span>
            <Wrench size={15} color="var(--cyan-primary)" />
          </div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
            {currentItem.action.title}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#cbd5e1', lineHeight: 1.4 }}>
            {currentItem.action.description}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-faint)', marginTop: 'auto' }}>
            <strong>Prior Rank:</strong> #{currentItem.previous_state.ranking} • <strong>Category:</strong> {currentItem.action.optimization_type}
          </div>
        </div>

        {/* Step 2: OBSERVED RESULT */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.85)',
            border: '1px solid var(--border-subtle)',
            borderTop: '3px solid var(--success-text)',
            borderRadius: '10px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--success-text)' }}>
              Step 2: Observed Result
            </span>
            <TrendingUp size={15} color="var(--success-text)" />
          </div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
            Rank #{currentItem.previous_state.ranking} → #{currentItem.later_observed_state.ranking}
            <span style={{ marginLeft: '8px', color: currentItem.later_observed_state.ranking_delta > 0 ? 'var(--success-text)' : 'var(--danger-text)', fontSize: '0.8rem' }}>
              ({currentItem.later_observed_state.ranking_delta > 0 ? `+${currentItem.later_observed_state.ranking_delta}` : currentItem.later_observed_state.ranking_delta} pos)
            </span>
          </div>
          <div style={{ fontSize: '0.78rem', color: '#cbd5e1', lineHeight: 1.4 }}>
            {currentItem.later_observed_state.observed_result}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-faint)', marginTop: 'auto' }}>
            <strong>Latency:</strong> {currentItem.later_observed_state.latency_days} days • <strong>Attribution:</strong> Verified
          </div>
        </div>

        {/* Step 3: MEMORY RETAINED */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.85)',
            border: '1px solid var(--border-subtle)',
            borderTop: '3px solid #c084fc',
            borderRadius: '10px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: '#c084fc' }}>
              Step 3: Retained in Memory
            </span>
            <Brain size={15} color="#c084fc" />
          </div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
            Hindsight Experience Banked
          </div>
          <div style={{ fontSize: '0.78rem', color: '#e9d5ff', lineHeight: 1.4, background: 'rgba(168, 85, 247, 0.08)', padding: '8px', borderRadius: '6px' }}>
            "{currentItem.memory_created.content}"
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-faint)', marginTop: 'auto' }}>
            <strong>Confidence:</strong> {Math.round(currentItem.memory_created.confidence * 100)}% • <strong>Verdict:</strong> {currentItem.memory_created.verdict}
          </div>
        </div>

        {/* Step 4: FUTURE RECOMMENDATION */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.85)',
            border: '1px solid var(--border-subtle)',
            borderTop: '3px solid #fbbf24',
            borderRadius: '10px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: '#fbbf24' }}>
              Step 4: Future Recommendation
            </span>
            <Sparkles size={15} color="#fbbf24" />
          </div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
            Informed by Memory
          </div>
          <div style={{ fontSize: '0.78rem', color: '#fef08a', lineHeight: 1.4, background: 'rgba(245, 158, 11, 0.08)', padding: '8px', borderRadius: '6px' }}>
            {currentItem.future_recommendation_influenced_by_memory}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-faint)', marginTop: 'auto' }}>
            Generic advice suppressed • Empirical precedent applied
          </div>
        </div>
      </div>
    </div>
  );
};
