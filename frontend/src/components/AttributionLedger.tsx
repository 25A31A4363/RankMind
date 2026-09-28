import React from 'react';
import { MemoryNode } from '../types';
import { Brain, ArrowUpRight, Minus } from 'lucide-react';

interface AttributionLedgerProps {
  memoryNodes: MemoryNode[];
}

export const AttributionLedger: React.FC<AttributionLedgerProps> = ({ memoryNodes }) => {
  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'rgba(56, 189, 248, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Brain size={18} color="var(--cyan-text)" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
              Hindsight Memory Ledger: What Worked vs. What Failed
            </h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Empirical historical attributions linking logged optimizations to observed rank outcomes
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {memoryNodes.map((node) => {
          const isPositive = node.verdict === 'confirmed_positive';
          const isNeutral = node.verdict === 'neutral';

          return (
            <div
              key={node.id}
              className="glass-panel-subtle"
              style={{
                padding: '16px',
                borderLeft: isPositive
                  ? '4px solid var(--success-text)'
                  : isNeutral
                  ? '4px solid var(--warning-text)'
                  : '4px solid var(--danger-text)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.92rem', fontWeight: 700, color: '#fff' }}>
                      {node.action_title}
                    </span>
                    <span
                      className="badge"
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        color: 'var(--text-muted)',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      {node.action_category.replace('_', ' ')}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-faint)', marginTop: '4px' }}>
                    Applied: {node.date_applied} • Evaluated: {node.date_evaluated} ({node.latency_days}d latency)
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase', fontWeight: 700 }}>
                      Rank Delta
                    </span>
                    <div
                      style={{
                        fontSize: '1rem',
                        fontWeight: 800,
                        color: isPositive ? 'var(--success-text)' : 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-end',
                        gap: '4px',
                      }}
                    >
                      {isPositive && <ArrowUpRight size={16} />}
                      {isNeutral && <Minus size={16} />}
                      #{node.rank_before} → #{node.rank_after} ({node.rank_delta >= 0 ? `+${node.rank_delta}` : node.rank_delta})
                    </div>
                  </div>

                  <div>
                    <span
                      className={`badge ${
                        isPositive ? 'badge-proven' : isNeutral ? 'badge-hypothesis' : 'badge-negative'
                      }`}
                    >
                      {node.verdict.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Agent Distilled Lesson */}
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '6px',
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.84rem',
                  lineHeight: '1.5',
                  color: 'var(--text-muted)',
                }}
              >
                <span style={{ fontWeight: 700, color: '#fff', marginRight: '6px' }}>
                  🧠 Agent Distilled Lesson:
                </span>
                {node.agent_distilled_lesson}
                <div style={{ marginTop: '4px', fontSize: '0.75rem', color: 'var(--text-faint)' }}>
                  Attribution Confidence Score: {(node.confidence_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
