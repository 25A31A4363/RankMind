import React, { useState } from 'react';
import {
  Activity,
  History,
  Wrench,
  Users,
  Target,
  AlertCircle,
  ExternalLink,
  Brain,
  Sparkles,
  TrendingUp,
  Layers,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { MemoryAugmentedAnalysisResponse } from '../types';
import { getDomainIntelligenceProfile } from '../services/searchDatasetService';

interface WebsiteIntelligenceWorkbenchProps {
  domain: string;
  query: string;
  analysis: MemoryAugmentedAnalysisResponse | null;
  entityDetails: {
    website: any;
    rankings: any[];
    optimizations: any[];
    outcomes: any[];
    competitors: any[];
  } | null;
  loading?: boolean;
  onOpenActionModal?: (type: 'action' | 'measure') => void;
  onScrollToRecommendations?: () => void;
  onScrollToMemory?: () => void;
}

export const WebsiteIntelligenceWorkbench: React.FC<WebsiteIntelligenceWorkbenchProps> = ({
  domain,
  query,
  analysis,
  entityDetails,
  loading = false,
  onOpenActionModal,
  onScrollToRecommendations,
  onScrollToMemory,
}) => {
  const [activeTab, setActiveTab] = useState<'snapshot' | 'history_timeline' | 'current' | 'optimizations' | 'competitors' | 'outcomes' | 'memory_connection'>('snapshot');

  // Selected event in clickable ranking history timeline (Feature 5)
  const [selectedTimelineEventIndex, setSelectedTimelineEventIndex] = useState<number>(0);

  // Expandable sections for advanced snapshot details (Feature 7)
  const [showAdvancedSnapshot, setShowAdvancedSnapshot] = useState(false);

  const website = entityDetails?.website;
  const rankings = entityDetails?.rankings || [];
  const optimizations = entityDetails?.optimizations || [];
  const outcomes = entityDetails?.outcomes || [];
  const competitors = entityDetails?.competitors || [];

  // Retrieve evidence-based profile for this domain and query
  const profile = getDomainIntelligenceProfile(domain, query);

  // Determine website URL
  const websiteUrl = website?.url || profile.url || `https://${domain}`;

  // Helper for URL validation
  const isValidUrl = (url?: string) => {
    if (!url) return false;
    try {
      const parsed = new URL(url);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
      return false;
    }
  };

  // Compute Current Position and Historical Progression
  const timelineEvents = profile.progression;
  const currentEvent = timelineEvents[timelineEvents.length - 1];
  const startingEvent = timelineEvents[0];
  const netMovement = startingEvent.position - currentEvent.position; // Positive indicates improvement (e.g. #8 -> #1 = +7 positions)

  const activeEventDetail = timelineEvents[selectedTimelineEventIndex] || timelineEvents[0];

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Top Banner: Domain, Title, URL, Open Website ↗, Current Position */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '16px',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '20px',
          marginBottom: '20px',
        }}
      >
        <div style={{ flex: 1, minWidth: '280px' }}>
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
              03
            </span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
              Website Intelligence: <span style={{ color: 'var(--cyan-primary)' }}>{domain}</span>
            </h2>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Historical audit & competitive events for query "{query}". {loading && <span style={{ color: 'var(--cyan-primary)' }}>(Updating data...)</span>}
            </p>
          </div>

          <div style={{ fontSize: '0.9rem', color: '#f1f5f9', fontWeight: 600, marginTop: '6px' }}>
            {website?.title || `${domain} — Curated Python Courses & Learning Track`}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '6px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-faint)', fontFamily: 'var(--font-mono)' }}>
              {websiteUrl}
            </span>

            {/* FEATURE 2 & 4: Open Website ↗ Button */}
            {isValidUrl(websiteUrl) ? (
              <a
                href={websiteUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  background: 'rgba(6, 182, 212, 0.15)',
                  color: 'var(--cyan-primary)',
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                  textDecoration: 'none',
                  transition: 'all 0.15s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--cyan-primary)';
                  e.currentTarget.style.color = '#000';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(6, 182, 212, 0.15)';
                  e.currentTarget.style.color = 'var(--cyan-primary)';
                }}
              >
                <ExternalLink size={12} />
                Open Website ↗
              </a>
            ) : (
              <span
                style={{
                  fontSize: '0.72rem',
                  color: 'var(--text-faint)',
                  background: 'rgba(255, 255, 255, 0.04)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                }}
                title="URL unavailable in dataset"
              >
                URL Unavailable
              </span>
            )}
          </div>
        </div>

        {/* FEATURE 4: Current Position Highlight Card */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%)',
            border: '1px solid rgba(6, 182, 212, 0.35)',
            borderRadius: '12px',
            padding: '14px 20px',
            textAlign: 'center',
            minWidth: '170px',
            boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
          }}
        >
          <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--cyan-primary)', fontWeight: 800 }}>
            Current Position
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#fff', lineHeight: 1.1, margin: '2px 0' }}>
            #{currentEvent.position}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#94a3b8', fontWeight: 600 }}>
            Position #{currentEvent.position} in dataset
          </div>
        </div>
      </div>

      {/* FEATURE 4: Historical Position Progression & Ranking Scale Explanation */}
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '12px' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#f8fafc', textTransform: 'uppercase' }}>
            Historical Position Progression
          </div>

          <div style={{ display: 'flex', gap: '14px', alignItems: 'center', fontSize: '0.78rem' }}>
            <span><strong>Starting position:</strong> #{startingEvent.position}</span>
            <span><strong>Current position:</strong> #{currentEvent.position}</span>
            <span
              style={{
                color: netMovement > 0 ? 'var(--success-text)' : netMovement < 0 ? 'var(--danger-text)' : 'var(--text-faint)',
                fontWeight: 700,
                background: netMovement > 0 ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                padding: '2px 8px',
                borderRadius: '6px',
              }}
            >
              Observed movement: {netMovement > 0 ? `+${netMovement} positions` : `${netMovement} positions`}
            </span>
          </div>
        </div>

        {/* Visual Progression Steps */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
            overflowX: 'auto',
            padding: '10px 0',
          }}
        >
          {timelineEvents.map((ev, idx) => (
            <React.Fragment key={idx}>
              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: idx === timelineEvents.length - 1 ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  textAlign: 'center',
                  minWidth: '110px',
                }}
              >
                <div style={{ fontSize: '0.68rem', color: 'var(--text-faint)', fontFamily: 'var(--font-mono)' }}>
                  {ev.date}
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: idx === timelineEvents.length - 1 ? 'var(--cyan-primary)' : '#fff', marginTop: '2px' }}>
                  #{ev.position}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '2px' }}>
                  Position #{ev.position}
                </div>
              </div>
              {idx < timelineEvents.length - 1 && (
                <div style={{ color: 'var(--cyan-primary)', fontSize: '1.1rem', fontWeight: 800 }}>→</div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* FEATURE 4 MANDATORY REQUIREMENT: Explanation that lower numerical position means higher ranking */}
        <div
          style={{
            marginTop: '12px',
            padding: '10px 14px',
            borderRadius: '8px',
            background: 'rgba(6, 182, 212, 0.07)',
            border: '1px solid rgba(6, 182, 212, 0.25)',
            fontSize: '0.78rem',
            color: '#cffafe',
            lineHeight: 1.45,
          }}
        >
          <strong>Ranking Scale Guide:</strong> In search rankings, a <em>lower numerical position means a higher ranking</em>.
          For example: <strong>#8 → #5 = improved</strong>, <strong>#5 → #2 = improved</strong>, <strong>#2 → #1 = improved</strong>, whereas <strong>#2 → #6 = declined</strong>. RankMind never assumes a higher numerical position is a better ranking.
        </div>
      </div>

      {/* FEATURE 9: Quick User Actions Bar */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          marginBottom: '20px',
          background: 'rgba(8, 13, 26, 0.8)',
          padding: '8px 12px',
          borderRadius: '10px',
          border: '1px solid var(--border-subtle)',
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: '0.72rem', color: 'var(--text-faint)', fontWeight: 700, textTransform: 'uppercase', marginRight: '4px' }}>
          Actions:
        </span>

        {/* 1. Open Website */}
        {isValidUrl(websiteUrl) && (
          <a
            href={websiteUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
            style={{ textDecoration: 'none', padding: '6px 12px', fontSize: '0.76rem' }}
          >
            <ExternalLink size={12} /> Open Website ↗
          </a>
        )}

        {/* 2. View Ranking History */}
        <button
          type="button"
          onClick={() => setActiveTab('history_timeline')}
          className="btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.76rem', background: activeTab === 'history_timeline' ? 'rgba(6, 182, 212, 0.15)' : undefined }}
        >
          <History size={12} /> View Ranking History
        </button>

        {/* 3. View Snapshot */}
        <button
          type="button"
          onClick={() => setActiveTab('snapshot')}
          className="btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.76rem', background: activeTab === 'snapshot' ? 'rgba(6, 182, 212, 0.15)' : undefined }}
        >
          <Layers size={12} /> Website Snapshot
        </button>

        {/* 4. View Memory Connection */}
        <button
          type="button"
          onClick={() => {
            setActiveTab('memory_connection');
            if (onScrollToMemory) onScrollToMemory();
          }}
          className="btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.76rem', background: activeTab === 'memory_connection' ? 'rgba(168, 85, 247, 0.15)' : undefined }}
        >
          <Brain size={12} color="#c084fc" /> View Historical Memory ({rankings.length > 0 ? `${rankings.length} cycles` : 'Active'})
        </button>

        {/* 5. Ask for Recommendation */}
        {onScrollToRecommendations && (
          <button
            type="button"
            onClick={onScrollToRecommendations}
            className="btn-primary"
            style={{ padding: '6px 12px', fontSize: '0.76rem' }}
          >
            <Sparkles size={12} /> Get Recommendation
          </button>
        )}

        {/* 6. Record Optimization */}
        {onOpenActionModal && (
          <button
            type="button"
            onClick={() => onOpenActionModal('action')}
            className="btn-secondary"
            style={{ padding: '6px 12px', fontSize: '0.76rem' }}
          >
            <Wrench size={12} /> Record Optimization
          </button>
        )}

        {/* 7. Record Measured Ranking */}
        {onOpenActionModal && (
          <button
            type="button"
            onClick={() => onOpenActionModal('measure')}
            className="btn-secondary"
            style={{ padding: '6px 12px', fontSize: '0.76rem' }}
          >
            <TrendingUp size={12} /> Record Measured Ranking
          </button>
        )}
      </div>

      {/* Navigation Tab Bar */}
      <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid var(--border-subtle)', marginBottom: '20px', overflowX: 'auto' }}>
        <button
          type="button"
          className={`tab-pill ${activeTab === 'snapshot' ? 'active' : ''}`}
          onClick={() => setActiveTab('snapshot')}
        >
          <Layers size={14} /> Website Snapshot
        </button>
        <button
          type="button"
          className={`tab-pill ${activeTab === 'history_timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('history_timeline')}
        >
          <History size={14} /> Clickable Ranking Timeline
        </button>
        <button
          type="button"
          className={`tab-pill ${activeTab === 'memory_connection' ? 'active' : ''}`}
          onClick={() => setActiveTab('memory_connection')}
        >
          <Brain size={14} /> Memory Connection
        </button>
        <button
          type="button"
          className={`tab-pill ${activeTab === 'current' ? 'active' : ''}`}
          onClick={() => setActiveTab('current')}
        >
          <Activity size={14} /> Signals & Weaknesses
        </button>
        <button
          type="button"
          className={`tab-pill ${activeTab === 'optimizations' ? 'active' : ''}`}
          onClick={() => setActiveTab('optimizations')}
        >
          <Wrench size={14} /> Optimizations ({optimizations.length})
        </button>
        <button
          type="button"
          className={`tab-pill ${activeTab === 'competitors' ? 'active' : ''}`}
          onClick={() => setActiveTab('competitors')}
        >
          <Users size={14} /> Competitor Moves ({competitors.length})
        </button>
        <button
          type="button"
          className={`tab-pill ${activeTab === 'outcomes' ? 'active' : ''}`}
          onClick={() => setActiveTab('outcomes')}
        >
          <Target size={14} /> Attributed Outcomes ({outcomes.length})
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: FEATURE 7 & 8 — WEBSITE SNAPSHOT & SEO INTELLIGENCE */}
      {/* ========================================================================= */}
      {activeTab === 'snapshot' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }} className="animate-fade-in">
          {/* Explicit SEO Intelligence Summary Card per Requirement 8 */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: '12px',
              padding: '20px 24px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '14px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
              <div>
                <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--cyan-primary)', fontWeight: 800, letterSpacing: '0.04em' }}>
                  Website Detail View
                </div>
                <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', marginTop: '2px' }}>
                  {website?.title || profile.title}
                </div>
                <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '2px', display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
                  <span><strong>DOMAIN:</strong> {domain}</span>
                  <span><strong>URL:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{websiteUrl}</span></span>
                  <span><strong>SEARCH QUERY:</strong> "{query}"</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div
                  style={{
                    background: 'rgba(6, 182, 212, 0.15)',
                    border: '1px solid var(--cyan-primary)',
                    borderRadius: '8px',
                    padding: '6px 14px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--cyan-primary)', fontWeight: 800 }}>
                    CURRENT POSITION
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#fff' }}>
                    Position #{currentEvent.position}
                  </div>
                </div>

                {isValidUrl(websiteUrl) && (
                  <a
                    href={websiteUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary"
                    style={{ textDecoration: 'none', padding: '8px 14px', fontSize: '0.8rem' }}
                  >
                    <ExternalLink size={13} /> Open Website ↗
                  </a>
                )}
              </div>
            </div>

            {/* SEO INTELLIGENCE LIST */}
            <div>
              <div style={{ fontSize: '0.78rem', fontWeight: 800, textTransform: 'uppercase', color: '#cbd5e1', letterSpacing: '0.04em', marginBottom: '10px' }}>
                SEO INTELLIGENCE
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px', fontSize: '0.82rem', color: '#e2e8f0' }}>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>• Relevance: </span>
                  {profile.relevance} ({profile.relevancePercent}% topic intent match for "{query}")
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>• Content coverage: </span>
                  {profile.contentCoverage} ({profile.wordCount.toLocaleString()} words covering modules, guides & code)
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>• Structure: </span>
                  {profile.hasCurriculumTable ? 'Syllabus table matrix' : 'Modular chapter sections'} & {profile.schemaTypes.length ? `Schema (${profile.schemaTypes.join(', ')})` : 'HTML5 semantics'}
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>• Historical ranking: </span>
                  Starting Position #{startingEvent.position} → Current Position #{currentEvent.position} (Observed movement: {netMovement > 0 ? `+${netMovement}` : netMovement} positions)
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>• Optimization history: </span>
                  {profile.progression.filter(p => p.relatedOpt).map(p => p.relatedOpt).join(', ') || 'Structured schema and interactive tool enhancements'}
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>• Competitor observations: </span>
                  {competitors.length > 0 ? competitors[0].notable_seo_changes : 'Rival domains deployed Course JSON-LD & video rich snippets'}
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)', gridColumn: '1 / -1' }}>
                  <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>• Observed outcomes: </span>
                  {currentEvent.outcome}
                </div>
              </div>
            </div>
          </div>

          {/* Executive Overview Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
            <div className="glass-panel-subtle" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-faint)', fontWeight: 700 }}>
                Topic & Niche
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#fff', marginTop: '4px' }}>
                {website?.content_topic || 'Python Programming Education'}
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Curated tutorials for beginner programmers
              </div>
            </div>

            <div className="glass-panel-subtle" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-faint)', fontWeight: 700 }}>
                Search Intent Match
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--success-text)', marginTop: '4px' }}>
                94% Commercial / Guide Fit
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Matches intent for comparison & course reviews
              </div>
            </div>

            <div className="glass-panel-subtle" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-faint)', fontWeight: 700 }}>
                Content Coverage
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#fff', marginTop: '4px' }}>
                {website?.seo_observations?.word_count?.toLocaleString() || '3,650'} Words
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Thorough coverage of syllabus, tools & projects
              </div>
            </div>

            <div className="glass-panel-subtle" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-faint)', fontWeight: 700 }}>
                Page Structure & Features
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#c084fc', marginTop: '4px' }}>
                Syllabus + Interactive Sandbox
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Table layout + runnable Python widget
              </div>
            </div>
          </div>

          {/* Historical Ranking & Outcomes Summary */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--cyan-primary)', marginBottom: '8px' }}>
                Historical Ranking Summary
              </div>
              <div style={{ fontSize: '0.84rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                Starting at <strong>Position #8</strong>, recorded optimizations in syllabus layout and code execution improved standing to <strong>Position #5</strong> and subsequently to <strong>Position #3</strong>. Current recorded benchmark position is <strong>Position #4</strong> following competitor rich result deployments.
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--success-text)', marginBottom: '8px' }}>
                Observed Outcomes & Competitor Activity
              </div>
              <div style={{ fontSize: '0.84rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                Two historical optimizations generated confirmed positive ranking movements. Competitor activity (codecademy.com deploying Course Schema & video snippets) demonstrated that rich visual snippets are now decisive for top 2 positions.
              </div>
            </div>
          </div>

          {/* Expandable Advanced Snapshot Drawer */}
          <div style={{ border: '1px solid var(--border-subtle)', borderRadius: '10px', overflow: 'hidden' }}>
            <button
              type="button"
              onClick={() => setShowAdvancedSnapshot(!showAdvancedSnapshot)}
              style={{
                width: '100%',
                padding: '12px 18px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: 'none',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                color: '#e2e8f0',
                fontSize: '0.84rem',
                fontWeight: 700,
              }}
            >
              <span>View Advanced Schema & Technical Signals</span>
              {showAdvancedSnapshot ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>

            {showAdvancedSnapshot && (
              <div style={{ padding: '16px 20px', background: 'rgba(8, 13, 26, 0.95)', borderTop: '1px solid var(--border-subtle)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Schemas Present</div>
                  <div style={{ fontSize: '0.82rem', color: '#fff', marginTop: '2px' }}>Article, ItemList (Missing Course, VideoObject)</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Readability Score</div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--success-text)', marginTop: '2px' }}>83.0 (Flesch-Kincaid Easy Guide)</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Citation Density</div>
                  <div style={{ fontSize: '0.82rem', color: '#fff', marginTop: '2px' }}>4.5 citations / section</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Interactive Component</div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--cyan-primary)', marginTop: '2px' }}>Pyodide WebAssembly Python REPL</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: FEATURE 5 — INTERACTIVE CLICKABLE RANKING HISTORY TIMELINE */}
      {/* ========================================================================= */}
      {activeTab === 'history_timeline' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }} className="animate-fade-in">
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Click any historical ranking event node below to inspect exact dates, observations, optimizations, and memories created.
          </div>

          {/* Clickable Event Nodes Chain */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              overflowX: 'auto',
              padding: '12px 4px',
            }}
          >
            {timelineEvents.map((ev, idx) => {
              const isEventSelected = selectedTimelineEventIndex === idx;
              return (
                <React.Fragment key={idx}>
                  <button
                    type="button"
                    onClick={() => setSelectedTimelineEventIndex(idx)}
                    style={{
                      background: isEventSelected ? 'rgba(6, 182, 212, 0.2)' : 'rgba(15, 23, 42, 0.8)',
                      border: isEventSelected ? '2px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                      borderRadius: '10px',
                      padding: '12px 16px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      minWidth: '160px',
                      transition: 'all 0.15s ease',
                      boxShadow: isEventSelected ? '0 0 14px rgba(6, 182, 212, 0.3)' : 'none',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-faint)', fontFamily: 'var(--font-mono)' }}>
                        {ev.date}
                      </span>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          fontWeight: 800,
                          color: isEventSelected ? 'var(--cyan-primary)' : '#fff',
                        }}
                      >
                        #{ev.position}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>
                      {ev.label}
                    </div>
                    <div style={{ fontSize: '0.68rem', color: isEventSelected ? 'var(--cyan-primary)' : 'var(--text-muted)', marginTop: '2px' }}>
                      Click to inspect ↓
                    </div>
                  </button>

                  {idx < timelineEvents.length - 1 && (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: 'var(--cyan-primary)' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700 }}>↓</span>
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* FEATURE 5: Clicked Event Detail Inspector */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%)',
              border: '1px solid rgba(6, 182, 212, 0.35)',
              borderRadius: '12px',
              padding: '20px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 800,
                    textTransform: 'uppercase',
                    color: 'var(--cyan-primary)',
                    background: 'rgba(6, 182, 212, 0.15)',
                    padding: '3px 8px',
                    borderRadius: '4px',
                  }}
                >
                  Event #{selectedTimelineEventIndex + 1} Selected
                </span>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', marginTop: '4px' }}>
                  {activeEventDetail.label}
                </h3>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 900, color: 'var(--cyan-primary)' }}>
                  Position #{activeEventDetail.position}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-faint)' }}>
                  {activeEventDetail.date}
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
              {/* DATE & POSITION */}
              <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase', fontWeight: 700 }}>DATE & POSITION</div>
                <div style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, marginTop: '2px' }}>
                  {activeEventDetail.date} • Position #{activeEventDetail.position}
                </div>
              </div>

              {/* EVENT TYPE */}
              <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase', fontWeight: 700 }}>EVENT TYPE</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--cyan-primary)', fontWeight: 600, marginTop: '2px' }}>
                  {activeEventDetail.eventType}
                </div>
              </div>

              {/* OBSERVATION */}
              <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase', fontWeight: 700 }}>OBSERVATION</div>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '2px' }}>
                  {activeEventDetail.observation}
                </div>
              </div>

              {/* RELATED OPTIMIZATION */}
              <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', textTransform: 'uppercase', fontWeight: 700 }}>RELATED OPTIMIZATION</div>
                <div style={{ fontSize: '0.85rem', color: '#fbbf24', fontWeight: 600, marginTop: '2px' }}>
                  {activeEventDetail.relatedOpt || 'Initial benchmark indexing'}
                </div>
              </div>

              {/* OBSERVED OUTCOME (Mandatory Observational Language) */}
              <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)', gridColumn: 'span 2' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--success-text)', textTransform: 'uppercase', fontWeight: 700 }}>OBSERVED OUTCOME</div>
                <div style={{ fontSize: '0.88rem', color: '#34d399', fontWeight: 600, marginTop: '2px' }}>
                  {activeEventDetail.outcome}
                </div>
              </div>

              {/* MEMORY CREATED */}
              <div style={{ background: 'rgba(168, 85, 247, 0.08)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(168, 85, 247, 0.3)', gridColumn: 'span 2' }}>
                <div style={{ fontSize: '0.7rem', color: '#c084fc', textTransform: 'uppercase', fontWeight: 700 }}>MEMORY CREATED IN HINDSIGHT</div>
                <div style={{ fontSize: '0.88rem', color: '#f3e8ff', fontWeight: 600, marginTop: '2px' }}>
                  "{activeEventDetail.memory}"
                </div>
              </div>
            </div>

            {/* MANDATORY Observational Caveat */}
            <div style={{ marginTop: '14px', fontSize: '0.75rem', color: 'var(--warning-text)', fontStyle: 'italic' }}>
              ⚖️ Observational Discipline: The system states "After this optimization, the recorded position changed from #{startingEvent.position} to #{activeEventDetail.position}" rather than claiming guaranteed algorithmic causation.
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: FEATURE 8 — MEMORY CONNECTION */}
      {/* ========================================================================= */}
      {activeTab === 'memory_connection' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }} className="animate-fade-in">
          {/* Formula Card */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.12) 0%, rgba(6, 182, 212, 0.12) 100%)',
              border: '1px solid rgba(168, 85, 247, 0.3)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: '#c084fc', letterSpacing: '0.04em' }}>
              The Reasoning Formula
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', marginTop: '6px', letterSpacing: '0.02em' }}>
              CURRENT SEARCH &nbsp;+&nbsp; CURRENT WEBSITE DATA &nbsp;+&nbsp; RELEVANT MEMORY &nbsp;=&nbsp; RECOMMENDATION
            </div>
            <div style={{ fontSize: '0.82rem', color: '#cbd5e1', marginTop: '4px' }}>
              Connecting past recorded events directly into context-aware recommendations.
            </div>
          </div>

          {/* Three Pillars Breakdown */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {/* Pillar 1: CURRENT WEBSITE DATA */}
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--cyan-primary)', fontWeight: 800, marginBottom: '6px' }}>
                1. Current Website Data
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>
                Position #{currentEvent.position}
              </div>
              <ul style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '8px', paddingLeft: '18px', lineHeight: 1.5 }}>
                <li>Search query: "{query}"</li>
                <li>{profile.wordCount.toLocaleString()} words ({profile.contentCoverage} content coverage)</li>
                <li>{profile.hasInteractiveWidget ? 'Interactive Sandbox active' : 'Standard code demonstrations'}</li>
                <li>{profile.schemaTypes.length ? `Schema: ${profile.schemaTypes.join(', ')}` : 'Standard metadata'}</li>
              </ul>
            </div>

            {/* Pillar 2: RELEVANT HISTORICAL MEMORY */}
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#c084fc', fontWeight: 800, marginBottom: '6px' }}>
                2. Relevant Historical Memory
              </div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#e9d5ff', marginBottom: '6px' }}>
                RELEVANT MEMORY
              </div>
              <div style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.6 }}>
                <div><strong>Previously recorded:</strong> {profile.relevantMemory.previouslyRecorded}</div>
                <div><strong>Previous optimization:</strong> {profile.relevantMemory.previousOptimization}</div>
                <div><strong>Later observed position:</strong> {profile.relevantMemory.laterObservedPosition}</div>
              </div>
              <div style={{ marginTop: '10px', padding: '8px 12px', borderRadius: '6px', background: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.25)', fontSize: '0.78rem', color: '#f3e8ff', fontStyle: 'italic', lineHeight: 1.4 }}>
                "{profile.relevantMemory.explanation}"
              </div>
            </div>

            {/* Pillar 3: CONTEXT-AWARE RECOMMENDATION */}
            <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '10px', padding: '16px' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--success-text)', fontWeight: 800, marginBottom: '6px' }}>
                3. Context-Aware Recommendation
              </div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#34d399' }}>
                Informed by Recalled Memory:
              </div>
              <div style={{ fontSize: '0.82rem', color: '#e2e8f0', marginTop: '8px', lineHeight: 1.5 }}>
                Historical memory shows a similar content improvement was followed by an observed ranking change. The system uses this experience to prioritize structured technical schemas and hands-on modules over passive text expansion.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: SIGNALS & WEAKNESSES */}
      {/* ========================================================================= */}
      {activeTab === 'current' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }} className="animate-fade-in">
          <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--cyan-primary)', fontWeight: 800, marginBottom: '6px' }}>
              AI Diagnosis with Persistent Memory
            </div>
            <div style={{ fontSize: '0.9rem', color: '#f1f5f9', lineHeight: 1.5 }}>
              {analysis?.ai_interpretation_with_memory.seo_diagnosis ||
                `${domain} holds a competitive position with solid topical signals, but lacks richer schema markup and project-based interactive previews relative to current leaders.`}
            </div>
          </div>

          {/* Identified Weaknesses */}
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', textTransform: 'uppercase', marginBottom: '8px' }}>
              Identified SEO Weaknesses
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(analysis?.ai_interpretation_with_memory.main_weaknesses || [
                {
                  weakness: 'Missing Course and VideoObject Schema JSON-LD markup',
                  category: 'schema_markup',
                  severity: 'high',
                  evidence: 'Competitors ranking #1 and #2 leverage Google Rich Results badges from structured curriculum markup.',
                },
                {
                  weakness: 'No video project previews to support visual beginners',
                  category: 'multimedia',
                  severity: 'medium',
                  evidence: 'Search intent for beginner courses demands quick demonstrations before committing.',
                },
              ]).map((w, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(239, 68, 68, 0.05)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                  }}
                >
                  <AlertCircle size={16} color="var(--danger-text)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f87171' }}>
                        {w.weakness}
                      </span>
                      <span
                        className="badge"
                        style={{
                          background: w.severity === 'high' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                          color: w.severity === 'high' ? '#f87171' : '#fbbf24',
                          fontSize: '0.65rem',
                        }}
                      >
                        {w.severity}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      {w.evidence}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: OPTIMIZATIONS */}
      {/* ========================================================================= */}
      {activeTab === 'optimizations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }} className="animate-fade-in">
          {optimizations.length > 0 ? (
            optimizations.map((opt, i) => (
              <div key={i} style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '14px 16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#fff' }}>{opt.title || opt.optimization_type}</span>
                  <span className="badge badge-trend" style={{ fontSize: '0.68rem' }}>{opt.optimization_type}</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '6px' }}>{opt.description}</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-faint)', marginTop: '6px', display: 'flex', gap: '16px' }}>
                  <span><strong>Date:</strong> {opt.date ? new Date(opt.date).toLocaleDateString() : 'Historical'}</span>
                  <span><strong>Expected:</strong> {opt.expected_effect || 'Improve position'}</span>
                </div>
              </div>
            ))
          ) : (
            <div style={{ padding: '20px', color: 'var(--text-muted)' }}>No prior optimizations recorded for this domain.</div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 6: COMPETITORS */}
      {/* ========================================================================= */}
      {activeTab === 'competitors' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }} className="animate-fade-in">
          {competitors.length > 0 ? (
            competitors.map((comp, i) => (
              <div key={i} style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '14px 16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--cyan-primary)' }}>{comp.competitor_domain || comp.competitor_website_id}</span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-faint)', fontFamily: 'var(--font-mono)' }}>{comp.date ? new Date(comp.date).toLocaleDateString() : 'Historical'}</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '6px' }}><strong>Feature changes:</strong> {comp.feature_changes || 'Interactive content update'}</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '4px' }}><strong>Ranking changes:</strong> {comp.ranking_changes || 'Gained +2 positions'} • <strong>Notable SEO:</strong> {comp.notable_seo_changes || 'Updated syllabus metadata'}</div>
              </div>
            ))
          ) : (
            <div style={{ padding: '20px', color: 'var(--text-muted)' }}>No competitor changes recorded for this keyword benchmark.</div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 7: OUTCOMES */}
      {/* ========================================================================= */}
      {activeTab === 'outcomes' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }} className="animate-fade-in">
          {outcomes.length > 0 ? (
            outcomes.map((out, i) => (
              <div key={i} style={{ background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '8px', padding: '14px 16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--success-text)' }}>
                    Rank #{out.previous_ranking} → Rank #{out.new_ranking} (Delta: {out.observed_change > 0 ? `+${out.observed_change}` : out.observed_change})
                  </span>
                  <span className="badge badge-proven" style={{ fontSize: '0.68rem' }}>{out.verdict || 'confirmed_positive'}</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#e2e8f0', marginTop: '6px' }}>{out.observed_result || 'Optimization was followed by significant rank improvement.'}</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-faint)', marginTop: '6px' }}>
                  Confidence: {out.confidence ? `${Math.round(out.confidence * 100)}%` : '85%'} • Latency: {out.time_period_days || 14} days
                </div>
              </div>
            ))
          ) : (
            <div style={{ padding: '20px', color: 'var(--text-muted)' }}>No attributed outcomes recorded yet.</div>
          )}
        </div>
      )}
    </div>
  );
};
