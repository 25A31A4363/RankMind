import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset
from app.repositories.seo_repository import SEORepository
from app.db.database import DB_PATH


class TestBaselineSEOAnalyzer(unittest.TestCase):
    """Test suite verifying the Baseline SEO Analyzer (Without Hindsight Memory)."""

    @classmethod
    def setUpClass(cls):
        populate_synthetic_seo_dataset(reset=True)
        cls.client = TestClient(app)
        cls.repo = SEORepository(DB_PATH)

    def test_analyzer_on_target_website(self):
        # Target site: learnpythonhub.io
        site = self.repo.get_website_by_domain("learnpythonhub.io")
        self.assertIsNotNone(site)

        payload = {
            "query": "best python courses for beginners",
            "website_id": site.id,
        }

        res = self.client.post("/api/v1/analyzer/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Baseline flags
        self.assertFalse(data["hindsight_memory_applied"])
        self.assertEqual(data["data_source_type"], "synthetic_database")
        self.assertIn("BASELINE STATIC SEO ANALYZER", data["disclaimer"])
        self.assertEqual(data["target_domain"], "learnpythonhub.io")

        # 1. Current Observations
        obs = data["current_observations"]
        self.assertEqual(obs["search_intent_detected"], "commercial")
        self.assertGreaterEqual(obs["intent_match_score"], 70.0)
        self.assertIsNotNone(obs["title"]["title_text"])
        self.assertGreaterEqual(obs["content_completeness"]["word_count"], 2000)
        self.assertTrue(obs["user_experience"]["has_interactive_widget"])
        self.assertFalse(obs["user_experience"]["has_video_preview"])

        # 2. Problems
        problems = data["problems"]
        self.assertGreaterEqual(len(problems), 1)
        prob_ids = [p["id"] for p in problems]
        self.assertIn("prob_missing_video", prob_ids)

        # 3. Opportunities
        opps = data["opportunities"]
        self.assertGreaterEqual(len(opps), 1)
        opp_ids = [o["id"] for o in opps]
        self.assertIn("opp_video_curriculum", opp_ids)

        # 4. Recommended Actions
        actions = data["recommended_actions"]
        self.assertGreaterEqual(len(actions), 1)
        self.assertEqual(actions[0]["priority"], 1)

        # Machine-Readable LLM Summary
        summary = data["llm_prompt_summary"]
        self.assertIn("BASELINE SEO ANALYSIS REPORT", summary)
        self.assertIn("1. CURRENT OBSERVATIONS", summary)
        self.assertIn("2. PROBLEMS IDENTIFIED", summary)
        self.assertIn("3. OPPORTUNITIES", summary)
        self.assertIn("4. RECOMMENDED ACTIONS", summary)

    def test_analyzer_on_adhoc_url(self):
        payload = {
            "query": "how to build rest api python",
            "url": "https://random-blog.dev/python-api-tutorial",
            "custom_title": "How to Build a REST API in Python from Scratch",
            "custom_content": "In this tutorial we will learn how to build a REST API in Python using standard libraries...",
        }

        res = self.client.post("/api/v1/analyzer/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertFalse(data["hindsight_memory_applied"])
        self.assertEqual(data["data_source_type"], "ad_hoc_input")
        self.assertEqual(data["target_domain"], "random-blog.dev")
        self.assertEqual(data["current_observations"]["search_intent_detected"], "informational")

    def test_analyzer_presets_endpoint(self):
        res = self.client.get("/api/v1/analyzer/presets")
        self.assertEqual(res.status_code, 200)
        presets = res.json()
        self.assertGreaterEqual(len(presets), 3)

    def test_analyzer_html_ui_endpoint(self):
        res = self.client.get("/analyzer")
        self.assertEqual(res.status_code, 200)
        self.assertIn("RankMind Baseline SEO Analyzer", res.text)
        self.assertIn("CURRENT OBSERVATIONS", res.text)
        self.assertIn("Zero Hindsight Memory", res.text)


if __name__ == "__main__":
    unittest.main()
