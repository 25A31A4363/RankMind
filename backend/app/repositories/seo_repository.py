import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.db.database import get_connection, DB_PATH
from app.models.domain_schemas import (
    SearchQueryCreate,
    SearchQueryUpdate,
    SearchQueryResponse,
    WebsiteCreate,
    WebsiteUpdate,
    WebsiteResponse,
    RankingHistoryCreate,
    RankingHistoryResponse,
    SEOOptimizationCreate,
    SEOOptimizationUpdate,
    SEOOptimizationResponse,
    CompetitorHistoryCreate,
    CompetitorHistoryResponse,
    OutcomeCreate,
    OutcomeUpdate,
    OutcomeResponse,
    ContentCitationCreate,
    ContentCitationUpdate,
    ContentCitationResponse,
    UserInteractionCreate,
    UserInteractionUpdate,
    UserInteractionResponse,
)


def _gen_id(prefix: str = "") -> str:
    uid = uuid.uuid4().hex[:12]
    return f"{prefix}_{uid}" if prefix else uid


def _iso(dt: Optional[datetime]) -> str:
    if dt is None:
        return datetime.now(timezone.utc).isoformat()
    return dt.isoformat()


def _parse_dt(iso_str: Optional[str]) -> datetime:
    if not iso_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


class SEORepository:
    """Complete CRUD Repository handling all 8 SEO & Search Intelligence entities."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    # ==========================================
    # 1. SEARCH QUERY CRUD
    # ==========================================

    def create_search_query(self, data: SearchQueryCreate) -> SearchQueryResponse:
        qid = _gen_id("sq")
        date_str = _iso(data.date)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO search_queries (id, query, target_keyword, search_intent, date, location)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (qid, data.query, data.target_keyword, data.search_intent.value, date_str, data.location),
            )
        return self.get_search_query(qid)

    def get_search_query(self, query_id: str) -> Optional[SearchQueryResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT sq.*, COUNT(rh.id) as results_count
                FROM search_queries sq
                LEFT JOIN ranking_history rh ON rh.search_query_id = sq.id
                WHERE sq.id = ?
                GROUP BY sq.id
                """,
                (query_id,),
            ).fetchone()
            if not row:
                return None
            return SearchQueryResponse(
                id=row["id"],
                query=row["query"],
                target_keyword=row["target_keyword"],
                search_intent=row["search_intent"],
                date=_parse_dt(row["date"]),
                location=row["location"],
                results_count=row["results_count"],
            )

    def list_search_queries(self, limit: int = 50) -> List[SearchQueryResponse]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT sq.*, COUNT(rh.id) as results_count
                FROM search_queries sq
                LEFT JOIN ranking_history rh ON rh.search_query_id = sq.id
                GROUP BY sq.id
                ORDER BY sq.date DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [
                SearchQueryResponse(
                    id=r["id"],
                    query=r["query"],
                    target_keyword=r["target_keyword"],
                    search_intent=r["search_intent"],
                    date=_parse_dt(r["date"]),
                    location=r["location"],
                    results_count=r["results_count"],
                )
                for r in rows
            ]

    def update_search_query(self, query_id: str, data: SearchQueryUpdate) -> Optional[SearchQueryResponse]:
        fields, params = [], []
        if data.query is not None:
            fields.append("query = ?")
            params.append(data.query)
        if data.target_keyword is not None:
            fields.append("target_keyword = ?")
            params.append(data.target_keyword)
        if data.search_intent is not None:
            fields.append("search_intent = ?")
            params.append(data.search_intent.value)
        if data.location is not None:
            fields.append("location = ?")
            params.append(data.location)

        if not fields:
            return self.get_search_query(query_id)

        params.append(query_id)
        with get_connection(self.db_path) as conn:
            conn.execute(f"UPDATE search_queries SET {', '.join(fields)} WHERE id = ?", params)
        return self.get_search_query(query_id)

    # ==========================================
    # 2. WEBSITE CRUD
    # ==========================================

    def create_website(self, data: WebsiteCreate) -> WebsiteResponse:
        wid = data.id or _gen_id("site")
        now_str = _iso(None)
        obs_json = json.dumps(data.seo_observations)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO websites (id, domain, title, url, content_topic, seo_observations, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (wid, data.domain.lower(), data.title, data.url, data.content_topic, obs_json, now_str, now_str),
            )
        return self.get_website(wid)

    def get_website(self, website_id: str) -> Optional[WebsiteResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM websites WHERE id = ?", (website_id,)).fetchone()
            if not row:
                return None
            return WebsiteResponse(
                id=row["id"],
                domain=row["domain"],
                title=row["title"],
                url=row["url"],
                content_topic=row["content_topic"],
                seo_observations=json.loads(row["seo_observations"] or "{}"),
                created_at=_parse_dt(row["created_at"]),
                updated_at=_parse_dt(row["updated_at"]),
            )

    def get_website_by_domain(self, domain: str) -> Optional[WebsiteResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM websites WHERE domain = ?", (domain.lower(),)).fetchone()
            if not row:
                return None
            return WebsiteResponse(
                id=row["id"],
                domain=row["domain"],
                title=row["title"],
                url=row["url"],
                content_topic=row["content_topic"],
                seo_observations=json.loads(row["seo_observations"] or "{}"),
                created_at=_parse_dt(row["created_at"]),
                updated_at=_parse_dt(row["updated_at"]),
            )

    def list_websites(self) -> List[WebsiteResponse]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM websites ORDER BY domain ASC").fetchall()
            return [
                WebsiteResponse(
                    id=r["id"],
                    domain=r["domain"],
                    title=r["title"],
                    url=r["url"],
                    content_topic=r["content_topic"],
                    seo_observations=json.loads(r["seo_observations"] or "{}"),
                    created_at=_parse_dt(r["created_at"]),
                    updated_at=_parse_dt(r["updated_at"]),
                )
                for r in rows
            ]

    def update_website(self, website_id: str, data: WebsiteUpdate) -> Optional[WebsiteResponse]:
        fields, params = [], []
        if data.domain is not None:
            fields.append("domain = ?")
            params.append(data.domain.lower())
        if data.title is not None:
            fields.append("title = ?")
            params.append(data.title)
        if data.url is not None:
            fields.append("url = ?")
            params.append(data.url)
        if data.content_topic is not None:
            fields.append("content_topic = ?")
            params.append(data.content_topic)
        if data.seo_observations is not None:
            fields.append("seo_observations = ?")
            params.append(json.dumps(data.seo_observations))

        if not fields:
            return self.get_website(website_id)

        fields.append("updated_at = ?")
        params.append(_iso(None))
        params.append(website_id)

        with get_connection(self.db_path) as conn:
            conn.execute(f"UPDATE websites SET {', '.join(fields)} WHERE id = ?", params)
        return self.get_website(website_id)

    # ==========================================
    # 3. RANKING HISTORY CRUD
    # ==========================================

    def create_ranking_entry(self, data: RankingHistoryCreate) -> RankingHistoryResponse:
        rid = _gen_id("rh")
        date_str = _iso(data.date)
        change = data.change_in_position
        if data.previous_position is not None and change == 0:
            change = data.previous_position - data.position

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO ranking_history (id, website_id, search_query_id, keyword, date, position, previous_position, change_in_position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (rid, data.website_id, data.search_query_id, data.keyword, date_str, data.position, data.previous_position, change),
            )
        return self.get_ranking_entry(rid)

    def get_ranking_entry(self, entry_id: str) -> Optional[RankingHistoryResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT rh.*, w.domain
                FROM ranking_history rh
                JOIN websites w ON w.id = rh.website_id
                WHERE rh.id = ?
                """,
                (entry_id,),
            ).fetchone()
            if not row:
                return None
            return RankingHistoryResponse(
                id=row["id"],
                website_id=row["website_id"],
                domain=row["domain"],
                search_query_id=row["search_query_id"],
                keyword=row["keyword"],
                date=_parse_dt(row["date"]),
                position=row["position"],
                previous_position=row["previous_position"],
                change_in_position=row["change_in_position"],
            )

    def list_ranking_history(self, website_id: str, keyword: Optional[str] = None) -> List[RankingHistoryResponse]:
        with get_connection(self.db_path) as conn:
            sql = """
                SELECT rh.*, w.domain
                FROM ranking_history rh
                JOIN websites w ON w.id = rh.website_id
                WHERE rh.website_id = ?
            """
            params = [website_id]
            if keyword:
                sql += " AND rh.keyword LIKE ?"
                params.append(f"%{keyword}%")
            sql += " ORDER BY rh.date ASC"

            rows = conn.execute(sql, params).fetchall()
            return [
                RankingHistoryResponse(
                    id=r["id"],
                    website_id=r["website_id"],
                    domain=r["domain"],
                    search_query_id=r["search_query_id"],
                    keyword=r["keyword"],
                    date=_parse_dt(r["date"]),
                    position=r["position"],
                    previous_position=r["previous_position"],
                    change_in_position=r["change_in_position"],
                )
                for r in rows
            ]

    # ==========================================
    # 4. SEO OPTIMIZATION CRUD
    # ==========================================

    def create_optimization(self, data: SEOOptimizationCreate) -> SEOOptimizationResponse:
        oid = _gen_id("opt")
        date_str = _iso(data.date)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO seo_optimizations (id, website_id, date, optimization_type, description, reason_for_optimization, expected_effect, observed_effect)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (oid, data.website_id, date_str, data.optimization_type.value, data.description, data.reason_for_optimization, data.expected_effect, data.observed_effect),
            )
        return self.get_optimization(oid)

    def get_optimization(self, opt_id: str) -> Optional[SEOOptimizationResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT opt.*, w.domain
                FROM seo_optimizations opt
                JOIN websites w ON w.id = opt.website_id
                WHERE opt.id = ?
                """,
                (opt_id,),
            ).fetchone()
            if not row:
                return None
            return SEOOptimizationResponse(
                id=row["id"],
                website_id=row["website_id"],
                domain=row["domain"],
                date=_parse_dt(row["date"]),
                optimization_type=row["optimization_type"],
                description=row["description"],
                reason_for_optimization=row["reason_for_optimization"],
                expected_effect=row["expected_effect"],
                observed_effect=row["observed_effect"],
            )

    def list_optimizations(self, website_id: str) -> List[SEOOptimizationResponse]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT opt.*, w.domain
                FROM seo_optimizations opt
                JOIN websites w ON w.id = opt.website_id
                WHERE opt.website_id = ?
                ORDER BY opt.date DESC
                """,
                (website_id,),
            ).fetchall()
            return [
                SEOOptimizationResponse(
                    id=r["id"],
                    website_id=r["website_id"],
                    domain=r["domain"],
                    date=_parse_dt(r["date"]),
                    optimization_type=r["optimization_type"],
                    description=r["description"],
                    reason_for_optimization=r["reason_for_optimization"],
                    expected_effect=r["expected_effect"],
                    observed_effect=r["observed_effect"],
                )
                for r in rows
            ]

    def update_optimization(self, opt_id: str, data: SEOOptimizationUpdate) -> Optional[SEOOptimizationResponse]:
        fields, params = [], []
        if data.description is not None:
            fields.append("description = ?")
            params.append(data.description)
        if data.reason_for_optimization is not None:
            fields.append("reason_for_optimization = ?")
            params.append(data.reason_for_optimization)
        if data.expected_effect is not None:
            fields.append("expected_effect = ?")
            params.append(data.expected_effect)
        if data.observed_effect is not None:
            fields.append("observed_effect = ?")
            params.append(data.observed_effect)

        if not fields:
            return self.get_optimization(opt_id)

        params.append(opt_id)
        with get_connection(self.db_path) as conn:
            conn.execute(f"UPDATE seo_optimizations SET {', '.join(fields)} WHERE id = ?", params)
        return self.get_optimization(opt_id)

    # ==========================================
    # 5. COMPETITOR HISTORY CRUD
    # ==========================================

    def create_competitor_history(self, data: CompetitorHistoryCreate) -> CompetitorHistoryResponse:
        cid = _gen_id("comp_hist")
        date_str = _iso(data.date)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO competitor_history (id, competitor_website_id, keyword, date, content_changes, feature_changes, ranking_changes, notable_seo_changes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid,
                    data.competitor_website_id,
                    data.keyword,
                    date_str,
                    json.dumps(data.content_changes),
                    json.dumps(data.feature_changes),
                    json.dumps(data.ranking_changes),
                    json.dumps(data.notable_seo_changes),
                ),
            )
        return self.get_competitor_history(cid)

    def get_competitor_history(self, history_id: str) -> Optional[CompetitorHistoryResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT ch.*, w.domain as competitor_domain
                FROM competitor_history ch
                JOIN websites w ON w.id = ch.competitor_website_id
                WHERE ch.id = ?
                """,
                (history_id,),
            ).fetchone()
            if not row:
                return None
            return CompetitorHistoryResponse(
                id=row["id"],
                competitor_website_id=row["competitor_website_id"],
                competitor_domain=row["competitor_domain"],
                keyword=row["keyword"],
                date=_parse_dt(row["date"]),
                content_changes=json.loads(row["content_changes"] or "[]"),
                feature_changes=json.loads(row["feature_changes"] or "[]"),
                ranking_changes=json.loads(row["ranking_changes"] or "{}"),
                notable_seo_changes=json.loads(row["notable_seo_changes"] or "[]"),
            )

    def list_competitor_history(self, competitor_website_id: Optional[str] = None, keyword: Optional[str] = None) -> List[CompetitorHistoryResponse]:
        with get_connection(self.db_path) as conn:
            sql = """
                SELECT ch.*, w.domain as competitor_domain
                FROM competitor_history ch
                JOIN websites w ON w.id = ch.competitor_website_id
                WHERE 1=1
            """
            params = []
            if competitor_website_id:
                sql += " AND ch.competitor_website_id = ?"
                params.append(competitor_website_id)
            if keyword:
                sql += " AND ch.keyword LIKE ?"
                params.append(f"%{keyword}%")
            sql += " ORDER BY ch.date DESC"

            rows = conn.execute(sql, params).fetchall()
            return [
                CompetitorHistoryResponse(
                    id=r["id"],
                    competitor_website_id=r["competitor_website_id"],
                    competitor_domain=r["competitor_domain"],
                    keyword=r["keyword"],
                    date=_parse_dt(r["date"]),
                    content_changes=json.loads(r["content_changes"] or "[]"),
                    feature_changes=json.loads(r["feature_changes"] or "[]"),
                    ranking_changes=json.loads(r["ranking_changes"] or "{}"),
                    notable_seo_changes=json.loads(r["notable_seo_changes"] or "[]"),
                )
                for r in rows
            ]

    # ==========================================
    # 6. OUTCOME CRUD (Causal Attribution)
    # ==========================================

    def create_outcome(self, data: OutcomeCreate) -> OutcomeResponse:
        out_id = _gen_id("out")
        date_str = _iso(data.date)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO outcomes (id, website_id, optimization_id, previous_ranking, new_ranking, observed_change, date, confidence, uncertainty_factors)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    out_id,
                    data.website_id,
                    data.optimization_id,
                    data.previous_ranking,
                    data.new_ranking,
                    data.observed_change,
                    date_str,
                    data.confidence,
                    json.dumps(data.uncertainty_factors),
                ),
            )
            # Auto-update parent optimization's observed_effect if empty
            conn.execute(
                """
                UPDATE seo_optimizations
                SET observed_effect = ?
                WHERE id = ? AND (observed_effect IS NULL OR observed_effect = '')
                """,
                (f"Rank moved from #{data.previous_ranking} to #{data.new_ranking} ({data.observed_change})", data.optimization_id),
            )
        return self.get_outcome(out_id)

    def get_outcome(self, outcome_id: str) -> Optional[OutcomeResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT o.*, w.domain, opt.optimization_type
                FROM outcomes o
                JOIN websites w ON w.id = o.website_id
                JOIN seo_optimizations opt ON opt.id = o.optimization_id
                WHERE o.id = ?
                """,
                (outcome_id,),
            ).fetchone()
            if not row:
                return None
            return OutcomeResponse(
                id=row["id"],
                website_id=row["website_id"],
                domain=row["domain"],
                optimization_id=row["optimization_id"],
                optimization_type=row["optimization_type"],
                previous_ranking=row["previous_ranking"],
                new_ranking=row["new_ranking"],
                observed_change=row["observed_change"],
                date=_parse_dt(row["date"]),
                confidence=row["confidence"],
                uncertainty_factors=json.loads(row["uncertainty_factors"] or "[]"),
            )

    def list_outcomes(self, website_id: Optional[str] = None) -> List[OutcomeResponse]:
        with get_connection(self.db_path) as conn:
            sql = """
                SELECT o.*, w.domain, opt.optimization_type
                FROM outcomes o
                JOIN websites w ON w.id = o.website_id
                JOIN seo_optimizations opt ON opt.id = o.optimization_id
                WHERE 1=1
            """
            params = []
            if website_id:
                sql += " AND o.website_id = ?"
                params.append(website_id)
            sql += " ORDER BY o.date DESC"

            rows = conn.execute(sql, params).fetchall()
            return [
                OutcomeResponse(
                    id=r["id"],
                    website_id=r["website_id"],
                    domain=r["domain"],
                    optimization_id=r["optimization_id"],
                    optimization_type=r["optimization_type"],
                    previous_ranking=r["previous_ranking"],
                    new_ranking=r["new_ranking"],
                    observed_change=r["observed_change"],
                    date=_parse_dt(r["date"]),
                    confidence=r["confidence"],
                    uncertainty_factors=json.loads(r["uncertainty_factors"] or "[]"),
                )
                for r in rows
            ]

    def update_outcome(self, outcome_id: str, data: OutcomeUpdate) -> Optional[OutcomeResponse]:
        fields, params = [], []
        if data.previous_ranking is not None:
            fields.append("previous_ranking = ?")
            params.append(data.previous_ranking)
        if data.new_ranking is not None:
            fields.append("new_ranking = ?")
            params.append(data.new_ranking)
        if data.observed_change is not None:
            fields.append("observed_change = ?")
            params.append(data.observed_change)
        if data.confidence is not None:
            fields.append("confidence = ?")
            params.append(data.confidence)
        if data.uncertainty_factors is not None:
            fields.append("uncertainty_factors = ?")
            params.append(json.dumps(data.uncertainty_factors))

        if not fields:
            return self.get_outcome(outcome_id)

        params.append(outcome_id)
        with get_connection(self.db_path) as conn:
            conn.execute(f"UPDATE outcomes SET {', '.join(fields)} WHERE id = ?", params)
        return self.get_outcome(outcome_id)

    # ==========================================
    # 7. CONTENT / CITATION INFORMATION CRUD
    # ==========================================

    def create_citation(self, data: ContentCitationCreate) -> ContentCitationResponse:
        cit_id = _gen_id("cit")
        now_str = _iso(None)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO content_citations (id, website_id, search_query_id, source_title, source_url, citation_snippet, citation_type, is_used_by_app, citation_metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cit_id,
                    data.website_id,
                    data.search_query_id,
                    data.source_title,
                    data.source_url,
                    data.citation_snippet,
                    data.citation_type.value,
                    1 if data.is_used_by_app else 0,
                    json.dumps(data.citation_metadata),
                    now_str,
                ),
            )
        return self.get_citation(cit_id)

    def get_citation(self, citation_id: str) -> Optional[ContentCitationResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM content_citations WHERE id = ?", (citation_id,)).fetchone()
            if not row:
                return None
            return ContentCitationResponse(
                id=row["id"],
                website_id=row["website_id"],
                search_query_id=row["search_query_id"],
                source_title=row["source_title"],
                source_url=row["source_url"],
                citation_snippet=row["citation_snippet"],
                citation_type=row["citation_type"],
                is_used_by_app=bool(row["is_used_by_app"]),
                citation_metadata=json.loads(row["citation_metadata"] or "{}"),
                created_at=_parse_dt(row["created_at"]),
            )

    def list_citations(self, website_id: Optional[str] = None, only_used: bool = True) -> List[ContentCitationResponse]:
        with get_connection(self.db_path) as conn:
            sql = "SELECT * FROM content_citations WHERE 1=1"
            params = []
            if website_id:
                sql += " AND website_id = ?"
                params.append(website_id)
            if only_used:
                sql += " AND is_used_by_app = 1"
            sql += " ORDER BY created_at DESC"

            rows = conn.execute(sql, params).fetchall()
            return [
                ContentCitationResponse(
                    id=r["id"],
                    website_id=r["website_id"],
                    search_query_id=r["search_query_id"],
                    source_title=r["source_title"],
                    source_url=r["source_url"],
                    citation_snippet=r["citation_snippet"],
                    citation_type=r["citation_type"],
                    is_used_by_app=bool(r["is_used_by_app"]),
                    citation_metadata=json.loads(r["citation_metadata"] or "{}"),
                    created_at=_parse_dt(r["created_at"]),
                )
                for r in rows
            ]

    def update_citation(self, citation_id: str, data: ContentCitationUpdate) -> Optional[ContentCitationResponse]:
        fields, params = [], []
        if data.source_title is not None:
            fields.append("source_title = ?")
            params.append(data.source_title)
        if data.source_url is not None:
            fields.append("source_url = ?")
            params.append(data.source_url)
        if data.citation_snippet is not None:
            fields.append("citation_snippet = ?")
            params.append(data.citation_snippet)
        if data.citation_type is not None:
            fields.append("citation_type = ?")
            params.append(data.citation_type.value)
        if data.is_used_by_app is not None:
            fields.append("is_used_by_app = ?")
            params.append(1 if data.is_used_by_app else 0)
        if data.citation_metadata is not None:
            fields.append("citation_metadata = ?")
            params.append(json.dumps(data.citation_metadata))

        if not fields:
            return self.get_citation(citation_id)

        params.append(citation_id)
        with get_connection(self.db_path) as conn:
            conn.execute(f"UPDATE content_citations SET {', '.join(fields)} WHERE id = ?", params)
        return self.get_citation(citation_id)

    # ==========================================
    # 8. USER INTERACTION CRUD
    # ==========================================

    def create_user_interaction(self, data: UserInteractionCreate) -> UserInteractionResponse:
        ui_id = _gen_id("ui")
        date_str = _iso(data.created_at)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO user_interactions (id, search_query_id, query_text, selected_website_id, question_asked, recommendation_requested, recommendation_provided, feedback, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ui_id,
                    data.search_query_id,
                    data.query_text,
                    data.selected_website_id,
                    data.question_asked,
                    data.recommendation_requested,
                    data.recommendation_provided,
                    json.dumps(data.feedback),
                    date_str,
                ),
            )
        return self.get_user_interaction(ui_id)

    def get_user_interaction(self, interaction_id: str) -> Optional[UserInteractionResponse]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT ui.*, w.domain as selected_domain
                FROM user_interactions ui
                LEFT JOIN websites w ON w.id = ui.selected_website_id
                WHERE ui.id = ?
                """,
                (interaction_id,),
            ).fetchone()
            if not row:
                return None
            return UserInteractionResponse(
                id=row["id"],
                search_query_id=row["search_query_id"],
                query_text=row["query_text"],
                selected_website_id=row["selected_website_id"],
                selected_domain=row["selected_domain"],
                question_asked=row["question_asked"],
                recommendation_requested=row["recommendation_requested"],
                recommendation_provided=row["recommendation_provided"],
                feedback=json.loads(row["feedback"] or "{}"),
                created_at=_parse_dt(row["created_at"]),
            )

    def list_user_interactions(self, query_text: Optional[str] = None, website_id: Optional[str] = None) -> List[UserInteractionResponse]:
        with get_connection(self.db_path) as conn:
            sql = """
                SELECT ui.*, w.domain as selected_domain
                FROM user_interactions ui
                LEFT JOIN websites w ON w.id = ui.selected_website_id
                WHERE 1=1
            """
            params = []
            if query_text:
                sql += " AND ui.query_text LIKE ?"
                params.append(f"%{query_text}%")
            if website_id:
                sql += " AND ui.selected_website_id = ?"
                params.append(website_id)
            sql += " ORDER BY ui.created_at DESC"

            rows = conn.execute(sql, params).fetchall()
            return [
                UserInteractionResponse(
                    id=r["id"],
                    search_query_id=r["search_query_id"],
                    query_text=r["query_text"],
                    selected_website_id=r["selected_website_id"],
                    selected_domain=r["selected_domain"],
                    question_asked=r["question_asked"],
                    recommendation_requested=r["recommendation_requested"],
                    recommendation_provided=r["recommendation_provided"],
                    feedback=json.loads(r["feedback"] or "{}"),
                    created_at=_parse_dt(r["created_at"]),
                )
                for r in rows
            ]

    def update_user_interaction(self, interaction_id: str, data: UserInteractionUpdate) -> Optional[UserInteractionResponse]:
        fields, params = [], []
        if data.feedback is not None:
            fields.append("feedback = ?")
            params.append(json.dumps(data.feedback))
        if data.recommendation_provided is not None:
            fields.append("recommendation_provided = ?")
            params.append(data.recommendation_provided)

        if not fields:
            return self.get_user_interaction(interaction_id)

        params.append(interaction_id)
        with get_connection(self.db_path) as conn:
            conn.execute(f"UPDATE user_interactions SET {', '.join(fields)} WHERE id = ?", params)
        return self.get_user_interaction(interaction_id)
