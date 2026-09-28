import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.db.database import get_connection, DB_PATH
from app.models.hindsight_schemas import (
    MemoryCategory,
    HindsightMemoryItem,
    RetentionLogItem,
    RecallLogItem,
    RetentionDecisionLogItem,
)

# Configuration from environment
HINDSIGHT_API_URL = os.environ.get("HINDSIGHT_API_URL", "http://localhost:8888")
DEFAULT_BANK_ID = os.environ.get("HINDSIGHT_BANK_ID", "rankmind-seo")

# Ensure Hindsight tables exist in SQLite
HINDSIGHT_SQL = """
CREATE TABLE IF NOT EXISTS hindsight_memories (
    id TEXT PRIMARY KEY,
    bank_id TEXT NOT NULL,
    category TEXT NOT NULL,
    target_keyword TEXT NOT NULL,
    target_domain TEXT,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    tags TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_hm_bank ON hindsight_memories(bank_id);
CREATE INDEX IF NOT EXISTS idx_hm_keyword ON hindsight_memories(target_keyword);
CREATE INDEX IF NOT EXISTS idx_hm_category ON hindsight_memories(category);
CREATE INDEX IF NOT EXISTS idx_hm_domain ON hindsight_memories(target_domain);

CREATE TABLE IF NOT EXISTS hindsight_retain_logs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    bank_id TEXT NOT NULL,
    category TEXT NOT NULL,
    target_keyword TEXT NOT NULL,
    target_domain TEXT,
    content_snippet TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS hindsight_recall_logs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    bank_id TEXT NOT NULL,
    query TEXT NOT NULL,
    target_domain TEXT,
    recalled_count INTEGER NOT NULL,
    recalled_memory_ids TEXT NOT NULL DEFAULT '[]',
    why_relevant_summary TEXT NOT NULL
);
"""

# Initialize tables
with get_connection(DB_PATH) as _conn:
    _conn.executescript(HINDSIGHT_SQL)


class HindsightMemoryClient:
    """Persistent Hindsight memory client integrating official SDK syntax with resilient local storage.
    
    Adheres strictly to the official Hindsight API pattern:
    - retain(bank_id, content, metadata, tags, timestamp)
    - recall(bank_id, query, tags, budget, max_tokens)
    """

    def __init__(self, base_url: str = HINDSIGHT_API_URL, default_bank: str = DEFAULT_BANK_ID, db_path=DB_PATH):
        self.base_url = base_url
        self.default_bank = default_bank
        self.db_path = db_path
        self._official_client = None
        self._server_available = False
        try:
            import httpx
            from hindsight_client import Hindsight
            try:
                probe = httpx.get(f"{self.base_url}/health", timeout=0.15)
                if probe.status_code < 500:
                    self._server_available = True
                    self._official_client = Hindsight(base_url=self.base_url)
            except Exception:
                self._server_available = False
        except Exception:
            self._official_client = None
            self._server_available = False

    # =========================================================================
    # RETAIN (Save new experience into Hindsight memory)
    # =========================================================================

    def retain(
        self,
        category: MemoryCategory,
        content: str,
        target_keyword: str,
        target_domain: Optional[str] = None,
        bank_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> HindsightMemoryItem:
        """Retains an SEO event/fact into the Hindsight memory bank."""
        bank = bank_id or self.default_bank
        mem_id = f"mem_{category.value[:3]}_{uuid.uuid4().hex[:8]}"
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        meta = metadata or {}
        tag_list = tags or []
        if category.value not in tag_list:
            tag_list.append(category.value)
        if target_keyword not in tag_list:
            tag_list.append(target_keyword)

        # 1. Store in local persistent Hindsight store
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO hindsight_memories (id, bank_id, category, target_keyword, target_domain, content, timestamp, metadata, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mem_id,
                    bank,
                    category.value,
                    target_keyword.lower(),
                    target_domain.lower() if target_domain else None,
                    content,
                    ts,
                    json.dumps(meta),
                    json.dumps(tag_list),
                ),
            )

            # 2. Record developer retention audit log
            log_id = f"ret_log_{uuid.uuid4().hex[:8]}"
            conn.execute(
                """
                INSERT INTO hindsight_retain_logs (id, timestamp, bank_id, category, target_keyword, target_domain, content_snippet, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    ts,
                    bank,
                    category.value,
                    target_keyword.lower(),
                    target_domain.lower() if target_domain else None,
                    content[:140] + ("..." if len(content) > 140 else ""),
                    json.dumps(tag_list),
                ),
            )

        # 3. If official server is reachable, also dispatch retain to official Hindsight SDK
        if self._official_client:
            try:
                self._official_client.retain(
                    bank_id=bank,
                    content=content,
                    metadata={"keyword": target_keyword, "category": category.value, **{k: str(v) for k, v in meta.items()}},
                    tags=tag_list,
                )
            except Exception:
                # Local persistence remains the authority
                pass

        return HindsightMemoryItem(
            id=mem_id,
            bank_id=bank,
            category=category,
            content=content,
            target_keyword=target_keyword,
            target_domain=target_domain,
            timestamp=ts,
            metadata=meta,
            tags=tag_list,
        )

    # =========================================================================
    # RECALL (Multi-strategy relevant memory retrieval)
    # =========================================================================

    def recall(
        self,
        query: str,
        target_domain: Optional[str] = None,
        current_position: Optional[int] = None,
        target_deficiencies: Optional[List[str]] = None,
        bank_id: Optional[str] = None,
        categories: Optional[List[MemoryCategory]] = None,
        max_memories: int = 6,
        max_tokens: int = 4096,
    ) -> List[HindsightMemoryItem]:
        """Recalls relevant historical memories evaluated across all 8 dimensions:
        1. same website
        2. same keyword
        3. related keywords
        4. similar optimization
        5. previous ranking behavior
        6. competitor behavior
        7. previous outcomes
        8. previous user interactions
        """
        bank = bank_id or self.default_bank
        from app.services.hindsight.relevance_ranker import relevance_ranking_layer

        selected = relevance_ranking_layer.rank_and_select_memories(
            query=query,
            target_domain=target_domain,
            current_position=current_position,
            target_deficiencies=target_deficiencies,
            categories=categories,
            bank_id=bank,
            max_memories=max_memories,
            max_tokens=max_tokens,
        )

        # Record recall audit log
        log_id = f"rec_log_{uuid.uuid4().hex[:8]}"
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO hindsight_recall_logs (id, timestamp, bank_id, query, target_domain, recalled_count, recalled_memory_ids, why_relevant_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    datetime.now(timezone.utc).isoformat(),
                    bank,
                    query,
                    target_domain,
                    len(selected),
                    json.dumps([m.id for m in selected]),
                    f"Recalled {len(selected)} relevant memories evaluated across 8 dimensions for query '{query}' and domain '{target_domain}'",
                ),
            )

        return selected

    # =========================================================================
    # AUDIT LOGGING INSPECTION
    # =========================================================================

    def list_retention_logs(self, limit: int = 50) -> List[RetentionLogItem]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM hindsight_retain_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [
                RetentionLogItem(
                    id=r["id"],
                    timestamp=r["timestamp"],
                    bank_id=r["bank_id"],
                    category=MemoryCategory(r["category"]),
                    target_keyword=r["target_keyword"],
                    target_domain=r["target_domain"],
                    content_snippet=r["content_snippet"],
                    tags=json.loads(r["tags"] or "[]"),
                )
                for r in rows
            ]

    def list_recall_logs(self, limit: int = 50) -> List[RecallLogItem]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM hindsight_recall_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [
                RecallLogItem(
                    id=r["id"],
                    timestamp=r["timestamp"],
                    bank_id=r["bank_id"],
                    query=r["query"],
                    target_domain=r["target_domain"],
                    recalled_count=r["recalled_count"],
                    recalled_memory_ids=json.loads(r["recalled_memory_ids"] or "[]"),
                    why_relevant_summary=r["why_relevant_summary"],
                )
                for r in rows
            ]

    def list_all_memories(self, category: Optional[MemoryCategory] = None) -> List[HindsightMemoryItem]:
        with get_connection(self.db_path) as conn:
            sql = "SELECT * FROM hindsight_memories WHERE 1=1"
            params = []
            if category:
                sql += " AND category = ?"
                params.append(category.value)
            sql += " ORDER BY timestamp DESC"
            rows = conn.execute(sql, params).fetchall()
            return [
                HindsightMemoryItem(
                    id=r["id"],
                    bank_id=r["bank_id"],
                    category=MemoryCategory(r["category"]),
                    content=r["content"],
                    target_keyword=r["target_keyword"],
                    target_domain=r["target_domain"],
                    timestamp=r["timestamp"],
                    metadata=json.loads(r["metadata"] or "{}"),
                    tags=json.loads(r["tags"] or "[]"),
                )
                for r in rows
            ]

    def list_retention_decisions(
        self, decision: Optional[str] = None, limit: int = 50
    ) -> List[RetentionDecisionLogItem]:
        with get_connection(self.db_path) as conn:
            sql = "SELECT * FROM hindsight_retention_decisions WHERE 1=1"
            params = []
            if decision:
                sql += " AND decision = ?"
                params.append(decision.upper())
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
            return [
                RetentionDecisionLogItem(
                    id=r["id"],
                    timestamp=r["timestamp"],
                    bank_id=r["bank_id"],
                    event_type=r["event_type"],
                    website=r["website"],
                    keyword=r["keyword"],
                    decision=r["decision"],
                    reason=r["reason"],
                    importance_score=r["importance_score"],
                    fingerprint=r["fingerprint"],
                    content_snippet=r["content_snippet"],
                    normalized_data=json.loads(r["normalized_data"] or "{}"),
                )
                for r in rows
            ]


hindsight_client = HindsightMemoryClient()
