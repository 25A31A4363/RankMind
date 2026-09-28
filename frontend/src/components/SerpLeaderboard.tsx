import React from 'react';
import { SERPSnapshot } from '../types';
import { X, Code2, Video, Table } from 'lucide-react';

interface SerpLeaderboardProps {
  snapshot: SERPSnapshot;
  targetDomain: string;
}

export const SerpLeaderboard: React.FC<SerpLeaderboardProps> = ({ snapshot, targetDomain }) => {
  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
            Live SERP Leaderboard & Feature Matrix
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Cycle {snapshot.cycle_index} Snapshot ({snapshot.items.length} evaluated rankings)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
            Intent: Informational / Commercial Guide
          </span>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-faint)' }}>
              <th style={{ padding: '10px 12px', width: '60px' }}>Rank</th>
              <th style={{ padding: '10px 12px' }}>Domain & Page Title</th>
              <th style={{ padding: '10px 12px', textAlign: 'center' }}>Interactive Tool</th>
              <th style={{ padding: '10px 12px', textAlign: 'center' }}>Video Preview</th>
              <th style={{ padding: '10px 12px', textAlign: 'center' }}>Syllabus Matrix</th>
              <th style={{ padding: '10px 12px' }}>Schema.org Types</th>
              <th style={{ padding: '10px 12px', textAlign: 'right' }}>Word Count</th>
            </tr>
          </thead>
          <tbody>
            {snapshot.items.map((item) => {
              const isTarget = item.domain === targetDomain;
              return (
                <tr
                  key={item.url}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    background: isTarget ? 'rgba(99, 102, 241, 0.12)' : 'transparent',
                    boxShadow: isTarget ? 'inset 3px 0 0 var(--brand-primary)' : 'none',
                  }}
                >
                  {/* Rank */}
                  <td style={{ padding: '12px', fontWeight: 800 }}>
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: item.rank <= 3 ? 'rgba(255, 255, 255, 0.08)' : 'transparent',
                        color: item.rank === 1 ? '#fbbf24' : item.rank === 2 ? '#94a3b8' : item.rank === 3 ? '#d97706' : 'var(--text-muted)',
                        border: item.rank <= 3 ? '1px solid var(--border-subtle)' : 'none',
                      }}
                    >
                      #{item.rank}
                    </div>
                  </td>

                  {/* Domain & Title */}
                  <td style={{ padding: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 600, color: isTarget ? 'var(--brand-primary-light)' : '#fff' }}>
                        {item.domain}
                      </span>
                      {isTarget && (
                        <span className="badge badge-proven" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                          Your Page
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px', maxWidth: '380px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.title}
                    </div>
                  </td>

                  {/* Interactive Tool */}
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    {item.has_interactive_widget ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--success-text)', fontSize: '0.78rem', fontWeight: 600 }}>
                        <Code2 size={15} /> Yes
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)', fontSize: '0.78rem' }}>
                        <X size={15} />
                      </span>
                    )}
                  </td>

                  {/* Video Preview */}
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    {item.has_video_preview ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--cyan-text)', fontSize: '0.78rem', fontWeight: 600 }}>
                        <Video size={15} /> Yes
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)', fontSize: '0.78rem' }}>
                        <X size={15} />
                      </span>
                    )}
                  </td>

                  {/* Curriculum / Syllabus Table */}
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    {item.has_curriculum_table ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#c084fc', fontSize: '0.78rem', fontWeight: 600 }}>
                        <Table size={15} /> Yes
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)', fontSize: '0.78rem' }}>
                        <X size={15} />
                      </span>
                    )}
                  </td>

                  {/* Schema Types */}
                  <td style={{ padding: '12px' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '240px' }}>
                      {item.schema_types.map((schema) => (
                        <span
                          key={schema}
                          style={{
                            fontSize: '0.7rem',
                            padding: '2px 6px',
                            background: 'rgba(255, 255, 255, 0.05)',
                            borderRadius: '4px',
                            color: 'var(--text-muted)',
                            border: '1px solid var(--border-subtle)',
                          }}
                        >
                          {schema}
                        </span>
                      ))}
                    </div>
                  </td>

                  {/* Word Count */}
                  <td style={{ padding: '12px', textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {item.word_count.toLocaleString()} w
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
