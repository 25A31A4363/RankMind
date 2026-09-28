import React, { useState, useEffect } from 'react';
import { Search, Sparkles, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react';

interface SearchBarProps {
  query: string;
  onSearch: (newQuery: string) => void;
  loading?: boolean;
  currentStep: number; // 1 to 7 in the workflow
  onStepClick: (stepIndex: number) => void;
  hasSearched: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  onSearch,
  loading = false,
  currentStep,
  onStepClick,
  hasSearched: _hasSearched,
}) => {
  // Search input must initially be empty per product spec
  const [inputValue, setInputValue] = useState(query || '');

  // Keep input synced if query changes externally
  useEffect(() => {
    setInputValue(query || '');
  }, [query]);

  const exampleQueries = [
    'Java tutorials for beginners',
    'coding problem solving websites',
    'best free photography courses',
    'best places to visit in Hyderabad',
    'how to make pizza',
    'best laptops for students under 60000',
    'Indian history',
    'how does solar energy work',
    'best books to learn psychology',
    'C++ tutorials',
    'best tourist places in Kerala',
  ];

  const workflowSteps = [
    { num: 1, label: 'Query', desc: 'Understand intent' },
    { num: 2, label: 'Discovery & Rank', desc: 'Multi-factor evaluation' },
    { num: 3, label: 'Intelligence Profile', desc: 'Content & signals' },
    { num: 4, label: 'Recall Memory', desc: 'Hindsight past knowledge' },
    { num: 5, label: 'Why Ranked?', desc: 'Transparent explanation' },
    { num: 6, label: 'Interact & Retain', desc: 'Open site & learn' },
    { num: 7, label: 'Closed Loop', desc: 'Future searches improve' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSearch(inputValue.trim());
    }
  };

  // Clicking an example query populates the search input without forcing auto-submit
  const handleSelectExample = (example: string) => {
    setInputValue(example);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* 60-Second Guided Workflow Stepper */}
      <div
        className="glass-panel"
        style={{
          padding: '16px 20px',
          background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.9) 0%, rgba(12, 20, 39, 0.9) 100%)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                width: '22px',
                height: '22px',
                borderRadius: '50%',
                background: 'rgba(6, 182, 212, 0.2)',
                color: 'var(--cyan-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '11px',
                fontWeight: 800,
              }}
            >
              ⟳
            </span>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '0.02em', textTransform: 'uppercase' }}>
              Autonomous SEO Search & Intelligence Loop
            </span>
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Stateless tools give generic advice • <strong style={{ color: 'var(--cyan-primary)' }}>RankMind learns which actions move rankings</strong>
          </span>
        </div>

        {/* Stepper track */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
            gap: '8px',
          }}
        >
          {workflowSteps.map((s) => {
            const isActive = currentStep === s.num;
            const isCompleted = currentStep > s.num;
            return (
              <button
                key={s.num}
                type="button"
                onClick={() => onStepClick(s.num)}
                style={{
                  background: isActive
                    ? 'rgba(6, 182, 212, 0.15)'
                    : isCompleted
                    ? 'rgba(16, 185, 129, 0.08)'
                    : 'rgba(255, 255, 255, 0.02)',
                  border: isActive
                    ? '1px solid var(--cyan-primary)'
                    : isCompleted
                    ? '1px solid rgba(16, 185, 129, 0.3)'
                    : '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px 12px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span
                    style={{
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      fontFamily: 'var(--font-mono)',
                      color: isActive
                        ? 'var(--cyan-primary)'
                        : isCompleted
                        ? 'var(--success-text)'
                        : 'var(--text-faint)',
                    }}
                  >
                    0{s.num}
                  </span>
                  {isCompleted ? (
                    <CheckCircle2 size={13} color="var(--success-text)" />
                  ) : isActive ? (
                    <span
                      style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: 'var(--cyan-primary)',
                        boxShadow: '0 0 8px var(--cyan-primary)',
                      }}
                    />
                  ) : null}
                </div>
                <div
                  style={{
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    color: isActive ? '#fff' : isCompleted ? '#e2e8f0' : 'var(--text-muted)',
                  }}
                >
                  {s.label}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-faint)', lineHeight: 1.2 }}>
                  {s.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Hero Search Box */}
      <div
        className="glass-panel"
        style={{
          padding: '24px 28px',
          background: 'radial-gradient(ellipse at 50% -20%, rgba(6, 182, 212, 0.12) 0%, rgba(12, 20, 39, 0.95) 75%)',
        }}
      >
        <div style={{ marginBottom: '16px' }}>
          <label
            htmlFor="main-search-input"
            style={{
              display: 'block',
              fontSize: '1.25rem',
              fontWeight: 800,
              color: '#fff',
              letterSpacing: '-0.02em',
              marginBottom: '6px',
            }}
          >
            What do you want to search for?
          </label>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Search any query to evaluate multiple competing websites, inspect ranking movements, and recall historical Hindsight memory.
          </p>
        </div>

        {/* Primary Manual Search Form - ONLY ONE PRIMARY INPUT: SEARCH QUERY */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '280px', position: 'relative' }}>
            <Search
              size={18}
              style={{
                position: 'absolute',
                left: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--cyan-primary)',
              }}
            />
            <input
              id="main-search-input"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="What do you want to find? (e.g. Java tutorials, best places to visit in Hyderabad, how to make pizza)..."
              style={{
                width: '100%',
                padding: '14px 18px 14px 44px',
                background: '#090e1c',
                border: '1px solid rgba(255, 255, 255, 0.14)',
                borderRadius: '10px',
                color: '#fff',
                fontSize: '0.95rem',
                outline: 'none',
                boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.4)',
                transition: 'border-color 0.2s, box-shadow 0.2s',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--cyan-primary)';
                e.target.style.boxShadow = '0 0 0 3px rgba(6, 182, 212, 0.2)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'rgba(255, 255, 255, 0.14)';
                e.target.style.boxShadow = 'inset 0 2px 4px rgba(0,0,0,0.4)';
              }}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !inputValue.trim()}
            style={{
              padding: '14px 28px',
              fontSize: '0.95rem',
              borderRadius: '10px',
              whiteSpace: 'nowrap',
              opacity: !inputValue.trim() ? 0.6 : 1,
              cursor: !inputValue.trim() ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? (
              <>Analyzing...</>
            ) : (
              <>
                <Sparkles size={16} />
                Search
              </>
            )}
          </button>
        </form>

        {/* Optional Example Queries - Clicking populates search box without auto-submitting */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-faint)', fontWeight: 600 }}>Try:</span>
          {exampleQueries.map((example) => {
            const isMatch = inputValue.toLowerCase() === example.toLowerCase();
            return (
              <button
                key={example}
                type="button"
                onClick={() => handleSelectExample(example)}
                style={{
                  background: isMatch ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                  border: isMatch ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  padding: '4px 10px',
                  fontSize: '0.75rem',
                  color: isMatch ? '#fff' : 'var(--text-muted)',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                }}
              >
                <span>{example}</span>
                <ArrowRight size={11} color={isMatch ? 'var(--cyan-primary)' : 'var(--text-faint)'} />
              </button>
            );
          })}
        </div>

        {/* MANDATORY Synthetic Data Disclaimer Banner */}
        <div
          style={{
            marginTop: '16px',
            padding: '10px 14px',
            borderRadius: '8px',
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px',
          }}
        >
          <AlertTriangle size={16} color="var(--warning-text)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ fontSize: '0.75rem', color: '#fef3c7', lineHeight: 1.45 }}>
            <strong>Demo/Synthetic Search Data:</strong> Rankings, traffic estimates, and SERP features shown are evaluated from controlled synthetic benchmark datasets for development & demonstration. <em>RankMind AI does not claim access to Google's private ranking algorithm or invent live Google rankings.</em>
          </div>
        </div>
      </div>
    </div>
  );
};
