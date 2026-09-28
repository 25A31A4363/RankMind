import React, { useState, useRef } from 'react';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { SearchResultsComparison } from './components/SearchResultsComparison';
import { WebsiteIntelligenceWorkbench } from './components/WebsiteIntelligenceWorkbench';
import { AiRecommendationCard } from './components/AiRecommendationCard';
import { MemoryPanel } from './components/MemoryPanel';
import { LearningTimelineView } from './components/LearningTimelineView';
import { BeforeAfterToggle } from './components/BeforeAfterToggle';
import { ActionLoggerModal } from './components/ActionLoggerModal';
import {
  SERPSnapshot,
  SERPItem,
  MemoryAugmentedAnalysisResponse,
  BeforeAfterComparisonResponse,
  WebsiteEventTimeline,
  LearningHistoryItem,
  UserFeedbackInput,
  QueryUnderstanding,
} from './types';
import {
  fetchSnapshots,
  fetchMemoryAnalysis,
  fetchWebsiteDetails,
  fetchBeforeAfterComparison,
  fetchWebsiteTimeline,
  fetchLearningHistory,
  submitUserFeedback,
  resetDemoState,
  executeIntelligenceSearch,
  recordWebsiteInteraction,
} from './services/api';
import {
  getSERPItemsForQuery,
  getFallbackMemoryAnalysis,
  SearchSession,
} from './services/searchDatasetService';
import { AlertCircle, Search, History as HistoryIcon, PlusCircle } from 'lucide-react';

export const App: React.FC = () => {
  // REQUIREMENT 1 & 11: The search box must initially be EMPTY. No default query, no default target website.
  const [query, setQuery] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('');

  // General-Purpose Website Intelligence State
  const [queryUnderstanding, setQueryUnderstanding] = useState<QueryUnderstanding | null>(null);
  const [sourceLabel, setSourceLabel] = useState<string>("Based on RankMind's available dataset");
  const [insufficientResults, setInsufficientResults] = useState<boolean>(false);
  const [insufficientMessage, setInsufficientMessage] = useState<string>('');

  // Search Sessions State (Requirement 12 & 14)
  const [searchSessions, setSearchSessions] = useState<SearchSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');

  // Data States
  const [snapshots, setSnapshots] = useState<SERPSnapshot[]>([]);
  const [analysis, setAnalysis] = useState<MemoryAugmentedAnalysisResponse | null>(null);
  const [entityDetails, setEntityDetails] = useState<any | null>(null);
  const [comparison, setComparison] = useState<BeforeAfterComparisonResponse | null>(null);
  const [timeline, setTimeline] = useState<WebsiteEventTimeline | null>(null);
  const [learningHistory, setLearningHistory] = useState<LearningHistoryItem[]>([]);
  const [currentSERPItems, setCurrentSERPItems] = useState<SERPItem[]>([]);

  // UI & Loading States
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState<'action' | 'measure'>('action');
  const [prefillRecommendation, setPrefillRecommendation] = useState<any | null>(null);

  // Section Refs for smooth scrolling
  const searchRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const intelligenceRef = useRef<HTMLDivElement>(null);
  const memoryRef = useRef<HTMLDivElement>(null);
  const recommendationRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);

  // Primary Data Loader for a selected query and domain
  const loadIntelligence = async (targetQ: string, targetDom: string) => {
    try {
      setError(null);

      // 1. Fetch snapshots and determine current position
      const snaps = await fetchSnapshots(targetQ).catch(() => []);
      setSnapshots(snaps);

      let currentPos = 1;
      const items = getSERPItemsForQuery(targetQ);
      const found = items.find((it) => it.domain === targetDom);
      if (found) currentPos = found.rank;

      // 2. Fetch Hindsight Memory Analysis (with client evidence fallback)
      let analysisData = await fetchMemoryAnalysis(targetQ, targetDom, undefined, currentPos).catch((e) => {
        console.warn('Backend hindsight analysis notice, using client fallback:', e);
        return null;
      });
      if (!analysisData) {
        analysisData = getFallbackMemoryAnalysis(targetDom, targetQ);
      }
      setAnalysis(analysisData);

      // 3. Fetch Entity Details
      const siteId = `site_${targetDom.split('.')[0]}`;
      const entData = await fetchWebsiteDetails(siteId, targetQ).catch(() => null);
      setEntityDetails(entData);

      // 4. Fetch Before/After Comparison
      const compData = await fetchBeforeAfterComparison(targetDom, targetQ).catch(() => null);
      setComparison(compData);

      // 5. Fetch Timeline & Learning History
      const [tlData, histData] = await Promise.all([
        fetchWebsiteTimeline(targetDom, targetQ).catch(() => null),
        fetchLearningHistory(targetDom).catch(() => ({ items: [] })),
      ]);
      setTimeline(tlData);
      setLearningHistory(histData?.items || []);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load SEO intelligence data');
    }
  };

  // Open Website with Hindsight Retention (Requirements 14 & 15)
  const handleOpenWebsite = async (item: SERPItem) => {
    try {
      await recordWebsiteInteraction({
        query,
        domain: item.domain,
        url: item.url,
        rankmind_position: item.rank,
        interaction_type: 'open_website',
      });
      // Refresh memory analysis in background
      fetchMemoryAnalysis(query, item.domain).then((upd) => {
        if (upd) setAnalysis(upd);
      }).catch(() => null);
    } catch (e) {
      console.warn('Hindsight retain interaction notice:', e);
    }
  };

  // Handle Search Submission (Requirements 2, 3, 4, 5, 12, 13, 14, 15)
  const handleSearch = async (newQuery: string) => {
    if (!newQuery.trim()) return;
    const cleanQ = newQuery.trim();

    setQuery(cleanQ);
    setHasSearched(true);
    setLoading(true);

    // Multi-stage realistic pipeline progress (Requirement 22)
    setLoadingStage('Understanding your query...');
    await new Promise((r) => setTimeout(r, 220));

    setLoadingStage('Finding relevant resources...');
    await new Promise((r) => setTimeout(r, 220));

    setLoadingStage('Analyzing available evidence...');
    await new Promise((r) => setTimeout(r, 250));

    setLoadingStage("Recalling RankMind's previous knowledge...");
    await new Promise((r) => setTimeout(r, 250));

    setLoadingStage('Ranking resources...');
    await new Promise((r) => setTimeout(r, 200));

    let items: SERPItem[] = [];
    try {
      const backendRes = await executeIntelligenceSearch(cleanQ);
      if (backendRes) {
        items = backendRes.results || [];
        setQueryUnderstanding(backendRes.query_understanding || null);
        setSourceLabel(backendRes.source_label || "Based on RankMind's available dataset");
        setInsufficientResults(backendRes.insufficient_results || false);
        setInsufficientMessage(backendRes.message || '');
      }
    } catch (err) {
      console.warn('Backend intelligence search notice, using client dataset fallback:', err);
      items = getSERPItemsForQuery(cleanQ);
      setQueryUnderstanding(null);
      setSourceLabel("Based on RankMind's available dataset");
      setInsufficientResults(items.length === 0);
      setInsufficientMessage(items.length === 0 ? 'Not enough relevant resources found for this search topic.' : '');
    }

    setCurrentSERPItems(items);

    const strongestDomain = items[0]?.domain || '';
    setSelectedDomain(strongestDomain);

    // Create Search Session object
    const sessionId = `session_${Date.now()}`;
    setCurrentSessionId(sessionId);
    const newSession: SearchSession = {
      sessionId,
      userQuery: cleanQ,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      analyzedWebsites: items.map((it) => it.domain),
      rankingPositions: items.reduce((acc, it) => ({ ...acc, [it.domain]: it.rank }), {}),
      strongestDomain,
      selectedWebsite: strongestDomain,
    };

    setSearchSessions((prev) => [
      newSession,
      ...prev.filter((s) => s.userQuery.toLowerCase() !== cleanQ.toLowerCase()),
    ]);

    if (strongestDomain) {
      await loadIntelligence(cleanQ, strongestDomain);
    }

    setCurrentStep(2);
    setLoading(false);
    setLoadingStage('');

    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  // Handle Website Selection from Search Results (Requirement 7 & 8)
  const handleSelectDomain = async (domain: string) => {
    setSelectedDomain(domain);
    setCurrentStep(3);
    setLoading(true);
    await loadIntelligence(query, domain);
    setLoading(false);

    // Update current session's selected website
    setSearchSessions((prev) =>
      prev.map((s) => (s.sessionId === currentSessionId ? { ...s, selectedWebsite: domain } : s))
    );

    intelligenceRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // Handle Switching Between Previous Search Sessions (Requirement 12)
  const handleSwitchSession = async (session: SearchSession) => {
    setQuery(session.userQuery);
    setSelectedDomain(session.selectedWebsite);
    setCurrentSessionId(session.sessionId);
    setCurrentStep(2);
    setLoading(true);

    try {
      const backendRes = await executeIntelligenceSearch(session.userQuery);
      if (backendRes) {
        setCurrentSERPItems(backendRes.results || []);
        setQueryUnderstanding(backendRes.query_understanding || null);
        setSourceLabel(backendRes.source_label || "Based on RankMind's available dataset");
        setInsufficientResults(backendRes.insufficient_results || false);
        setInsufficientMessage(backendRes.message || '');
      }
    } catch {
      const items = getSERPItemsForQuery(session.userQuery);
      setCurrentSERPItems(items);
      setInsufficientResults(items.length === 0);
    }

    if (session.selectedWebsite) {
      await loadIntelligence(session.userQuery, session.selectedWebsite);
    }
    setLoading(false);

    resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // Handle Reset to New Empty Search State
  const handleNewSearch = () => {
    setQuery('');
    setHasSearched(false);
    setSelectedDomain('');
    setCurrentSERPItems([]);
    setAnalysis(null);
    setCurrentStep(1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Stepper Click Handler
  const handleStepClick = (stepIndex: number) => {
    setCurrentStep(stepIndex);
    if (stepIndex === 1) searchRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (stepIndex === 2) resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (stepIndex === 3) intelligenceRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (stepIndex === 4) memoryRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (stepIndex === 5) recommendationRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (stepIndex === 6) {
      setIsModalOpen(true);
    }
    if (stepIndex === 7) timelineRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Record Action Modal Handler (Step 6)
  const handleOpenActionModal = (rec?: any, tab: 'action' | 'measure' = 'action') => {
    setPrefillRecommendation(rec || null);
    setModalTab(tab);
    setIsModalOpen(true);
    setCurrentStep(6);
  };

  // User Feedback Handler (Requirement 15)
  const handleUserFeedback = async (feedback: UserFeedbackInput) => {
    await submitUserFeedback(feedback).catch((err) => {
      console.warn('Feedback recorded locally:', err);
    });
    setCurrentStep(7);

    // Update session with user feedback
    setSearchSessions((prev) =>
      prev.map((s) =>
        s.sessionId === currentSessionId
          ? { ...s, userFeedback: feedback.is_useful ? 'useful' : 'not_useful' }
          : s
      )
    );

    // Reload memory analysis to reflect new feedback
    const updatedAnalysis = await fetchMemoryAnalysis(query, selectedDomain).catch(() => null);
    if (updatedAnalysis) setAnalysis(updatedAnalysis);
  };

  // Reset Demo State
  const handleResetDemo = async () => {
    if (confirm('Reset intelligence state to clean seed benchmark scenario?')) {
      await resetDemoState();
      if (hasSearched) {
        await loadIntelligence(query, selectedDomain);
      }
    }
  };

  // Compute items to display
  const displayItems = hasSearched ? currentSERPItems : [];
  const currentSelectedRank = displayItems.find((it) => it.domain === selectedDomain)?.rank || 1;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-app)' }}>
      {/* Brand Navigation Header */}
      <Header
        onOpenLogModal={() => handleOpenActionModal()}
        onResetDemo={handleResetDemo}
        loading={loading}
        query={query || (hasSearched ? '' : 'Ready to search')}
        targetDomain={selectedDomain}
        currentRank={hasSearched ? currentSelectedRank : null}
      />

      {/* Main Content Workspace */}
      <main
        style={{
          maxWidth: '1440px',
          width: '100%',
          margin: '0 auto',
          padding: '24px 20px',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '28px',
        }}
      >
        {/* Error notification if any */}
        {error && (
          <div
            style={{
              padding: '12px 18px',
              borderRadius: '8px',
              background: 'var(--danger-bg)',
              border: '1px solid var(--danger-border)',
              color: 'var(--danger-text)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '0.85rem',
            }}
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* 1. SEARCH SECTION */}
        <div ref={searchRef}>
          {!hasSearched ? (
            /* REQUIREMENT 11: Empty-State Screen when user opens RankMind AI */
            <div
              className="glass-panel animate-fade-in"
              style={{
                padding: '44px 32px',
                textAlign: 'center',
                background: 'radial-gradient(ellipse at 50% -20%, rgba(6, 182, 212, 0.16) 0%, rgba(12, 20, 39, 0.96) 75%)',
                borderRadius: '16px',
                border: '1px solid var(--border-subtle)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
              }}
            >
              <div
                style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '14px',
                  background: 'linear-gradient(135deg, var(--cyan-primary), #6366f1)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 24px rgba(6, 182, 212, 0.4)',
                  marginBottom: '18px',
                }}
              >
                <Search size={26} color="#fff" />
              </div>

              <h1
                style={{
                  fontSize: '2.1rem',
                  fontWeight: 900,
                  color: '#fff',
                  letterSpacing: '-0.03em',
                  marginBottom: '10px',
                }}
              >
                Search the web intelligently.
              </h1>

              <p
                style={{
                  fontSize: '1rem',
                  color: '#94a3b8',
                  maxWidth: '660px',
                  margin: '0 auto 28px auto',
                  lineHeight: 1.5,
                }}
              >
                Enter a query to analyze available results, ranking history, and historical SEO intelligence.
              </p>

              {/* Primary Empty-State Search Bar */}
              <div style={{ maxWidth: '820px', margin: '0 auto', textAlign: 'left' }}>
                <SearchBar
                  query={query}
                  onSearch={handleSearch}
                  loading={loading}
                  currentStep={currentStep}
                  onStepClick={handleStepClick}
                  hasSearched={hasSearched}
                />
              </div>
            </div>
          ) : (
            /* Active Search Bar after user has executed a query */
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#f8fafc', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Active Search Query:
                  </span>
                  <span
                    style={{
                      fontSize: '0.9rem',
                      fontWeight: 700,
                      color: 'var(--cyan-primary)',
                      background: 'rgba(6, 182, 212, 0.12)',
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                      padding: '4px 12px',
                      borderRadius: '8px',
                    }}
                  >
                    "{query}"
                  </span>
                </div>

                <button
                  type="button"
                  onClick={handleNewSearch}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 14px',
                    borderRadius: '8px',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    background: 'rgba(255, 255, 255, 0.04)',
                    color: '#e2e8f0',
                    border: '1px solid var(--border-subtle)',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                >
                  <PlusCircle size={13} color="var(--cyan-primary)" />
                  New Search
                </button>
              </div>

              <SearchBar
                query={query}
                onSearch={handleSearch}
                loading={loading}
                currentStep={currentStep}
                onStepClick={handleStepClick}
                hasSearched={hasSearched}
              />
            </div>
          )}
        </div>

        {/* Multi-Search Sessions Bar (Requirements 12 & 14) */}
        {searchSessions.length > 0 && (
          <div
            className="glass-panel"
            style={{
              padding: '12px 18px',
              background: 'rgba(15, 23, 42, 0.85)',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              flexWrap: 'wrap',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-faint)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>
              <HistoryIcon size={14} color="var(--cyan-primary)" />
              <span>Search Sessions ({searchSessions.length}):</span>
            </div>

            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', flex: 1 }}>
              {searchSessions.map((s, idx) => {
                const isActive = s.sessionId === currentSessionId;
                return (
                  <button
                    key={s.sessionId}
                    type="button"
                    onClick={() => handleSwitchSession(s)}
                    style={{
                      background: isActive ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                      border: isActive ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                      borderRadius: '6px',
                      padding: '4px 10px',
                      fontSize: '0.76rem',
                      color: isActive ? '#fff' : 'var(--text-muted)',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <span style={{ fontWeight: 800, color: isActive ? 'var(--cyan-primary)' : 'var(--text-faint)' }}>
                      #{idx + 1}
                    </span>
                    <span>{s.userQuery}</span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-faint)' }}>({s.timestamp})</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Realistic Multi-Stage Loading State Banner (Requirement 13) */}
        {loading && (
          <div
            className="glass-panel animate-fade-in"
            style={{
              padding: '24px 32px',
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(15, 23, 42, 0.95) 100%)',
              border: '1px solid rgba(6, 182, 212, 0.4)',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  border: '2px solid rgba(6, 182, 212, 0.3)',
                  borderTopColor: 'var(--cyan-primary)',
                  animation: 'spin 0.8s linear infinite',
                }}
              />
              <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#fff' }}>
                {loadingStage || 'Processing Search & Intelligence Pipeline...'}
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--cyan-primary)', fontWeight: 600 }}>
              Analyzing available websites • Comparing results • Recalling Hindsight memory • Synthesizing recommendation
            </div>
          </div>
        )}

        {/* RESULTS & INTELLIGENCE SUITE (Only shown once user has searched) */}
        {hasSearched && (
          <>
            {/* 2. SEARCH RESULTS / WEBSITE COMPARISON */}
            <div ref={resultsRef}>
              <SearchResultsComparison
                items={displayItems}
                selectedDomain={selectedDomain}
                onSelectDomain={handleSelectDomain}
                query={query}
                cycleIndex={snapshots.length || 5}
                queryUnderstanding={queryUnderstanding}
                sourceLabel={sourceLabel}
                insufficientResults={insufficientResults}
                insufficientMessage={insufficientMessage}
                onOpenWebsite={handleOpenWebsite}
              />
            </div>

            {/* 3. WEBSITE INTELLIGENCE WORKBENCH */}
            <div ref={intelligenceRef}>
              <WebsiteIntelligenceWorkbench
                domain={selectedDomain}
                query={query}
                analysis={analysis}
                entityDetails={entityDetails}
                loading={loading}
                onOpenActionModal={(type) => handleOpenActionModal(undefined, type)}
                onScrollToRecommendations={() => recommendationRef.current?.scrollIntoView({ behavior: 'smooth' })}
                onScrollToMemory={() => memoryRef.current?.scrollIntoView({ behavior: 'smooth' })}
              />
            </div>

            {/* Two-Column Responsive Grid for 4. AI Recommendation and 5. Memory Panel */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))',
                gap: '24px',
              }}
            >
              {/* 4. AI RECOMMENDATION & USER FEEDBACK (Requirement 15) */}
              <div ref={recommendationRef}>
                <AiRecommendationCard
                  recommendations={analysis?.context_aware_recommendations || []}
                  query={query}
                  domain={selectedDomain}
                  onRecordActionClick={(rec) => handleOpenActionModal(rec)}
                  onSubmitFeedback={handleUserFeedback}
                />
              </div>

              {/* 5. MEMORY PANEL */}
              <div ref={memoryRef}>
                <MemoryPanel
                  memories={analysis?.recalled_memories || []}
                  suppressedTactics={analysis?.suppressed_tactics || []}
                  query={query}
                  domain={selectedDomain}
                  loading={loading}
                />
              </div>
            </div>

            {/* 6. LEARNING TIMELINE */}
            <div ref={timelineRef}>
              <LearningTimelineView
                timeline={timeline}
                historyItems={learningHistory}
                website={selectedDomain}
                loading={loading}
              />
            </div>

            {/* 7. BEFORE / AFTER MEMORY TOGGLE */}
            <div>
              <BeforeAfterToggle comparison={comparison} loading={loading} />
            </div>
          </>
        )}
      </main>

      {/* Global Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--border-subtle)',
          padding: '20px 24px',
          textAlign: 'center',
          fontSize: '0.8rem',
          color: 'var(--text-faint)',
          background: 'rgba(8, 13, 26, 0.95)',
        }}
      >
        <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <strong style={{ color: '#cbd5e1' }}>RankMind</strong> — Persistent SEO & Search Intelligence Platform
          </div>
          <div>
            Powered by Deep Hindsight Memory • Multi-Cycle Closed Learning Loop
          </div>
        </div>
      </footer>

      {/* Action Logger & Measurement Modal */}
      <ActionLoggerModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onActionComplete={async () => {
          await loadIntelligence(query, selectedDomain);
        }}
        prefill={prefillRecommendation}
        query={query}
        targetDomain={selectedDomain}
        initialTab={modalTab}
      />
    </div>
  );
};

export default App;
