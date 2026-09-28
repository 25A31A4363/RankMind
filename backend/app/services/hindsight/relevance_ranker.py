import json
import re
from typing import List, Optional, Dict, Any, Tuple
from app.models.hindsight_schemas import (
    MemoryCategory,
    HindsightMemoryItem,
)
from app.db.database import get_connection, DB_PATH


class RelevanceRankingLayer:
    """Intelligent Relevance-Ranking Layer for Hindsight Memory Retrieval.
    
    Evaluates candidate memories across 8 distinct dimensions:
    1. same website
    2. same keyword
    3. related keywords
    4. similar optimization
    5. previous ranking behavior
    6. competitor behavior
    7. previous outcomes
    8. previous user interactions
    
    Ensures bounded retrieval within token budgets and explains why each memory was recalled.
    """

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def rank_and_select_memories(
        self,
        query: str,
        target_domain: Optional[str] = None,
        current_position: Optional[int] = None,
        target_deficiencies: Optional[List[str]] = None,
        categories: Optional[List[MemoryCategory]] = None,
        bank_id: str = "rankmind-seo",
        max_memories: int = 6,
        max_tokens: int = 4096,
    ) -> List[HindsightMemoryItem]:
        """Evaluates all candidate memories in the bank, scores them across the 8 dimensions,
        and returns the top-ranked, category-stratified subset within budget.
        """
        q_clean = query.lower().strip()
        tokens = [t for t in re.split(r"\W+", q_clean) if len(t) > 2]

        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM hindsight_memories WHERE bank_id = ?",
                (bank_id,),
            ).fetchall()

        scored_candidates: List[HindsightMemoryItem] = []

        for r in rows:
            mem_cat = MemoryCategory(r["category"])
            if categories and mem_cat not in categories:
                continue

            r_kw = r["target_keyword"].lower()
            r_domain = (r["target_domain"] or "").lower()
            r_content = r["content"].lower()
            r_meta = json.loads(r["metadata"] or "{}")
            r_tags = [t.lower() for t in json.loads(r["tags"] or "[]")]

            score = 0.0
            dimensions_matched: List[str] = []

            # -------------------------------------------------------------
            # 1. SAME WEBSITE DIMENSION (+0.35)
            # -------------------------------------------------------------
            if target_domain and r_domain:
                if target_domain.lower() == r_domain:
                    score += 0.35
                    dimensions_matched.append(f"Same website: Direct history for '{target_domain}'")

            # -------------------------------------------------------------
            # 2. SAME KEYWORD DIMENSION (+0.40)
            # -------------------------------------------------------------
            if r_kw == q_clean:
                score += 0.40
                dimensions_matched.append(f"Same keyword: Exact query match ('{r['target_keyword']}')")
            elif q_clean in r_kw or r_kw in q_clean:
                score += 0.30
                dimensions_matched.append(f"Same keyword: Phrase match ('{r['target_keyword']}')")

            # -------------------------------------------------------------
            # 3. RELATED KEYWORDS DIMENSION (up to +0.25)
            # -------------------------------------------------------------
            # Token overlap & topical synonyms (e.g. python, courses, tutorial, beginners, learn)
            overlap_hits = sum(1 for t in tokens if t in r_kw or t in r_content or any(t in tag for tag in r_tags))
            if overlap_hits > 0:
                kw_boost = min(0.25, overlap_hits * 0.08)
                score += kw_boost
                dimensions_matched.append(f"Related keywords: Semantic overlap ({overlap_hits} term hits)")

            # -------------------------------------------------------------
            # 4. SIMILAR OPTIMIZATION DIMENSION (+0.20)
            # -------------------------------------------------------------
            opt_type = r_meta.get("optimization_type", "").lower()
            relevant_opt_types = [
                "structured_schema", "course_schema", "interactive_widget",
                "code_sandbox", "video_preview", "curriculum_matrix", "content_structure", "title_refactor"
            ]
            
            matched_opts = [o for o in relevant_opt_types if o in opt_type or o in r_tags or o.replace("_", " ") in r_content]
            if matched_opts:
                score += 0.20
                dimensions_matched.append(f"Similar optimization: Involves [{matched_opts[0].replace('_', ' ').upper()}]")
            elif target_deficiencies:
                # If memory addresses one of target site's current deficiencies
                for defic in target_deficiencies:
                    if defic.lower() in r_content or defic.lower() in opt_type:
                        score += 0.18
                        dimensions_matched.append(f"Similar optimization: Directly addresses current deficiency '{defic}'")
                        break

            # -------------------------------------------------------------
            # 5. PREVIOUS RANKING BEHAVIOR DIMENSION (+0.15)
            # -------------------------------------------------------------
            r_pos = r_meta.get("position") or r_meta.get("rank_before")
            if current_position is not None and r_pos is not None:
                # Similar starting baseline position (e.g. both around #8 or top 10)
                if abs(r_pos - current_position) <= 2:
                    score += 0.15
                    dimensions_matched.append(f"Previous ranking behavior: Shared baseline rank (#{r_pos} vs #{current_position})")
            elif "ranking" in r_tags or mem_cat == MemoryCategory.RANKING_HISTORY:
                # Historical ranking trajectory milestone
                score += 0.10
                dimensions_matched.append(f"Previous ranking behavior: Historical SERP position transition recorded")

            # -------------------------------------------------------------
            # 6. COMPETITOR BEHAVIOR DIMENSION (+0.25)
            # -------------------------------------------------------------
            if mem_cat == MemoryCategory.COMPETITOR_HISTORY or "competitor" in r_tags:
                score += 0.25
                comp_name = r_meta.get("competitor") or r["target_domain"] or "SERP rival"
                dimensions_matched.append(f"Competitor behavior: Observed rival counter-action by '{comp_name}'")

            # -------------------------------------------------------------
            # 7. PREVIOUS OUTCOMES DIMENSION (+0.30)
            # -------------------------------------------------------------
            if mem_cat == MemoryCategory.OUTCOME_HISTORY or "outcome" in r_tags or "causal" in r_tags:
                score += 0.30
                verdict = r_meta.get("verdict", "OBSERVED")
                dimensions_matched.append(f"Previous outcomes: Empirical causal outcome record (verdict: {verdict})")

            # -------------------------------------------------------------
            # 8. PREVIOUS USER INTERACTIONS DIMENSION (+0.15)
            # -------------------------------------------------------------
            if "feedback" in r_tags or "recommendation_decision" in r_tags or "interaction" in r_tags:
                score += 0.15
                dimensions_matched.append("Previous user interactions: User feedback or accepted/rejected recommendation context")

            # Normalize score to max 1.0
            final_score = min(round(score, 2), 1.0)

            # Quality threshold (filter out weak or unrelated memories)
            if final_score >= 0.20:
                why_text = "; ".join(dimensions_matched) if dimensions_matched else "Relevant historical SEO context"
                scored_candidates.append(
                    HindsightMemoryItem(
                        id=r["id"],
                        bank_id=r["bank_id"],
                        category=mem_cat,
                        content=r["content"],
                        target_keyword=r["target_keyword"],
                        target_domain=r["target_domain"],
                        timestamp=r["timestamp"],
                        relevance_score=final_score,
                        why_relevant=why_text,
                        metadata=r_meta,
                        tags=r_tags,
                    )
                )

        # -------------------------------------------------------------
        # CATEGORY-STRATIFIED DIVERSITY SELECTION (Within Token Budget)
        # -------------------------------------------------------------
        scored_candidates.sort(key=lambda x: (x.relevance_score or 0.0, x.timestamp), reverse=True)

        by_cat: Dict[MemoryCategory, List[HindsightMemoryItem]] = {}
        for item in scored_candidates:
            by_cat.setdefault(item.category, []).append(item)

        selected: List[HindsightMemoryItem] = []
        token_count = 0

        # Round 1: Take up to 2 items from highest-impact categories
        priority_categories = [
            MemoryCategory.OUTCOME_HISTORY,
            MemoryCategory.COMPETITOR_HISTORY,
            MemoryCategory.OPTIMIZATION_HISTORY,
            MemoryCategory.RANKING_HISTORY,
        ]

        for cat in priority_categories:
            for item in by_cat.get(cat, [])[:2]:
                est_tokens = len(item.content.split()) * 2
                if item not in selected and len(selected) < max_memories and (token_count + est_tokens <= max_tokens):
                    selected.append(item)
                    token_count += est_tokens

        # Round 2: Fill remaining quota with highest scoring memories
        for item in scored_candidates:
            est_tokens = len(item.content.split()) * 2
            if item not in selected and len(selected) < max_memories and (token_count + est_tokens <= max_tokens):
                selected.append(item)
                token_count += est_tokens

        return selected


relevance_ranking_layer = RelevanceRankingLayer()
