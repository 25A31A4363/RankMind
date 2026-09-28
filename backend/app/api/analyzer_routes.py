from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any

from app.services.seo_analyzer import seo_analyzer
from app.models.analyzer_schemas import BaselineAnalysisRequest, BaselineAnalysisResult
from app.repositories.seo_repository import SEORepository
from app.db.database import DB_PATH

router = APIRouter(prefix="", tags=["Baseline SEO Analyzer"])
repo = SEORepository(DB_PATH)


@router.post("/api/v1/analyzer/analyze", response_model=BaselineAnalysisResult, status_code=status.HTTP_200_OK)
def run_baseline_analysis(payload: BaselineAnalysisRequest) -> BaselineAnalysisResult:
    """Runs the Baseline SEO Analyzer without Hindsight memory.
    
    Produces structured:
    - CURRENT OBSERVATIONS
    - PROBLEMS
    - OPPORTUNITIES
    - RECOMMENDED ACTIONS
    - Machine-readable LLM prompt summary
    """
    try:
        result = seo_analyzer.analyze(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyzer error: {str(e)}")


@router.get("/api/v1/analyzer/presets")
def get_analyzer_presets() -> List[Dict[str, Any]]:
    """Returns ready-to-test preset queries and websites."""
    websites = repo.list_websites()
    queries = repo.list_search_queries()

    presets = [
        {
            "label": "Python Courses - Target Site (learnpythonhub.io)",
            "query": "best python courses for beginners",
            "website_domain": "learnpythonhub.io",
            "description": "Commercial guide with interactive tool, missing video preview and CourseSchema.",
        },
        {
            "label": "Python Courses - Competitor Leader (coursera.org)",
            "query": "best python courses for beginners",
            "website_domain": "coursera.org",
            "description": "High authority leader with CourseSchema, video previews, and accreditation.",
        },
        {
            "label": "FastAPI vs Express - Benchmark Site (benchmarks-dev.io)",
            "query": "fastapi vs express performance",
            "website_domain": "benchmarks-dev.io",
            "description": "Technical comparison with Docker reproducibility and Dataset schema.",
        },
        {
            "label": "AI Code Generation - Devtools Radar (devtools-radar.com)",
            "query": "ai code generation tools",
            "website_domain": "devtools-radar.com",
            "description": "Tool comparison with LeetCode blind testing dataset and pricing calculator.",
        },
    ]
    return presets


@router.get("/analyzer", response_class=HTMLResponse)
def render_analyzer_test_ui():
    """Serves a clean temporary developer testing interface for the baseline analyzer."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RankMind | Baseline SEO Analyzer (Zero Hindsight)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card: #111827;
      --card-subtle: #172238;
      --border: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(99, 102, 241, 0.4);
      --text: #f3f4f6;
      --muted: #9ca3af;
      --faint: #6b7280;
      --accent: #6366f1;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --cyan: #06b6d4;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }
    .container { max-width: 1380px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 16px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .badge-baseline { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
    .badge-no-hindsight { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    
    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }
    
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }
    @media (max-width: 768px) {
      .form-grid { grid-template-columns: 1fr; }
    }
    label {
      display: block;
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    input, select, textarea {
      width: 100%;
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: #fff;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 0.9rem;
      font-family: inherit;
    }
    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    
    .btn-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }
    button.btn-primary {
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 10px 22px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
    }
    button.btn-primary:hover { opacity: 0.9; }
    button.btn-preset {
      background: rgba(255, 255, 255, 0.05);
      color: var(--muted);
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.78rem;
      cursor: pointer;
    }
    button.btn-preset:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }

    /* 4 Output Sections Grid */
    .sections-container {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .section-title {
      font-size: 1.1rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      color: #fff;
    }
    
    .obs-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
    }
    .obs-card {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
    }
    .obs-card-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--faint);
      text-transform: uppercase;
      margin-bottom: 4px;
    }
    .obs-card-val {
      font-size: 0.95rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 4px;
    }
    .obs-card-sub {
      font-size: 0.8rem;
      color: var(--muted);
    }

    /* Problem / Opportunity / Recommendation Cards */
    .card-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .item-card {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 18px;
    }
    .item-card.sev-high { border-left: 4px solid var(--danger); }
    .item-card.sev-medium { border-left: 4px solid var(--warning); }
    .item-card.sev-low { border-left: 4px solid var(--muted); }
    .item-card.opp { border-left: 4px solid var(--cyan); }
    .item-card.rec { border-left: 4px solid var(--success); }

    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      flex-wrap: wrap;
      gap: 8px;
    }
    .item-title { font-size: 0.95rem; font-weight: 700; color: #fff; }
    .item-desc { font-size: 0.84rem; color: var(--muted); line-height: 1.5; }
    .item-guide {
      margin-top: 8px;
      font-size: 0.8rem;
      background: rgba(0, 0, 0, 0.3);
      padding: 8px 12px;
      border-radius: 6px;
      color: var(--cyan);
    }

    .raw-viewer {
      background: #05070c;
      border: 1px solid var(--border);
      padding: 14px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      color: #93c5fd;
      max-height: 380px;
      overflow-y: auto;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <div style="display:flex; align-items:center; gap:10px;">
          <h1 style="font-size:1.35rem; font-weight:800;">RankMind Baseline SEO Analyzer</h1>
          <span class="badge badge-baseline">Static On-Page Evaluator v1.0</span>
          <span class="badge badge-no-hindsight">Zero Hindsight Memory</span>
        </div>
        <p style="font-size:0.84rem; color:var(--muted); margin-top:4px;">
          Evaluates isolated on-page signals, search intent, metadata, and content structure. Acts as the baseline to compare against future memory-powered versions.
        </p>
      </div>
      <div>
        <span class="badge" style="background:rgba(255,255,255,0.06); color:var(--muted); border:1px solid var(--border);">
          Targeting: Structured 4-Section Output
        </span>
      </div>
    </header>

    <!-- Testing & Request Form -->
    <div class="panel">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
        <span style="font-size:0.85rem; font-weight:700; color:#fff;">Quick-Load Preset Scenarios:</span>
        <div style="display:flex; gap:8px; flex-wrap:wrap;" id="presetButtons">
          <!-- Populated by JS -->
        </div>
      </div>

      <form id="analyzeForm" onsubmit="handleAnalyze(event)">
        <div class="form-grid">
          <div>
            <label>Target Search Query / Keyword</label>
            <input type="text" id="queryInput" required value="best python courses for beginners" placeholder="e.g. best python courses for beginners">
          </div>
          <div>
            <label>Select Tracked Website Domain (or Enter Ad-hoc Below)</label>
            <select id="websiteSelect" onchange="handleWebsiteSelect()">
              <!-- Populated by JS -->
            </select>
          </div>
        </div>

        <div class="form-grid">
          <div>
            <label>Custom / Ad-Hoc URL (Optional)</label>
            <input type="text" id="urlInput" placeholder="https://example.com/page">
          </div>
          <div>
            <label>Custom Page Title (Optional Override)</label>
            <input type="text" id="titleInput" placeholder="Leave empty to use website record">
          </div>
        </div>

        <div class="btn-row">
          <div style="font-size:0.78rem; color:var(--faint);">
            ⚡ Evaluates intent, title, meta, headings, completeness, UX, and technical schemas.
          </div>
          <button type="submit" class="btn-primary" id="analyzeBtn">Run Baseline SEO Analysis</button>
        </div>
      </form>
    </div>

    <!-- Results Container -->
    <div id="resultsContainer" class="sections-container" style="display:none;">
      
      <!-- Meta Card -->
      <div class="panel" style="padding:14px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; background:rgba(99,102,241,0.08); border-color:var(--border-accent);">
        <div>
          <span style="font-size:0.75rem; color:var(--muted); text-transform:uppercase; font-weight:700;">Analyzed Target:</span>
          <span style="font-size:1.05rem; font-weight:800; color:#fff; margin-left:6px;" id="resDomain"></span>
          <span style="font-size:0.85rem; color:var(--muted); margin-left:8px;" id="resUrl"></span>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
          <span class="badge badge-no-hindsight">Hindsight Memory: OFF</span>
          <span class="badge badge-baseline" id="resIntentBadge"></span>
        </div>
      </div>

      <!-- 1. CURRENT OBSERVATIONS -->
      <div class="panel">
        <h2 class="section-title">📋 1. CURRENT OBSERVATIONS</h2>
        <div class="obs-grid" id="obsGrid">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- 2. PROBLEMS -->
      <div class="panel">
        <h2 class="section-title">⚠️ 2. PROBLEMS IDENTIFIED (<span id="problemsCount">0</span>)</h2>
        <div class="card-list" id="problemsList">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- 3. OPPORTUNITIES -->
      <div class="panel">
        <h2 class="section-title">💡 3. OPPORTUNITIES (<span id="oppsCount">0</span>)</h2>
        <div class="card-list" id="oppsList">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- 4. RECOMMENDED ACTIONS -->
      <div class="panel">
        <h2 class="section-title">🎯 4. RECOMMENDED ACTIONS (<span id="recsCount">0</span>)</h2>
        <div class="card-list" id="recsList">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- Machine-Readable LLM Summary View -->
      <div class="panel">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <h2 class="section-title" style="margin-bottom:0;">🤖 Machine-Readable Summary for LLM Ingestion</h2>
          <button class="btn-preset" onclick="copyLlmSummary()">Copy for LLM Prompt</button>
        </div>
        <pre class="raw-viewer" id="llmSummaryText"></pre>
      </div>

      <!-- Raw JSON View -->
      <div class="panel">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <h2 class="section-title" style="margin-bottom:0;">🔍 Raw JSON Payload (API Output)</h2>
          <button class="btn-preset" onclick="toggleRaw()">Toggle View</button>
        </div>
        <pre class="raw-viewer" id="rawJsonText" style="display:none;"></pre>
      </div>

    </div>
  </div>

  <script>
    let websitesList = [];
    let currentResult = null;

    async function init() {
      await loadWebsites();
      await loadPresets();
      // Auto run first analysis
      handleAnalyze(new Event('submit'));
    }

    async function loadWebsites() {
      const res = await fetch('/api/v1/entities/websites');
      websitesList = await res.json();
      const sel = document.getElementById('websiteSelect');
      sel.innerHTML = '<option value="">-- Choose Seeded Website --</option>' + websitesList.map(w => `
        <option value="${w.id}" ${w.domain === 'learnpythonhub.io' ? 'selected' : ''}>
          ${w.domain} (${w.title.slice(0, 45)}...)
        </option>
      `).join('');
    }

    async function loadPresets() {
      const res = await fetch('/api/v1/analyzer/presets');
      const presets = await res.json();
      const container = document.getElementById('presetButtons');
      container.innerHTML = presets.map((p, idx) => `
        <button type="button" class="btn-preset" onclick="applyPreset(${idx}, ${JSON.stringify(p).replace(/"/g, '&quot;')})">
          ${p.label.split(' - ')[0]}
        </button>
      `).join('');
    }

    function applyPreset(idx, p) {
      document.getElementById('queryInput').value = p.query;
      const matchedSite = websitesList.find(w => w.domain === p.website_domain);
      if (matchedSite) {
        document.getElementById('websiteSelect').value = matchedSite.id;
        document.getElementById('urlInput').value = matchedSite.url;
      }
      handleAnalyze(new Event('submit'));
    }

    function handleWebsiteSelect() {
      const wid = document.getElementById('websiteSelect').value;
      const site = websitesList.find(w => w.id === wid);
      if (site) {
        document.getElementById('urlInput').value = site.url;
        document.getElementById('titleInput').value = site.title;
      }
    }

    async function handleAnalyze(e) {
      if (e && e.preventDefault) e.preventDefault();

      const btn = document.getElementById('analyzeBtn');
      btn.textContent = 'Analyzing Signals...';
      btn.disabled = true;

      const payload = {
        query: document.getElementById('queryInput').value,
        website_id: document.getElementById('websiteSelect').value || null,
        url: document.getElementById('urlInput').value || null,
        custom_title: document.getElementById('titleInput').value || null,
      };

      try {
        const res = await fetch('/api/v1/analyzer/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        currentResult = data;
        renderResults(data);
      } catch (err) {
        alert('Analysis Error: ' + err.message);
      } finally {
        btn.textContent = 'Run Baseline SEO Analysis';
        btn.disabled = false;
      }
    }

    function renderResults(data) {
      document.getElementById('resultsContainer').style.display = 'flex';
      document.getElementById('resDomain').textContent = data.target_domain;
      document.getElementById('resUrl').textContent = '(' + data.target_url + ')';
      document.getElementById('resIntentBadge').textContent = 'Intent: ' + data.current_observations.search_intent_detected.toUpperCase() + ' (' + data.current_observations.intent_match_score + '%)';

      // 1. Observations Grid
      const obs = data.current_observations;
      const grid = document.getElementById('obsGrid');
      grid.innerHTML = `
        <div class="obs-card">
          <div class="obs-card-label">Title Tag Analysis</div>
          <div class="obs-card-val">${obs.title.char_length} chars (${obs.title.title_status})</div>
          <div class="obs-card-sub">${obs.title.title_text}</div>
        </div>
        <div class="obs-card">
          <div class="obs-card-label">Content Completeness</div>
          <div class="obs-card-val">${obs.content_completeness.word_count.toLocaleString()} Words (${obs.content_completeness.completeness_percentage}%)</div>
          <div class="obs-card-sub">Benchmark: ${obs.content_completeness.intent_benchmark_word_count} w • ${obs.content_completeness.estimated_read_time_minutes} min read (${obs.content_completeness.reading_ease_level})</div>
        </div>
        <div class="obs-card">
          <div class="obs-card-label">Heading Hierarchy</div>
          <div class="obs-card-val">H1: "${obs.headings.h1_text}"</div>
          <div class="obs-card-sub">${obs.headings.h2_count} H2 sections, ${obs.headings.h3_count} subtopics • Scan Score: ${obs.headings.scan_friendliness_score}/100</div>
        </div>
        <div class="obs-card">
          <div class="obs-card-label">User Experience Signals</div>
          <div class="obs-card-val">${obs.user_experience.has_interactive_widget ? '✅ Interactive Tool' : '❌ No Interactive Tool'}</div>
          <div class="obs-card-sub">${obs.user_experience.has_video_preview ? '✅ Video Preview Present' : '❌ Missing Video Preview'} • Dwell Impact: ${obs.user_experience.estimated_dwell_impact}</div>
        </div>
        <div class="obs-card">
          <div class="obs-card-label">Structured Schema.org</div>
          <div class="obs-card-val">${obs.technical_seo.schema_types_present.join(', ') || 'None'}</div>
          <div class="obs-card-sub">Rich Snippet Status: ${obs.technical_seo.rich_snippet_readiness}</div>
        </div>
        <div class="obs-card">
          <div class="obs-card-label">Content Scannability</div>
          <div class="obs-card-val">${obs.internal_structure.scannability_rating} Scannability</div>
          <div class="obs-card-sub">Comparison Matrix: ${obs.internal_structure.has_comparison_table ? 'Yes' : 'No'} • Bullet Lists: ${obs.internal_structure.bullet_list_count}</div>
        </div>
      `;

      // 2. Problems List
      document.getElementById('problemsCount').textContent = data.problems.length;
      document.getElementById('problemsList').innerHTML = data.problems.map(p => `
        <div class="item-card sev-${p.severity}">
          <div class="item-header">
            <span class="item-title">${p.problem}</span>
            <span class="badge" style="background:rgba(255,255,255,0.06);">${p.category.toUpperCase()} • SEVERITY: ${p.severity.toUpperCase()}</span>
          </div>
          <div class="item-desc">${p.impact}</div>
        </div>
      `).join('');

      // 3. Opportunities List
      document.getElementById('oppsCount').textContent = data.opportunities.length;
      document.getElementById('oppsList').innerHTML = data.opportunities.map(o => `
        <div class="item-card opp">
          <div class="item-header">
            <span class="item-title">${o.opportunity}</span>
            <span class="badge" style="background:rgba(6,182,212,0.15); color:var(--cyan); border:1px solid rgba(6,182,212,0.3);">${o.impact_potential.toUpperCase()} IMPACT</span>
          </div>
          <div class="item-desc">${o.rationale}</div>
        </div>
      `).join('');

      // 4. Recommended Actions List
      document.getElementById('recsCount').textContent = data.recommended_actions.length;
      document.getElementById('recsList').innerHTML = data.recommended_actions.map(a => `
        <div class="item-card rec">
          <div class="item-header">
            <span class="item-title">Priority ${a.priority}: ${a.action_title}</span>
            <span class="badge" style="background:rgba(16,185,129,0.15); color:var(--success); border:1px solid rgba(16,185,129,0.3);">${a.category.toUpperCase()}</span>
          </div>
          <div class="item-desc">${a.expected_benefit}</div>
          <div class="item-guide"><strong>Implementation Checklist:</strong> ${a.implementation_guide}</div>
        </div>
      `).join('');

      // LLM Machine-Readable Summary
      document.getElementById('llmSummaryText').textContent = data.llm_prompt_summary;

      // Raw JSON
      document.getElementById('rawJsonText').textContent = JSON.stringify(data, null, 2);
    }

    function toggleRaw() {
      const el = document.getElementById('rawJsonText');
      el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }

    function copyLlmSummary() {
      if (!currentResult) return;
      navigator.clipboard.writeText(currentResult.llm_prompt_summary);
      alert('LLM prompt summary copied to clipboard!');
    }

    window.onload = init;
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
