from typing import List, Dict, Any, Optional
from app.models.schemas import SERPSnapshot, CompetitorDiff, SERPItem


class DiffEngine:
    """Computes shifts between SERP snapshots and extracts competitor changes."""

    @staticmethod
    def compare_snapshots(snap_before: SERPSnapshot, snap_after: SERPSnapshot) -> List[CompetitorDiff]:
        diffs: List[CompetitorDiff] = []
        before_map: Dict[str, SERPItem] = {item.domain: item for item in snap_before.items}
        after_map: Dict[str, SERPItem] = {item.domain: item for item in snap_after.items}

        for domain, after_item in after_map.items():
            if domain in before_map:
                before_item = before_map[domain]
                rank_delta = before_item.rank - after_item.rank  # Positive = rank improved (e.g. 5 - 3 = +2)
                changes: List[str] = []
                shifts: Dict[str, Any] = {}

                # Check interactive widgets
                if not before_item.has_interactive_widget and after_item.has_interactive_widget:
                    changes.append("Introduced interactive tool or code widget")
                    shifts["has_interactive_widget"] = True
                elif before_item.has_interactive_widget and not after_item.has_interactive_widget:
                    changes.append("Removed interactive tool")
                    shifts["has_interactive_widget"] = False

                # Check video previews
                if not before_item.has_video_preview and after_item.has_video_preview:
                    changes.append("Added video curriculum / project previews")
                    shifts["has_video_preview"] = True

                # Check curriculum / syllabus matrix
                if not before_item.has_curriculum_table and after_item.has_curriculum_table:
                    changes.append("Structured comparison table or syllabus matrix added")
                    shifts["has_curriculum_table"] = True

                # Check schema changes
                new_schemas = set(after_item.schema_types) - set(before_item.schema_types)
                if new_schemas:
                    changes.append(f"Implemented new structured schemas: {', '.join(new_schemas)}")
                    shifts["new_schemas"] = list(new_schemas)

                # Check significant word count changes
                word_delta = after_item.word_count - before_item.word_count
                if abs(word_delta) >= 500:
                    changes.append(f"Content volume changed by {word_delta:+d} words")
                    shifts["word_count_delta"] = word_delta

                if changes or rank_delta != 0:
                    diffs.append(
                        CompetitorDiff(
                            id=f"diff_{snap_before.cycle_index}_{snap_after.cycle_index}_{domain.replace('.', '_')}",
                            query=snap_after.query,
                            domain=domain,
                            cycle_from=snap_before.cycle_index,
                            cycle_to=snap_after.cycle_index,
                            rank_delta=rank_delta,
                            changes_detected=changes if changes else ["Rank re-adjustment by search algorithm"],
                            feature_shifts=shifts,
                        )
                    )

        return diffs


diff_engine = DiffEngine()
