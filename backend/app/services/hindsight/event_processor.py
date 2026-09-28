import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.db.database import get_connection, DB_PATH
from app.models.hindsight_schemas import (
    MemoryCategory,
    RetentionDecisionEnum,
    NormalizedMemoryRepresentation,
    RawSEOEvent,
    RetentionDecisionResult,
    HindsightMemoryItem,
)
from app.services.hindsight.client import hindsight_client


class EventProcessingLayer:
    """Intelligent Event-Processing & Memory-Quality Layer for RankMind.
    
    Filters out noise, prevents meaningless duplicate memories, normalizes context,
    enforces correlational truth discipline, and decides:
    REMEMBER or DO NOT REMEMBER.
    """

    def __init__(self, client=hindsight_client, db_path=DB_PATH):
        self.client = client
        self.db_path = db_path

    # =========================================================================
    # CORE PIPELINE: PROCESS & EVALUATE
    # =========================================================================

    def process_and_evaluate_event(self, raw_event: RawSEOEvent) -> RetentionDecisionResult:
        """Main entrypoint: ingests a raw SEO event, evaluates its significance and uniqueness,
        and either retains it into Hindsight with normalized context or suppresses it.
        """
        event_type = raw_event.event_type.strip().lower()
        website = raw_event.website.strip().lower()
        keyword = raw_event.keyword.strip().lower()
        date_str = raw_event.date or datetime.now(timezone.utc).isoformat()
        details = raw_event.details or {}

        # 1. Step 1: Compute Deduplication Fingerprint
        fingerprint = self._compute_event_fingerprint(event_type, website, keyword, details)

        # 2. Step 2: Check for Meaningless Duplicates
        is_duplicate, dup_reason = self._check_duplicate(fingerprint, website, keyword, event_type)
        if is_duplicate:
            return self._record_rejection(
                event_type=event_type,
                website=website,
                keyword=keyword,
                date_str=date_str,
                reason=dup_reason,
                fingerprint=fingerprint,
                importance_score=0.0,
            )

        # 3. Step 3: Evaluate Memory Quality by Event Category
        if event_type in ["ranking_change", "ranking_milestone", "ranking"]:
            decision, reason, importance, norm_mem, mem_cat, tags = self._evaluate_ranking_event(
                website, keyword, date_str, details
            )
        elif event_type in ["optimization_performed", "seo_optimization", "optimization"]:
            decision, reason, importance, norm_mem, mem_cat, tags = self._evaluate_optimization_event(
                website, keyword, date_str, details
            )
        elif event_type in ["outcome_observed", "outcome", "causal_attribution"]:
            decision, reason, importance, norm_mem, mem_cat, tags = self._evaluate_outcome_event(
                website, keyword, date_str, details
            )
        elif event_type in ["competitor_change", "competitor_move", "competitor"]:
            decision, reason, importance, norm_mem, mem_cat, tags = self._evaluate_competitor_event(
                website, keyword, date_str, details
            )
        elif event_type in ["recommendation_decision", "recommendation"]:
            decision, reason, importance, norm_mem, mem_cat, tags = self._evaluate_recommendation_event(
                website, keyword, date_str, details
            )
        elif event_type in ["user_feedback", "feedback"]:
            decision, reason, importance, norm_mem, mem_cat, tags = self._evaluate_user_feedback(
                website, keyword, date_str, details
            )
        else:
            decision = RetentionDecisionEnum.DO_NOT_REMEMBER
            reason = f"Unrecognized event type '{event_type}'; skipped to prevent unindexed clutter."
            importance = 0.0
            norm_mem = None
            mem_cat = None
            tags = []

        # 4. Step 4: Handle Rejections
        if decision == RetentionDecisionEnum.DO_NOT_REMEMBER:
            return self._record_rejection(
                event_type=event_type,
                website=website,
                keyword=keyword,
                date_str=date_str,
                reason=reason,
                fingerprint=fingerprint,
                importance_score=importance,
            )

        # 5. Step 5: Handle Acceptance (REMEMBER) -> Retain into Hindsight
        content_string = self._format_retained_content(norm_mem)
        retained_item = self.client.retain(
            category=mem_cat,
            content=content_string,
            target_keyword=keyword,
            target_domain=website,
            timestamp=date_str,
            metadata={
                "normalized_event": norm_mem.event,
                "confidence": norm_mem.confidence,
                "uncertainty_factors": norm_mem.uncertainty_factors,
                "importance_score": importance,
                "fingerprint": fingerprint,
                **details,
            },
            tags=tags,
        )

        # 6. Step 6: Log Developer Decision as REMEMBER
        self._log_decision(
            event_type=event_type,
            website=website,
            keyword=keyword,
            decision="REMEMBER",
            reason=reason,
            importance_score=importance,
            fingerprint=fingerprint,
            content_snippet=content_string[:160],
            normalized_data=norm_mem.model_dump(),
            timestamp=date_str,
        )

        return RetentionDecisionResult(
            decision=RetentionDecisionEnum.REMEMBER,
            reason=reason,
            importance_score=importance,
            event_type=event_type,
            website=website,
            keyword=keyword,
            deduplication_fingerprint=fingerprint,
            normalized_memory=norm_mem,
            retained_memory_item=retained_item,
        )

    # =========================================================================
    # EVENT-SPECIFIC QUALITY EVALUATORS
    # =========================================================================

    def _evaluate_ranking_event(
        self, website: str, keyword: str, date_str: str, details: Dict[str, Any]
    ) -> Tuple[RetentionDecisionEnum, str, float, Optional[NormalizedMemoryRepresentation], Optional[MemoryCategory], List[str]]:
        """Evaluates ranking shifts:
        - Delta >= 2: SIGNIFICANT -> REMEMBER
        - Crossing into Top 3, Top 5, or Top 10: CRITICAL SERP MILESTONE -> REMEMBER
        - Baseline initial recording (position <= 20): REMEMBER
        - Micro-fluctuations (delta <= 1, outside tiers, e.g. #7 to #8 or #14 to #15): DO NOT REMEMBER
        """
        position = details.get("position") or details.get("new_ranking")
        previous_position = details.get("previous_position") or details.get("previous_ranking")
        delta = details.get("delta")

        if position is None:
            return (
                RetentionDecisionEnum.DO_NOT_REMEMBER,
                "Ranking event rejected: missing position data.",
                0.0, None, None, []
            )

        if delta is None and previous_position is not None:
            delta = previous_position - position

        # Baseline check (first time tracking)
        if previous_position is None or previous_position == 0:
            if position <= 30:
                norm = NormalizedMemoryRepresentation(
                    event="ranking_baseline_established",
                    website=website,
                    keyword=keyword,
                    date=date_str,
                    context=f"Initial tracking milestone recorded for '{website}' in query '{keyword}'.",
                    action="Initial baseline rank measurement",
                    result=f"Established baseline at Rank #{position}",
                    confidence=0.90,
                    uncertainty_factors=["Initial measurement; requires multi-cycle verification."],
                )
                return (
                    RetentionDecisionEnum.REMEMBER,
                    f"Baseline milestone: initial SERP placement established at Rank #{position}.",
                    0.75, norm, MemoryCategory.RANKING_HISTORY, ["ranking", "baseline", keyword, website]
                )
            else:
                return (
                    RetentionDecisionEnum.DO_NOT_REMEMBER,
                    f"Baseline ranking #{position} is too deep (>30) to warrant persistent institutional memory.",
                    0.20, None, None, []
                )

        delta_abs = abs(delta or 0)

        # Milestone tier crossings
        is_tier_crossing = (
            (previous_position > 3 and position <= 3)  # Top 3 visual pack
            or (previous_position <= 3 and position > 3)
            or (previous_position > 10 and position <= 10)  # Page 1 barrier
            or (previous_position <= 10 and position > 10)
        )

        if is_tier_crossing:
            direction = "entered" if position < previous_position else "dropped out of"
            tier = "Top 3 Visual Pack" if (position <= 3 or previous_position <= 3) else "Page 1 (Top 10)"
            movement_text = f"moved from #{previous_position} to #{position} ({delta:+d} positions)"
            
            norm = NormalizedMemoryRepresentation(
                event="ranking_tier_transition",
                website=website,
                keyword=keyword,
                date=date_str,
                context=f"Critical SERP barrier shift: domain {direction} {tier}.",
                action="SERP algorithm evaluation & competitor fluctuation",
                result=f"Observed ranking {movement_text}",
                confidence=0.88,
                uncertainty_factors=["SERP feature churn (snippets, maps, video carousels)."],
            )
            return (
                RetentionDecisionEnum.REMEMBER,
                f"Significant SERP milestone: domain {direction} {tier} (#{previous_position} -> #{position}).",
                0.90, norm, MemoryCategory.RANKING_HISTORY, ["ranking", "milestone", "tier_transition", keyword, website]
            )

        if delta_abs >= 2:
            movement_text = f"improved by +{delta} positions" if delta > 0 else f"dropped by {abs(delta)} positions"
            norm = NormalizedMemoryRepresentation(
                event="significant_ranking_shift",
                website=website,
                keyword=keyword,
                date=date_str,
                context=f"Observed organic ranking movement for keyword '{keyword}'.",
                action="Organic search visibility shift",
                result=f"After recent SERP updates, observed ranking moved from #{previous_position} to #{position} ({movement_text})",
                confidence=0.85,
                uncertainty_factors=["Correlational observation; daily search algorithm re-ranking."],
            )
            return (
                RetentionDecisionEnum.REMEMBER,
                f"Significant ranking movement of {delta:+d} positions (#{previous_position} -> #{position}) exceeds noise threshold.",
                0.80, norm, MemoryCategory.RANKING_HISTORY, ["ranking", "movement", keyword, website]
            )

        # Micro-fluctuations (delta <= 1 without tier crossing)
        return (
            RetentionDecisionEnum.DO_NOT_REMEMBER,
            f"Low-signal SERP micro-fluctuation (#{previous_position} -> #{position}, delta {delta:+d}) classified as normal noise.",
            0.15, None, None, []
        )

    def _evaluate_optimization_event(
        self, website: str, keyword: str, date_str: str, details: Dict[str, Any]
    ) -> Tuple[RetentionDecisionEnum, str, float, Optional[NormalizedMemoryRepresentation], Optional[MemoryCategory], List[str]]:
        """Evaluates optimizations:
        - Strategic enhancements (schemas, interactive tools, videos, architecture) -> REMEMBER
        - Cosmetic / trivial tweaks (typo fixes, whitespace, minor text churn < 50 words) -> DO NOT REMEMBER
        """
        opt_type = (details.get("optimization_type") or "general").lower()
        description = details.get("description") or details.get("action_title") or ""
        reason = details.get("reason") or details.get("reason_for_optimization") or "Strategic optimization"
        expected_effect = details.get("expected_effect") or "Improve search visibility and CTR"

        # Trivial / cosmetic checks
        trivial_keywords = ["typo", "spelling", "whitespace", "routine", "formatting", "minor copyedit", "comma"]
        desc_lower = description.lower()
        if any(t in desc_lower or t in opt_type for t in trivial_keywords):
            return (
                RetentionDecisionEnum.DO_NOT_REMEMBER,
                f"Trivial cosmetic optimization [{opt_type}: '{description[:50]}'] below persistent memory threshold.",
                0.10, None, None, []
            )

        # Word count churn below 50 words without structural changes
        word_delta = details.get("word_count_delta", 0)
        if 0 < abs(word_delta) < 50 and opt_type in ["content_update", "minor_text"]:
            return (
                RetentionDecisionEnum.DO_NOT_REMEMBER,
                f"Negligible text shift of {word_delta} words lacks strategic SEO impact.",
                0.15, None, None, []
            )

        # Significant strategic optimization
        norm = NormalizedMemoryRepresentation(
            event="optimization_performed",
            website=website,
            keyword=keyword,
            date=date_str,
            context=f"Optimization deployed for '{website}' targeting intent for keyword '{keyword}'. Reason: {reason}.",
            action=f"[{opt_type.upper()}] {description}",
            result=f"Deployed on-page enhancement. Expected direction: {expected_effect}.",
            confidence=0.85,
            uncertainty_factors=["Effect latency typically spans 14 to 30 days."],
        )
        return (
            RetentionDecisionEnum.REMEMBER,
            f"Strategic optimization [{opt_type}] with substantive on-page or schema structural leverage.",
            0.85, norm, MemoryCategory.OPTIMIZATION_HISTORY, ["optimization", opt_type, keyword, website]
        )

    def _evaluate_outcome_event(
        self, website: str, keyword: str, date_str: str, details: Dict[str, Any]
    ) -> Tuple[RetentionDecisionEnum, str, float, Optional[NormalizedMemoryRepresentation], Optional[MemoryCategory], List[str]]:
        """Evaluates causal/correlational outcomes:
        - Rigorously enforces correlational language: 'After this change, the observed ranking moved from X to Y'
        - Rejects premature checks (< 3 days with zero delta)
        """
        opt_title = details.get("optimization_title") or details.get("optimization") or "SEO Action"
        opt_type = details.get("optimization_type") or "optimization"
        rank_before = details.get("rank_before") or details.get("previous_ranking")
        rank_after = details.get("rank_after") or details.get("new_ranking")
        observed_result = details.get("observed_result") or details.get("observed_change") or "Ranking adjusted"
        time_period_days = details.get("time_period_days") or 21
        confidence = float(details.get("confidence") or 0.85)
        uncertainty = details.get("uncertainty_factors") or [
            "External SERP volatility and competitor counter-actions remain possible confounding factors"
        ]

        if rank_before is None or rank_after is None:
            return (
                RetentionDecisionEnum.DO_NOT_REMEMBER,
                "Outcome event rejected: requires both rank_before and rank_after values.",
                0.0, None, None, []
            )

        delta = rank_before - rank_after

        # Premature check filter: if checked < 3 days and zero movement, don't store premature noise
        if time_period_days < 3 and delta == 0:
            return (
                RetentionDecisionEnum.DO_NOT_REMEMBER,
                f"Premature outcome observation ({time_period_days} days) with zero ranking movement; insufficient time for crawl/indexing.",
                0.20, None, None, []
            )

        # STRICT CORRELATIONAL TRUTH DISCIPLINE
        correlational_result_text = (
            f"After this change ('{opt_title}' [{opt_type}]), the observed ranking moved from "
            f"#{rank_before} to #{rank_after} ({observed_result}) over a {time_period_days}-day latency window."
        )

        norm = NormalizedMemoryRepresentation(
            event="outcome_observed",
            website=website,
            keyword=keyword,
            date=date_str,
            context=f"Post-optimization tracking window ({time_period_days} days) for '{website}' on keyword '{keyword}'.",
            action=f"Deployed change: '{opt_title}' ({opt_type})",
            result=correlational_result_text,
            confidence=confidence,
            uncertainty_factors=uncertainty,
            language_discipline_note="Correlational observation: 'After this change, the observed ranking moved from X to Y' - no definitive causality asserted.",
        )

        return (
            RetentionDecisionEnum.REMEMBER,
            f"Empirical outcome recorded: observed ranking moved from #{rank_before} to #{rank_after} following '{opt_title}'.",
            0.95, norm, MemoryCategory.OUTCOME_HISTORY, ["outcome", "correlation", opt_type, keyword, website]
        )

    def _evaluate_competitor_event(
        self, website: str, keyword: str, date_str: str, details: Dict[str, Any]
    ) -> Tuple[RetentionDecisionEnum, str, float, Optional[NormalizedMemoryRepresentation], Optional[MemoryCategory], List[str]]:
        """Evaluates competitor changes:
        - Major changes (new features, video previews, schemas, rank surges) -> REMEMBER
        - Negligible competitor noise -> DO NOT REMEMBER
        """
        competitor = details.get("competitor_domain") or website
        content_changes = details.get("content_changes") or []
        feature_changes = details.get("feature_changes") or []
        seo_changes = details.get("notable_seo_changes") or []
        ranking_changes = details.get("ranking_changes") or {}

        has_substance = bool(content_changes or feature_changes or seo_changes or ranking_changes)
        if not has_substance:
            return (
                RetentionDecisionEnum.DO_NOT_REMEMBER,
                f"Competitor event for '{competitor}' has no measurable content or feature modifications.",
                0.10, None, None, []
            )

        summary_parts = []
        if content_changes:
            summary_parts.append(f"Content: {', '.join(content_changes)}")
        if feature_changes:
            summary_parts.append(f"Features: {', '.join(feature_changes)}")
        if seo_changes:
            summary_parts.append(f"SEO/Schemas: {', '.join(seo_changes)}")

        delta = ranking_changes.get("delta", 0)
        rank_text = f"rank delta {delta:+d}" if delta != 0 else "rank maintained"

        norm = NormalizedMemoryRepresentation(
            event="competitor_change",
            website=competitor,
            keyword=keyword,
            date=date_str,
            context=f"Competitor intelligence gathered for '{competitor}' competing in query '{keyword}'.",
            action=f"Competitor modifications: {'; '.join(summary_parts)}",
            result=f"Competitor {rank_text} in SERP ranking.",
            confidence=0.82,
            uncertainty_factors=["Observed via external crawl; partial visibility into internal experiments."],
        )

        return (
            RetentionDecisionEnum.REMEMBER,
            f"Competitor '{competitor}' deployed substantive updates altering SERP competition.",
            0.85, norm, MemoryCategory.COMPETITOR_HISTORY, ["competitor", competitor, keyword]
        )

    def _evaluate_recommendation_event(
        self, website: str, keyword: str, date_str: str, details: Dict[str, Any]
    ) -> Tuple[RetentionDecisionEnum, str, float, Optional[NormalizedMemoryRepresentation], Optional[MemoryCategory], List[str]]:
        """Tracks when a recommendation is accepted or rejected by user/strategist."""
        rec_id = details.get("recommendation_id", "rec_general")
        title = details.get("title", "Recommendation")
        action = details.get("decision", "ACCEPTED").upper()
        reason = details.get("reason", "Strategist prioritization")

        norm = NormalizedMemoryRepresentation(
            event="recommendation_decision",
            website=website,
            keyword=keyword,
            date=date_str,
            context=f"Strategist decision recorded for recommendation '{rec_id}'.",
            action=f"Recommendation [{title}] was marked as {action}",
            result=f"Decision: {action}. Strategic reason: {reason}.",
            confidence=0.95,
            uncertainty_factors=["Human workflow decision."],
        )

        return (
            RetentionDecisionEnum.REMEMBER,
            f"User/Strategist {action.lower()} recommendation '{title}'; retained to guide future recommendations.",
            0.75, norm, MemoryCategory.OPTIMIZATION_HISTORY, ["recommendation_decision", action.lower(), website, keyword]
        )

    def _evaluate_user_feedback(
        self, website: str, keyword: str, date_str: str, details: Dict[str, Any]
    ) -> Tuple[RetentionDecisionEnum, str, float, Optional[NormalizedMemoryRepresentation], Optional[MemoryCategory], List[str]]:
        """Tracks user feedback on analysis quality."""
        feedback_text = details.get("feedback_text", "")
        rating = details.get("rating", 5)

        if not feedback_text and rating is None:
            return (
                RetentionDecisionEnum.DO_NOT_REMEMBER,
                "User feedback event contains no text or score.",
                0.0, None, None, []
            )

        norm = NormalizedMemoryRepresentation(
            event="user_feedback",
            website=website,
            keyword=keyword,
            date=date_str,
            context=f"User feedback provided for SEO analysis on domain '{website}'.",
            action=f"User rating: {rating}/5",
            result=f"Feedback: \"{feedback_text}\"",
            confidence=0.90,
            uncertainty_factors=["Subjective user feedback."],
        )

        return (
            RetentionDecisionEnum.REMEMBER,
            f"User feedback received (rating {rating}/5); retained for agent quality refinement.",
            0.70, norm, MemoryCategory.OPTIMIZATION_HISTORY, ["feedback", website, keyword]
        )

    # =========================================================================
    # DEDUPLICATION & REJECTION HANDLING
    # =========================================================================

    def _compute_event_fingerprint(
        self, event_type: str, website: str, keyword: str, details: Dict[str, Any]
    ) -> str:
        """Generates deterministic hash based on normalized core parameters to identify duplicate events."""
        # Key discriminators
        core_tokens = []
        if event_type in ["ranking_change", "ranking_milestone", "ranking"]:
            pos = details.get("position") or details.get("new_ranking")
            prev = details.get("previous_position") or details.get("previous_ranking")
            core_tokens = [str(prev), str(pos)]
        elif event_type in ["optimization_performed", "seo_optimization", "optimization"]:
            opt_type = details.get("optimization_type", "")
            desc = details.get("description", "")[:40]
            core_tokens = [opt_type, desc]
        elif event_type in ["outcome_observed", "outcome", "causal_attribution"]:
            opt = details.get("optimization_title", "")[:30]
            r_before = details.get("rank_before", "")
            r_after = details.get("rank_after", "")
            core_tokens = [opt, str(r_before), str(r_after)]
        elif event_type in ["competitor_change", "competitor_move", "competitor"]:
            comp = details.get("competitor_domain", website)
            seo_c = details.get("notable_seo_changes", [])
            core_tokens = [comp, str(seo_c)]
        else:
            core_tokens = [json.dumps(details, sort_keys=True)]

        raw_str = f"{website.lower()}|{keyword.lower()}|{event_type}|{'|'.join(core_tokens)}".strip()
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]

    def _check_duplicate(
        self, fingerprint: str, website: str, keyword: str, event_type: str
    ) -> Tuple[bool, str]:
        """Checks if an identical event has already been retained in Hindsight."""
        with get_connection(self.db_path) as conn:
            # Check previously accepted decisions
            row = conn.execute(
                """
                SELECT id, timestamp, reason FROM hindsight_retention_decisions
                WHERE fingerprint = ? AND decision = 'REMEMBER'
                LIMIT 1
                """,
                (fingerprint,),
            ).fetchone()

            if row:
                return (
                    True,
                    f"Meaningless duplicate event: identical {event_type} for '{website}' on '{keyword}' "
                    f"has already been retained into memory (fingerprint: {fingerprint}, original decision ID: {row['id']})."
                )

        return False, ""

    def _record_rejection(
        self,
        event_type: str,
        website: str,
        keyword: str,
        date_str: str,
        reason: str,
        fingerprint: str,
        importance_score: float,
    ) -> RetentionDecisionResult:
        """Logs a DO NOT REMEMBER decision in the developer audit log and returns result."""
        self._log_decision(
            event_type=event_type,
            website=website,
            keyword=keyword,
            decision="DO NOT REMEMBER",
            reason=reason,
            importance_score=importance_score,
            fingerprint=fingerprint,
            content_snippet=None,
            normalized_data={"status": "rejected", "reason": reason},
            timestamp=date_str,
        )

        return RetentionDecisionResult(
            decision=RetentionDecisionEnum.DO_NOT_REMEMBER,
            reason=reason,
            importance_score=importance_score,
            event_type=event_type,
            website=website,
            keyword=keyword,
            deduplication_fingerprint=fingerprint,
            normalized_memory=None,
            retained_memory_item=None,
        )

    def _format_retained_content(self, norm: NormalizedMemoryRepresentation) -> str:
        """Formats the normalized memory representation into a dense, verifiable statement."""
        return (
            f"[{norm.event.upper()}] On {norm.date[:10]} for '{norm.website}' on '{norm.keyword}': "
            f"Action: {norm.action}. Result: {norm.result}. "
            f"Context: {norm.context} "
            f"(Confidence: {int(norm.confidence * 100)}%. "
            f"Confounders: {', '.join(norm.uncertainty_factors) if norm.uncertainty_factors else 'None noted'})."
        )

    def _log_decision(
        self,
        event_type: str,
        website: str,
        keyword: str,
        decision: str,
        reason: str,
        importance_score: float,
        fingerprint: str,
        content_snippet: Optional[str],
        normalized_data: Dict[str, Any],
        timestamp: str,
    ):
        """Stores decision in developer-visible SQLite audit table."""
        dec_id = f"dec_{uuid.uuid4().hex[:8]}"
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO hindsight_retention_decisions (
                    id, timestamp, bank_id, event_type, website, keyword, decision, reason, importance_score, fingerprint, content_snippet, normalized_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dec_id,
                    timestamp,
                    "rankmind-seo",
                    event_type,
                    website,
                    keyword,
                    decision,
                    reason,
                    importance_score,
                    fingerprint,
                    content_snippet,
                    json.dumps(normalized_data),
                ),
            )


event_processing_layer = EventProcessingLayer()
