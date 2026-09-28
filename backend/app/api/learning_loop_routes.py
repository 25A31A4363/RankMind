import json
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import HTMLResponse

from app.models.learning_loop_schemas import (
    WebsiteEventTimeline,
    LearningHistoryResponse,
    RecordActionRequest,
    RecordMeasureRequest,
    BeforeAfterComparisonResponse,
)
from app.services.learning_loop_service import learning_loop_service

router = APIRouter(prefix="", tags=["Complete SEO Learning Loop"])


# =============================================================================
# 1. EVENT TIMELINE ENDPOINT
# =============================================================================

@router.get(
    "/api/v1/learning-loop/timeline",
    response_model=WebsiteEventTimeline,
    status_code=status.HTTP_200_OK,
)
def get_website_event_timeline(
    website: str = Query("learnpythonhub.io", description="Target website domain"),
    keyword: Optional[str] = Query("best python courses for beginners", description="Target keyword"),
) -> WebsiteEventTimeline:
    """Returns the explicit chronological event timeline for a website,
    showing every step: Search -> Ranking -> Memory -> Recommendation -> Action -> Measure -> Retain -> Learn.
    """
    try:
        return learning_loop_service.get_website_timeline(website_domain=website, keyword=keyword)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline generation error: {str(e)}")


# =============================================================================
# 2. LEARNING HISTORY VIEW ENDPOINT
# =============================================================================

@router.get(
    "/api/v1/learning-loop/history",
    response_model=LearningHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_website_learning_history(
    website: str = Query("learnpythonhub.io", description="Target website domain"),
) -> LearningHistoryResponse:
    """Returns the structured Learning History view showing:
    - Previous state
    - Action
    - Later observed state
    - Memory created
    - Future recommendation influenced by memory
    """
    try:
        return learning_loop_service.get_learning_history(website_domain=website)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning history error: {str(e)}")


# =============================================================================
# 3. ACTION RECORDING ENDPOINT (Step 6)
# =============================================================================

@router.post(
    "/api/v1/learning-loop/action",
    status_code=status.HTTP_201_CREATED,
)
def record_optimization_action(payload: RecordActionRequest) -> Dict[str, Any]:
    """Step 6: User records an optimization/action taken on the website."""
    try:
        return learning_loop_service.record_action(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action recording error: {str(e)}")


# =============================================================================
# 4. MEASURE & RETAIN ENDPOINT (Steps 7 & 8)
# =============================================================================

@router.post(
    "/api/v1/learning-loop/measure",
    status_code=status.HTTP_201_CREATED,
)
def record_measured_outcome(payload: RecordMeasureRequest) -> Dict[str, Any]:
    """Steps 7 & 8: Records later observed ranking, creates outcome attribution,
    and retains the experience into Hindsight memory.
    """
    try:
        return learning_loop_service.record_measure(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Measurement recording error: {str(e)}")


# =============================================================================
# 5. BEFORE/AFTER COMPARISON ENDPOINT
# =============================================================================

@router.get(
    "/api/v1/learning-loop/before-after",
    response_model=BeforeAfterComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def get_before_after_comparison(
    website: str = Query("learnpythonhub.io", description="Target website domain"),
    query: str = Query("best python courses for beginners", description="Target query"),
) -> BeforeAfterComparisonResponse:
    """Demonstrates visually obvious before/after contrast:
    BEFORE MEMORY: Generic SEO analysis (word count fluff, no memory).
    AFTER MEMORY: Historical context + personalized recommendation (suppressed tactics, cited evidence).
    """
    try:
        return await learning_loop_service.get_before_after_contrast(
            website_domain=website, query=query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


# =============================================================================
# 6. INTERACTIVE HTML COCKPIT FOR THE COMPLETE SEO LEARNING LOOP
# =============================================================================

@router.get("/learning-loop", response_class=HTMLResponse)
def render_learning_loop_cockpit():
    """Interactive visual cockpit for inspecting and driving the 9-step SEO Learning Loop."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RankMind | Complete SEO Learning Loop</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #070a12;
      --card: #0f172a;
      --card-subtle: #162035;
      --border: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(99, 102, 241, 0.4);
      --text: #f8fafc;
      --muted: #94a3b8;
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --purple: #a855f7;
      --cyan: #06b6d4;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding-bottom: 80px;
    }}
    header {{
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 16px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; }}
    .logo-badge {{
      background: linear-gradient(135deg, #10b981, #06b6d4);
      width: 42px;
      height: 42px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      color: #fff;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
    }}
    .brand h1 {{ font-size: 20px; font-weight: 700; }}
    .brand span {{ font-size: 13px; color: var(--muted); }}
    .top-links {{ display: flex; gap: 12px; align-items: center; }}
    .nav-btn {{
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
      color: var(--text);
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s;
    }}
    .nav-btn:hover {{ background: rgba(255,255,255,0.08); border-color: var(--cyan); }}
    .container {{ max-width: 1400px; margin: 32px auto; padding: 0 24px; }}
    
    /* 9-Step Pipeline Stepper */
    .stepper-container {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 28px;
    }}
    .stepper-title {{ font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #e2e8f0; display: flex; align-items: center; gap: 8px; }}
    .stepper-track {{
      display: grid;
      grid-template-columns: repeat(9, 1fr);
      gap: 8px;
      position: relative;
    }}
    @media (max-width: 1100px) {{ .stepper-track {{ grid-template-columns: repeat(3, 1fr); gap: 12px; }} }}
    @media (max-width: 600px) {{ .stepper-track {{ grid-template-columns: 1fr; }} }}
    .step-pill {{
      background: #080d1a;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      transition: all 0.2s;
    }}
    .step-pill.active {{
      border-color: var(--cyan);
      background: rgba(6, 182, 212, 0.08);
      box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
    }}
    .step-header {{ display: flex; align-items: center; justify-content: space-between; }}
    .step-num {{ font-size: 11px; font-weight: 800; color: var(--cyan); font-family: 'JetBrains Mono'; }}
    .step-name {{ font-size: 12px; font-weight: 700; color: #fff; text-transform: uppercase; }}
    .step-desc {{ font-size: 11px; color: var(--muted); line-height: 1.3; }}

    /* Tabs */
    .tabs {{
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 24px;
      overflow-x: auto;
    }}
    .tab-btn {{
      padding: 12px 20px;
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--muted);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{ color: var(--text); }}
    .tab-btn.active {{
      color: var(--cyan);
      border-bottom-color: var(--cyan);
      background: rgba(6, 182, 212, 0.05);
    }}
    .tab-pane {{ display: none; }}
    .tab-pane.active {{ display: block; }}

    /* Panels & Cards */
    .panel {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .panel-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }}
    .panel-title {{ font-size: 18px; font-weight: 700; }}
    .panel-subtitle {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}

    /* Contrast Grid */
    .contrast-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-top: 20px;
    }}
    @media (max-width: 900px) {{ .contrast-grid {{ grid-template-columns: 1fr; }} }}
    .contrast-col {{
      background: #080d1a;
      border-radius: 12px;
      border: 1px solid var(--border);
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .contrast-col.before {{ border-top: 4px solid var(--danger); }}
    .contrast-col.after {{ border-top: 4px solid var(--success); }}
    .contrast-badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .contrast-badge.before {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}
    .contrast-badge.after {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}

    /* Timeline Vertical Cards */
    .timeline-container {{
      position: relative;
      margin-left: 20px;
      padding-left: 28px;
      border-left: 2px solid rgba(6, 182, 212, 0.3);
    }}
    .timeline-node {{
      position: relative;
      margin-bottom: 28px;
    }}
    .timeline-dot {{
      position: absolute;
      left: -37px;
      top: 4px;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--bg);
      border: 3px solid var(--cyan);
    }}
    .timeline-card {{
      background: #080d1a;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .timeline-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .timeline-title {{ font-size: 15px; font-weight: 700; color: #fff; }}
    .timeline-stage {{ font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(6, 182, 212, 0.15); color: var(--cyan); text-transform: uppercase; }}

    /* Learning History Card */
    .history-card {{
      background: #080d1a;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .history-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 12px;
    }}
    .history-title {{ font-size: 16px; font-weight: 700; color: #f1f5f9; }}
    .history-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}
    .history-block {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .history-label {{ font-size: 11px; text-transform: uppercase; font-weight: 700; color: var(--muted); }}
    .history-val {{ font-size: 13px; color: #e2e8f0; line-height: 1.4; }}

    /* Form Controls */
    .form-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }}
    .form-group {{ flex: 1; min-width: 240px; display: flex; flex-direction: column; gap: 8px; }}
    label {{ font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; }}
    input, select, textarea {{
      background: #0b1120;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
      color: #fff;
      font-family: inherit;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }}
    input:focus, select:focus, textarea:focus {{ border-color: var(--cyan); }}
    .btn {{
      padding: 12px 24px;
      border-radius: 8px;
      border: none;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--cyan), #0284c7);
      color: #fff;
      box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
    }}
    .btn-primary:hover {{ opacity: 0.95; transform: translateY(-1px); }}
    .btn-secondary {{
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: var(--text);
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="logo-badge">⟳</div>
      <div>
        <h1>Complete SEO Learning Loop</h1>
        <span>Persistent Experience-Driven Search Intelligence (Steps 1 → 9)</span>
      </div>
    </div>
    <div class="top-links">
      <a href="/hindsight" class="nav-btn">Hindsight Studio</a>
      <a href="/llm-analysis" class="nav-btn">LLM Reasoner</a>
      <a href="/analyzer" class="nav-btn">Baseline Analyzer</a>
    </div>
  </header>

  <div class="container">
    <!-- 9-Step Flow Pipeline -->
    <div class="stepper-container">
      <div class="stepper-title">
        <span>🔄 The Closed SEO Learning Loop Flow</span>
        <span style="font-size: 12px; color: var(--muted); font-weight: normal;">(Experience retained in Step 8 feeds forward to Step 9)</span>
      </div>
      <div class="stepper-track">
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">01</span>
            <span class="step-name">Search</span>
          </div>
          <div class="step-desc">User enters target search query</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">02</span>
            <span class="step-name">Analyze</span>
          </div>
          <div class="step-desc">Current on-page signals analyzed</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">03</span>
            <span class="step-name">Recall</span>
          </div>
          <div class="step-desc">8-dimension memory retrieval</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">04</span>
            <span class="step-name">Reason</span>
          </div>
          <div class="step-desc">LLM contextual synthesis</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">05</span>
            <span class="step-name">Recommend</span>
          </div>
          <div class="step-desc">Transparent evidence-based advice</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">06</span>
            <span class="step-name">Action</span>
          </div>
          <div class="step-desc">User records optimization</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">07</span>
            <span class="step-name">Measure</span>
          </div>
          <div class="step-desc">Later ranking result observed</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">08</span>
            <span class="step-name">Retain</span>
          </div>
          <div class="step-desc">Outcome stored into Hindsight</div>
        </div>
        <div class="step-pill active">
          <div class="step-header">
            <span class="step-num">09</span>
            <span class="step-name">Learn</span>
          </div>
          <div class="step-desc">Future advice uses this experience</div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('tab-before-after')">⚖️ Before / After Mode (Visually Obvious)</button>
      <button class="tab-btn" onclick="switchTab('tab-timeline')">📅 Website Event Timeline</button>
      <button class="tab-btn" onclick="switchTab('tab-history')">🧠 Learning History View</button>
      <button class="tab-btn" onclick="switchTab('tab-drive-loop')">⚡ Drive the Loop (Action & Measure)</button>
    </div>

    <!-- TAB 1: BEFORE / AFTER MODE -->
    <div id="tab-before-after" class="tab-pane active">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Before Memory vs After Memory Contrast Mode</div>
            <div class="panel-subtitle">Demonstrates how persistent memory transforms generic SEO checklists into institutional competitive intelligence.</div>
          </div>
          <button onclick="loadBeforeAfter()" class="btn btn-primary">Refresh Comparison</button>
        </div>

        <div id="beforeAfterArea">
          <div style="text-align: center; padding: 40px; color: var(--cyan);">Loading Before/After contrast...</div>
        </div>
      </div>
    </div>

    <!-- TAB 2: WEBSITE EVENT TIMELINE -->
    <div id="tab-timeline" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Website Event Timeline: learnpythonhub.io</div>
            <div class="panel-subtitle">Complete chronological event timeline from Search to Action to Measurement to Retain and Learn.</div>
          </div>
          <button onclick="loadTimeline()" class="btn btn-secondary">Refresh Timeline</button>
        </div>

        <div id="timelineArea">
          <div style="text-align: center; padding: 40px; color: var(--cyan);">Loading event timeline...</div>
        </div>
      </div>
    </div>

    <!-- TAB 3: LEARNING HISTORY VIEW -->
    <div id="tab-history" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Learning History View</div>
            <div class="panel-subtitle">Explicitly breaks down every evolutionary cycle: Previous State → Action → Later Observed State → Memory Created → Future Influence.</div>
          </div>
          <button onclick="loadHistory()" class="btn btn-secondary">Refresh History</button>
        </div>

        <div id="historyArea">
          <div style="text-align: center; padding: 40px; color: var(--cyan);">Loading learning history...</div>
        </div>
      </div>
    </div>

    <!-- TAB 4: DRIVE THE LOOP -->
    <div id="tab-drive-loop" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Drive the Loop: Record Action & Measure Later Outcome</div>
            <div class="panel-subtitle">Simulate or record real-world optimizations (Step 6) and post-optimization ranking outcomes (Steps 7 & 8) to update Hindsight in real time.</div>
          </div>
        </div>

        <!-- Action Recording Form (Step 6) -->
        <div style="background: #080d1a; border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
          <h3 style="font-size: 15px; margin-bottom: 12px; color: var(--cyan);">Step 6: Record an Optimization Action Taken</h3>
          <form onsubmit="submitAction(event)">
            <div class="form-row">
              <div class="form-group">
                <label>Website Domain</label>
                <input type="text" id="actionWebsite" value="learnpythonhub.io" required>
              </div>
              <div class="form-group">
                <label>Keyword</label>
                <input type="text" id="actionKeyword" value="best python courses for beginners" required>
              </div>
              <div class="form-group">
                <label>Optimization Type</label>
                <select id="actionType" required>
                  <option value="structured_schema">Structured Schema (Course / VideoObject)</option>
                  <option value="interactive_ux">Interactive UX (Code Sandbox)</option>
                  <option value="multimedia">Multimedia (Video Project Previews)</option>
                  <option value="content_depth">Content Depth (Word Count)</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group" style="flex: 2;">
                <label>Optimization Title</label>
                <input type="text" id="actionTitle" value="Deployed Course Schema & 90-Second Video Preview" required>
              </div>
              <div class="form-group" style="flex: 3;">
                <label>Description of Action</label>
                <input type="text" id="actionDescription" value="Injected Course JSON-LD markup and embedded 3 project walkthrough videos." required>
              </div>
            </div>
            <button type="submit" class="btn btn-primary" id="btnAction">Record Action (Step 6)</button>
            <span id="actionStatus" style="margin-left: 12px; font-size: 13px;"></span>
          </form>
        </div>

        <!-- Measurement & Retention Form (Steps 7 & 8) -->
        <div style="background: #080d1a; border: 1px solid var(--border); border-radius: 12px; padding: 20px;">
          <h3 style="font-size: 15px; margin-bottom: 12px; color: var(--success);">Steps 7 & 8: Record Later Observed Ranking & Retain in Memory</h3>
          <form onsubmit="submitMeasure(event)">
            <div class="form-row">
              <div class="form-group">
                <label>Website Domain</label>
                <input type="text" id="measureWebsite" value="learnpythonhub.io" required>
              </div>
              <div class="form-group">
                <label>Keyword</label>
                <input type="text" id="measureKeyword" value="best python courses for beginners" required>
              </div>
              <div class="form-group">
                <label>Optimization Category</label>
                <select id="measureType">
                  <option value="structured_schema">structured_schema</option>
                  <option value="interactive_ux">interactive_ux</option>
                  <option value="multimedia">multimedia</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Optimization Title</label>
                <input type="text" id="measureTitle" value="Course Schema & Video Previews" required>
              </div>
              <div class="form-group">
                <label>Previous Rank</label>
                <input type="number" id="measurePrevRank" value="4" min="1" max="100" required>
              </div>
              <div class="form-group">
                <label>Later Observed Rank</label>
                <input type="number" id="measureNewRank" value="2" min="1" max="100" required>
              </div>
              <div class="form-group">
                <label>Latency Window (Days)</label>
                <input type="number" id="measureDays" value="21" min="1" max="180">
              </div>
            </div>
            <button type="submit" class="btn btn-primary" id="btnMeasure" style="background: linear-gradient(135deg, var(--success), #059669);">Measure & Retain (Steps 7 & 8)</button>
            <span id="measureStatus" style="margin-left: 12px; font-size: 13px;"></span>
          </form>
          <div id="measureResultArea" style="margin-top: 16px;"></div>
        </div>

      </div>
    </div>

  </div>

  <script>
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      event.currentTarget.classList.add('active');
      document.getElementById(tabId).classList.add('active');

      if (tabId === 'tab-before-after') loadBeforeAfter();
      if (tabId === 'tab-timeline') loadTimeline();
      if (tabId === 'tab-history') loadHistory();
    }}

    async function loadBeforeAfter() {{
      const area = document.getElementById('beforeAfterArea');
      area.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--cyan);">Running Before vs After Analysis...</div>';

      try {{
        const res = await fetch('/api/v1/learning-loop/before-after?website=learnpythonhub.io');
        const data = await res.json();

        let matrixRows = '';
        data.key_differences_matrix.forEach(k => {{
          matrixRows += `
            <tr>
              <td style="font-weight: 700; color: #fff;">${{k.dimension}}</td>
              <td style="color: #fca5a5; font-size: 12px;">${{k.before_memory}}</td>
              <td style="color: #34d399; font-size: 12px;">${{k.after_memory}}</td>
            </tr>`;
        }});

        let beforeRecsHtml = '';
        data.before_memory.recommendations.forEach(r => {{
          beforeRecsHtml += `
            <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 8px;">
              <div style="font-weight: 700; color: #e2e8f0; font-size: 13px;">${{r.title}}</div>
              <div style="font-size: 12px; color: var(--muted); margin-top: 4px;">${{r.reasoning}}</div>
            </div>`;
        }});

        let afterRecsHtml = '';
        data.after_memory.recommendations.forEach(r => {{
          const why = r.why_am_i_seeing_this || {{}};
          afterRecsHtml += `
            <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
              <div style="font-weight: 700; color: #34d399; font-size: 13px;">${{r.title}}</div>
              <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">${{r.reasoning}}</div>
              
              <!-- Why am I seeing this card -->
              <div style="margin-top: 10px; background: rgba(6, 182, 212, 0.06); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 6px; padding: 10px;">
                <div style="font-weight: 700; font-size: 11px; text-transform: uppercase; color: var(--cyan); margin-bottom: 4px;">💡 Why am I seeing this recommendation?</div>
                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 2px;"><strong>Observation:</strong> <span style="color: #f1f5f9;">${{why.current_observation || '-'}}</span></div>
                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 2px;"><strong>Recalled Memory:</strong> <span style="color: #a5f3fc;">${{why.recalled_memory || '-'}}</span></div>
                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 2px;"><strong>Connection:</strong> <span style="color: #cbd5e1;">${{why.connection_between_them || '-'}}</span></div>
                <div style="font-size: 10px; color: var(--warning); margin-top: 4px; font-style: italic;">⚖️ ${{why.observational_caveat || ''}}</div>
              </div>
            </div>`;
        }});

        let suppressedListHtml = '';
        data.after_memory.suppressed_tactics.forEach(s => {{
          suppressedListHtml += `<li style="margin-bottom: 6px; color: #f87171; font-size: 12px;">🚫 ${{s}}</li>`;
        }});

        area.innerHTML = `
          <!-- Thesis Alert Banner -->
          <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 24px;">
            <div style="font-weight: 800; font-size: 14px; color: #fff; margin-bottom: 4px;">💡 Demonstration Thesis</div>
            <div style="font-size: 13px; color: #c7d2fe; line-height: 1.5;">${{data.demonstration_thesis}}</div>
          </div>

          <!-- Side-by-Side Comparison Columns -->
          <div class="contrast-grid">
            <!-- BEFORE MEMORY -->
            <div class="contrast-col before">
              <div>
                <span class="contrast-badge before">BEFORE MEMORY: Generic SEO Analysis</span>
                <h3 style="font-size: 16px; font-weight: 700; margin-top: 8px;">Isolated On-Page Baseline</h3>
                <p style="font-size: 12px; color: var(--muted); margin-top: 4px;">${{data.before_memory.limitations}}</p>
              </div>

              <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--muted); margin-bottom: 6px;">Diagnosis:</div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.4; background: rgba(255,255,255,0.02); padding: 10px; border-radius: 6px;">${{data.before_memory.seo_diagnosis}}</div>
              </div>

              <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--muted); margin-bottom: 6px;">Recommendations (Generic Heuristic):</div>
                ${{beforeRecsHtml}}
              </div>
            </div>

            <!-- AFTER MEMORY -->
            <div class="contrast-col after">
              <div>
                <span class="contrast-badge after">AFTER MEMORY: Context-Aware Intelligence</span>
                <h3 style="font-size: 16px; font-weight: 700; margin-top: 8px; color: #34d399;">Institutional Memory Reasoner</h3>
                <p style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Recalled ${{data.after_memory.recalled_memories_count}} verified historical events across 8 dimensions.</p>
              </div>

              <!-- Suppressed Tactics -->
              <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #fca5a5; text-transform: uppercase; margin-bottom: 6px;">Tactics Suppressed (Empirically Proven Ineffective):</div>
                <ul style="padding-left: 16px; margin: 0;">${{suppressedListHtml}}</ul>
              </div>

              <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #34d399; margin-bottom: 6px;">Context-Aware Recommendations (with Transparency):</div>
                ${{afterRecsHtml}}
              </div>
            </div>
          </div>

          <!-- Key Differences Table -->
          <div style="margin-top: 32px;">
            <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 12px;">📊 Architectural Key Differences Matrix</h3>
            <div style="overflow-x: auto; background: #080d1a; border: 1px solid var(--border); border-radius: 10px;">
              <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                  <tr style="border-bottom: 1px solid var(--border); background: #050811;">
                    <th style="padding: 12px; text-align: left; color: var(--muted); font-size: 11px;">DIMENSION</th>
                    <th style="padding: 12px; text-align: left; color: #f87171; font-size: 11px;">BEFORE MEMORY (STATELESS)</th>
                    <th style="padding: 12px; text-align: left; color: #34d399; font-size: 11px;">AFTER MEMORY (HINDSIGHT-AUGMENTED)</th>
                  </tr>
                </thead>
                <tbody>${{matrixRows}}</tbody>
              </table>
            </div>
          </div>
        `;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 20px;">Error loading comparison: ' + err.message + '</div>';
      }}
    }}

    async function loadTimeline() {{
      const area = document.getElementById('timelineArea');
      area.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--cyan);">Loading event timeline...</div>';

      try {{
        const res = await fetch('/api/v1/learning-loop/timeline?website=learnpythonhub.io');
        const data = await res.json();

        let timelineNodes = '';
        data.timeline.forEach(e => {{
          const isActionOrMeasure = e.stage === 'ACTION' || e.stage === 'MEASURE' || e.stage === 'RETAIN';
          const stageColor = isActionOrMeasure ? '#34d399' : 'var(--cyan)';

          timelineNodes += `
            <div class="timeline-node">
              <div class="timeline-dot" style="border-color: ${{stageColor}};"></div>
              <div class="timeline-card">
                <div class="timeline-header">
                  <div class="timeline-title">${{e.title}}</div>
                  <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="timeline-stage" style="color: ${{stageColor}};">STAGE: ${{e.stage}}</span>
                    <span class="mono" style="font-size: 11px; color: var(--muted);">${{e.timestamp.substring(0, 10)}}</span>
                  </div>
                </div>
                <div style="font-size: 13px; color: #cbd5e1; line-height: 1.4;">${{e.description}}</div>
                <div style="display: flex; gap: 12px; font-size: 11px; color: var(--muted); margin-top: 4px;">
                  <span>Step: <strong>#${{e.step_number}}</strong></span>
                  <span>Website: <span class="mono" style="color: #a5f3fc;">${{e.website}}</span></span>
                  ${{e.state_snapshot.ranking ? `<span>Rank: <strong style="color: #34d399;">#${{e.state_snapshot.ranking}}</strong></span>` : ''}}
                </div>
              </div>
            </div>`;
        }});

        area.innerHTML = `
          <div style="margin-bottom: 20px; font-size: 13px; color: var(--muted);">
            Website: <strong class="mono" style="color: #fff;">${{data.website}}</strong> | Current Position: <strong style="color: #34d399;">#${{data.current_position}}</strong> | Total Events: <strong>${{data.total_events}}</strong>
          </div>
          <div class="timeline-container">
            ${{timelineNodes}}
          </div>
        `;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 20px;">Error loading timeline: ' + err.message + '</div>';
      }}
    }}

    async function loadHistory() {{
      const area = document.getElementById('historyArea');
      area.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--cyan);">Loading learning history...</div>';

      try {{
        const res = await fetch('/api/v1/learning-loop/history?website=learnpythonhub.io');
        const data = await res.json();

        let cardsHtml = '';
        data.items.forEach(it => {{
          cardsHtml += `
            <div class="history-card">
              <div class="history-header">
                <div>
                  <div class="history-title">${{it.cycle_name}}</div>
                  <div style="font-size: 12px; color: var(--muted); margin-top: 2px;">Observed Date: ${{it.timestamp}} | Keyword: ${{it.keyword}}</div>
                </div>
                <span class="mono" style="font-size: 11px; padding: 4px 8px; border-radius: 4px; background: rgba(16, 185, 129, 0.15); color: #34d399;">
                  ${{it.memory_created.verdict}}
                </span>
              </div>

              <div class="history-grid">
                <!-- 1. Previous State -->
                <div class="history-block">
                  <div class="history-label">1. Previous State</div>
                  <div class="history-val">
                    <div><strong>Rank: #${{it.previous_state.ranking}}</strong></div>
                    <div style="color: var(--muted); font-size: 12px; margin-top: 2px;">${{it.previous_state.summary || ''}}</div>
                  </div>
                </div>

                <!-- 2. Action Taken -->
                <div class="history-block">
                  <div class="history-label">2. Action Taken</div>
                  <div class="history-val">
                    <div><strong style="color: var(--cyan);">${{it.action.title}}</strong></div>
                    <div style="color: #94a3b8; font-size: 12px; margin-top: 2px;">${{it.action.description}}</div>
                  </div>
                </div>

                <!-- 3. Later Observed State -->
                <div class="history-block">
                  <div class="history-label">3. Later Observed State</div>
                  <div class="history-val">
                    <div><strong style="color: #34d399;">Rank: #${{it.later_observed_state.ranking}}</strong> (${{it.later_observed_state.observed_result}})</div>
                    <div style="color: var(--muted); font-size: 12px; margin-top: 2px;">Latency: ${{it.later_observed_state.latency_days}} days</div>
                  </div>
                </div>

                <!-- 4. Memory Created -->
                <div class="history-block">
                  <div class="history-label">4. Memory Created in Hindsight</div>
                  <div class="history-val" style="font-size: 12px; color: #a5f3fc;">
                    "${{it.memory_created.content}}"
                  </div>
                </div>
              </div>

              <!-- 5. Future Recommendation Influenced -->
              <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 8px; padding: 12px;">
                <div style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: #a5b4fc; margin-bottom: 4px;">
                  🎯 5. Future Recommendation Influenced By Memory:
                </div>
                <div style="font-size: 13px; color: #f1f5f9; line-height: 1.4;">
                  ${{it.future_recommendation_influenced_by_memory}}
                </div>
              </div>
            </div>`;
        }});

        area.innerHTML = `
          <div style="margin-bottom: 20px; font-size: 13px; color: var(--muted);">
            Website: <strong class="mono" style="color: #fff;">${{data.website}}</strong> | Total Evolutionary Cycles: <strong>${{data.total_cycles}}</strong>
          </div>
          ${{cardsHtml}}
        `;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 20px;">Error loading history: ' + err.message + '</div>';
      }}
    }}

    async function submitAction(e) {{
      e.preventDefault();
      const statusSpan = document.getElementById('actionStatus');
      const btn = document.getElementById('btnAction');

      btn.disabled = true;
      btn.innerText = 'Recording...';
      statusSpan.innerText = '';

      try {{
        const payload = {{
          website: document.getElementById('actionWebsite').value,
          keyword: document.getElementById('actionKeyword').value,
          optimization_type: document.getElementById('actionType').value,
          title: document.getElementById('actionTitle').value,
          description: document.getElementById('actionDescription').value
        }};

        const res = await fetch('/api/v1/learning-loop/action', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});

        const data = await res.json();
        if (res.ok) {{
          statusSpan.innerHTML = '<span style="color: var(--success);">✓ Step 6 Action Recorded! (ID: ' + data.action_id + ')</span>';
        }} else {{
          statusSpan.innerHTML = '<span style="color: var(--danger);">✗ Error: ' + data.detail + '</span>';
        }}
      }} catch (err) {{
        statusSpan.innerHTML = '<span style="color: var(--danger);">✗ Network Error: ' + err.message + '</span>';
      }} finally {{
        btn.disabled = false;
        btn.innerText = 'Record Action (Step 6)';
      }}
    }}

    async function submitMeasure(e) {{
      e.preventDefault();
      const statusSpan = document.getElementById('measureStatus');
      const resultArea = document.getElementById('measureResultArea');
      const btn = document.getElementById('btnMeasure');

      btn.disabled = true;
      btn.innerText = 'Measuring & Retaining...';
      statusSpan.innerText = '';
      resultArea.innerHTML = '';

      try {{
        const payload = {{
          website: document.getElementById('measureWebsite').value,
          keyword: document.getElementById('measureKeyword').value,
          optimization_type: document.getElementById('measureType').value,
          optimization_title: document.getElementById('measureTitle').value,
          previous_ranking: parseInt(document.getElementById('measurePrevRank').value),
          new_ranking: parseInt(document.getElementById('measureNewRank').value),
          time_period_days: parseInt(document.getElementById('measureDays').value)
        }};

        const res = await fetch('/api/v1/learning-loop/measure', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});

        const data = await res.json();
        if (res.ok) {{
          statusSpan.innerHTML = '<span style="color: var(--success);">✓ Steps 7 & 8 Completed! Stored in Hindsight.</span>';
          resultArea.innerHTML = `
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 14px;">
              <div style="font-weight: 700; color: #34d399; font-size: 13px; margin-bottom: 6px;">
                🎉 Loop Closed: Rank Moved From #${{data.previous_ranking}} to #${{data.new_ranking}} (Delta: ${{data.rank_delta > 0 ? '+' : ''}}${{data.rank_delta}})
              </div>
              <div style="font-size: 13px; color: #f1f5f9; margin-bottom: 6px;">
                <strong>Gatekeeper Decision:</strong> ${{data.gatekeeper_decision}} (Importance Score: ${{(data.importance_score * 100).toFixed(0)}}%)
              </div>
              <div style="font-size: 12px; color: var(--cyan);">
                <strong>Step 9 Feedforward:</strong> ${{data.step_9_learn_summary}}
              </div>
            </div>
          `;
        }} else {{
          statusSpan.innerHTML = '<span style="color: var(--danger);">✗ Error: ' + data.detail + '</span>';
        }}
      }} catch (err) {{
        statusSpan.innerHTML = '<span style="color: var(--danger);">✗ Network Error: ' + err.message + '</span>';
      }} finally {{
        btn.disabled = false;
        btn.innerText = 'Measure & Retain (Steps 7 & 8)';
      }}
    }}

    // Auto load Before/After comparison on load
    window.onload = function() {{
      loadBeforeAfter();
    }};
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html, status_code=200)
