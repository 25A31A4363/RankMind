import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset
from app.services.hindsight.client import hindsight_client
from app.services.hindsight.memory_manager import hindsight_memory_manager
from app.services.learning_loop_service import learning_loop_service
from app.models.learning_loop_schemas import (
    RecordActionRequest,
    RecordMeasureRequest,
    LearningLoopStage,
)
from app.models.hindsight_schemas import MemoryCategory


class TestCompleteSEOLearningLoop(unittest.TestCase):
    """Test suite verifying the complete closed SEO Learning Loop:
    
    1. SEARCH: User enters query.
    2. ANALYZE: Current on-page signals analyzed.
    3. RECALL: Relevant memories recalled across 8 dimensions.
    4. REASON: LLM combines current information and historical memory.
    5. RECOMMEND: Agent provides evidence-based recommendations.
    6. ACTION: User records an optimization/action.
    7. MEASURE: System records later observed ranking/result.
    8. RETAIN: The new outcome is stored in Hindsight.
    9. LEARN: Future recommendations use this newly retained experience.
    
    Also tests:
    - Explicit website event timeline.
    - Structured 'Learning History' view (Previous state -> Action -> Later state -> Memory created -> Future influence).
    - Before / After contrast mode (Generic baseline vs Context-aware Hindsight).
    - Interactive Cockpit UI (/learning-loop).
    """

    @classmethod
    def setUpClass(cls):
        populate_synthetic_seo_dataset(reset=True)
        hindsight_memory_manager.sync_database_to_hindsight()
        cls.client = TestClient(app)

    def test_complete_learning_loop_steps_one_through_nine(self):
        """1. Verify the full 9-step learning loop execution from Search to Learn."""
        # Steps 1 to 5: Run Search, Analyze, Recall, Reason, and Recommend
        search_res = self.client.post(
            "/api/v1/hindsight/analyze",
            json={
                "query": "best python courses for beginners",
                "url": "https://learnpythonhub.io/courses",
                "current_position": 8,
                "provider": "local",
                "max_memories": 6,
            },
        )
        self.assertEqual(search_res.status_code, 200)
        data_initial = search_res.json()
        self.assertTrue(data_initial["hindsight_memory_applied"])
        self.assertGreater(len(data_initial["context_aware_recommendations"]), 0)

        # Step 6: ACTION - User records an optimization action
        action_payload = {
            "website": "learnpythonhub.io",
            "keyword": "best python courses for beginners",
            "optimization_type": "interactive_ux",
            "title": "Embedded Interactive Code Sandbox",
            "description": "Deployed runnable Python REPL editor directly below lesson modules.",
            "reason": "Provide active learning engagement to increase dwell time.",
            "expected_effect": "Anticipate +3 to +5 ranking surge into top 5.",
        }
        action_res = self.client.post("/api/v1/learning-loop/action", json=action_payload)
        self.assertEqual(action_res.status_code, 201)
        action_data = action_res.json()
        self.assertEqual(action_data["status"], "success")
        self.assertEqual(action_data["stage"], "ACTION")
        self.assertEqual(action_data["step_number"], 6)
        action_id = action_data["action_id"]
        self.assertIsNotNone(action_id)

        # Steps 7 & 8: MEASURE & RETAIN - System records later observed ranking and retains into Hindsight
        measure_payload = {
            "website": "learnpythonhub.io",
            "keyword": "best python courses for beginners",
            "action_id": action_id,
            "optimization_title": "Embedded Interactive Code Sandbox",
            "optimization_type": "interactive_ux",
            "previous_ranking": 8,
            "new_ranking": 5,
            "observed_result": "Rank moved from #8 to #5 (+3 positions)",
            "time_period_days": 14,
            "confidence": 0.95,
            "uncertainty_factors": ["Normal seasonal search traffic"],
        }
        measure_res = self.client.post("/api/v1/learning-loop/measure", json=measure_payload)
        self.assertEqual(measure_res.status_code, 201)
        measure_data = measure_res.json()
        self.assertEqual(measure_data["status"], "success")
        self.assertEqual(measure_data["previous_ranking"], 8)
        self.assertEqual(measure_data["new_ranking"], 5)
        self.assertEqual(measure_data["rank_delta"], 3)
        self.assertEqual(measure_data["gatekeeper_decision"], "REMEMBER")
        self.assertIsNotNone(measure_data["retained_memory"])

        # Step 9: LEARN - Future recommendations recall this newly retained experience
        recalled = hindsight_client.recall(
            query="best python courses for beginners",
            target_domain="learnpythonhub.io",
            max_memories=6,
        )
        self.assertGreater(len(recalled), 0)
        recalled_texts = [m.content for m in recalled]
        # Verify that an outcome recording movement from #8 to #5 is in memory
        self.assertTrue(any("#8 to #5" in text or "#8" in text for text in recalled_texts))

    def test_website_event_timeline(self):
        """2. Verify explicit chronological event timeline generation for a website."""
        res = self.client.get(
            "/api/v1/learning-loop/timeline",
            params={"website": "learnpythonhub.io", "keyword": "best python courses for beginners"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["website"], "learnpythonhub.io")
        self.assertEqual(data["keyword"], "best python courses for beginners")
        self.assertGreaterEqual(data["total_events"], 7)

        # Check that steps are sequential from 1 through 9
        stages = [e["stage"] for e in data["timeline"]]
        self.assertIn("SEARCH", stages)
        self.assertIn("ANALYZE", stages)
        self.assertIn("RECALL", stages)
        self.assertIn("REASON", stages)
        self.assertIn("RECOMMEND", stages)
        self.assertIn("ACTION", stages)
        self.assertIn("MEASURE", stages)
        self.assertIn("RETAIN", stages)
        self.assertIn("LEARN", stages)

        # Verify state snapshots contain ranking information
        has_rank_snapshot = any("ranking" in e["state_snapshot"] for e in data["timeline"])
        self.assertTrue(has_rank_snapshot)

    def test_learning_history_view(self):
        """3. Verify structured Learning History view showing:
        Previous state -> Action -> Later state -> Memory created -> Future influence.
        """
        res = self.client.get(
            "/api/v1/learning-loop/history",
            params={"website": "learnpythonhub.io"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["website"], "learnpythonhub.io")
        self.assertGreaterEqual(data["total_cycles"], 2)

        for it in data["items"]:
            # Check 1: Previous State
            self.assertIn("previous_state", it)
            self.assertIn("ranking", it["previous_state"])

            # Check 2: Action
            self.assertIn("action", it)
            self.assertIn("title", it["action"])
            self.assertIn("description", it["action"])
            self.assertIn("optimization_type", it["action"])

            # Check 3: Later Observed State
            self.assertIn("later_observed_state", it)
            self.assertIn("ranking", it["later_observed_state"])
            self.assertIn("ranking_delta", it["later_observed_state"])
            self.assertIn("observed_result", it["later_observed_state"])

            # Check 4: Memory Created
            self.assertIn("memory_created", it)
            self.assertIn("memory_id", it["memory_created"])
            self.assertIn("verdict", it["memory_created"])
            self.assertIn("observational_caveat", it["memory_created"])

            # Check 5: Future Recommendation Influenced By Memory
            self.assertIn("future_recommendation_influenced_by_memory", it)
            self.assertGreater(len(it["future_recommendation_influenced_by_memory"]), 10)

        # Verify Cycle 1 proves passive text ineffective
        cycle1 = data["items"][0]
        self.assertEqual(cycle1["action"]["optimization_type"], "content_depth")
        self.assertEqual(cycle1["later_observed_state"]["ranking_delta"], 0)
        self.assertIn("SUPPRESSED", cycle1["future_recommendation_influenced_by_memory"])

        # Verify Cycle 2 proves interactive sandbox success
        cycle2 = data["items"][1]
        self.assertEqual(cycle2["action"]["optimization_type"], "interactive_ux")
        self.assertEqual(cycle2["later_observed_state"]["ranking_delta"], 5)
        self.assertIn("interactive", cycle2["future_recommendation_influenced_by_memory"].lower())

    def test_before_after_mode_contrast(self):
        """4. Verify visually obvious Before / After comparison mode:
        BEFORE MEMORY: Generic SEO analysis (word count fluff, zero history).
        AFTER MEMORY: Historical context + personalized recommendation (suppressed tactics, cited evidence).
        """
        res = self.client.get(
            "/api/v1/learning-loop/before-after",
            params={"website": "learnpythonhub.io", "query": "best python courses for beginners"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["website"], "learnpythonhub.io")
        self.assertIn("demonstration_thesis", data)

        # 1. BEFORE MEMORY Checks
        before = data["before_memory"]
        self.assertFalse(before["memory_applied"])
        self.assertEqual(len(before["suppressed_tactics"]), 0)
        self.assertIn("limitations", before)

        # 2. AFTER MEMORY Checks
        after = data["after_memory"]
        self.assertTrue(after["memory_applied"])
        self.assertGreater(after["recalled_memories_count"], 0)
        self.assertGreater(len(after["suppressed_tactics"]), 0)
        self.assertIn("Passive Word Count Expansion", " ".join(after["suppressed_tactics"]))

        # Verify each recommendation in AFTER has transparent 'why_am_i_seeing_this'
        for r in after["recommendations"]:
            self.assertIn("why_am_i_seeing_this", r)
            why = r["why_am_i_seeing_this"]
            self.assertIn("current_observation", why)
            self.assertIn("recalled_memory", why)
            self.assertIn("connection_between_them", why)
            self.assertIn("observational_caveat", why)

        # 3. Key Differences Matrix Checks
        matrix = data["key_differences_matrix"]
        self.assertGreaterEqual(len(matrix), 4)
        dimensions = [d["dimension"] for d in matrix]
        self.assertIn("Historical Awareness", dimensions)
        self.assertIn("Content Strategy", dimensions)
        self.assertIn("Prescriptive Evidence", dimensions)

    def test_learning_loop_cockpit_ui(self):
        """5. Verify interactive Learning Loop Cockpit HTML interface renders correctly."""
        res = self.client.get("/learning-loop")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Complete SEO Learning Loop", res.text)
        self.assertIn("Before / After Mode", res.text)
        self.assertIn("Website Event Timeline", res.text)
        self.assertIn("Learning History View", res.text)
        self.assertIn("Drive the Loop", res.text)
        self.assertIn("The Closed SEO Learning Loop Flow", res.text)


if __name__ == "__main__":
    unittest.main()
