from typing import List, Optional
import uuid
from app.models.schemas import (
    OptimizationAction,
    SERPSnapshot,
    MemoryNode,
    AttributionVerdict,
    CompetitorDiff,
    ActionCategory,
)
from app.services.diff_engine import diff_engine


class AttributionEngine:
    """Evaluates optimization actions against rank outcomes and synthesizes empirical lessons."""

    @staticmethod
    def evaluate_action(
        action: OptimizationAction,
        snap_before: SERPSnapshot,
        snap_after: SERPSnapshot,
        competitor_diffs: List[CompetitorDiff],
    ) -> MemoryNode:
        # Find target domain rank in before snapshot
        before_item = next(
            (item for item in snap_before.items if item.domain == action.target_domain), None
        )
        # Find target domain rank in after snapshot
        after_item = next(
            (item for item in snap_after.items if item.domain == action.target_domain), None
        )

        rank_before = before_item.rank if before_item else 10
        rank_after = after_item.rank if after_item else 10
        rank_delta = rank_before - rank_after  # e.g., 8 - 3 = +5 improvement

        # Check for confounding competitor moves
        major_competitor_moves = [
            d for d in competitor_diffs
            if d.domain != action.target_domain and (d.rank_delta > 1 or len(d.changes_detected) > 1)
        ]

        # Calculate verdict and confidence
        if rank_delta >= 2:
            verdict = AttributionVerdict.CONFIRMED_POSITIVE
            confidence = 0.95 if not major_competitor_moves else 0.82
        elif rank_delta <= -2:
            if major_competitor_moves:
                verdict = AttributionVerdict.CONFOUNDED
                confidence = 0.70
            else:
                verdict = AttributionVerdict.CONFIRMED_NEGATIVE
                confidence = 0.85
        else:
            verdict = AttributionVerdict.NEUTRAL
            confidence = 0.90

        # Generate distilled lesson based on category and outcome
        lesson = AttributionEngine._distill_lesson(
            action=action,
            rank_delta=rank_delta,
            rank_before=rank_before,
            rank_after=rank_after,
            verdict=verdict,
        )

        return MemoryNode(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            query=action.query,
            target_domain=action.target_domain,
            action_id=action.id,
            action_category=action.category,
            action_title=action.title,
            date_applied=action.timestamp[:10],
            date_evaluated=snap_after.timestamp[:10],
            latency_days=21,
            rank_before=rank_before,
            rank_after=rank_after,
            rank_delta=rank_delta,
            verdict=verdict,
            confidence_score=confidence,
            agent_distilled_lesson=lesson,
        )

    @staticmethod
    def _distill_lesson(
        action: OptimizationAction,
        rank_delta: int,
        rank_before: int,
        rank_after: int,
        verdict: AttributionVerdict,
    ) -> str:
        if verdict == AttributionVerdict.CONFIRMED_POSITIVE:
            return (
                f"Action '{action.title}' delivered a +{rank_delta} position surge (#{rank_before} → #{rank_after}). "
                f"For query intent '{action.query}', {action.category.value.replace('_', ' ')} changes produced "
                f"statistically decisive ranking gains. Prioritize similar experiential upgrades."
            )
        elif verdict == AttributionVerdict.NEUTRAL:
            return (
                f"Action '{action.title}' produced zero rank delta (remained #{rank_after}). "
                f"In this search ecosystem, {action.category.value.replace('_', ' ')} alone does not differentiate "
                f"against top competitors. Avoid repeating this without structural or utility enhancements."
            )
        elif verdict == AttributionVerdict.CONFOUNDED:
            return (
                f"Rank shifted to #{rank_after} ({rank_delta:+d}), but concurrent competitor upgrades "
                f"confounded direct attribution. Re-evaluating next cycle after SERP stabilizes."
            )
        else:
            return (
                f"Rank declined ({rank_delta:+d}) following '{action.title}'. "
                f"Audit for search intent mismatch or cannibalization."
            )


attribution_engine = AttributionEngine()
