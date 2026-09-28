from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from app.core.config import APP_NAME, API_V1_PREFIX, DEFAULT_FLAGSHIP_QUERY, DEFAULT_TARGET_DOMAIN
from app.models.schemas import (
    AuditReport,
    SERPSnapshot,
    OptimizationAction,
    MemoryNode,
    CompetitorDiff,
)
from app.services.hindsight_store import hindsight_store
from app.services.strategy_agent import strategy_agent
from app.services.attribution_engine import attribution_engine
from app.services.diff_engine import diff_engine
from app.api.entity_routes import router as entity_router
from app.api.debug_routes import router as debug_router
from app.api.analyzer_routes import router as analyzer_router
from app.api.llm_routes import router as llm_router
from app.api.hindsight_routes import router as hindsight_router
from app.api.learning_loop_routes import router as learning_loop_router
from app.api.intelligence_routes import router as intelligence_router
from app.services.hindsight.memory_manager import hindsight_memory_manager
from app.services.hindsight.client import hindsight_client

app = FastAPI(
    title=APP_NAME,
    description="Empirical SEO & Search Intelligence Agent with Persistent Hindsight Memory",
    version="1.0.0",
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Hindsight memory if bank is empty
@app.on_event("startup")
async def startup_hindsight_sync():
    if len(hindsight_client.list_all_memories()) == 0:
        hindsight_memory_manager.sync_database_to_hindsight()

# Mount CRUD routes for all 8 entities
app.include_router(entity_router, prefix=API_V1_PREFIX)

# Mount developer inspection and debug routes
app.include_router(debug_router)

# Mount Baseline SEO Analyzer routes & testing UI
app.include_router(analyzer_router)

# Mount LLM SEO Reasoning Agent routes & test studio
app.include_router(llm_router)

# Mount Hindsight Persistent Memory routes & Developer Studio
app.include_router(hindsight_router)

# Mount Complete SEO Learning Loop routes & Cockpit
app.include_router(learning_loop_router)

# Mount General-Purpose Website Intelligence & Ranking routes
app.include_router(intelligence_router)


@app.get(f"{API_V1_PREFIX}/health")
async def health_check():
    return {
        "status": "healthy",
        "service": APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "memory_active": True,
    }


@app.get(f"{API_V1_PREFIX}/queries")
async def list_tracked_queries():
    return {
        "queries": [
            {
                "query": DEFAULT_FLAGSHIP_QUERY,
                "target_domain": DEFAULT_TARGET_DOMAIN,
                "category": "Technology Education",
                "cycles_recorded": 4,
            }
        ]
    }


@app.get(f"{API_V1_PREFIX}/audit", response_model=AuditReport)
async def get_audit_report(
    query: str = Query(DEFAULT_FLAGSHIP_QUERY),
    target_domain: str = Query(DEFAULT_TARGET_DOMAIN),
):
    try:
        report = strategy_agent.generate_audit_report(query=query, target_domain=target_domain)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_V1_PREFIX}/snapshots", response_model=List[SERPSnapshot])
async def get_snapshots(query: str = Query(DEFAULT_FLAGSHIP_QUERY)):
    return hindsight_store.get_snapshots(query)


@app.get(f"{API_V1_PREFIX}/attributions", response_model=List[MemoryNode])
async def get_attributions(query: str = Query(DEFAULT_FLAGSHIP_QUERY)):
    return hindsight_store.get_memory_nodes(query)


@app.get(f"{API_V1_PREFIX}/diffs", response_model=List[CompetitorDiff])
async def get_diffs(query: str = Query(DEFAULT_FLAGSHIP_QUERY)):
    return hindsight_store.get_diffs(query)


@app.post(f"{API_V1_PREFIX}/actions", response_model=OptimizationAction)
async def log_action(action: OptimizationAction):
    if not action.id:
        action.id = f"act_{uuid.uuid4().hex[:8]}"
    if not action.timestamp:
        action.timestamp = datetime.now(timezone.utc).isoformat()
    hindsight_store.add_action(action)
    return action


@app.post(f"{API_V1_PREFIX}/reset-demo")
async def reset_demo_state():
    hindsight_store.reset_demo()
    return {"status": "success", "message": "Demo state reset to initial 4-cycle seed scenario"}
