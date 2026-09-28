import React, { useState } from 'react';
import { BeforeAfterComparisonResponse } from '../types';

interface BeforeAfterToggleProps {
  comparison: BeforeAfterComparisonResponse | null;
  loading?: boolean;
}

export const BeforeAfterToggle: React.FC<BeforeAfterToggleProps> = ({
  comparison,
  loading = false,
}) => {
  const [mode, setMode] = useState<'with_memory' | 'without_memory'>('with_memory');

  if (loading && !comparison) {
    return (
      <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--cyan-primary)' }}>
        Generating Before / After Memory contrast comparison...
      </div>
    );
  }

  const beforeRecs = comparison?.before_memory.recommendations || [
    {
      id: 'rec_before_1',
      title: 'Expand Article Word Count to 5,000+ Words',
      category: 'content_depth',
      reasoning: 'Standard SEO advice suggests longer content ranks higher in competitive programming niches.',
    },
    {
      id: 'rec_before_2',
      title: 'Repeat Target Keyword "best python courses" in 5 More Subheadings',
      category: 'onpage_keywords',
      reasoning: 'Increase keyword density from 1.2% to 2.5% to trigger algorithmic topical relevance.',
    },
  ];

  const afterRecs = comparison?.after_memory.recommendations || [
    {
      id: 'rec_after_1',
      title: 'Deploy Course & VideoObject Schema JSON-LD + 90-Sec Previews',
      category: 'structured_schema',
      reasoning: 'Hindsight memory demonstrates in Cycle 2 that structured syllabus & interactive sandboxes lifted position by +3, whereas raw word count expansion in Cycle 2 produced zero ranking movement.',
      why_am_i_seeing_this: {
        current_observation: 'Missing Course JSON-LD schema while competitor codecademy.com holds rich snippet badges.',
        recalled_memory: 'In Cycle 2, expanding word count to 4,500w without interactive utility produced +0 movement.',
        connection_between_them: 'Top ranking positions #1-#3 strictly require rich structured snippets and code playground.',
        recommendation: 'Implement Schema.org markup and short project previews rather than adding unneeded text.',
        observational_caveat: 'Observed ranking correlation from past cycles does not guarantee immediate indexing.',
      },
    },
  ];

  const suppressedTactics = comparison?.after_memory.suppressed_tactics || [
    'Bulk 2,000-word text expansion without structure (Cycle 2 proved 0 ranking lift)',
    'Keyword density stuffing (Ignored by intent matching algorithms)',
  ];

  const matrix = comparison?.key_differences_matrix || [
    {
      dimension: 'Diagnostic Strategy',
      before_memory: 'Static checklist based on general heuristics',
      after_memory: 'Dynamic synthesis of current SERP + historical site movements',
    },
    {
      dimension: 'Tactic Suppression',
      before_memory: 'None (Repeats previously failed tactics over and over)',
      after_memory: 'Suppresses tactics empirically proven ineffective in past cycles',
    },
    {
      dimension: 'Evidence Basis',
      before_memory: 'Theoretical general best-practices',
      after_memory: 'Direct attribution from past optimizations on this exact keyword',
    },
    {
      dimension: 'Transparency',
      before_memory: 'Black box generic output',
      after_memory: 'Full "Why am I seeing this?" transparent breakdown',
    },
  ];

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Header with Prominent Toggle */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
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
            07
          </span>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff' }}>
              Before / After Memory Toggle
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Inspect how persistent Hindsight memory fundamentally shifts recommendations from generic checklists to competitive intelligence.
            </p>
          </div>
        </div>

        {/* Toggle Switch */}
        <div
          style={{
            display: 'inline-flex',
            background: '#090e1c',
            border: '1px solid var(--border-subtle)',
            borderRadius: '12px',
            padding: '4px',
            boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)',
          }}
        >
          <button
            type="button"
            onClick={() => setMode('without_memory')}
            style={{
              padding: '8px 18px',
              borderRadius: '8px',
              fontSize: '0.82rem',
              fontWeight: 700,
              background: mode === 'without_memory' ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
              color: mode === 'without_memory' ? '#f87171' : 'var(--text-muted)',
              border: mode === 'without_memory' ? '1px solid rgba(239, 68, 68, 0.4)' : 'none',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            WITHOUT MEMORY
          </button>
          <button
            type="button"
            onClick={() => setMode('with_memory')}
            style={{
              padding: '8px 18px',
              borderRadius: '8px',
              fontSize: '0.82rem',
              fontWeight: 700,
              background: mode === 'with_memory' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
              color: mode === 'with_memory' ? 'var(--success-text)' : 'var(--text-muted)',
              border: mode === 'with_memory' ? '1px solid rgba(16, 185, 129, 0.4)' : 'none',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            WITH MEMORY
          </button>
        </div>
      </div>

      {/* Mode View */}
      {mode === 'without_memory' ? (
        <div
          className="animate-fade-in"
          style={{
            background: 'rgba(239, 68, 68, 0.04)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <span
              className="badge"
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                color: '#f87171',
                border: '1px solid rgba(239, 68, 68, 0.3)',
              }}
            >
              Stateless Baseline Mode (No Memory Applied)
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: '#fca5a5', marginBottom: '14px', lineHeight: 1.45 }}>
            <strong>Limitation:</strong> The agent does not know what was already tried on this site. It blindly recommends textbook rules (e.g. write 5,000 words, stuff keywords), risking wasted effort on tactics that previously failed.
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {beforeRecs.map((r, i) => (
              <div
                key={r.id || i}
                style={{
                  background: 'rgba(15, 23, 42, 0.7)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: '8px',
                  padding: '14px',
                }}
              >
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f87171' }}>
                  {r.title}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {r.reasoning}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div
          className="animate-fade-in"
          style={{
            background: 'rgba(16, 185, 129, 0.04)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <span
              className="badge"
              style={{
                background: 'rgba(16, 185, 129, 0.15)',
                color: 'var(--success-text)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              Hindsight Persistent Memory Active
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: '#6ee7b7', marginBottom: '14px', lineHeight: 1.45 }}>
            <strong>Strategic Advantage:</strong> The agent recalls that structured curriculum tables and sandbox widgets previously drove a +5 total rank lift, while generic word count expansion produced zero lift.
          </div>

          {/* Suppressed Tactics */}
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              borderRadius: '8px',
              padding: '10px 14px',
              marginBottom: '14px',
            }}
          >
            <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#fca5a5', textTransform: 'uppercase', marginBottom: '4px' }}>
              Bad Tactics Suppressed by Experience:
            </div>
            {suppressedTactics.map((s, idx) => (
              <div key={idx} style={{ fontSize: '0.78rem', color: '#fecaca' }}>
                🚫 {s}
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {afterRecs.map((r, i) => (
              <div
                key={r.id || i}
                style={{
                  background: 'rgba(15, 23, 42, 0.7)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  borderRadius: '8px',
                  padding: '14px',
                }}
              >
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--success-text)' }}>
                  {r.title}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '4px' }}>
                  {r.reasoning}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comparison Matrix Table */}
      <div>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', textTransform: 'uppercase', marginBottom: '10px' }}>
          Key Differences Matrix: Stateless Baseline vs Hindsight Memory
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-faint)', textTransform: 'uppercase', fontSize: '0.7rem' }}>
                <th style={{ padding: '10px' }}>Dimension</th>
                <th style={{ padding: '10px', color: '#f87171' }}>Without Memory</th>
                <th style={{ padding: '10px', color: 'var(--success-text)' }}>With Memory</th>
              </tr>
            </thead>
            <tbody>
              {matrix.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '10px', fontWeight: 700, color: '#f1f5f9' }}>
                    {row.dimension}
                  </td>
                  <td style={{ padding: '10px', color: '#fca5a5' }}>
                    {row.before_memory}
                  </td>
                  <td style={{ padding: '10px', color: '#6ee7b7' }}>
                    {row.after_memory}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
