import React, { useState } from 'react';
import {
  Sparkles,
  HelpCircle,
  ThumbsUp,
  ThumbsDown,
  Send,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { ContextAwareRecommendation, UserFeedbackInput } from '../types';

interface AiRecommendationCardProps {
  recommendations: ContextAwareRecommendation[];
  query: string;
  domain: string;
  onRecordActionClick?: (rec: ContextAwareRecommendation) => void;
  onSubmitFeedback: (feedback: UserFeedbackInput) => Promise<void>;
}

export const AiRecommendationCard: React.FC<AiRecommendationCardProps> = ({
  recommendations,
  query,
  domain,
  onRecordActionClick,
  onSubmitFeedback,
}) => {
  const [selectedRecIndex, setSelectedRecIndex] = useState(0);
  const [isWhyExpanded, setIsWhyExpanded] = useState(true);
  
  // Feedback state
  const [decision, setDecision] = useState<'accepted' | 'rejected' | null>(null);
  const [isUseful, setIsUseful] = useState<boolean>(true);
  const [explanation, setExplanation] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const activeRec = recommendations[selectedRecIndex] || recommendations[0];

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!decision) return;
    try {
      setSubmittingFeedback(true);
      await onSubmitFeedback({
        search_query: query,
        website_domain: domain,
        recommendation_id: activeRec?.id || 'rec_default',
        recommendation_title: activeRec?.title || 'Recommended Action',
        decision,
        is_useful: isUseful,
        explanation: explanation.trim() || `User ${decision} recommendation: ${activeRec?.title}`,
      });
      setFeedbackSubmitted(true);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (!activeRec) {
    return (
      <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No recommendations generated yet. Select a website and run analysis.
      </div>
    );
  }

  const why = activeRec.why_am_i_seeing_this || {
    current_observation: 'Target page missing Course JSON-LD schema & video walkthroughs.',
    recalled_memory: 'In Cycle 2, adding structured curriculum and video preview resulted in a +3 rank movement.',
    connection_between_them: 'Competitors holding positions #1-#2 leverage video rich snippets.',
    recommendation: 'Deploy Schema.org Course markup and 90-sec interactive project preview.',
    observational_caveat: 'Past correlation does not guarantee future algorithmic ranking.',
  };

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
            04
          </span>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} color="var(--cyan-primary)" />
              Recommended Next Action
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              AI recommendation synthesized from current signals and recalled Hindsight memories.
            </p>
          </div>
        </div>

        {/* Priority & Category Badges */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <span className="badge badge-proven" style={{ padding: '4px 10px' }}>
            Priority #{activeRec.priority || 1}
          </span>
          <span className="badge badge-trend" style={{ padding: '4px 10px' }}>
            {activeRec.category || 'Schema & UX'}
          </span>
        </div>
      </div>

      {/* Rec Selector Chips if multiple */}
      {recommendations.length > 1 && (
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
          {recommendations.map((r, i) => (
            <button
              key={r.id || i}
              type="button"
              onClick={() => {
                setSelectedRecIndex(i);
                setFeedbackSubmitted(false);
                setDecision(null);
              }}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                fontWeight: 600,
                background: selectedRecIndex === i ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: selectedRecIndex === i ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                color: selectedRecIndex === i ? '#fff' : 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              Option {i + 1}: {r.title.slice(0, 32)}...
            </button>
          ))}
        </div>
      )}

      {/* Main Recommended Action Box */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>
              {activeRec.title}
            </h3>
            <p style={{ fontSize: '0.88rem', color: '#cbd5e1', lineHeight: 1.5, maxWidth: '850px' }}>
              {activeRec.reasoning}
            </p>
          </div>

          {onRecordActionClick && (
            <button
              type="button"
              className="btn-primary"
              onClick={() => onRecordActionClick(activeRec)}
              style={{ padding: '10px 18px', fontSize: '0.82rem' }}
            >
              Record Action in Loop <ArrowRight size={14} />
            </button>
          )}
        </div>

        {/* Expected Direction of Improvement */}
        {activeRec.expected_direction_of_improvement && (
          <div
            style={{
              marginTop: '14px',
              padding: '8px 12px',
              background: 'rgba(16, 185, 129, 0.1)',
              borderRadius: '6px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.8rem',
              color: 'var(--success-text)',
            }}
          >
            <CheckCircle2 size={15} />
            <span><strong>Expected Effect:</strong> {activeRec.expected_direction_of_improvement}</span>
          </div>
        )}

        {/* Implementation Steps */}
        {activeRec.implementation_steps && activeRec.implementation_steps.length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-faint)', marginBottom: '8px' }}>
              Concrete Implementation Steps:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {activeRec.implementation_steps.map((step, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px',
                    fontSize: '0.82rem',
                    color: '#e2e8f0',
                  }}
                >
                  <span
                    style={{
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      background: 'rgba(255,255,255,0.08)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '10px',
                      fontWeight: 700,
                      flexShrink: 0,
                    }}
                  >
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* WHY? SECTION (Mandatory Transparent Evidence Breakdown) */}
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(6, 182, 212, 0.25)',
          borderRadius: '12px',
          overflow: 'hidden',
          marginBottom: '20px',
        }}
      >
        <button
          type="button"
          onClick={() => setIsWhyExpanded(!isWhyExpanded)}
          style={{
            width: '100%',
            padding: '14px 18px',
            background: 'rgba(6, 182, 212, 0.08)',
            border: 'none',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            color: '#fff',
            fontSize: '0.88rem',
            fontWeight: 700,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HelpCircle size={17} color="var(--cyan-primary)" />
            <span>Why is this recommended? (Transparent Evidence Breakdown)</span>
          </div>
          {isWhyExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {isWhyExpanded && (
          <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {/* 1. Observation */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '130px', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 800, color: 'var(--text-faint)', flexShrink: 0, paddingTop: '2px' }}>
                Observation:
              </div>
              <div style={{ fontSize: '0.84rem', color: '#e2e8f0', lineHeight: 1.45 }}>
                {why.current_observation}
              </div>
            </div>

            {/* 2. Recalled Memory */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '130px', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 800, color: 'var(--cyan-primary)', flexShrink: 0, paddingTop: '2px' }}>
                Recalled Memory:
              </div>
              <div style={{ fontSize: '0.84rem', color: '#a5f3fc', lineHeight: 1.45, background: 'rgba(6, 182, 212, 0.06)', padding: '6px 10px', borderRadius: '6px' }}>
                {why.recalled_memory}
              </div>
            </div>

            {/* 3. Connection Between Them */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '130px', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 800, color: '#c084fc', flexShrink: 0, paddingTop: '2px' }}>
                Connection:
              </div>
              <div style={{ fontSize: '0.84rem', color: '#e2e8f0', lineHeight: 1.45 }}>
                {why.connection_between_them}
              </div>
            </div>

            {/* 4. Recommendation */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '130px', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 800, color: 'var(--success-text)', flexShrink: 0, paddingTop: '2px' }}>
                Recommendation:
              </div>
              <div style={{ fontSize: '0.84rem', color: '#34d399', lineHeight: 1.45, fontWeight: 600 }}>
                {why.recommendation}
              </div>
            </div>

            {/* 5. Observational Caveat */}
            <div
              style={{
                marginTop: '6px',
                padding: '8px 12px',
                borderRadius: '6px',
                background: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.25)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.74rem',
                color: '#fef3c7',
              }}
            >
              <ShieldAlert size={14} color="var(--warning-text)" />
              <span><strong>Observational Caveat:</strong> {why.observational_caveat}</span>
            </div>
          </div>
        )}
      </div>

      {/* FEEDBACK SECTION (Area 8) */}
      <div
        style={{
          background: 'rgba(8, 13, 26, 0.7)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '16px 20px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '12px' }}>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff' }}>
              Provide Feedback to Memory Engine
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Decisions feed into Hindsight memory so future recommendations reflect user operational choices.
            </div>
          </div>

          {feedbackSubmitted && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                color: 'var(--success-text)',
                fontSize: '0.78rem',
                fontWeight: 700,
                background: 'rgba(16, 185, 129, 0.15)',
                padding: '4px 10px',
                borderRadius: '6px',
              }}
            >
              <CheckCircle2 size={14} /> Retained in Hindsight Memory!
            </span>
          )}
        </div>

        <form onSubmit={handleFeedbackSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              type="button"
              onClick={() => {
                setDecision('accepted');
                setFeedbackSubmitted(false);
              }}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 700,
                background: decision === 'accepted' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                border: decision === 'accepted' ? '1px solid var(--success-text)' : '1px solid var(--border-subtle)',
                color: decision === 'accepted' ? 'var(--success-text)' : 'var(--text-muted)',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <ThumbsUp size={14} /> Accept Recommendation
            </button>

            <button
              type="button"
              onClick={() => {
                setDecision('rejected');
                setFeedbackSubmitted(false);
              }}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 700,
                background: decision === 'rejected' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                border: decision === 'rejected' ? '1px solid var(--danger-text)' : '1px solid var(--border-subtle)',
                color: decision === 'rejected' ? 'var(--danger-text)' : 'var(--text-muted)',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <ThumbsDown size={14} /> Reject Recommendation
            </button>

            <label style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--text-muted)', cursor: 'pointer', marginLeft: '6px' }}>
              <input
                type="checkbox"
                checked={isUseful}
                onChange={(e) => setIsUseful(e.target.checked)}
              />
              Mark as useful
            </label>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={explanation}
              onChange={(e) => setExplanation(e.target.value)}
              placeholder="Add explanation (e.g. 'Engineering will deploy video preview next week, schema already verified')"
              style={{
                flex: 1,
                padding: '10px 14px',
                background: '#0a0f1d',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '0.82rem',
                outline: 'none',
              }}
            />
            <button
              type="submit"
              disabled={!decision || submittingFeedback}
              className="btn-secondary"
              style={{
                padding: '10px 18px',
                fontSize: '0.82rem',
                opacity: !decision || submittingFeedback ? 0.5 : 1,
              }}
            >
              <Send size={13} /> {submittingFeedback ? 'Saving...' : 'Submit to Memory'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
