import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.models.hindsight_schemas import (
    MemoryCategory,
    HindsightMemoryItem,
)
from app.services.hindsight.client import hindsight_client
from app.repositories.seo_repository import SEORepository
from app.db.database import DB_PATH


class HindsightMemoryManager:
    """High-level SEO memory manager operating across the 4 core Hindsight categories.
    
    1. RANKING HISTORY
    2. OPTIMIZATION HISTORY
    3. COMPETITOR HISTORY
    4. OUTCOME HISTORY
    """

    def __init__(self, client=hindsight_client, db_path=DB_PATH):
        self.client = client
        self.repo = SEORepository(db_path)

    # =========================================================================
    # 1. RANKING HISTORY RETENTION
    # =========================================================================

    def retain_ranking_milestone(
        self,
        domain: str,
        keyword: str,
        date_str: str,
        position: int,
        previous_position: Optional[int] = None,
        change: int = 0,
    ) -> HindsightMemoryItem:
        """Remembers: website, keyword, date, ranking, ranking movement."""
        movement_text = "held position"
        if change > 0:
            movement_text = f"improved by +{change} positions (#{previous_position} → #{position})"
        elif change < 0:
            movement_text = f"dropped by {abs(change)} positions (#{previous_position} → #{position})"
        elif previous_position:
            movement_text = f"remained stable at #{position}"
        else:
            movement_text = f"initial baseline recorded at #{position}"

        content = (
            f"On {date_str[:10]}, '{domain}' held Rank #{position} for target keyword '{keyword}'. "
            f"Ranking movement: {movement_text}."
        )

        return self.client.retain(
            category=MemoryCategory.RANKING_HISTORY,
            content=content,
            target_keyword=keyword,
            target_domain=domain,
            timestamp=date_str,
            metadata={
                "position": position,
                "previous_position": previous_position or position,
                "delta": change,
            },
            tags=["ranking", keyword.lower(), domain.lower()],
        )

    # =========================================================================
    # 2. OPTIMIZATION HISTORY RETENTION
    # =========================================================================

    def retain_optimization_event(
        self,
        domain: str,
        keyword: str,
        optimization_type: str,
        description: str,
        reason: str,
        expected_effect: str,
        date_str: str,
    ) -> HindsightMemoryItem:
        """Remembers: optimization performed, date, website, reason, context."""
        content = (
            f"Optimization Deployed on {date_str[:10]} for '{domain}' on '{keyword}': "
            f"[{optimization_type.replace('_', ' ').upper()}] {description} "
            f"Strategic Reason: {reason}. Expected Effect: {expected_effect}."
        )

        return self.client.retain(
            category=MemoryCategory.OPTIMIZATION_HISTORY,
            content=content,
            target_keyword=keyword,
            target_domain=domain,
            timestamp=date_str,
            metadata={
                "optimization_type": optimization_type,
                "expected_effect": expected_effect,
            },
            tags=["optimization", optimization_type, keyword.lower(), domain.lower()],
        )

    # =========================================================================
    # 3. COMPETITOR HISTORY RETENTION
    # =========================================================================

    def retain_competitor_event(
        self,
        competitor_domain: str,
        keyword: str,
        content_changes: List[str],
        feature_changes: List[str],
        notable_seo_changes: List[str],
        ranking_changes: Dict[str, Any],
        date_str: str,
    ) -> HindsightMemoryItem:
        """Remembers: competitor changes, date, observed ranking changes, important competitive events."""
        changes_summary = []
        if content_changes:
            changes_summary.append(f"Content: {', '.join(content_changes)}")
        if feature_changes:
            changes_summary.append(f"Features: {', '.join(feature_changes)}")
        if notable_seo_changes:
            changes_summary.append(f"SEO/Schemas: {', '.join(notable_seo_changes)}")

        delta = ranking_changes.get("delta", 0)
        rank_text = f"rank moved by {delta:+d}" if delta != 0 else "rank maintained"

        content = (
            f"Competitor Counter-Action on {date_str[:10]} by '{competitor_domain}' for '{keyword}': "
            f"{'; '.join(changes_summary)}. Resulting in: {rank_text}."
        )

        return self.client.retain(
            category=MemoryCategory.COMPETITOR_HISTORY,
            content=content,
            target_keyword=keyword,
            target_domain=competitor_domain,
            timestamp=date_str,
            metadata={
                "competitor": competitor_domain,
                "rank_delta": delta,
            },
            tags=["competitor", competitor_domain.lower(), keyword.lower()],
        )

    # =========================================================================
    # 4. OUTCOME HISTORY RETENTION (Causal Attribution)
    # =========================================================================

    def retain_outcome_attribution(
        self,
        domain: str,
        keyword: str,
        optimization_title: str,
        optimization_type: str,
        rank_before: int,
        rank_after: int,
        observed_result: str,
        time_period_days: int,
        confidence: float,
        uncertainty_factors: List[str],
        date_str: str,
    ) -> HindsightMemoryItem:
        """Remembers: optimization, previous ranking, later ranking, observed result, time period, uncertainty."""
        delta = rank_before - rank_after
        verdict = "CONFIRMED_POSITIVE" if delta >= 2 else "NEUTRAL" if delta == 0 else "CONFOUNDED_OR_NEGATIVE"

        content = (
            f"Observed SEO Outcome on {date_str[:10]} for '{domain}' on keyword '{keyword}': "
            f"After this change ('{optimization_title}' [{optimization_type}]), the observed ranking moved from #{rank_before} to #{rank_after} ({observed_result}) "
            f"over a {time_period_days}-day latency window. Observed pattern: {verdict}. "
            f"Correlation Confidence: {int(confidence * 100)}%. "
            f"Uncertainty Confounders: {', '.join(uncertainty_factors) if uncertainty_factors else 'External SERP volatility and competitor counter-actions remain possible confounding factors'}."
        )

        return self.client.retain(
            category=MemoryCategory.OUTCOME_HISTORY,
            content=content,
            target_keyword=keyword,
            target_domain=domain,
            timestamp=date_str,
            metadata={
                "optimization_type": optimization_type,
                "rank_before": rank_before,
                "rank_after": rank_after,
                "rank_delta": delta,
                "confidence": confidence,
                "verdict": verdict,
                "uncertainty_factors": uncertainty_factors,
            },
            tags=["outcome", "causal", optimization_type, keyword.lower(), domain.lower()],
        )

    def recall_for_query(
        self,
        query: str,
        target_domain: Optional[str] = None,
        current_position: Optional[int] = None,
        target_deficiencies: Optional[List[str]] = None,
        max_memories: int = 6,
    ) -> List[HindsightMemoryItem]:
        """Recalls relevant memories for a query, prioritizing causal outcomes and competitor moves across 8 dimensions."""
        return self.client.recall(
            query=query,
            target_domain=target_domain,
            current_position=current_position,
            target_deficiencies=target_deficiencies,
            max_memories=max_memories,
        )

    # =========================================================================
    # SYNC DATABASE TO HINDSIGHT
    # =========================================================================

    def sync_database_to_hindsight(self):
        """Populates the Hindsight memory bank from existing historical database records."""
        # 1. Ranking history
        websites = {w.id: w for w in self.repo.list_websites()}
        queries = {q.id: q for q in self.repo.list_search_queries()}

        for site_id, site in websites.items():
            ranks = self.repo.list_ranking_history(site_id)
            for r in ranks:
                self.retain_ranking_milestone(
                    domain=site.domain,
                    keyword=r.keyword,
                    date_str=r.date.isoformat(),
                    position=r.position,
                    previous_position=r.previous_position,
                    change=r.change_in_position,
                )

            # 2. Optimizations
            opts = self.repo.list_optimizations(site_id)
            for o in opts:
                self.retain_optimization_event(
                    domain=site.domain,
                    keyword=site.content_topic,
                    optimization_type=o.optimization_type,
                    description=o.description,
                    reason=o.reason_for_optimization,
                    expected_effect=o.expected_effect,
                    date_str=o.date.isoformat(),
                )

            # 3. Outcomes
            outs = self.repo.list_outcomes(site_id)
            for out in outs:
                opt_rec = self.repo.get_optimization(out.optimization_id)
                self.retain_outcome_attribution(
                    domain=site.domain,
                    keyword="python courses" if "python" in site.domain else site.content_topic,
                    optimization_title=opt_rec.description if opt_rec else "SEO Optimization",
                    optimization_type=out.optimization_type or "general",
                    rank_before=out.previous_ranking,
                    rank_after=out.new_ranking,
                    observed_result=out.observed_change,
                    time_period_days=21,
                    confidence=out.confidence,
                    uncertainty_factors=out.uncertainty_factors,
                    date_str=out.date.isoformat(),
                )

        # 4. Competitors
        comp_records = self.repo.list_competitor_history()
        for ch in comp_records:
            comp_site = websites.get(ch.competitor_website_id)
            comp_domain = comp_site.domain if comp_site else "competitor"
            self.retain_competitor_event(
                competitor_domain=comp_domain,
                keyword=ch.keyword,
                content_changes=ch.content_changes,
                feature_changes=ch.feature_changes,
                notable_seo_changes=ch.notable_seo_changes,
                ranking_changes=ch.ranking_changes,
                date_str=ch.date.isoformat(),
            )


hindsight_memory_manager = HindsightMemoryManager()
