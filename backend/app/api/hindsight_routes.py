import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, status, Header
from fastapi.responses import HTMLResponse

from app.models.hindsight_schemas import (
    MemoryCategory,
    HindsightMemoryItem,
    HindsightRetainRequest,
    HindsightRecallRequest,
    HindsightRecallResponse,
    RetentionLogItem,
    RecallLogItem,
    MemoryAugmentedAnalysisRequest,
    MemoryAugmentedAnalysisResponse,
    RawSEOEvent,
    RetentionDecisionResult,
    RetentionDecisionLogItem,
    RetentionDecisionEnum,
)
from app.services.hindsight.client import hindsight_client
from app.services.hindsight.memory_manager import hindsight_memory_manager
from app.services.hindsight.event_processor import event_processing_layer
from app.services.llm.hindsight_reasoning_agent import hindsight_reasoning_agent
from app.services.llm.llm_analysis_service import llm_analysis_service
from app.models.llm_schemas import LLMAnalysisRequest
from app.repositories.seo_repository import SEORepository
from app.db.database import DB_PATH

router = APIRouter(prefix="", tags=["Hindsight Persistent Memory Layer"])
repo = SEORepository(DB_PATH)


# =============================================================================
# 1. RETAIN ENDPOINT (Save new experience into Hindsight memory)
# =============================================================================

@router.post(
    "/api/v1/hindsight/retain",
    response_model=HindsightMemoryItem,
    status_code=status.HTTP_201_CREATED,
)
async def retain_memory(payload: HindsightRetainRequest) -> HindsightMemoryItem:
    """Retains a new experience into Hindsight under one of the 4 core categories:
    
    1. RANKING HISTORY
    2. OPTIMIZATION HISTORY
    3. COMPETITOR HISTORY
    4. OUTCOME HISTORY
    """
    try:
        mem = hindsight_client.retain(
            category=payload.category,
            content=payload.content,
            target_keyword=payload.target_keyword,
            target_domain=payload.target_domain,
            bank_id=payload.bank_id,
            timestamp=payload.timestamp,
            metadata=payload.metadata,
            tags=payload.tags,
        )
        return mem
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hindsight Retention Error: {str(e)}",
        )


# =============================================================================
# 1B. EVENT PROCESSING & MEMORY QUALITY LAYER (Gatekeeper)
# =============================================================================

@router.post(
    "/api/v1/hindsight/process-event",
    response_model=RetentionDecisionResult,
    status_code=status.HTTP_200_OK,
)
def process_seo_event(payload: RawSEOEvent) -> RetentionDecisionResult:
    """Intelligent event-processing & memory-quality layer:
    Determines whether an incoming event is worth remembering (REMEMBER)
    or should be ignored as noise / duplicate (DO NOT REMEMBER).
    """
    try:
        result = event_processing_layer.process_and_evaluate_event(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Event Processing Error: {str(e)}",
        )


@router.get(
    "/api/v1/hindsight/decisions",
    response_model=List[RetentionDecisionLogItem],
    status_code=status.HTTP_200_OK,
)
def list_memory_quality_decisions(
    decision: Optional[str] = Query(None, description="Filter by 'REMEMBER' or 'DO NOT REMEMBER'"),
    limit: int = Query(50, ge=1, le=200),
) -> List[RetentionDecisionLogItem]:
    """Developer-visible log of all memory-quality layer decisions (REMEMBER vs DO NOT REMEMBER)."""
    return hindsight_client.list_retention_decisions(decision=decision, limit=limit)


# =============================================================================
# 2. RECALL ENDPOINT (Retrieve relevant historical memories for query)
# =============================================================================

@router.get(
    "/api/v1/hindsight/recall",
    response_model=HindsightRecallResponse,
    status_code=status.HTTP_200_OK,
)
async def recall_memories(
    query: str = Query(..., min_length=2, description="Target query or keyword to recall memories for"),
    domain: Optional[str] = Query(None, description="Optional target domain"),
    max_memories: int = Query(6, ge=1, le=20, description="Max memories to retrieve"),
    bank_id: str = Query("rankmind-seo", description="Hindsight bank identifier"),
) -> HindsightRecallResponse:
    """Recalls relevant historical memories for a query, prioritizing causal outcomes and competitor intelligence.
    
    Returns relevance scores and explicit 'why_relevant' explanations.
    """
    try:
        memories = hindsight_client.recall(
            query=query,
            target_domain=domain,
            bank_id=bank_id,
            max_memories=max_memories,
        )

        audit_log_id = f"audit_{uuid.uuid4().hex[:8]}"
        summary = (
            f"Recalled {len(memories)} historical memories for query '{query}' "
            + (f"and domain '{domain}'" if domain else "across all domains")
        )

        return HindsightRecallResponse(
            bank_id=bank_id,
            query=query,
            target_domain=domain,
            total_recalled=len(memories),
            memories=memories,
            relevance_summary=summary,
            audit_log_id=audit_log_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hindsight Recall Error: {str(e)}",
        )


# =============================================================================
# 3. MEMORY-AUGMENTED SEO ANALYSIS ENDPOINT
# =============================================================================

@router.post(
    "/api/v1/hindsight/analyze",
    response_model=MemoryAugmentedAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_with_hindsight_memory(
    payload: MemoryAugmentedAnalysisRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> MemoryAugmentedAnalysisResponse:
    """Executes the complete Hindsight memory loop:
    
    CURRENT SEO DATA + RECALLED MEMORY
    → LLM REASONING
    → CONTEXT-AWARE RECOMMENDATIONS
    """
    try:
        if not payload.api_key and x_api_key:
            payload.api_key = x_api_key

        res = await hindsight_reasoning_agent.analyze_with_memory(payload)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hindsight Memory Analysis Error: {str(e)}",
        )


# =============================================================================
# 4. SIDE-BY-SIDE CONTRAST: BASELINE VS HINDSIGHT
# =============================================================================

@router.get("/api/v1/hindsight/compare")
async def compare_baseline_vs_hindsight(
    query: str = Query("best python courses for beginners", description="Target search query"),
    domain: Optional[str] = Query(None, description="Optional target domain"),
    website_id: Optional[str] = Query(None, description="Optional website ID"),
):
    """Demonstrates that the exact same query produces a more context-aware recommendation
    when historical memory exists, compared to a naive static baseline analyzer.
    """
    try:
        target_website_id = website_id if isinstance(website_id, str) and website_id else None
        target_domain = domain if isinstance(domain, str) and domain else None
        target_query = query if isinstance(query, str) else "best python courses for beginners"

        # 1. Run Baseline Analysis (No Memory)
        base_req = LLMAnalysisRequest(
            query=target_query,
            website_id=target_website_id,
            provider="local",
        )
        base_res = await llm_analysis_service.run_analysis(base_req)

        # 2. Run Hindsight-Augmented Analysis (With Memory)
        mem_req = MemoryAugmentedAnalysisRequest(
            query=target_query,
            website_id=target_website_id,
            provider="local",
            max_memories=6,
        )
        mem_res = await hindsight_reasoning_agent.analyze_with_memory(mem_req)

        return {
            "query": query,
            "target_domain": mem_res.target_domain,
            "demonstration_thesis": "Historical memory prevents recommending tactics that empirically failed and prescribes counter-moves against competitor advances.",
            "baseline_stateless": {
                "hindsight_memory_applied": False,
                "seo_diagnosis": base_res.ai_interpretation.seo_diagnosis,
                "top_recommendations": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "category": r.category,
                        "reasoning": r.reasoning,
                    }
                    for r in base_res.recommendations[:3]
                ],
                "inherent_limitation": "Operates without historical awareness; cannot know whether text expansion or specific schemas previously failed or succeeded.",
            },
            "hindsight_augmented": {
                "hindsight_memory_applied": True,
                "recalled_memories_count": len(mem_res.recalled_memories),
                "recalled_memories_sample": [
                    {
                        "category": m.category,
                        "content": m.content,
                        "relevance_score": m.relevance_score,
                        "why_relevant": m.why_relevant,
                    }
                    for m in mem_res.recalled_memories[:4]
                ],
                "suppressed_tactics": mem_res.suppressed_tactics,
                "seo_diagnosis_with_memory": mem_res.ai_interpretation_with_memory.get("seo_diagnosis"),
                "context_aware_recommendations": [
                    {
                        "id": r.id if hasattr(r, "id") else r.get("id"),
                        "title": r.title if hasattr(r, "title") else r.get("title"),
                        "category": r.category if hasattr(r, "category") else r.get("category"),
                        "reasoning": r.reasoning if hasattr(r, "reasoning") else r.get("reasoning"),
                        "expected_direction_of_improvement": (
                            r.expected_direction_of_improvement if hasattr(r, "expected_direction_of_improvement")
                            else r.get("expected_direction_of_improvement")
                        ),
                        "why_am_i_seeing_this": (
                            r.why_am_i_seeing_this.model_dump() if hasattr(r, "why_am_i_seeing_this") and hasattr(r.why_am_i_seeing_this, "model_dump")
                            else r.get("why_am_i_seeing_this") if isinstance(r, dict) else {}
                        ),
                    }
                    for r in mem_res.context_aware_recommendations[:3]
                ],
                "memory_impact_analysis": mem_res.memory_impact_analysis,
            },
            "strategic_contrast_summary": mem_res.baseline_vs_hindsight_contrast,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


# =============================================================================
# 5. AUDIT LOGGING INSPECTION ENDPOINT
# =============================================================================

@router.get("/api/v1/hindsight/logs")
def get_hindsight_audit_logs(
    log_type: str = Query("all", pattern="^(all|retain|recall|decisions)$"),
    limit: int = Query(50, ge=1, le=200),
):
    """Allows developers to inspect:
    - what was retained
    - what was recalled
    - why it was relevant
    - memory-quality decisions (REMEMBER vs DO NOT REMEMBER)
    """
    retain_logs = []
    recall_logs = []
    decisions = []

    if log_type in ["all", "retain"]:
        retain_logs = hindsight_client.list_retention_logs(limit=limit)

    if log_type in ["all", "recall"]:
        recall_logs = hindsight_client.list_recall_logs(limit=limit)

    if log_type in ["all", "decisions"]:
        decisions = hindsight_client.list_retention_decisions(limit=limit)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_retention_events": len(retain_logs),
        "total_recall_events": len(recall_logs),
        "total_decision_events": len(decisions),
        "retention_logs": retain_logs,
        "recall_logs": recall_logs,
        "retention_decisions": decisions,
    }


# =============================================================================
# 6. MEMORY BANK EXPLORER ENDPOINT
# =============================================================================

@router.get("/api/v1/hindsight/memories")
def list_hindsight_memories(
    category: Optional[MemoryCategory] = None,
):
    """Lists all memories stored in the persistent Hindsight store."""
    mems = hindsight_client.list_all_memories(category=category)
    return {
        "total_memories": len(mems),
        "category_filter": category.value if category else "all",
        "memories": mems,
    }


# =============================================================================
# 7. SYNC DATABASE TO HINDSIGHT ENDPOINT
# =============================================================================

@router.post("/api/v1/hindsight/sync")
def sync_database_records():
    """Populates Hindsight memory bank from existing historical database records."""
    before_count = len(hindsight_client.list_all_memories())
    hindsight_memory_manager.sync_database_to_hindsight()
    after_count = len(hindsight_client.list_all_memories())
    return {
        "status": "success",
        "synced_records": after_count - before_count,
        "total_memories": after_count,
    }


# =============================================================================
# 8. INTERACTIVE DEVELOPER TESTING STUDIO (HTML UI)
# =============================================================================

@router.get("/hindsight", response_class=HTMLResponse)
def render_hindsight_developer_studio():
    """Interactive developer cockpit for inspecting, recalling, and contrasting Hindsight SEO memory."""
    # Ensure memory bank is synced if empty
    if len(hindsight_client.list_all_memories()) == 0:
        hindsight_memory_manager.sync_database_to_hindsight()

    total_mems = len(hindsight_client.list_all_memories())
    ranking_mems = len(hindsight_client.list_all_memories(MemoryCategory.RANKING_HISTORY))
    opt_mems = len(hindsight_client.list_all_memories(MemoryCategory.OPTIMIZATION_HISTORY))
    comp_mems = len(hindsight_client.list_all_memories(MemoryCategory.COMPETITOR_HISTORY))
    out_mems = len(hindsight_client.list_all_memories(MemoryCategory.OUTCOME_HISTORY))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RankMind | Hindsight Persistent Memory Studio</title>
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
      background: rgba(15, 23, 42, 0.8);
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
      background: linear-gradient(135deg, var(--purple), var(--primary));
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      color: #fff;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }}
    .brand h1 {{ font-size: 20px; font-weight: 700; }}
    .brand span {{ font-size: 13px; color: var(--muted); }}
    .top-links {{ display: flex; gap: 16px; align-items: center; }}
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
    .nav-btn:hover {{ background: rgba(255,255,255,0.08); border-color: var(--primary); }}
    .container {{ max-width: 1400px; margin: 32px auto; padding: 0 24px; }}
    
    /* Stats Bar */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }}
    .stat-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      position: relative;
      overflow: hidden;
    }}
    .stat-card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: var(--accent-color, var(--primary));
    }}
    .stat-num {{ font-size: 28px; font-weight: 800; color: #fff; font-family: 'JetBrains Mono', monospace; }}
    .stat-label {{ font-size: 13px; color: var(--muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}

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
      color: var(--primary);
      border-bottom-color: var(--primary);
      background: rgba(99, 102, 241, 0.05);
    }}
    .tab-pane {{ display: none; }}
    .tab-pane.active {{ display: block; }}

    /* Cards & Panels */
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
      margin-bottom: 16px;
    }}
    .panel-title {{ font-size: 18px; font-weight: 700; }}
    .panel-subtitle {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}

    /* Query & Inputs */
    .form-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }}
    .form-group {{ flex: 1; min-width: 260px; display: flex; flex-direction: column; gap: 8px; }}
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
    input:focus, select:focus, textarea:focus {{ border-color: var(--primary); }}
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
      background: linear-gradient(135deg, var(--primary), var(--primary-hover));
      color: #fff;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
    }}
    .btn-primary:hover {{ opacity: 0.95; transform: translateY(-1px); }}
    .btn-secondary {{
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: var(--text);
    }}
    .btn-secondary:hover {{ background: rgba(255,255,255,0.06); }}

    /* Contrast Box */
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
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .contrast-col.baseline {{ border-top: 4px solid var(--muted); }}
    .contrast-col.hindsight {{ border-top: 4px solid var(--success); }}
    .contrast-badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .contrast-badge.baseline {{ background: rgba(148, 163, 184, 0.15); color: #cbd5e1; }}
    .contrast-badge.hindsight {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}

    /* Badges & Tags */
    .badge {{
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .badge-ranking {{ background: rgba(6, 182, 212, 0.15); color: var(--cyan); border: 1px solid rgba(6, 182, 212, 0.3); }}
    .badge-optimization {{ background: rgba(99, 102, 241, 0.15); color: var(--primary); border: 1px solid rgba(99, 102, 241, 0.3); }}
    .badge-competitor {{ background: rgba(245, 158, 11, 0.15); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.3); }}
    .badge-outcome {{ background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }}

    /* Tables */
    .table-container {{ overflow-x: auto; margin-top: 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
    th {{ background: #070c18; padding: 12px; color: var(--muted); font-size: 11px; text-transform: uppercase; border-bottom: 1px solid var(--border); }}
    td {{ padding: 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    tr:hover td {{ background: rgba(255,255,255,0.02); }}
    .mono {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; }}

    /* Memory Card */
    .memory-card {{
      background: #080d1a;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .memory-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--muted); }}
    .memory-content {{ font-size: 14px; line-height: 1.5; color: #e2e8f0; }}
    .memory-why {{ font-size: 12px; color: var(--cyan); background: rgba(6, 182, 212, 0.08); padding: 6px 10px; border-radius: 6px; border-left: 3px solid var(--cyan); }}

    /* Alert Banner */
    .alert-banner {{
      background: rgba(99, 102, 241, 0.1);
      border: 1px solid rgba(99, 102, 241, 0.3);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .alert-text {{ font-size: 14px; color: #c7d2fe; }}
    .alert-text strong {{ color: #fff; }}

    /* Code Blocks */
    pre {{ background: #050811; padding: 14px; border-radius: 8px; border: 1px solid var(--border); overflow-x: auto; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #a5f3fc; }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="logo-badge">H</div>
      <div>
        <h1>Hindsight Memory Studio</h1>
        <span>Persistent Institutional SEO Intelligence Layer</span>
      </div>
    </div>
    <div class="top-links">
      <a href="/learning-loop" class="nav-btn" style="border-color: var(--cyan); color: #a5f3fc;">🔄 Learning Loop</a>
      <a href="/analyzer" class="nav-btn">Baseline Analyzer</a>
      <a href="/llm-analysis" class="nav-btn">LLM Reasoner</a>
      <button onclick="syncDatabase()" class="nav-btn" style="border-color: var(--primary); color: #a5b4fc;">⚡ Re-Sync Memory</button>
    </div>
  </header>

  <div class="container">
    <!-- Top Alert Banner -->
    <div class="alert-banner">
      <div class="alert-text">
        <strong>Hindsight is CENTRAL to RankMind:</strong> The agent does not simply run static analyzers. It retains ranking milestones, optimization experiments, competitor counter-moves, and causal attributions to provide empirical context-aware recommendations over time.
      </div>
      <button onclick="runComparisonDemo()" class="btn btn-primary" style="white-space: nowrap;">
        ▶ Run Memory vs Baseline Demo
      </button>
    </div>

    <!-- Stats Bar -->
    <div class="stats-grid">
      <div class="stat-card" style="--accent-color: var(--purple);">
        <div class="stat-num">{total_mems}</div>
        <div class="stat-label">Total Memories Stored</div>
      </div>
      <div class="stat-card" style="--accent-color: var(--cyan);">
        <div class="stat-num">{ranking_mems}</div>
        <div class="stat-label">Ranking History</div>
      </div>
      <div class="stat-card" style="--accent-color: var(--primary);">
        <div class="stat-num">{opt_mems}</div>
        <div class="stat-label">Optimization History</div>
      </div>
      <div class="stat-card" style="--accent-color: var(--warning);">
        <div class="stat-num">{comp_mems}</div>
        <div class="stat-label">Competitor History</div>
      </div>
      <div class="stat-card" style="--accent-color: var(--success);">
        <div class="stat-num">{out_mems}</div>
        <div class="stat-label">Outcome History</div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('tab-compare')">⚖️ Baseline vs Hindsight Contrast</button>
      <button class="tab-btn" onclick="switchTab('tab-quality')">🛡️ Event-Quality Gatekeeper (REMEMBER vs IGNORE)</button>
      <button class="tab-btn" onclick="switchTab('tab-recall')">🔍 Query Recall Inspector</button>
      <button class="tab-btn" onclick="switchTab('tab-memories')">🧠 Memory Bank Explorer</button>
      <button class="tab-btn" onclick="switchTab('tab-logs')">📋 Developer Audit Logs</button>
      <button class="tab-btn" onclick="switchTab('tab-retain')">➕ Retain New Event</button>
    </div>

    <!-- TAB 1B: EVENT-QUALITY & RETENTION DECISION GATEKEEPER -->
    <div id="tab-quality" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">🛡️ Event-Processing & Memory-Quality Layer</div>
            <div class="panel-subtitle">Evaluates raw SEO events: filters out low-signal noise, suppresses meaningless duplicates, normalizes context, and enforces correlational truth discipline (REMEMBER vs DO NOT REMEMBER).</div>
          </div>
        </div>

        <!-- Preset Buttons -->
        <div style="margin-bottom: 20px; display: flex; gap: 8px; flex-wrap: wrap;">
          <button type="button" class="btn btn-secondary" onclick="loadEventPreset('ranking_surge')">📈 Significant Rank Surge (+5)</button>
          <button type="button" class="btn btn-secondary" onclick="loadEventPreset('tier_transition')">🏆 Top 3 Tier Milestone (#14 -> #3)</button>
          <button type="button" class="btn btn-secondary" onclick="loadEventPreset('ranking_noise')">💤 Micro-Fluctuation Noise (#15 -> #14)</button>
          <button type="button" class="btn btn-secondary" onclick="loadEventPreset('important_optimization')">⚡ Important Optimization (Schema)</button>
          <button type="button" class="btn btn-secondary" onclick="loadEventPreset('trivial_typo')">🧹 Trivial Typo (Cosmetic Edit)</button>
          <button type="button" class="btn btn-secondary" onclick="loadEventPreset('correlational_outcome')">📊 Empirical Outcome (Correlational)</button>
        </div>

        <form id="qualityEventForm" onsubmit="evaluateEventQuality(event)">
          <div class="form-row">
            <div class="form-group">
              <label>Event Type</label>
              <select id="eventQualityType" required>
                <option value="ranking_change">ranking_change (Position movement)</option>
                <option value="optimization_performed">optimization_performed (SEO action)</option>
                <option value="outcome_observed">outcome_observed (Correlational result)</option>
                <option value="competitor_change">competitor_change (Rival actions)</option>
                <option value="recommendation_decision">recommendation_decision (Accepted/Rejected)</option>
                <option value="user_feedback">user_feedback (User input)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Website Domain</label>
              <input type="text" id="eventQualityWebsite" value="learnpythonhub.io" required>
            </div>
            <div class="form-group">
              <label>Target Keyword</label>
              <input type="text" id="eventQualityKeyword" value="best python courses for beginners" required>
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 16px;">
            <label>Event Details (JSON)</label>
            <textarea id="eventQualityDetails" rows="4" style="font-family: 'JetBrains Mono'; font-size: 13px;" required></textarea>
          </div>

          <button type="submit" class="btn btn-primary" id="btnEvaluateEvent">Evaluate & Process Event</button>
        </form>

        <div id="qualityEvaluationArea" style="margin-top: 24px;"></div>

        <!-- Decision Log Table -->
        <div style="margin-top: 32px; border-top: 1px solid var(--border); padding-top: 24px;">
          <div class="panel-header">
            <div>
              <div class="panel-title" style="font-size: 16px;">📋 Recent Memory-Quality Decisions</div>
              <div class="panel-subtitle">Developer-visible log showing why events were remembered or suppressed.</div>
            </div>
            <button type="button" onclick="loadDecisionsTable()" class="btn btn-secondary">Refresh Decisions</button>
          </div>
          <div id="decisionsTableArea"></div>
        </div>
      </div>
    </div>

    <!-- TAB 1: SIDE-BY-SIDE CONTRAST -->
    <div id="tab-compare" class="tab-pane active">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Side-by-Side Demonstration: Baseline vs Hindsight Memory</div>
            <div class="panel-subtitle">Demonstrates that the same query produces a vastly superior, context-aware strategy when historical memory is recalled.</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group" style="flex: 2;">
            <label>Search Query / Target Keyword</label>
            <input type="text" id="compareQuery" value="best python courses for beginners">
          </div>
          <div class="form-group" style="flex: 1;">
            <label>Target Domain (Optional)</label>
            <input type="text" id="compareDomain" value="learnpythonhub.io">
          </div>
          <div class="form-group" style="flex: 0 0 160px; justify-content: flex-end;">
            <button onclick="runComparisonDemo()" class="btn btn-primary" id="btnCompare">Compare Strategies</button>
          </div>
        </div>

        <div id="compareResultsArea">
          <!-- Populated by JS -->
          <div style="text-align: center; padding: 40px; color: var(--muted);">
            Click <strong>"Compare Strategies"</strong> or use the top demo button to view the side-by-side contrast.
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: QUERY RECALL INSPECTOR -->
    <div id="tab-recall" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Query Recall Inspector</div>
            <div class="panel-subtitle">Inspect exactly what memories Hindsight recalls, their relevance scores, and why each was recalled.</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group" style="flex: 2;">
            <label>Target SEO Query</label>
            <input type="text" id="recallQuery" value="best python courses for beginners">
          </div>
          <div class="form-group" style="flex: 1;">
            <label>Target Domain (Optional)</label>
            <input type="text" id="recallDomain" value="learnpythonhub.io">
          </div>
          <div class="form-group" style="flex: 0 0 120px;">
            <label>Max Memories</label>
            <select id="recallMax">
              <option value="4">4</option>
              <option value="6" selected>6</option>
              <option value="10">10</option>
            </select>
          </div>
          <div class="form-group" style="flex: 0 0 140px; justify-content: flex-end;">
            <button onclick="runRecallQuery()" class="btn btn-primary" id="btnRecall">Recall Memories</button>
          </div>
        </div>

        <div id="recallResultsArea">
          <div style="text-align: center; padding: 40px; color: var(--muted);">
            Enter a query to inspect relevant memories.
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: MEMORY BANK EXPLORER -->
    <div id="tab-memories" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Memory Bank Explorer</div>
            <div class="panel-subtitle">Browse all persisted memories across the 4 core categories.</div>
          </div>
          <div style="display: flex; gap: 8px;">
            <select id="filterCategory" onchange="loadMemories()">
              <option value="">All Categories</option>
              <option value="ranking_history">Ranking History</option>
              <option value="optimization_history">Optimization History</option>
              <option value="competitor_history">Competitor History</option>
              <option value="outcome_history">Outcome History</option>
            </select>
            <button onclick="loadMemories()" class="btn btn-secondary">Refresh</button>
          </div>
        </div>

        <div id="memoriesTableArea">
          <div style="text-align: center; padding: 30px; color: var(--muted);">Loading memories...</div>
        </div>
      </div>
    </div>

    <!-- TAB 4: DEVELOPER AUDIT LOGS -->
    <div id="tab-logs" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Developer Audit Logs</div>
            <div class="panel-subtitle">Detailed trail of: what was retained, what was recalled, and why it was relevant.</div>
          </div>
          <div style="display: flex; gap: 8px;">
            <select id="logTypeFilter" onchange="loadLogs()">
              <option value="all">All Logs</option>
              <option value="recall">Recall Logs Only</option>
              <option value="retain">Retention Logs Only</option>
            </select>
            <button onclick="loadLogs()" class="btn btn-secondary">Refresh Logs</button>
          </div>
        </div>

        <div id="logsArea">
          <div style="text-align: center; padding: 30px; color: var(--muted);">Loading audit logs...</div>
        </div>
      </div>
    </div>

    <!-- TAB 5: RETAIN NEW EVENT -->
    <div id="tab-retain" class="tab-pane">
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Retain New Event into Hindsight</div>
            <div class="panel-subtitle">Complete the memory loop: record a new ranking shift, optimization action, competitor move, or outcome attribution.</div>
          </div>
        </div>

        <form id="retainForm" onsubmit="submitRetain(event)">
          <div class="form-row">
            <div class="form-group">
              <label>Memory Category</label>
              <select id="retainCategory" required>
                <option value="ranking_history">1. RANKING HISTORY</option>
                <option value="optimization_history">2. OPTIMIZATION HISTORY</option>
                <option value="competitor_history">3. COMPETITOR HISTORY</option>
                <option value="outcome_history" selected>4. OUTCOME HISTORY (Causal Attribution)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Target Keyword</label>
              <input type="text" id="retainKeyword" placeholder="e.g. best python courses for beginners" required>
            </div>
            <div class="form-group">
              <label>Target Domain / Competitor</label>
              <input type="text" id="retainDomain" placeholder="e.g. learnpythonhub.io" required>
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 16px;">
            <label>Memory Content / Fact Description</label>
            <textarea id="retainContent" rows="4" placeholder="Detailed factual description of the event, ranking delta, optimization reason, or causal outcome..." required></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Tags (Comma-separated)</label>
              <input type="text" id="retainTags" placeholder="e.g. outcome, course-schema, video-preview">
            </div>
            <div class="form-group">
              <label>JSON Metadata (Optional)</label>
              <input type="text" id="retainMetadata" value='{{"rank_before": 4, "rank_after": 2, "delta": 2}}'>
            </div>
          </div>

          <button type="submit" class="btn btn-primary" id="btnSubmitRetain">Retain into Hindsight</button>
          <span id="retainStatus" style="margin-left: 16px; font-size: 13px;"></span>
        </form>
      </div>
    </div>

  </div>

  <script>
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      event.currentTarget.classList.add('active');
      document.getElementById(tabId).classList.add('active');

      if (tabId === 'tab-memories') loadMemories();
      if (tabId === 'tab-logs') loadLogs();
      if (tabId === 'tab-quality') loadDecisionsTable();
    }}

    async function syncDatabase() {{
      try {{
        const res = await fetch('/api/v1/hindsight/sync', {{ method: 'POST' }});
        const data = await res.json();
        alert('Database sync successful! Total memories: ' + data.total_memories);
        location.reload();
      }} catch (err) {{
        alert('Sync error: ' + err.message);
      }}
    }}

    async function runComparisonDemo() {{
      const query = document.getElementById('compareQuery').value;
      const domain = document.getElementById('compareDomain').value;
      const btn = document.getElementById('btnCompare');
      const area = document.getElementById('compareResultsArea');

      btn.disabled = true;
      btn.innerText = 'Analyzing...';
      area.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--cyan);">Running Baseline & Hindsight Memory Reasoning...</div>';

      try {{
        const res = await fetch(`/api/v1/hindsight/compare?query=${{encodeURIComponent(query)}}&domain=${{encodeURIComponent(domain)}}`);
        const data = await res.json();

        let baseRecsHtml = '';
        data.baseline_stateless.top_recommendations.forEach(r => {{
          baseRecsHtml += `
            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 8px;">
              <div style="font-weight: 700; color: #e2e8f0; font-size: 13px;">[${{r.category.toUpperCase()}}] ${{r.title}}</div>
              <div style="font-size: 12px; color: var(--muted); margin-top: 4px;">${{r.reasoning}}</div>
            </div>`;
        }});

        let memRecsHtml = '';
        data.hindsight_augmented.context_aware_recommendations.forEach((r, idx) => {{
          const why = r.why_am_i_seeing_this || {{}};
          const whyHtml = why.recalled_memory ? `
            <div style="margin-top: 10px; background: rgba(6, 182, 212, 0.06); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 6px; padding: 10px;">
              <div style="font-weight: 700; font-size: 11px; text-transform: uppercase; color: var(--cyan); margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                <span>💡 Why am I seeing this recommendation?</span>
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;"><strong>Current Observation:</strong> <span style="color: #f1f5f9;">${{why.current_observation || '-'}}</span></div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;"><strong>Recalled Memory:</strong> <span style="color: #a5f3fc;">${{why.recalled_memory || '-'}}</span></div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;"><strong>Connection:</strong> <span style="color: #cbd5e1;">${{why.connection_between_them || '-'}}</span></div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;"><strong>Recommendation:</strong> <span style="color: #34d399;">${{why.recommendation || r.title}}</span></div>
              <div style="font-size: 10px; color: var(--warning); margin-top: 4px; font-style: italic;">⚖️ ${{why.observational_caveat || 'Historical relationship is observational and not guaranteed.'}}</div>
            </div>` : '';

          memRecsHtml += `
            <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
              <div style="font-weight: 700; color: #34d399; font-size: 13px;">[${{r.category.toUpperCase()}}] ${{r.title}}</div>
              <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">${{r.reasoning}}</div>
              <div style="font-size: 11px; color: var(--cyan); margin-top: 4px;">🎯 Expected: ${{r.expected_direction_of_improvement}}</div>
              ${{whyHtml}}
            </div>`;
        }});

        let suppressedHtml = '';
        data.hindsight_augmented.suppressed_tactics.forEach(s => {{
          suppressedHtml += `<li style="margin-bottom: 6px; color: #f87171; font-size: 12px;">🚫 ${{s}}</li>`;
        }});

        let recalledSampleHtml = '';
        data.hindsight_augmented.recalled_memories_sample.forEach(m => {{
          recalledSampleHtml += `
            <div style="background: #050811; border-left: 3px solid var(--primary); padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-size: 11px;">
              <div style="color: var(--muted);"><span class="badge badge-${{m.category.replace('_history', '')}}">${{m.category.toUpperCase()}}</span> (Relevance: ${{m.relevance_score}})</div>
              <div style="color: #e2e8f0; margin-top: 2px;">${{m.content}}</div>
              <div style="color: var(--cyan); margin-top: 2px;">💡 Why Relevant: ${{m.why_relevant}}</div>
            </div>`;
        }});

        area.innerHTML = `
          <!-- Summary Banner -->
          <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
            <div style="font-weight: 800; font-size: 15px; color: #fff; margin-bottom: 6px;">🧠 Strategic Contrast Summary</div>
            <div style="font-size: 13px; color: #e2e8f0; line-height: 1.5;">${{data.strategic_contrast_summary}}</div>
          </div>

          <!-- Side by Side Grid -->
          <div class="contrast-grid">
            <!-- Left: Baseline -->
            <div class="contrast-col baseline">
              <div>
                <span class="contrast-badge baseline">Stateless Baseline (No Memory)</span>
                <h3 style="font-size: 16px; font-weight: 700; margin-top: 8px;">Generic Heuristic Advice</h3>
                <p style="font-size: 12px; color: var(--muted); margin-top: 4px;">${{data.baseline_stateless.inherent_limitation}}</p>
              </div>

              <div>
                <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--muted); margin-bottom: 8px;">Diagnosis:</div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.5; background: rgba(255,255,255,0.02); padding: 10px; border-radius: 6px;">${{data.baseline_stateless.seo_diagnosis}}</div>
              </div>

              <div>
                <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--muted); margin-bottom: 8px;">Baseline Recommendations:</div>
                ${{baseRecsHtml}}
              </div>
            </div>

            <!-- Right: Hindsight Memory -->
            <div class="contrast-col hindsight">
              <div>
                <span class="contrast-badge hindsight">Hindsight Memory-Augmented</span>
                <h3 style="font-size: 16px; font-weight: 700; margin-top: 8px; color: #34d399;">Context-Aware Strategy</h3>
                <p style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Recalled ${{data.hindsight_augmented.recalled_memories_count}} verified historical events to guide decision making.</p>
              </div>

              <!-- Recalled Evidence Sample -->
              <div>
                <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--cyan); margin-bottom: 8px;">Recalled Historical Evidence:</div>
                ${{recalledSampleHtml}}
              </div>

              <!-- Disproven Tactics Suppressed -->
              <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px;">
                <div style="font-size: 12px; font-weight: 700; color: #fca5a5; text-transform: uppercase; margin-bottom: 6px;">Tactics Explicitly Suppressed (Empirically Failed):</div>
                <ul style="padding-left: 16px; margin: 0;">${{suppressedHtml}}</ul>
              </div>

              <!-- Context-Aware Recommendations -->
              <div>
                <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #34d399; margin-bottom: 8px;">Context-Aware Prescriptions:</div>
                ${{memRecsHtml}}
              </div>
            </div>
          </div>
        `;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 20px;">Error running comparison: ' + err.message + '</div>';
      }} finally {{
        btn.disabled = false;
        btn.innerText = 'Compare Strategies';
      }}
    }}

    async function runRecallQuery() {{
      const query = document.getElementById('recallQuery').value;
      const domain = document.getElementById('recallDomain').value;
      const maxMems = document.getElementById('recallMax').value;
      const btn = document.getElementById('btnRecall');
      const area = document.getElementById('recallResultsArea');

      btn.disabled = true;
      btn.innerText = 'Recalling...';

      try {{
        const res = await fetch(`/api/v1/hindsight/recall?query=${{encodeURIComponent(query)}}&domain=${{encodeURIComponent(domain)}}&max_memories=${{maxMems}}`);
        const data = await res.json();

        if (data.memories.length === 0) {{
          area.innerHTML = '<div style="padding: 20px; color: var(--muted);">No matching memories found for this query.</div>';
          return;
        }}

        let html = `
          <div style="margin-bottom: 16px; font-size: 13px; color: var(--muted);">
            Recalled <strong>${{data.memories.length}}</strong> memories for query: "<em>${{data.query}}</em>"
          </div>`;

        data.memories.forEach(m => {{
          const catClass = m.category.replace('_history', '');
          html += `
            <div class="memory-card">
              <div class="memory-meta">
                <div style="display: flex; gap: 8px; align-items: center;">
                  <span class="badge badge-${{catClass}}">${{m.category.toUpperCase()}}</span>
                  <span class="mono">${{m.target_domain || 'General'}}</span>
                  <span style="color: var(--muted);">•</span>
                  <span>${{m.timestamp.substring(0, 10)}}</span>
                </div>
                <div style="font-weight: 700; color: #34d399; font-family: 'JetBrains Mono';">
                  Relevance: ${{m.relevance_score}}
                </div>
              </div>
              <div class="memory-content">${{m.content}}</div>
              <div class="memory-why">🎯 Why Relevant: ${{m.why_relevant}}</div>
            </div>`;
        }});

        area.innerHTML = html;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 20px;">Error: ' + err.message + '</div>';
      }} finally {{
        btn.disabled = false;
        btn.innerText = 'Recall Memories';
      }}
    }}

    async function loadMemories() {{
      const cat = document.getElementById('filterCategory').value;
      const area = document.getElementById('memoriesTableArea');
      area.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--muted);">Loading memories...</div>';

      try {{
        const url = cat ? `/api/v1/hindsight/memories?category=${{encodeURIComponent(cat)}}` : '/api/v1/hindsight/memories';
        const res = await fetch(url);
        const data = await res.json();

        let rowsHtml = '';
        data.memories.forEach(m => {{
          const catClass = m.category.replace('_history', '');
          rowsHtml += `
            <tr>
              <td><span class="badge badge-${{catClass}}">${{m.category.toUpperCase()}}</span></td>
              <td class="mono">${{m.timestamp.substring(0, 10)}}</td>
              <td class="mono" style="color: #a5f3fc;">${{m.target_domain || '-'}}</td>
              <td>${{m.target_keyword}}</td>
              <td style="line-height: 1.4;">${{m.content}}</td>
            </tr>`;
        }});

        area.innerHTML = `
          <div style="margin-bottom: 12px; font-size: 13px; color: var(--muted);">Total Memories: <strong>${{data.total_memories}}</strong></div>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Date</th>
                  <th>Domain</th>
                  <th>Keyword</th>
                  <th>Memory Fact Content</th>
                </tr>
              </thead>
              <tbody>${{rowsHtml}}</tbody>
            </table>
          </div>`;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 20px;">Error: ' + err.message + '</div>';
      }}
    }}

    async function loadLogs() {{
      const filter = document.getElementById('logTypeFilter').value;
      const area = document.getElementById('logsArea');
      area.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--muted);">Loading audit logs...</div>';

      try {{
        const res = await fetch(`/api/v1/hindsight/logs?log_type=${{filter}}`);
        const data = await res.json();

        let html = '';

        if (data.recall_logs.length > 0) {{
          html += '<h3 style="font-size: 15px; margin-bottom: 12px; color: var(--cyan);">🔍 Recent Recall Events (Audit Log)</h3>';
          let recallRows = '';
          data.recall_logs.forEach(l => {{
            recallRows += `
              <tr>
                <td class="mono">${{l.timestamp.substring(11, 19)}}</td>
                <td><strong>${{l.query}}</strong></td>
                <td class="mono">${{l.target_domain || '-'}}</td>
                <td><span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399;">${{l.recalled_count}} recalled</span></td>
                <td style="color: var(--cyan);">${{l.why_relevant_summary}}</td>
              </tr>`;
          }});
          html += `
            <div class="table-container" style="margin-bottom: 24px;">
              <table>
                <thead>
                  <tr><th>Time</th><th>Query</th><th>Domain</th><th>Count</th><th>Why Relevant Summary</th></tr>
                </thead>
                <tbody>${{recallRows}}</tbody>
              </table>
            </div>`;
        }}

        if (data.retention_logs.length > 0) {{
          html += '<h3 style="font-size: 15px; margin-bottom: 12px; color: var(--primary);">💾 Recent Retention Events (Audit Log)</h3>';
          let retRows = '';
          data.retention_logs.forEach(l => {{
            const catClass = l.category.replace('_history', '');
            retRows += `
              <tr>
                <td class="mono">${{l.timestamp.substring(11, 19)}}</td>
                <td><span class="badge badge-${{catClass}}">${{l.category.toUpperCase()}}</span></td>
                <td class="mono">${{l.target_domain || '-'}}</td>
                <td>${{l.target_keyword}}</td>
                <td>${{l.content_snippet}}</td>
              </tr>`;
          }});
          html += `
            <div class="table-container">
              <table>
                <thead>
                  <tr><th>Time</th><th>Category</th><th>Domain</th><th>Keyword</th><th>Snippet</th></tr>
                </thead>
                <tbody>${{retRows}}</tbody>
              </table>
            </div>`;
        }}

        area.innerHTML = html;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 20px;">Error: ' + err.message + '</div>';
      }}
    }}

    async function submitRetain(e) {{
      e.preventDefault();
      const statusSpan = document.getElementById('retainStatus');
      const btn = document.getElementById('btnSubmitRetain');

      btn.disabled = true;
      btn.innerText = 'Retaining...';
      statusSpan.innerText = '';

      try {{
        let metadata = {{}};
        try {{
          metadata = JSON.parse(document.getElementById('retainMetadata').value);
        }} catch (_) {{}}

        const tags = document.getElementById('retainTags').value.split(',').map(t => t.trim()).filter(Boolean);

        const payload = {{
          category: document.getElementById('retainCategory').value,
          content: document.getElementById('retainContent').value,
          target_keyword: document.getElementById('retainKeyword').value,
          target_domain: document.getElementById('retainDomain').value,
          metadata: metadata,
          tags: tags,
        }};

        const res = await fetch('/api/v1/hindsight/retain', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});

        if (res.ok) {{
          const mem = await res.json();
          statusSpan.innerHTML = '<span style="color: var(--success);">✓ Successfully retained memory ID: ' + mem.id + '</span>';
          document.getElementById('retainForm').reset();
        }} else {{
          const err = await res.json();
          statusSpan.innerHTML = '<span style="color: var(--danger);">✗ Retention failed: ' + err.detail + '</span>';
        }}
      }} catch (err) {{
        statusSpan.innerHTML = '<span style="color: var(--danger);">✗ Network error: ' + err.message + '</span>';
      }} finally {{
        btn.disabled = false;
        btn.innerText = 'Retain into Hindsight';
      }}
    }}

    async function evaluateEventQuality(e) {{
      e.preventDefault();
      const btn = document.getElementById('btnEvaluateEvent');
      const area = document.getElementById('qualityEvaluationArea');

      btn.disabled = true;
      btn.innerText = 'Evaluating...';

      try {{
        let details = {{}};
        try {{
          details = JSON.parse(document.getElementById('eventQualityDetails').value);
        }} catch (err) {{
          alert('Invalid JSON in event details: ' + err.message);
          btn.disabled = false;
          btn.innerText = 'Evaluate & Process Event';
          return;
        }}

        const payload = {{
          event_type: document.getElementById('eventQualityType').value,
          website: document.getElementById('eventQualityWebsite').value,
          keyword: document.getElementById('eventQualityKeyword').value,
          details: details
        }};

        const res = await fetch('/api/v1/hindsight/process-event', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});

        const data = await res.json();
        const isRemember = data.decision === 'REMEMBER';
        const badgeColor = isRemember ? 'var(--success)' : 'var(--danger)';
        const badgeBg = isRemember ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)';

        let normHtml = '';
        if (data.normalized_memory) {{
          const nm = data.normalized_memory;
          normHtml = `
            <div style="margin-top: 16px; background: #050811; border: 1px solid var(--border); border-radius: 8px; padding: 14px;">
              <div style="font-size: 11px; text-transform: uppercase; color: var(--cyan); font-weight: 700; margin-bottom: 6px;">Normalized Context Stored into Hindsight:</div>
              <div style="font-size: 13px; color: #e2e8f0; margin-bottom: 4px;"><strong>Action:</strong> ${{nm.action}}</div>
              <div style="font-size: 13px; color: #34d399; margin-bottom: 4px;"><strong>Result:</strong> ${{nm.result}}</div>
              <div style="font-size: 12px; color: var(--muted); margin-bottom: 4px;"><strong>Context:</strong> ${{nm.context}}</div>
              <div style="font-size: 11px; color: var(--warning); margin-top: 6px;">⚖️ ${{nm.language_discipline_note}}</div>
            </div>`;
        }}

        area.innerHTML = `
          <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid var(--border); border-left: 4px solid ${{badgeColor}}; border-radius: 10px; padding: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <span style="background: ${{badgeBg}}; color: ${{badgeColor}}; padding: 6px 12px; border-radius: 6px; font-weight: 800; font-size: 13px;">
                GATEKEEPER DECISION: ${{data.decision}}
              </span>
              <span class="mono" style="font-size: 12px; color: var(--muted);">Fingerprint: ${{data.deduplication_fingerprint}}</span>
            </div>
            <div style="font-size: 14px; color: #f8fafc; line-height: 1.5; margin-bottom: 8px;">
              <strong>Evaluation Reason:</strong> ${{data.reason}}
            </div>
            <div style="font-size: 12px; color: var(--cyan);">
              Importance Score: <strong>${{(data.importance_score * 100).toFixed(0)}}%</strong>
            </div>
            ${{normHtml}}
          </div>
        `;

        loadDecisionsTable();
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 16px;">Error processing event: ' + err.message + '</div>';
      }} finally {{
        btn.disabled = false;
        btn.innerText = 'Evaluate & Process Event';
      }}
    }}

    async function loadDecisionsTable() {{
      const area = document.getElementById('decisionsTableArea');
      area.innerHTML = '<div style="padding: 16px; color: var(--muted);">Loading decisions...</div>';

      try {{
        const res = await fetch('/api/v1/hindsight/decisions?limit=25');
        const list = await res.json();

        if (list.length === 0) {{
          area.innerHTML = '<div style="padding: 16px; color: var(--muted);">No decision logs recorded yet.</div>';
          return;
        }}

        let rows = '';
        list.forEach(d => {{
          const isRem = d.decision === 'REMEMBER';
          const badgeClass = isRem ? 'badge-outcome' : 'badge-competitor';
          rows += `
            <tr>
              <td class="mono">${{d.timestamp.substring(11, 19)}}</td>
              <td><span class="badge ${{badgeClass}}">${{d.decision}}</span></td>
              <td class="mono">${{d.event_type}}</td>
              <td class="mono" style="color: #a5f3fc;">${{d.website}}</td>
              <td style="font-size: 12px; line-height: 1.4;">${{d.reason}}</td>
              <td class="mono">${{(d.importance_score * 100).toFixed(0)}}%</td>
              <td class="mono" style="color: var(--muted);">${{d.fingerprint}}</td>
            </tr>`;
        }});

        area.innerHTML = `
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Decision</th>
                  <th>Event Type</th>
                  <th>Website</th>
                  <th>Gatekeeper Reason</th>
                  <th>Score</th>
                  <th>Fingerprint</th>
                </tr>
              </thead>
              <tbody>${{rows}}</tbody>
            </table>
          </div>`;
      }} catch (err) {{
        area.innerHTML = '<div style="color: var(--danger); padding: 16px;">Error: ' + err.message + '</div>';
      }}
    }}

    function loadEventPreset(presetKey) {{
      const typeInput = document.getElementById('eventQualityType');
      const webInput = document.getElementById('eventQualityWebsite');
      const kwInput = document.getElementById('eventQualityKeyword');
      const detInput = document.getElementById('eventQualityDetails');

      if (presetKey === 'ranking_surge') {{
        typeInput.value = 'ranking_change';
        webInput.value = 'learnpythonhub.io';
        kwInput.value = 'best python courses for beginners';
        detInput.value = JSON.stringify({{
          position: 3,
          previous_position: 8,
          delta: 5
        }}, null, 2);
      }} else if (presetKey === 'tier_transition') {{
        typeInput.value = 'ranking_change';
        webInput.value = 'freshlearner.org';
        kwInput.value = 'python data science';
        detInput.value = JSON.stringify({{
          position: 3,
          previous_position: 14,
          delta: 11
        }}, null, 2);
      }} else if (presetKey === 'ranking_noise') {{
        typeInput.value = 'ranking_change';
        webInput.value = 'learnpythonhub.io';
        kwInput.value = 'best python courses for beginners';
        detInput.value = JSON.stringify({{
          position: 14,
          previous_position: 15,
          delta: 1
        }}, null, 2);
      }} else if (presetKey === 'important_optimization') {{
        typeInput.value = 'optimization_performed';
        webInput.value = 'freshlearner.org';
        kwInput.value = 'python data science';
        detInput.value = JSON.stringify({{
          optimization_type: 'structured_schema',
          description: 'Deployed Course & VideoObject JSON-LD structured schemas',
          reason: 'Qualify for Google Course Carousel rich card snippets',
          expected_effect: 'Anticipated +25% organic click-through rate'
        }}, null, 2);
      }} else if (presetKey === 'trivial_typo') {{
        typeInput.value = 'optimization_performed';
        webInput.value = 'freshlearner.org';
        kwInput.value = 'python data science';
        detInput.value = JSON.stringify({{
          optimization_type: 'typo_fix',
          description: 'Corrected minor spelling and punctuation typo in footer disclaimer',
          reason: 'Routine copy hygiene'
        }}, null, 2);
      }} else if (presetKey === 'correlational_outcome') {{
        typeInput.value = 'outcome_observed';
        webInput.value = 'freshlearner.org';
        kwInput.value = 'python data science';
        detInput.value = JSON.stringify({{
          optimization_title: 'Deployed Course JSON-LD schema',
          optimization_type: 'structured_schema',
          rank_before: 14,
          rank_after: 3,
          observed_result: 'Rank moved from #14 to #3 (+11 positions)',
          time_period_days: 21,
          confidence: 0.88,
          uncertainty_factors: ['External search core update occurred during evaluation window']
        }}, null, 2);
      }}
    }}

    // Initialize preset on load
    loadEventPreset('ranking_surge');

    // Auto-load comparison on page load
    window.onload = function() {{
      runComparisonDemo();
      loadDecisionsTable();
    }};
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html, status_code=200)
