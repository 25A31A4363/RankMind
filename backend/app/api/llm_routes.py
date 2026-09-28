from fastapi import APIRouter, HTTPException, Query, status, Header
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any

from app.models.llm_schemas import LLMAnalysisRequest, LLMAnalysisResponse
from app.services.llm.llm_analysis_service import llm_analysis_service
from app.repositories.seo_repository import SEORepository
from app.db.database import DB_PATH

router = APIRouter(prefix="", tags=["LLM SEO Reasoning Agent"])
repo = SEORepository(DB_PATH)


@router.post("/api/v1/llm/analyze", response_model=LLMAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_with_llm(
    payload: LLMAnalysisRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> LLMAnalysisResponse:
    """Executes LLM-powered SEO reasoning over verified on-page observations.
    
    Guarantees strict separation of:
    - OBSERVED DATA
    - AI INTERPRETATION
    - RECOMMENDATIONS
    """
    try:
        # Use header API key if payload does not have one
        if not payload.api_key and x_api_key:
            payload.api_key = x_api_key

        result = await llm_analysis_service.run_analysis(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM Reasoning Error: {str(e)}",
        )


@router.get("/llm-analysis", response_class=HTMLResponse)
def render_llm_test_interface():
    """Serves an interactive developer interface to test LLM-powered SEO reasoning."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RankMind | LLM SEO Reasoning Agent</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #070a12;
      --card: #0f172a;
      --card-subtle: #162035;
      --border: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(99, 102, 241, 0.4);
      --text: #f8fafc;
      --muted: #94a3b8;
      --faint: #64748b;
      --accent: #6366f1;
      --accent-light: #818cf8;
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
    .container { max-width: 1400px; margin: 0 auto; }
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
    .badge-llm { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
    .badge-no-hindsight { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-truth { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
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
      font-size: 0.76rem;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    input, select {
      width: 100%;
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: #fff;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 0.9rem;
      font-family: inherit;
    }
    input:focus, select:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    button.btn-primary {
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 11px 24px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.92rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
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

    /* 3 Layer Distinction Layout */
    .layer-container {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .layer-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      position: relative;
    }
    .layer-card.layer-observed { border-top: 4px solid var(--cyan); }
    .layer-card.layer-interpretation { border-top: 4px solid var(--accent); }
    .layer-card.layer-recommendations { border-top: 4px solid var(--success); }

    .layer-title {
      font-size: 1.15rem;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 8px;
    }

    .obs-metrics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .obs-pill {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      padding: 12px 14px;
      border-radius: 8px;
    }
    .obs-pill-title { font-size: 0.7rem; color: var(--faint); text-transform: uppercase; font-weight: 700; margin-bottom: 2px; }
    .obs-pill-val { font-size: 0.95rem; font-weight: 700; color: #fff; }

    .weakness-card {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      margin-bottom: 10px;
    }
    .weakness-card.sev-high { border-left: 4px solid var(--danger); }
    .weakness-card.sev-medium { border-left: 4px solid var(--warning); }
    .weakness-card.sev-low { border-left: 4px solid var(--muted); }

    .rec-card {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 12px;
      border-left: 4px solid var(--success);
    }
    .rec-title { font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: 6px; }
    .rec-reasoning { font-size: 0.88rem; color: var(--text); line-height: 1.6; margin-bottom: 10px; }
    .rec-impact {
      font-size: 0.82rem;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: #34d399;
      padding: 8px 12px;
      border-radius: 6px;
      margin-bottom: 10px;
    }
    .rec-steps {
      font-size: 0.82rem;
      color: var(--muted);
      background: rgba(0, 0, 0, 0.25);
      padding: 10px 14px;
      border-radius: 6px;
    }
    .rec-steps li { margin-left: 18px; margin-top: 4px; }

    .questions-box {
      background: rgba(245, 158, 11, 0.08);
      border: 1px solid rgba(245, 158, 11, 0.25);
      border-radius: 8px;
      padding: 16px;
      margin-top: 14px;
    }
    .questions-box ul { margin-left: 20px; font-size: 0.85rem; color: #fde68a; margin-top: 6px; }
    .questions-box li { margin-top: 4px; }

    .raw-box {
      background: #04060a;
      border: 1px solid var(--border);
      padding: 14px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      color: #93c5fd;
      max-height: 350px;
      overflow-y: auto;
      white-space: pre-wrap;
    }
    
    .spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <div style="display:flex; align-items:center; gap:10px;">
          <h1 style="font-size:1.4rem; font-weight:800;">RankMind LLM SEO Reasoning Agent</h1>
          <span class="badge badge-llm">Modular LLM Pipeline</span>
          <span class="badge badge-no-hindsight">Zero Hindsight Memory</span>
          <span class="badge badge-truth">Strict Truth Discipline</span>
        </div>
        <p style="font-size:0.84rem; color:var(--muted); margin-top:4px;">
          Empirical reasoning engine that ingests verified on-page signals and synthesizes diagnosis, weaknesses, and recommendations without hallucinating historical metrics.
        </p>
      </div>
      <div>
        <a href="/analyzer" style="color:var(--accent-light); font-size:0.85rem; text-decoration:none; font-weight:600; margin-right:12px;">← Static Baseline</a>
        <a href="/debug" style="color:var(--cyan); font-size:0.85rem; text-decoration:none; font-weight:600;">Data Inspector →</a>
      </div>
    </header>

    <!-- Request & Provider Form -->
    <div class="panel">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
        <span style="font-size:0.85rem; font-weight:700; color:#fff;">Quick-Load Preset Scenarios:</span>
        <div style="display:flex; gap:8px; flex-wrap:wrap;" id="presets">
          <!-- Populated by JS -->
        </div>
      </div>

      <form id="llmForm" onsubmit="handleRunLLM(event)">
        <div class="form-grid">
          <div>
            <label>Target Search Query / Keyword</label>
            <input type="text" id="queryInput" required value="best python courses for beginners">
          </div>
          <div>
            <label>Target Website (Select Seeded Entity)</label>
            <select id="websiteSelect" onchange="syncWebsiteInfo()">
              <!-- Populated by JS -->
            </select>
          </div>
        </div>

        <div class="form-grid">
          <div>
            <label>LLM Provider</label>
            <select id="providerSelect">
              <option value="auto">Auto-Detect (Local Engine if no API key)</option>
              <option value="local">Local Deterministic Reasoning Engine (No Key Needed)</option>
              <option value="gemini">Google Gemini (gemini-1.5-flash)</option>
              <option value="openai">OpenAI (gpt-4o-mini / Compatible)</option>
            </select>
          </div>
          <div>
            <label>API Key (Optional / Reads from ENV if unset)</label>
            <input type="password" id="apiKeyInput" placeholder="Optional: Enter GEMINI_API_KEY or OPENAI_API_KEY">
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div style="font-size:0.78rem; color:var(--faint);">
            🛡️ Strict truth discipline active: The LLM is forbidden from hallucinating past rank movements.
          </div>
          <button type="submit" class="btn-primary" id="runBtn">
            <span>Run LLM SEO Reasoning</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Error Banner -->
    <div id="errorBanner" style="display:none; padding:12px 16px; border-radius:8px; background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.3); color:#fca5a5; font-size:0.85rem; margin-bottom:20px;">
      <!-- Error content -->
    </div>

    <!-- Results Container: The 3 Distinct Layers -->
    <div id="resultsArea" class="layer-container" style="display:none;">

      <!-- Meta Bar -->
      <div style="background:rgba(99,102,241,0.08); border:1px solid var(--border-accent); padding:12px 20px; border-radius:10px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div>
          <span style="font-size:0.75rem; color:var(--muted); text-transform:uppercase; font-weight:700;">Analyzed:</span>
          <span style="font-size:1.05rem; font-weight:800; color:#fff; margin-left:6px;" id="metaDomain"></span>
          <span style="font-size:0.82rem; color:var(--muted); margin-left:8px;" id="metaQuery"></span>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
          <span class="badge" style="background:rgba(255,255,255,0.06); color:var(--muted);" id="metaProvider"></span>
          <span class="badge badge-no-hindsight">Hindsight Memory: OFF</span>
        </div>
      </div>

      <!-- LAYER 1: VERIFIED OBSERVED DATA -->
      <div class="layer-card layer-observed">
        <div class="layer-title">
          <span>📊 LAYER 1: VERIFIED OBSERVED DATA</span>
          <span class="badge" style="background:rgba(6,182,212,0.15); color:var(--cyan); border:1px solid rgba(6,182,212,0.3);">
            Factual Grounding (No AI Hallucination)
          </span>
        </div>
        <p style="font-size:0.84rem; color:var(--muted); margin-bottom:14px;">
          The verifiable inputs extracted by the deterministic SEO analyzer that were supplied to the LLM:
        </p>
        <div class="obs-metrics" id="obsPills">
          <!-- Populated by JS -->
        </div>
        <div id="compBox" style="font-size:0.82rem; background:rgba(0,0,0,0.25); padding:10px 14px; border-radius:6px; color:var(--muted);">
          <!-- Competitor context -->
        </div>
      </div>

      <!-- LAYER 2: AI INTERPRETATION & DIAGNOSIS -->
      <div class="layer-card layer-interpretation">
        <div class="layer-title">
          <span>🧠 LAYER 2: AI INTERPRETATION & DIAGNOSIS</span>
          <span class="badge" style="background:rgba(99,102,241,0.15); color:var(--accent-light); border:1px solid rgba(99,102,241,0.3);">
            Heuristic Reasoning (Not Observed Fact)
          </span>
        </div>

        <div style="margin-bottom:16px;">
          <div style="font-size:0.76rem; font-weight:700; color:var(--faint); text-transform:uppercase; margin-bottom:4px;">Diagnostic Assessment</div>
          <p style="font-size:0.92rem; color:var(--text); line-height:1.6;" id="aiDiagnosis"></p>
        </div>

        <div style="margin-bottom:16px;">
          <div style="font-size:0.76rem; font-weight:700; color:var(--faint); text-transform:uppercase; margin-bottom:4px;">Search Intent Fit Evaluation</div>
          <p style="font-size:0.9rem; color:var(--muted); line-height:1.6;" id="intentFit"></p>
        </div>

        <div style="margin-bottom:16px;">
          <div style="font-size:0.76rem; font-weight:700; color:var(--faint); text-transform:uppercase; margin-bottom:8px;">Identified Main Weaknesses</div>
          <div id="weaknessList">
            <!-- Populated by JS -->
          </div>
        </div>

        <!-- Missing Evidence Box -->
        <div class="questions-box">
          <div style="font-size:0.85rem; font-weight:700; color:#fbbf24;">
            ❓ Insufficient Evidence / Clarifying Questions Identified by AI:
          </div>
          <p style="font-size:0.78rem; color:var(--muted); margin-top:2px;">
            The model identified areas where evidence was incomplete to prevent ungrounded guessing:
          </p>
          <ul id="missingQuestions">
            <!-- Populated by JS -->
          </ul>
        </div>
      </div>

      <!-- LAYER 3: PRESCRIPTIVE RECOMMENDATIONS -->
      <div class="layer-card layer-recommendations">
        <div class="layer-title">
          <span>🎯 LAYER 3: PRESCRIPTIVE RECOMMENDATIONS</span>
          <span class="badge" style="background:rgba(16,185,129,0.15); color:var(--success); border:1px solid rgba(16,185,129,0.3);">
            Forward-Looking Actions
          </span>
        </div>
        <p style="font-size:0.84rem; color:var(--muted); margin-bottom:16px;">
          Strategic recommendations with explicit heuristic rationale and expected direction of improvement:
        </p>
        <div id="recList">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- Raw Inspection Box -->
      <div class="panel">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <h2 style="font-size:1.05rem; font-weight:800; color:#fff;">🔍 Raw Prompt Sent & JSON Response</h2>
          <button class="btn-preset" onclick="toggleRaw()">Toggle Raw Inspector</button>
        </div>
        <div id="rawContainer" style="display:none;">
          <div style="font-size:0.75rem; font-weight:700; color:var(--faint); text-transform:uppercase; margin-bottom:4px;">Prompt Dispatched to LLM:</div>
          <pre class="raw-box" id="rawPrompt" style="margin-bottom:14px;"></pre>
          <div style="font-size:0.75rem; font-weight:700; color:var(--faint); text-transform:uppercase; margin-bottom:4px;">Structured JSON Output:</div>
          <pre class="raw-box" id="rawResponse"></pre>
        </div>
      </div>

    </div>
  </div>

  <script>
    let websites = [];
    let currentResult = null;

    async function init() {
      await loadWebsites();
      setupPresets();
      // Auto run first analysis
      handleRunLLM(new Event('submit'));
    }

    async function loadWebsites() {
      const res = await fetch('/api/v1/entities/websites');
      websites = await res.json();
      const sel = document.getElementById('websiteSelect');
      sel.innerHTML = websites.map(w => `
        <option value="${w.id}" ${w.domain === 'learnpythonhub.io' ? 'selected' : ''}>
          ${w.domain} (${w.title.slice(0, 40)}...)
        </option>
      `).join('');
    }

    function setupPresets() {
      const presets = [
        { label: "Python Courses (learnpythonhub.io)", query: "best python courses for beginners", domain: "learnpythonhub.io" },
        { label: "Competitor Leader (coursera.org)", query: "best python courses for beginners", domain: "coursera.org" },
        { label: "FastAPI Benchmarks (benchmarks-dev.io)", query: "fastapi vs express performance", domain: "benchmarks-dev.io" },
        { label: "AI Code Tools (devtools-radar.com)", query: "ai code generation tools", domain: "devtools-radar.com" }
      ];

      const pDiv = document.getElementById('presets');
      pDiv.innerHTML = presets.map((p, i) => `
        <button type="button" class="btn-preset" onclick="applyPreset('${p.query}', '${p.domain}')">
          ${p.label.split(' (')[0]}
        </button>
      `).join('');
    }

    function applyPreset(query, domain) {
      document.getElementById('queryInput').value = query;
      const matched = websites.find(w => w.domain === domain);
      if (matched) document.getElementById('websiteSelect').value = matched.id;
      handleRunLLM(new Event('submit'));
    }

    function syncWebsiteInfo() {}

    async function handleRunLLM(e) {
      if (e && e.preventDefault) e.preventDefault();

      const btn = document.getElementById('runBtn');
      btn.innerHTML = '<span class="spinner"></span> <span>Synthesizing LLM Reasoning...</span>';
      btn.disabled = true;
      document.getElementById('errorBanner').style.display = 'none';

      const payload = {
        query: document.getElementById('queryInput').value,
        website_id: document.getElementById('websiteSelect').value || null,
        provider: document.getElementById('providerSelect').value,
        api_key: document.getElementById('apiKeyInput').value || null
      };

      try {
        const res = await fetch('/api/v1/llm/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || 'LLM execution error');
        }

        const data = await res.json();
        currentResult = data;
        renderResults(data);
      } catch (err) {
        const errEl = document.getElementById('errorBanner');
        errEl.textContent = 'Error: ' + err.message;
        errEl.style.display = 'block';
      } finally {
        btn.innerHTML = '<span>Run LLM SEO Reasoning</span>';
        btn.disabled = false;
      }
    }

    function renderResults(data) {
      document.getElementById('resultsArea').style.display = 'flex';
      document.getElementById('metaDomain').textContent = data.target_domain;
      document.getElementById('metaQuery').textContent = '"' + data.query + '"';
      document.getElementById('metaProvider').textContent = 'Provider: ' + data.provider_used;

      // Layer 1: Observed Data
      const obs = data.observed_data;
      document.getElementById('obsPills').innerHTML = `
        <div class="obs-pill">
          <div class="obs-pill-title">Detected Intent</div>
          <div class="obs-pill-val">${obs.search_intent_detected.toUpperCase()} (${obs.intent_match_score}%)</div>
        </div>
        <div class="obs-pill">
          <div class="obs-pill-title">Word Count</div>
          <div class="obs-pill-val">${obs.word_count.toLocaleString()} Words</div>
        </div>
        <div class="obs-pill">
          <div class="obs-pill-title">Interactive Tool</div>
          <div class="obs-pill-val">${obs.has_interactive_widget ? '✅ Active Tool' : '❌ None'}</div>
        </div>
        <div class="obs-pill">
          <div class="obs-pill-title">Video Preview</div>
          <div class="obs-pill-val">${obs.has_video_preview ? '✅ Video Present' : '❌ Missing Video'}</div>
        </div>
        <div class="obs-pill">
          <div class="obs-pill-title">Comparison Matrix</div>
          <div class="obs-pill-val">${obs.has_comparison_table ? '✅ Tabular Matrix' : '❌ No Table'}</div>
        </div>
        <div class="obs-pill">
          <div class="obs-pill-title">Schemas Present</div>
          <div class="obs-pill-val">${obs.schema_types_present.join(', ') || 'Article'}</div>
        </div>
      `;

      if (obs.competitor_context_available && obs.competitor_context_available.length > 0) {
        document.getElementById('compBox').innerHTML = '<strong>Competitor Benchmark: </strong>' +
          obs.competitor_context_available.map(c => `<code>${c.domain}</code> (${c.word_count}w, Video: ${c.has_video_preview}, Interactive: ${c.has_interactive_widget})`).join(' • ');
      } else {
        document.getElementById('compBox').innerHTML = 'No direct competitor snapshot available.';
      }

      // Layer 2: AI Interpretation
      const ai = data.ai_interpretation;
      document.getElementById('aiDiagnosis').textContent = ai.seo_diagnosis;
      document.getElementById('intentFit').textContent = ai.intent_fit_assessment;

      document.getElementById('weaknessList').innerHTML = ai.main_weaknesses.map(w => `
        <div class="weakness-card sev-${w.severity}">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <strong style="color:#fff; font-size:0.92rem;">${w.weakness}</strong>
            <span class="badge" style="background:rgba(255,255,255,0.06); font-size:0.7rem;">${w.category.toUpperCase()} • ${w.severity.toUpperCase()} SEVERITY</span>
          </div>
          <div style="font-size:0.83rem; color:var(--muted);">${w.evidence}</div>
        </div>
      `).join('');

      document.getElementById('missingQuestions').innerHTML = ai.missing_evidence_or_questions.map(q => `
        <li>${q}</li>
      `).join('');

      // Layer 3: Recommendations
      document.getElementById('recList').innerHTML = data.recommendations.map(r => `
        <div class="rec-card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:6px;">
            <div class="rec-title">Priority ${r.priority}: ${r.title}</div>
            <span class="badge" style="background:rgba(16,185,129,0.15); color:var(--success); border:1px solid rgba(16,185,129,0.3);">${r.category.toUpperCase()}</span>
          </div>
          <div class="rec-reasoning"><strong>Heuristic Rationale:</strong> ${r.reasoning}</div>
          <div class="rec-impact"><strong>Expected Direction of Improvement:</strong> ${r.expected_direction_of_improvement}</div>
          <div class="rec-steps">
            <strong>Implementation Checklist:</strong>
            <ul>
              ${r.implementation_steps.map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
        </div>
      `).join('');

      // Raw Prompt & Response
      document.getElementById('rawPrompt').textContent = data.raw_prompt_sent;
      document.getElementById('rawResponse').textContent = JSON.stringify(data, null, 2);
    }

    function toggleRaw() {
      const el = document.getElementById('rawContainer');
      el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }

    window.onload = init;
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
