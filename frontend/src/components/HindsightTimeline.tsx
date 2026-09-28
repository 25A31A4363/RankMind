import React, { useState } from 'react';
import { SERPSnapshot } from '../types';
import { Milestone } from 'lucide-react';

interface HindsightTimelineProps {
  snapshots: SERPSnapshot[];
  targetDomain?: string;
}

export const HindsightTimeline: React.FC<HindsightTimelineProps> = ({ snapshots }) => {
  const [selectedCycle, setSelectedCycle] = useState<number>(snapshots.length - 1);

  const cycleDetails: Record<number, { title: string; eventBadge: string; eventDesc: string; delta: string; deltaType: 'neutral' | 'positive' | 'negative' }> = {
    0: {
      title: 'T-90d Baseline Ingestion',
      eventBadge: 'Baseline Established',
      eventDesc: 'Initial evaluation of target page against top competitors. Page was a standard text comparison listicle.',
      delta: 'Rank #8',
      deltaType: 'neutral',
    },
    1: {
      title: 'T-60d Evaluation',
      eventBadge: 'Action: +1.6k Word Fluff',
      eventDesc: 'Team added 1,600 words of passive text. Result: Exact same rank (#8). Attribution: Fluff content has zero causal impact.',
      delta: 'Δ 0 (Remained #8)',
      deltaType: 'neutral',
    },
    2: {
      title: 'T-30d Evaluation',
      eventBadge: 'Action: Interactive Sandbox & Matrix',
      eventDesc: 'Added in-browser Python runner & filterable comparison matrix. Result: Decisive surge from #8 to #3 (+5 positions)!',
      delta: 'Δ +5 (#8 → #3)',
      deltaType: 'positive',
    },
    3: {
      title: 'Current Cycle (Today)',
      eventBadge: 'Competitor Counter-Action',
      eventDesc: 'Coursera & freeCodeCamp added video previews & credential schemas. Target slipped slightly from #3 to #4.',
      delta: 'Δ -1 (#3 → #4)',
      deltaType: 'negative',
    },
  };

  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
            Historical Hindsight Trajectory
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Empirical ranking timeline showing action milestones and competitor counter-moves
          </p>
        </div>
        <span className="badge badge-trend">
          4 Recorded Snapshots
        </span>
      </div>

      {/* Cycle Step Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginBottom: '16px' }}>
        {snapshots.map((snap) => {
          const detail = cycleDetails[snap.cycle_index] || {
            title: `Cycle ${snap.cycle_index}`,
            eventBadge: 'Snapshot Recorded',
            eventDesc: 'SERP state archived in Hindsight store.',
            delta: 'Rank Monitored',
            deltaType: 'neutral',
          };
          const isSelected = selectedCycle === snap.cycle_index;

          return (
            <div
              key={snap.id}
              onClick={() => setSelectedCycle(snap.cycle_index)}
              style={{
                padding: '14px',
                borderRadius: '10px',
                cursor: 'pointer',
                background: isSelected ? 'var(--bg-card-hover)' : 'var(--bg-card-subtle)',
                border: isSelected ? '1px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                boxShadow: isSelected ? '0 0 16px rgba(99, 102, 241, 0.25)' : 'none',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-faint)', textTransform: 'uppercase', fontWeight: 700 }}>
                  Cycle {snap.cycle_index}
                </span>
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color:
                      detail.deltaType === 'positive'
                        ? 'var(--success-text)'
                        : detail.deltaType === 'negative'
                        ? 'var(--danger-text)'
                        : 'var(--text-muted)',
                  }}
                >
                  {detail.delta}
                </span>
              </div>

              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff', marginBottom: '6px' }}>
                {detail.title}
              </div>

              <div
                style={{
                  fontSize: '0.72rem',
                  display: 'inline-block',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  color: 'var(--text-muted)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                {detail.eventBadge}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Cycle In-Depth Detail Box */}
      {cycleDetails[selectedCycle] && (
        <div
          style={{
            padding: '16px',
            borderRadius: '8px',
            background: 'rgba(99, 102, 241, 0.06)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
          }}
        >
          <Milestone size={20} color="var(--brand-primary-light)" style={{ marginTop: '2px', flexShrink: 0 }} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                Cycle {selectedCycle} Milestone: {cycleDetails[selectedCycle].title}
              </span>
              <span className="badge badge-proven">
                {cycleDetails[selectedCycle].eventBadge}
              </span>
            </div>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
              {cycleDetails[selectedCycle].eventDesc}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
