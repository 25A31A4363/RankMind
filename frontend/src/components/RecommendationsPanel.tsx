import React, { useState } from 'react';
import { AuditReport, RecommendationItem } from '../types';
import { Eye, History, ArrowRight } from 'lucide-react';

interface RecommendationsPanelProps {
  report: AuditReport;
  onCommitAction: (rec: RecommendationItem) => void;
}

export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({
  report,
  onCommitAction,
}) => {
  const [activeTab, setActiveTab] = useState<'recommendations' | 'observations' | 'outcomes'>('recommendations');

  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      {/* Perspective Tabs Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '14px', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
            Triangulated Intelligence & Recommendations
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Distinguishing live observations, historical precedents, and evidence-tiered recommendations
          </p>
        </div>

        {/* View Switcher */}
        <div style={{ display: 'flex', background: 'var(--bg-app)', padding: '3px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setActiveTab('recommendations')}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              background: activeTab === 'recommendations' ? 'var(--brand-primary)' : 'transparent',
              color: activeTab === 'recommendations' ? '#fff' : 'var(--text-muted)',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Prescriptive Recommendations ({report.prescriptive_recommendations.length})
          </button>
          <button
            onClick={() => setActiveTab('observations')}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              background: activeTab === 'observations' ? 'var(--brand-primary)' : 'transparent',
              color: activeTab === 'observations' ? '#fff' : 'var(--text-muted)',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Current Observations ({report.current_observations.length})
          </button>
          <button
            onClick={() => setActiveTab('outcomes')}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              background: activeTab === 'outcomes' ? 'var(--brand-primary)' : 'transparent',
              color: activeTab === 'outcomes' ? '#fff' : 'var(--text-muted)',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Observed Outcomes Summary
          </button>
        </div>
      </div>

      {/* Tab 1: Prescriptive Recommendations */}
      {activeTab === 'recommendations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {report.prescriptive_recommendations.map((rec) => {
            const isProven = rec.evidence_tier === 'historically_proven';
            const isTrend = rec.evidence_tier === 'competitor_trend';

            return (
              <div
                key={rec.id}
                className="glass-panel-subtle"
                style={{
                  padding: '16px',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          width: '22px',
                          height: '22px',
                          borderRadius: '50%',
                          background: 'rgba(255, 255, 255, 0.08)',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.75rem',
                          fontWeight: 800,
                        }}
                      >
                        {rec.priority}
                      </span>
                      <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#fff' }}>
                        {rec.title}
                      </h3>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      className={`badge ${
                        isProven ? 'badge-proven' : isTrend ? 'badge-trend' : 'badge-hypothesis'
                      }`}
                    >
                      {isProven ? 'Historically Proven' : isTrend ? 'Competitor Trend' : 'Hypothesis'}
                    </span>
                    <button
                      onClick={() => onCommitAction(rec)}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '5px',
                        padding: '5px 10px',
                        borderRadius: '6px',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        background: 'rgba(99, 102, 241, 0.2)',
                        color: 'var(--brand-primary-light)',
                        border: '1px solid var(--brand-primary)',
                        cursor: 'pointer',
                      }}
                    >
                      Commit to Action Plan
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px', lineHeight: '1.5' }}>
                  {rec.rationale}
                </p>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.8rem', background: 'rgba(0, 0, 0, 0.2)', padding: '10px', borderRadius: '6px' }}>
                  <div>
                    <span style={{ color: 'var(--text-faint)', fontWeight: 600 }}>Expected Delta Impact: </span>
                    <span style={{ color: 'var(--success-text)', fontWeight: 700 }}>{rec.expected_impact}</span>
                  </div>
                  {rec.historical_precedent && (
                    <div>
                      <span style={{ color: 'var(--text-faint)', fontWeight: 600 }}>Historical Precedent: </span>
                      <span style={{ color: 'var(--cyan-text)' }}>{rec.historical_precedent}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tab 2: Current Observations */}
      {activeTab === 'observations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {report.current_observations.map((obs, idx) => (
            <div
              key={idx}
              className="glass-panel-subtle"
              style={{
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
              }}
            >
              <Eye size={16} color="var(--brand-primary-light)" style={{ marginTop: '3px', flexShrink: 0 }} />
              <div style={{ fontSize: '0.86rem', color: '#fff', lineHeight: '1.5' }}>{obs}</div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: Observed Outcomes Summary */}
      {activeTab === 'outcomes' && (
        <div
          className="glass-panel-subtle"
          style={{
            padding: '20px',
            borderLeft: '4px solid var(--cyan-text)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <History size={18} color="var(--cyan-text)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff' }}>
              Historical Causal Trajectory Summary
            </h3>
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            {report.observed_outcomes_summary}
          </p>
        </div>
      )}
    </div>
  );
};
