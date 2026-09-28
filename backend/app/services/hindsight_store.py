import json
from pathlib import Path
from typing import List, Optional, Dict
from app.core.config import DATA_DIR
from app.models.schemas import (
    SERPSnapshot,
    OptimizationAction,
    CompetitorDiff,
    MemoryNode,
    AuditReport,
)
from app.seed.scenarios import (
    SEED_QUERY,
    SEED_TARGET_DOMAIN,
    SNAPSHOT_0,
    SNAPSHOT_1,
    SNAPSHOT_2,
    SNAPSHOT_3_CURRENT,
    ACTION_1,
    ACTION_2,
    COMPETITOR_DIFF_1,
    MEMORY_NODE_1,
    MEMORY_NODE_2,
    SEED_RECOMMENDATIONS,
)


class HindsightStore:
    """Persistent storage for SERP snapshots, optimization actions, and learned memory nodes."""

    def __init__(self):
        self.snapshots_file = DATA_DIR / "snapshots.json"
        self.actions_file = DATA_DIR / "actions.json"
        self.diffs_file = DATA_DIR / "diffs.json"
        self.memory_file = DATA_DIR / "memory_nodes.json"
        self._initialize_storage()

    def _initialize_storage(self):
        """Initializes storage files with realistic seed data if not already present."""
        if not self.snapshots_file.exists():
            self._save_json(
                self.snapshots_file,
                [
                    SNAPSHOT_0.model_dump(),
                    SNAPSHOT_1.model_dump(),
                    SNAPSHOT_2.model_dump(),
                    SNAPSHOT_3_CURRENT.model_dump(),
                ],
            )
        if not self.actions_file.exists():
            self._save_json(
                self.actions_file,
                [
                    ACTION_1.model_dump(),
                    ACTION_2.model_dump(),
                ],
            )
        if not self.diffs_file.exists():
            self._save_json(
                self.diffs_file,
                [
                    COMPETITOR_DIFF_1.model_dump(),
                ],
            )
        if not self.memory_file.exists():
            self._save_json(
                self.memory_file,
                [
                    MEMORY_NODE_1.model_dump(),
                    MEMORY_NODE_2.model_dump(),
                ],
            )

    def _read_json(self, path: Path) -> List[Dict]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_json(self, path: Path, data: List[Dict]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_snapshots(self, query: str) -> List[SERPSnapshot]:
        raw = self._read_json(self.snapshots_file)
        return [SERPSnapshot(**s) for s in raw if s.get("query").lower() == query.lower()]

    def get_latest_snapshot(self, query: str) -> Optional[SERPSnapshot]:
        snaps = self.get_snapshots(query)
        if not snaps:
            return None
        return sorted(snaps, key=lambda s: s.cycle_index, reverse=True)[0]

    def add_snapshot(self, snapshot: SERPSnapshot):
        raw = self._read_json(self.snapshots_file)
        raw.append(snapshot.model_dump())
        self._save_json(self.snapshots_file, raw)

    def get_actions(self, query: str) -> List[OptimizationAction]:
        raw = self._read_json(self.actions_file)
        return [OptimizationAction(**a) for a in raw if a.get("query").lower() == query.lower()]

    def add_action(self, action: OptimizationAction):
        raw = self._read_json(self.actions_file)
        raw.append(action.model_dump())
        self._save_json(self.actions_file, raw)

    def get_diffs(self, query: str) -> List[CompetitorDiff]:
        raw = self._read_json(self.diffs_file)
        return [CompetitorDiff(**d) for d in raw if d.get("query").lower() == query.lower()]

    def add_diff(self, diff: CompetitorDiff):
        raw = self._read_json(self.diffs_file)
        raw.append(diff.model_dump())
        self._save_json(self.diffs_file, raw)

    def get_memory_nodes(self, query: str) -> List[MemoryNode]:
        raw = self._read_json(self.memory_file)
        return [MemoryNode(**m) for m in raw if m.get("query").lower() == query.lower()]

    def add_memory_node(self, node: MemoryNode):
        raw = self._read_json(self.memory_file)
        raw.append(node.model_dump())
        self._save_json(self.memory_file, raw)

    def reset_demo(self):
        """Resets the state back to the original seed scenarios."""
        self._save_json(
            self.snapshots_file,
            [
                SNAPSHOT_0.model_dump(),
                SNAPSHOT_1.model_dump(),
                SNAPSHOT_2.model_dump(),
                SNAPSHOT_3_CURRENT.model_dump(),
            ],
        )
        self._save_json(
            self.actions_file,
            [
                ACTION_1.model_dump(),
                ACTION_2.model_dump(),
            ],
        )
        self._save_json(
            self.diffs_file,
            [
                COMPETITOR_DIFF_1.model_dump(),
            ],
        )
        self._save_json(
            self.memory_file,
            [
                MEMORY_NODE_1.model_dump(),
                MEMORY_NODE_2.model_dump(),
            ],
        )


hindsight_store = HindsightStore()
