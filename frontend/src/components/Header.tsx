import React from 'react';
import { History, PlusCircle, RotateCcw, Brain, Activity, ExternalLink } from 'lucide-react';

interface HeaderProps {
  onOpenLogModal: () => void;
  onResetDemo: () => void;
  loading: boolean;
  query: string;
  targetDomain: string;
  currentRank?: number | null;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenLogModal,
  onResetDemo,
  loading,
  query,
  targetDomain,
  currentRank,
}) => {
  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(12, 20, 39, 0.92)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        padding: '14px 24px',
      }}
    >
      <div
        style={{
          maxWidth: '1440px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px',
        }}
      >
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, var(--cyan-primary), #6366f1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(6, 182, 212, 0.35)',
            }}
          >
            <History size={20} color="#fff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.02em' }}>
                RankMind
              </span>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: 'var(--success-text)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                }}
              >
                <span
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: 'var(--success-text)',
                    boxShadow: '0 0 6px var(--success-text)',
                  }}
                />
                Hindsight Memory Active
              </span>
              {currentRank !== undefined && currentRank !== null && (
                <span
                  style={{
                    fontSize: '0.72rem',
                    color: 'var(--cyan-primary)',
                    background: 'rgba(6, 182, 212, 0.1)',
                    border: '1px solid rgba(6, 182, 212, 0.25)',
                    padding: '2px 8px',
                    borderRadius: '8px',
                    fontWeight: 700,
                  }}
                >
                  {targetDomain} (Rank #{currentRank})
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
              Search Intelligence & Memory-Powered SEO Agent • Tracking: "{query}"
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <a
            href="/learning-loop"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '7px 12px',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              background: 'rgba(255, 255, 255, 0.04)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border-subtle)',
              textDecoration: 'none',
              transition: 'all 0.15s',
            }}
          >
            <Activity size={13} />
            <span>Learning Loop Cockpit</span>
            <ExternalLink size={11} color="var(--text-faint)" />
          </a>

          <a
            href="/hindsight"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '7px 12px',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              background: 'rgba(255, 255, 255, 0.04)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border-subtle)',
              textDecoration: 'none',
              transition: 'all 0.15s',
            }}
          >
            <Brain size={13} />
            <span>Hindsight Studio</span>
            <ExternalLink size={11} color="var(--text-faint)" />
          </a>

          <button
            onClick={onResetDemo}
            disabled={loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '7px 12px',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              background: 'rgba(255, 255, 255, 0.04)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border-subtle)',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={13} />
            Reset Demo
          </button>

          <button
            onClick={onOpenLogModal}
            disabled={loading}
            className="btn-primary"
            style={{
              padding: '8px 16px',
              fontSize: '0.82rem',
              borderRadius: '8px',
            }}
          >
            <PlusCircle size={14} />
            Drive Loop (Action / Measure)
          </button>
        </div>
      </div>
    </header>
  );
};
