import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset
from app.services.hindsight.client import hindsight_client
from app.services.hindsight.memory_manager import hindsight_memory_manager
from app.models.hindsight_schemas import MemoryCategory


class TestHindsightPersistentMemory(unittest.TestCase):
    """Test suite verifying Hindsight Persistent Memory Integration:
    
    1. Retention across 4 core categories:
       - RANKING HISTORY
       - OPTIMIZATION HISTORY
       - COMPETITOR HISTORY
       - OUTCOME HISTORY
    2. Category-stratified recall with relevance scoring and 'why relevant' attribution.
    3. Developer audit logs for retention and recall.
    4. Memory-augmented SEO analysis with suppressed failed tactics.
    5. Side-by-side comparison: Baseline vs Hindsight.
    6. Developer Studio UI.
    """

    @classmethod
    def setUpClass(cls):
        populate_synthetic_seo_dataset(reset=True)
        hindsight_memory_manager.sync_database_to_hindsight()
        cls.client = TestClient(app)

    def test_retention_all_four_categories(self):
        """1. Verify retention of all 4 mandatory memory categories."""
        # 1. Ranking History
        mem_rank = hindsight_memory_manager.retain_ranking_milestone(
            domain="testsite.io",
            keyword="python web development",
            date_str="2026-09-20",
            position=6,
            previous_position=10,
            change=4,
        )
        self.assertEqual(mem_rank.category, MemoryCategory.RANKING_HISTORY)
        self.assertIn("improved by +4 positions", mem_rank.content)
        self.assertEqual(mem_rank.metadata["delta"], 4)

        # 2. Optimization History
        mem_opt = hindsight_memory_manager.retain_optimization_event(
            domain="testsite.io",
            keyword="python web development",
            optimization_type="structured_schema",
            description="Added TechArticle schema with code snippets",
            reason="Improve developer CTR in code search snippets",
            expected_effect="Rich card display",
            date_str="2026-09-15",
        )
        self.assertEqual(mem_opt.category, MemoryCategory.OPTIMIZATION_HISTORY)
        self.assertIn("Added TechArticle schema", mem_opt.content)
        self.assertIn("optimization", mem_opt.tags)

        # 3. Competitor History
        mem_comp = hindsight_memory_manager.retain_competitor_event(
            competitor_domain="rivalcourses.com",
            keyword="python web development",
            content_changes=["Added 10 code walkthroughs"],
            feature_changes=["Launched free IDE runner"],
            notable_seo_changes=["Added Course schema"],
            ranking_changes={"rank_before": 5, "rank_after": 2, "delta": 3},
            date_str="2026-09-18",
        )
        self.assertEqual(mem_comp.category, MemoryCategory.COMPETITOR_HISTORY)
        self.assertIn("rivalcourses.com", mem_comp.content)
        self.assertIn("competitor", mem_comp.tags)

        # 4. Outcome History (Causal Attribution)
        mem_out = hindsight_memory_manager.retain_outcome_attribution(
            domain="testsite.io",
            keyword="python web development",
            optimization_title="Added TechArticle schema",
            optimization_type="structured_schema",
            rank_before=10,
            rank_after=6,
            observed_result="Rank improved by +4 positions",
            time_period_days=14,
            confidence=0.88,
            uncertainty_factors=["Minor seasonal developer search lift"],
            date_str="2026-09-25",
        )
        self.assertEqual(mem_out.category, MemoryCategory.OUTCOME_HISTORY)
        self.assertEqual(mem_out.metadata["verdict"], "CONFIRMED_POSITIVE")
        self.assertEqual(mem_out.metadata["confidence"], 0.88)
        self.assertIn("causal", mem_out.tags)

    def test_recall_relevance_and_attribution(self):
        """2. Verify that recall retrieves relevant memories with relevance scores and 'why relevant' reasons."""
        res = self.client.get(
            "/api/v1/hindsight/recall",
            params={
                "query": "best python courses for beginners",
                "domain": "learnpythonhub.io",
                "max_memories": 6,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["query"], "best python courses for beginners")
        self.assertEqual(data["target_domain"], "learnpythonhub.io")
        self.assertGreater(data["total_recalled"], 0)
        self.assertLessEqual(data["total_recalled"], 6)

        # Verify each recalled memory has relevance score and why_relevant explanation
        for m in data["memories"]:
            self.assertIn("id", m)
            self.assertIn("category", m)
            self.assertIn("content", m)
            self.assertGreaterEqual(m["relevance_score"], 0.25)
            self.assertIsNotNone(m["why_relevant"])
            self.assertGreater(len(m["why_relevant"]), 5)

        # Verify that causal outcome memories have high relevance (1.0 or category boost)
        outcome_mems = [m for m in data["memories"] if m["category"] == "outcome_history"]
        self.assertGreater(len(outcome_mems), 0)
        self.assertGreaterEqual(outcome_mems[0]["relevance_score"], 0.8)
        self.assertIn("Empirical causal outcome record", outcome_mems[0]["why_relevant"])

    def test_developer_audit_logging(self):
        """3. Verify developer audit logs for retention and recall events."""
        res = self.client.get("/api/v1/hindsight/logs?log_type=all&limit=20")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("retention_logs", data)
        self.assertIn("recall_logs", data)
        self.assertGreater(len(data["retention_logs"]), 0)
        self.assertGreater(len(data["recall_logs"]), 0)

        # Inspect retention log structure
        ret_sample = data["retention_logs"][0]
        self.assertIn("id", ret_sample)
        self.assertIn("category", ret_sample)
        self.assertIn("content_snippet", ret_sample)
        self.assertIn("tags", ret_sample)

        # Inspect recall log structure
        rec_sample = data["recall_logs"][0]
        self.assertIn("id", rec_sample)
        self.assertIn("query", rec_sample)
        self.assertIn("recalled_count", rec_sample)
        self.assertIn("why_relevant_summary", rec_sample)

    def test_memory_augmented_analysis_flow(self):
        """4. Verify full memory-augmented analysis flow:
        CURRENT DATA + RECALLED MEMORY -> LLM REASONING -> CONTEXT-AWARE RECOMMENDATION.
        """
        payload = {
            "query": "best python courses for beginners",
            "provider": "local",
            "max_memories": 6,
        }

        res = self.client.post("/api/v1/hindsight/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data["hindsight_memory_applied"])
        self.assertEqual(data["target_domain"], "learnpythonhub.io")

        # 1. Recalled Memories with why_relevant
        self.assertGreater(len(data["recalled_memories"]), 0)
        for m in data["recalled_memories"]:
            self.assertIsNotNone(m["why_relevant"])

        # 2. Suppressed Tactics (Generic advice explicitly rejected due to past empirical failure)
        self.assertGreater(len(data["suppressed_tactics"]), 0)
        suppressed_text = " ".join(data["suppressed_tactics"])
        self.assertIn("Passive Word Count Expansion", suppressed_text)

        # 3. Context-Aware Recommendations citing memory
        self.assertGreater(len(data["context_aware_recommendations"]), 0)
        rec_titles = [r["title"] for r in data["context_aware_recommendations"]]
        rec_text = " ".join(rec_titles)
        # Should prioritize Course Schema and Video Walkthroughs over word-count expansion
        self.assertTrue("Course" in rec_text or "Video" in rec_text)

        # 4. Strategic Contrast Summary
        self.assertIsNotNone(data["baseline_vs_hindsight_contrast"])
        self.assertIn("Hindsight memory proves", data["baseline_vs_hindsight_contrast"])

    def test_baseline_vs_hindsight_compare_endpoint(self):
        """5. Verify the side-by-side comparison endpoint showing how memory transforms recommendations."""
        res = self.client.get(
            "/api/v1/hindsight/compare",
            params={"query": "best python courses for beginners"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("baseline_stateless", data)
        self.assertIn("hindsight_augmented", data)
        self.assertIn("strategic_contrast_summary", data)

        # Verify baseline has no memory
        self.assertFalse(data["baseline_stateless"]["hindsight_memory_applied"])

        # Verify hindsight has memory applied and suppressed tactics
        self.assertTrue(data["hindsight_augmented"]["hindsight_memory_applied"])
        self.assertGreater(len(data["hindsight_augmented"]["suppressed_tactics"]), 0)
        self.assertGreater(len(data["hindsight_augmented"]["recalled_memories_sample"]), 0)

    def test_hindsight_developer_studio_ui(self):
        """6. Verify that the interactive Developer Studio HTML UI renders successfully."""
        res = self.client.get("/hindsight")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Hindsight Memory Studio", res.text)
        self.assertIn("Baseline vs Hindsight Contrast", res.text)
        self.assertIn("Query Recall Inspector", res.text)
        self.assertIn("Memory Bank Explorer", res.text)
        self.assertIn("Developer Audit Logs", res.text)


if __name__ == "__main__":
    unittest.main()
