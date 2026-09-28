import React from 'react';
import {
  Brain,
  ShieldBan,
  Database,
} from 'lucide-react';
import { HindsightMemoryItem } from '../types';

interface MemoryPanelProps {
  memories: HindsightMemoryItem[];
  suppressedTactics?: string[];
  query: string;
  domain: string;
  loading?: boolean;
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({
  memories,
  suppressedTactics = [],
  query,
  domain,
  loading = false,
}) => {
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
          marginBottom: '18px',
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
            05
          </span>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Brain size={18} color="var(--cyan-primary)" />
              Remembered from Previous SEO Activity
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Empirical experiences recalled from persistent Hindsight memory bank for "{query}" on <strong style={{ color: 'var(--cyan-primary)' }}>{domain}</strong>.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <span
            className="badge"
            style={{
              background: 'rgba(6, 182, 212, 0.12)',
              color: 'var(--cyan-primary)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              padding: '4px 10px',
            }}
          >
            <Database size={13} /> {memories.length} Memories Recalled
          </span>
        </div>
      </div>

      {/* Suppressed Tactics Banner */}
      {suppressedTactics.length > 0 && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '10px',
            padding: '14px 18px',
            marginBottom: '18px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <ShieldBan size={16} color="var(--danger-text)" />
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#fca5a5', textTransform: 'uppercase', letterSpacing: '0.02em' }}>
              Tactics Suppressed by Memory (Empirically Proven Ineffective)
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {suppressedTactics.map((tactic, idx) => (
              <div
                key={idx}
                style={{
                  fontSize: '0.8rem',
                  color: '#fecaca',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px',
                }}
              >
                <span style={{ color: 'var(--danger-text)', fontWeight: 800 }}>✕</span>
                <span>{tactic}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Memories Grid */}
      {loading ? (
        <div style={{ padding: '30px', textAlign: 'center', color: 'var(--cyan-primary)' }}>
          Recalling past SEO experiences from Hindsight...
        </div>
      ) : memories.length === 0 ? (
        <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No memories retrieved yet. Ensure Hindsight is populated with historical cycles.
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '14px',
          }}
        >
          {memories.map((m) => {
            const matchScore = m.relevance_score ? Math.round(m.relevance_score * 100) : 95;
            let categoryColor = 'var(--cyan-primary)';
            if (m.category === 'outcome_history') categoryColor = 'var(--success-text)';
            if (m.category === 'competitor_history') categoryColor = '#c084fc';
            if (m.category === 'optimization_history') categoryColor = '#fbbf24';

            return (
              <div
                key={m.id}
                style={{
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                  transition: 'border-color 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.35)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                }}
              >
                <div>
                  {/* Category & Relevance Badge */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span
                      style={{
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        color: categoryColor,
                        border: `1px solid ${categoryColor}33`,
                      }}
                    >
                      {m.category.replace('_', ' ')}
                    </span>
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        color: matchScore >= 90 ? 'var(--success-text)' : 'var(--cyan-text)',
                      }}
                    >
                      {matchScore}% Relevance
                    </span>
                  </div>

                  {/* Content */}
                  <div style={{ fontSize: '0.84rem', color: '#f1f5f9', lineHeight: 1.45, fontWeight: 500 }}>
                    {m.content}
                  </div>
                </div>

                {/* Why Relevant Footnote */}
                {m.why_relevant && (
                  <div
                    style={{
                      background: 'rgba(6, 182, 212, 0.05)',
                      borderLeft: '2px solid var(--cyan-primary)',
                      padding: '6px 10px',
                      borderRadius: '0 4px 4px 0',
                      fontSize: '0.74rem',
                      color: '#cbd5e1',
                    }}
                  >
                    <strong style={{ color: 'var(--cyan-primary)' }}>Why recalled:</strong> {m.why_relevant}
                  </div>
                )}

                {/* Footer metadata */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.7rem', color: 'var(--text-faint)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px' }}>
                  <span>Bank: {m.bank_id || 'hindsight_bank'}</span>
                  <span>{m.timestamp ? new Date(m.timestamp).toLocaleDateString() : 'Historical'}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
