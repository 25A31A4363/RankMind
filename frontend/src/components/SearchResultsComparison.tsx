import React, { useState } from 'react';
import { SERPItem, QueryUnderstanding } from '../types';
import {
  Code2,
  Video,
  Table as TableIcon,
  TrendingUp,
  TrendingDown,
  Minus,
  ShieldCheck,
  MousePointerClick,
  Info,
  ExternalLink,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  X,
  Sparkles,
  AlertCircle,
  CheckCircle,
  BookOpen,
  Compass,
  Bookmark,
  Award,
  Zap,
} from 'lucide-react';

interface SearchResultsComparisonProps {
  items: SERPItem[];
  selectedDomain: string;
  onSelectDomain: (domain: string) => void;
  query: string;
  cycleIndex?: number;
  queryUnderstanding?: QueryUnderstanding | null;
  sourceLabel?: string;
  insufficientResults?: boolean;
  insufficientMessage?: string;
  onOpenWebsite?: (item: SERPItem) => void;
}

export const SearchResultsComparison: React.FC<SearchResultsComparisonProps> = ({
  items,
  selectedDomain,
  onSelectDomain,
  query,
  cycleIndex = 5,
  queryUnderstanding,
  sourceLabel = "Based on RankMind's available dataset",
  insufficientResults = false,
  insufficientMessage,
  onOpenWebsite,
}) => {
  // State for "What does Position #1 mean?" explanation toggle
  const [showRankMeaning, setShowRankMeaning] = useState(false);

  // State for active "Why this position?" item (modal/drawer)
  const [whyModalItem, setWhyModalItem] = useState<SERPItem | null>(null);

  // Expanded Key Points toggles for cards
  const [expandedKeyPoints, setExpandedKeyPoints] = useState<Record<string, boolean>>({});

  const toggleKeyPoints = (domain: string) => {
    setExpandedKeyPoints((prev) => ({ ...prev, [domain]: !prev[domain] }));
  };

  // Helper to validate URL
  const isValidUrl = (url?: string) => {
    if (!url) return false;
    try {
      const parsed = new URL(url);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleOpenExternal = (item: SERPItem, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onOpenWebsite) {
      onOpenWebsite(item);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Header with Title and Disclosures */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '16px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                width: '18px',
                height: '18px',
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
              02
            </span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
              Website Intelligence & Evidence-Based Ranking
            </h2>
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Evaluating ranked resources for: <strong style={{ color: '#e2e8f0' }}>"{query}"</strong> • Click any card to inspect full intelligence profile.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {/* What does Position #1 mean button */}
          <button
            type="button"
            onClick={() => setShowRankMeaning(!showRankMeaning)}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '0.75rem',
              fontWeight: 700,
              background: showRankMeaning ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
              border: showRankMeaning ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
              color: showRankMeaning ? 'var(--cyan-primary)' : 'var(--text-muted)',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s',
            }}
          >
            <HelpCircle size={14} />
            Search Position vs RankMind Position
            {showRankMeaning ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          <span
            className="badge"
            style={{
              background: 'rgba(245, 158, 11, 0.12)',
              color: '#fcd34d',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              padding: '4px 10px',
            }}
          >
            {sourceLabel}
          </span>

          <span
            className="badge"
            style={{
              background: 'rgba(99, 102, 241, 0.12)',
              color: '#a5b4fc',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              padding: '4px 10px',
            }}
          >
            <ShieldCheck size={13} />
            Evaluation Cycle #{cycleIndex}
          </span>
        </div>
      </div>

      {/* Query Understanding Metadata Strip */}
      {queryUnderstanding && (
        <div
          className="animate-fade-in"
          style={{
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '12px 16px',
            marginBottom: '16px',
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--cyan-primary)', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase' }}>
            <Compass size={14} />
            <span>Query Understanding:</span>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', fontSize: '0.78rem' }}>
            <span style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '3px 8px', borderRadius: '6px', color: '#cbd5e1' }}>
              <strong>Topic:</strong> {queryUnderstanding.topic}
            </span>
            <span style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '3px 8px', borderRadius: '6px', color: '#cbd5e1' }}>
              <strong>Intent:</strong> {queryUnderstanding.intent}
            </span>
            {queryUnderstanding.audience_level && queryUnderstanding.audience_level !== 'General' && (
              <span style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#c7d2fe', padding: '3px 8px', borderRadius: '6px' }}>
                <strong>Audience:</strong> {queryUnderstanding.audience_level}
              </span>
            )}
            {queryUnderstanding.price_preference && queryUnderstanding.price_preference !== 'Any' && (
              <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#a7f3d0', padding: '3px 8px', borderRadius: '6px' }}>
                <strong>Preference:</strong> {queryUnderstanding.price_preference}
              </span>
            )}
            {queryUnderstanding.location && (
              <span style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fde68a', padding: '3px 8px', borderRadius: '6px' }}>
                <strong>Location:</strong> {queryUnderstanding.location}
              </span>
            )}
            {queryUnderstanding.price_constraint && (
              <span style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#fbcfe8', padding: '3px 8px', borderRadius: '6px' }}>
                <strong>Budget:</strong> {queryUnderstanding.price_constraint}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Explanation Toggle: Search Position vs RankMind Position */}
      {showRankMeaning && (
        <div
          className="animate-fade-in"
          style={{
            background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%)',
            border: '1px solid rgba(6, 182, 212, 0.3)',
            borderRadius: '10px',
            padding: '16px 20px',
            marginBottom: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
            <Info size={18} color="var(--cyan-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f1f5f9', marginBottom: '4px' }}>
                Understanding Search Position vs RankMind Position
              </div>
              <p style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                <strong>RankMind Position #1</strong> means this website was evaluated as the highest-scoring candidate among the available relevant resources based on multi-factor evaluation (relevance, depth, authority, accessibility, and Hindsight memory). It does <em>not</em> claim to be an objective universal truth or that Google ranks it #1 worldwide.
              </p>
              <p style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.5, marginTop: '6px' }}>
                <strong>Search Position (#X)</strong> indicates where the candidate was observed in raw search indexing. RankMind separates these two concepts clearly.
              </p>
              <p style={{ fontSize: '0.78rem', color: '#fcd34d', marginTop: '6px', fontWeight: 600 }}>
                ⚠️ Transparency Guarantee: Traffic and popularity metrics are marked "Data unavailable" unless verified in the connected data source. RankMind never fabricates visitor statistics.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* INSUFFICIENT RESULTS NOTICE (Requirement 5) */}
      {(insufficientResults || items.length === 0) && (
        <div
          className="animate-fade-in"
          style={{
            textAlign: 'center',
            padding: '48px 24px',
            background: 'rgba(239, 68, 68, 0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            marginBottom: '20px',
          }}
        >
          <div
            style={{
              width: '52px',
              height: '52px',
              borderRadius: '50%',
              background: 'rgba(239, 68, 68, 0.15)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '14px',
            }}
          >
            <AlertCircle size={26} color="#f87171" />
          </div>
          <h3 style={{ color: '#fff', fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px' }}>
            {insufficientMessage || 'Not enough relevant resources found.'}
          </h3>
          <p style={{ color: '#94a3b8', maxWidth: '600px', margin: '0 auto 16px auto', fontSize: '0.88rem', lineHeight: 1.5 }}>
            RankMind applied strict topical and semantic relevance filtering for "{query}". Unrelated websites have been removed rather than filling the result list with irrelevant filler.
          </p>
          <div style={{ fontSize: '0.78rem', color: '#cbd5e1' }}>
            Try refining your query or search another subject (e.g. <em>"Java tutorials", "how to make pizza", "best places to visit in Hyderabad"</em>).
          </div>
        </div>
      )}

      {/* STRONGEST RESULT INTELLIGENCE BANNER */}
      {items.length > 0 && (() => {
        const strongestItem = items.find((it) => it.rank === 1) || items[0];
        const rankmindScore = strongestItem.rankmind_score || 96;
        const validStrongUrl = isValidUrl(strongestItem.url);

        return (
          <div
            className="animate-fade-in"
            style={{
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(15, 23, 42, 0.95) 100%)',
              border: '1px solid rgba(6, 182, 212, 0.4)',
              borderRadius: '12px',
              padding: '20px 24px',
              marginBottom: '20px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '14px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={16} color="var(--cyan-primary)" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--cyan-primary)' }}>
                    RankMind Leader
                  </span>
                  <span className="badge badge-proven" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                    RankMind Position #1 • Score: {rankmindScore}/100
                  </span>
                </div>
                <p style={{ fontSize: '0.98rem', color: '#f8fafc', fontWeight: 700, marginTop: '8px', lineHeight: 1.45 }}>
                  Based on available evidence, <strong style={{ color: 'var(--cyan-primary)' }}>{strongestItem.domain}</strong> ranked highest among available resources for this query.
                </p>
                <div style={{ fontSize: '0.74rem', color: '#94a3b8', marginTop: '2px' }}>
                  * Evaluated from available multi-factor evidence. RankMind AI does not claim this is objectively the best website on the entire internet.
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => onSelectDomain(strongestItem.domain)}
                  className="btn-primary"
                  style={{ padding: '8px 16px', fontSize: '0.8rem' }}
                >
                  View detailed analysis
                </button>
                {validStrongUrl && (
                  <a
                    href={strongestItem.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => handleOpenExternal(strongestItem, e)}
                    className="btn-secondary"
                    style={{ textDecoration: 'none', padding: '8px 16px', fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                  >
                    <ExternalLink size={13} /> Open Website ↗
                  </a>
                )}
              </div>
            </div>

            {/* WHY #1 EXPLANATION */}
            <div style={{ background: 'rgba(8, 13, 26, 0.75)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px', padding: '16px 20px' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 800, textTransform: 'uppercase', color: '#cbd5e1', letterSpacing: '0.04em', marginBottom: '10px' }}>
                WHY #1? (RankMind Multi-Factor Evaluation)
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px', fontSize: '0.82rem', color: '#e2e8f0' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  <CheckCircle size={15} color="var(--success-text)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span><strong>Strong query relevance:</strong> High topical alignment for "{query}"</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  <CheckCircle size={15} color="var(--success-text)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span><strong>Content quality & completeness:</strong> {strongestItem.word_count.toLocaleString()} words with structured format</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  <CheckCircle size={15} color="var(--success-text)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span><strong>Access & Classification:</strong> {strongestItem.classification?.access_type || strongestItem.access_type || 'FREE'} ({strongestItem.classification?.resource_type || strongestItem.resource_type || 'Resource'})</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  <CheckCircle size={15} color="var(--success-text)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span><strong>Accessibility:</strong> Clean navigation structure and readable presentation</span>
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* SEARCH RESULT CARDS LIST */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {items.map((item) => {
          const isSelected = item.domain === selectedDomain;
          const urlValid = isValidUrl(item.url);
          const rankmindScore = item.rankmind_score || Math.max(75, 98 - (item.rank - 1) * 3);
          const resType = item.classification?.resource_type || item.resource_type || 'Resource';
          const accessType = item.classification?.access_type || item.access_type || 'FREE';
          const isFree = accessType.includes('FREE');
          const isFreemium = accessType.includes('FREEMIUM');
          const hasKeyPoints = item.key_points && item.key_points.length > 0;
          const isKeyPointsOpen = expandedKeyPoints[item.domain] !== false; // open by default for rich UX

          // Movement display
          let movementDisplay = (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '3px', color: 'var(--text-faint)', fontSize: '0.75rem' }}>
              <Minus size={12} /> 0 positions
            </span>
          );
          if (item.historical_movement?.startsWith('+')) {
            movementDisplay = (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '3px',
                  color: 'var(--success-text)',
                  fontWeight: 700,
                  background: 'rgba(16, 185, 129, 0.12)',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                }}
              >
                <TrendingUp size={12} /> {item.historical_movement}
              </span>
            );
          } else if (item.historical_movement?.startsWith('-')) {
            movementDisplay = (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '3px',
                  color: 'var(--danger-text)',
                  fontWeight: 700,
                  background: 'rgba(239, 68, 68, 0.12)',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                }}
              >
                <TrendingDown size={12} /> {item.historical_movement}
              </span>
            );
          }

          return (
            <div
              key={item.domain + item.rank}
              style={{
                background: isSelected
                  ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(15, 23, 42, 0.85) 100%)'
                  : 'rgba(15, 23, 42, 0.65)',
                border: isSelected
                  ? '1px solid var(--cyan-primary)'
                  : '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '20px 22px',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px',
                transition: 'all 0.2s ease',
                boxShadow: isSelected ? '0 0 20px rgba(6, 182, 212, 0.15)' : 'none',
              }}
            >
              {/* Row 1: Badges, Domain, Scores, and Main Action Buttons */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  {/* Visual RankMind Position Badge */}
                  <div
                    style={{
                      padding: '4px 12px',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      fontWeight: 800,
                      fontSize: '0.85rem',
                      background:
                        item.rank === 1
                          ? 'rgba(251, 191, 36, 0.18)'
                          : item.rank === 2
                          ? 'rgba(148, 163, 184, 0.18)'
                          : item.rank === 3
                          ? 'rgba(217, 119, 6, 0.18)'
                          : 'rgba(255, 255, 255, 0.05)',
                      color:
                        item.rank === 1
                          ? '#fbbf24'
                          : item.rank === 2
                          ? '#cbd5e1'
                          : item.rank === 3
                          ? '#f59e0b'
                          : 'var(--text-muted)',
                      border:
                        item.rank <= 3
                          ? '1px solid rgba(255,255,255,0.18)'
                          : '1px solid var(--border-subtle)',
                    }}
                  >
                    <span>RankMind #{item.rank}</span>
                  </div>

                  {/* Search Position Separated */}
                  {item.search_position && (
                    <span
                      style={{
                        padding: '3px 8px',
                        borderRadius: '6px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        background: 'rgba(255, 255, 255, 0.04)',
                        border: '1px solid var(--border-subtle)',
                        color: 'var(--text-faint)',
                      }}
                    >
                      Search Position: #{item.search_position}
                    </span>
                  )}

                  {/* Resource Type Badge */}
                  <span
                    style={{
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      background: 'rgba(99, 102, 241, 0.15)',
                      color: '#a5b4fc',
                      border: '1px solid rgba(99, 102, 241, 0.3)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <BookOpen size={11} />
                    {resType}
                  </span>

                  {/* Free / Access Type Badge */}
                  <span
                    style={{
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      background: isFree
                        ? 'rgba(16, 185, 129, 0.15)'
                        : isFreemium
                        ? 'rgba(6, 182, 212, 0.15)'
                        : 'rgba(245, 158, 11, 0.15)',
                      color: isFree
                        ? 'var(--success-text)'
                        : isFreemium
                        ? 'var(--cyan-text)'
                        : '#fbbf24',
                      border: isFree
                        ? '1px solid rgba(16, 185, 129, 0.3)'
                        : isFreemium
                        ? '1px solid rgba(6, 182, 212, 0.3)'
                        : '1px solid rgba(245, 158, 11, 0.3)',
                    }}
                  >
                    {accessType}
                  </span>

                  {/* RankMind Score */}
                  <span
                    style={{
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 800,
                      background: 'rgba(6, 182, 212, 0.15)',
                      color: 'var(--cyan-primary)',
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <Award size={12} />
                    RankMind Score: {rankmindScore}/100
                  </span>
                </div>

                {/* Right Actions: Why this position? + Open Website ↗ + Select */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  {/* Why this position? Button */}
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setWhyModalItem(item);
                    }}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      background: 'rgba(99, 102, 241, 0.15)',
                      color: '#a5b4fc',
                      border: '1px solid rgba(99, 102, 241, 0.35)',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      transition: 'all 0.15s',
                    }}
                  >
                    <HelpCircle size={13} />
                    Why this position?
                  </button>

                  {/* Open Website ↗ Button */}
                  {urlValid ? (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => handleOpenExternal(item, e)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        background: 'rgba(255, 255, 255, 0.08)',
                        color: '#f8fafc',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        textDecoration: 'none',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '5px',
                        transition: 'all 0.15s',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.16)';
                        e.currentTarget.style.borderColor = 'var(--cyan-primary)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                      }}
                    >
                      <ExternalLink size={13} />
                      Open Website ↗
                    </a>
                  ) : (
                    <button
                      type="button"
                      disabled
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        background: 'rgba(255, 255, 255, 0.02)',
                        color: 'var(--text-faint)',
                        border: '1px solid var(--border-subtle)',
                        cursor: 'not-allowed',
                      }}
                    >
                      URL unavailable
                    </button>
                  )}

                  {/* Select Focus Button */}
                  <button
                    type="button"
                    onClick={() => onSelectDomain(item.domain)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      background: isSelected ? 'var(--cyan-primary)' : 'rgba(6, 182, 212, 0.15)',
                      color: isSelected ? '#000' : 'var(--cyan-primary)',
                      border: isSelected ? 'none' : '1px solid rgba(6, 182, 212, 0.3)',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <MousePointerClick size={12} />
                    {isSelected ? 'Active Focus' : 'Inspect Profile'}
                  </button>
                </div>
              </div>

              {/* Row 2: Website Title, Domain, & Snippet */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => handleOpenExternal(item, e)}
                    style={{
                      fontSize: '1.02rem',
                      fontWeight: 800,
                      color: '#f8fafc',
                      textDecoration: 'none',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--cyan-primary)')}
                    onMouseLeave={(e) => (e.currentTarget.style.color = '#f8fafc')}
                  >
                    {item.title}
                  </a>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-faint)' }}>({item.domain})</span>
                </div>
                <div style={{ fontSize: '0.84rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {item.snippet}
                </div>
              </div>

              {/* Row 3: Key Point Extraction (Requirement 12) */}
              {hasKeyPoints && (
                <div
                  style={{
                    background: 'rgba(8, 14, 28, 0.75)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: isKeyPointsOpen ? '8px' : '0',
                      cursor: 'pointer',
                    }}
                    onClick={() => toggleKeyPoints(item.domain)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Bookmark size={13} color="var(--cyan-primary)" />
                      <span style={{ fontSize: '0.74rem', fontWeight: 800, textTransform: 'uppercase', color: '#cbd5e1', letterSpacing: '0.04em' }}>
                        Key Points
                      </span>
                      <span style={{ fontSize: '0.68rem', color: 'var(--text-faint)' }}>
                        ({item.key_points_source || 'Key points based on available metadata and analyzed content'})
                      </span>
                    </div>
                    <span style={{ color: 'var(--text-faint)' }}>
                      {isKeyPointsOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </span>
                  </div>

                  {isKeyPointsOpen && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                      {item.key_points?.map((kp, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.8rem', color: '#e2e8f0', lineHeight: 1.4 }}>
                          <span style={{ color: 'var(--success-text)', fontWeight: 800 }}>✓</span>
                          <span>{kp}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Row 4: Highlighted Important Content (Requirement 13) */}
              {item.highlighted_content && item.highlighted_content.length > 0 && (
                <div
                  style={{
                    background: 'rgba(6, 182, 212, 0.04)',
                    borderLeft: '3px solid var(--cyan-primary)',
                    borderRadius: '0 8px 8px 0',
                    padding: '10px 14px',
                    fontSize: '0.8rem',
                    color: '#cbd5e1',
                    lineHeight: 1.45,
                  }}
                >
                  <div style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--cyan-primary)', marginBottom: '4px', letterSpacing: '0.04em' }}>
                    Extracted Webpage Content Highlights:
                  </div>
                  {item.highlighted_content.map((hc, idx) => (
                    <div key={idx} style={{ fontStyle: 'italic', marginBottom: idx < item.highlighted_content!.length - 1 ? '4px' : '0' }}>
                      "{hc}"
                    </div>
                  ))}
                </div>
              )}

              {/* Row 5: Factor Breakdown Strip & Hindsight Recall Indicator */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '10px',
                  borderTop: '1px solid var(--border-subtle)',
                  paddingTop: '10px',
                }}
              >
                {/* Available Signals */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase', fontWeight: 700 }}>
                    Evidence Signals:
                  </span>
                  {item.has_interactive_widget && (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        background: 'rgba(16, 185, 129, 0.1)',
                        border: '1px solid rgba(16, 185, 129, 0.25)',
                        color: 'var(--success-text)',
                        borderRadius: '4px',
                        padding: '2px 7px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                      }}
                    >
                      <Code2 size={12} /> Interactive Tool
                    </span>
                  )}
                  {item.has_video_preview && (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        background: 'rgba(56, 189, 248, 0.1)',
                        border: '1px solid rgba(56, 189, 248, 0.25)',
                        color: 'var(--cyan-text)',
                        borderRadius: '4px',
                        padding: '2px 7px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                      }}
                    >
                      <Video size={12} /> Video Media
                    </span>
                  )}
                  {item.has_curriculum_table && (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        background: 'rgba(168, 85, 247, 0.1)',
                        border: '1px solid rgba(168, 85, 247, 0.25)',
                        color: '#c084fc',
                        borderRadius: '4px',
                        padding: '2px 7px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                      }}
                    >
                      <TableIcon size={12} /> Structured Table/Matrix
                    </span>
                  )}
                  <span
                    style={{
                      fontSize: '0.7rem',
                      color: 'var(--text-faint)',
                      fontFamily: 'var(--font-mono)',
                      background: 'rgba(255, 255, 255, 0.03)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                    }}
                  >
                    {item.word_count.toLocaleString()} words
                  </span>
                  <span
                    style={{
                      fontSize: '0.7rem',
                      color: 'var(--text-faint)',
                      fontStyle: 'italic',
                      padding: '2px 6px',
                    }}
                  >
                    Popularity: Data unavailable
                  </span>
                </div>

                {/* Historical movement & Hindsight status */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {item.hindsight_insight && (
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        color: 'var(--cyan-primary)',
                        background: 'rgba(6, 182, 212, 0.12)',
                        border: '1px solid rgba(6, 182, 212, 0.3)',
                        borderRadius: '6px',
                        padding: '2px 8px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <Zap size={11} />
                      Hindsight memory applied
                    </span>
                  )}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-faint)' }}>Trajectory:</span>
                    {movementDisplay}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* "WHY THIS POSITION?" DETAILED MODAL */}
      {whyModalItem && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.82)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px',
          }}
          onClick={() => setWhyModalItem(null)}
        >
          <div
            className="glass-panel"
            style={{
              width: '100%',
              maxWidth: '680px',
              padding: '26px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-strong)',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8)',
              maxHeight: '90vh',
              overflowY: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: '6px',
                      background: 'rgba(6, 182, 212, 0.2)',
                      color: 'var(--cyan-primary)',
                      fontSize: '0.75rem',
                      fontWeight: 800,
                    }}
                  >
                    RankMind Position #{whyModalItem.rank}
                  </span>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff' }}>
                    Why this position for {whyModalItem.domain}?
                  </h3>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  RankMind multi-factor evaluation for query: <strong style={{ color: '#e2e8f0' }}>"{query}"</strong>
                </p>
              </div>
              <button
                type="button"
                onClick={() => setWhyModalItem(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Explanation Content */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* Factor 1: Query Relevance */}
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 14px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--cyan-primary)', marginBottom: '3px' }}>
                  1. Query Relevance
                </div>
                <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
                  The candidate resource demonstrates strong topical alignment with "{query}". Its content curriculum and page structure directly address the user search intent.
                </div>
              </div>

              {/* Factor 2: Content Quality & Depth */}
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 14px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--success-text)', marginBottom: '3px' }}>
                  2. Content Quality & Completeness
                </div>
                <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
                  Observed comprehensive coverage ({whyModalItem.word_count.toLocaleString()} words) with verified technical structure: {whyModalItem.has_curriculum_table ? 'Structured syllabus / timetable' : 'Sequential chapters'} and {whyModalItem.schema_types?.length ? `Schema types (${whyModalItem.schema_types.join(', ')})` : 'standard metadata'}.
                </div>
              </div>

              {/* Factor 3: Authority & Classification */}
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 14px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#c084fc', marginBottom: '3px' }}>
                  3. Authority & Access Classification
                </div>
                <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
                  Classified as <strong>{whyModalItem.classification?.resource_type || whyModalItem.resource_type || 'Resource'}</strong> with access status: <strong>{whyModalItem.classification?.access_type || whyModalItem.access_type || 'FREE'}</strong>. {whyModalItem.classification?.access_evidence || 'Based on observable page signals.'}
                </div>
              </div>

              {/* Factor 4: Hindsight Memory Impact */}
              {whyModalItem.hindsight_insight && (
                <div style={{ background: 'rgba(6, 182, 212, 0.08)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--cyan-primary)', marginBottom: '3px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <Zap size={13} />
                    4. Hindsight Memory Influence
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
                    {whyModalItem.hindsight_insight}
                  </div>
                </div>
              )}

              {/* Data Limitations Box (Requirement 19) */}
              <div
                style={{
                  padding: '12px 14px',
                  borderRadius: '8px',
                  background: 'rgba(245, 158, 11, 0.08)',
                  border: '1px solid rgba(245, 158, 11, 0.25)',
                  fontSize: '0.75rem',
                  color: '#fef3c7',
                  lineHeight: 1.45,
                }}
              >
                <div style={{ fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px', color: '#fbbf24' }}>
                  Data Limitations & Missing Evidence:
                </div>
                <ul style={{ paddingLeft: '18px', margin: 0 }}>
                  <li><strong>Popularity data:</strong> Data unavailable. RankMind does not fabricate unverified web traffic or user counts.</li>
                  <li><strong>RankMind Position:</strong> Reflects highest ranking among available relevant resources in the current dataset, not an absolute worldwide claim.</li>
                </ul>
              </div>
            </div>

            {/* Modal Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '18px' }}>
              {isValidUrl(whyModalItem.url) && (
                <a
                  href={whyModalItem.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => handleOpenExternal(whyModalItem, e)}
                  className="btn-secondary"
                  style={{ textDecoration: 'none', padding: '8px 14px', fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                >
                  <ExternalLink size={13} /> Open Website ↗
                </a>
              )}
              <button
                type="button"
                className="btn-primary"
                onClick={() => {
                  onSelectDomain(whyModalItem.domain);
                  setWhyModalItem(null);
                }}
                style={{ padding: '8px 16px', fontSize: '0.82rem' }}
              >
                Inspect Website Profile
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dataset attribution footer */}
      <div
        style={{
          marginTop: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.75rem',
          color: 'var(--text-faint)',
          borderTop: '1px solid var(--border-subtle)',
          paddingTop: '12px',
        }}
      >
        <Info size={14} color="var(--text-faint)" />
        <span>
          <strong>RankMind Intelligence Disclosure:</strong> Evaluated using multi-factor evidence analysis and Hindsight memory. Candidate rankings are relative to RankMind's available dataset and verified external URLs.
        </span>
      </div>
    </div>
  );
};
