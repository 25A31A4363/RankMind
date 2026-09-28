import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset
from app.repositories.seo_repository import SEORepository
from app.db.database import DB_PATH
from app.services.llm.providers import get_llm_provider, LocalDeterministicLLMProvider, GeminiLLMProvider, OpenAILLMProvider


class TestLLMSEOAnalyzer(unittest.TestCase):
    """Test suite verifying LLM-powered SEO Reasoning, 3-layer distinction, and truth discipline."""

    @classmethod
    def setUpClass(cls):
        populate_synthetic_seo_dataset(reset=True)
        cls.client = TestClient(app)
        cls.repo = SEORepository(DB_PATH)

    def test_modular_provider_factory(self):
        # 1. Local fallback provider
        prov_local = get_llm_provider("local")
        self.assertIsInstance(prov_local, LocalDeterministicLLMProvider)

        # 2. Gemini provider with key
        prov_gemini = get_llm_provider("gemini", api_key="fake-gemini-key")
        self.assertIsInstance(prov_gemini, GeminiLLMProvider)

        # 3. OpenAI provider with key
        prov_openai = get_llm_provider("openai", api_key="fake-openai-key")
        self.assertIsInstance(prov_openai, OpenAILLMProvider)

    def test_llm_analysis_three_layer_partition(self):
        site = self.repo.get_website_by_domain("learnpythonhub.io")
        self.assertIsNotNone(site)

        payload = {
            "query": "best python courses for beginners",
            "website_id": site.id,
            "provider": "local",
        }

        res = self.client.post("/api/v1/llm/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Check metadata & truth discipline
        self.assertFalse(data["hindsight_memory_applied"])
        self.assertEqual(data["query"], "best python courses for beginners")
        self.assertEqual(data["target_domain"], "learnpythonhub.io")

        # ----------------------------------------------------
        # LAYER 1: VERIFIED OBSERVED DATA
        # ----------------------------------------------------
        obs = data["observed_data"]
        self.assertEqual(obs["target_domain"], "learnpythonhub.io")
        self.assertEqual(obs["search_intent_detected"], "commercial")
        self.assertTrue(obs["has_interactive_widget"])
        self.assertFalse(obs["has_video_preview"])
        self.assertIsNotNone(obs["competitor_context_available"])

        # ----------------------------------------------------
        # LAYER 2: AI INTERPRETATION & DIAGNOSIS
        # ----------------------------------------------------
        ai = data["ai_interpretation"]
        self.assertIsNotNone(ai["seo_diagnosis"])
        self.assertIsNotNone(ai["intent_fit_assessment"])
        self.assertIn("No historical ranking timeline or causal memory", ai["disclaimer"])
        
        # Weaknesses list
        self.assertGreaterEqual(len(ai["main_weaknesses"]), 2)
        weakness_texts = [w["weakness"].lower() for w in ai["main_weaknesses"]]
        self.assertTrue(any("schema" in w for w in weakness_texts))
        self.assertTrue(any("video" in w for w in weakness_texts))

        # Explicit Missing Evidence / Questions when evidence is insufficient
        self.assertGreaterEqual(len(ai["missing_evidence_or_questions"]), 1)
        self.assertTrue(any("bounce" in q.lower() or "backlink" in q.lower() or "server" in q.lower() for q in ai["missing_evidence_or_questions"]))

        # ----------------------------------------------------
        # LAYER 3: PRESCRIPTIVE RECOMMENDATIONS
        # ----------------------------------------------------
        recs = data["recommendations"]
        self.assertGreaterEqual(len(recs), 2)
        for r in recs:
            self.assertIsNotNone(r["title"])
            self.assertIsNotNone(r["reasoning"])
            self.assertIsNotNone(r["expected_direction_of_improvement"])
            self.assertGreaterEqual(len(r["implementation_steps"]), 1)

    def test_llm_analysis_html_test_interface(self):
        res = self.client.get("/llm-analysis")
        self.assertEqual(res.status_code, 200)
        self.assertIn("RankMind LLM SEO Reasoning Agent", res.text)
        self.assertIn("LAYER 1: VERIFIED OBSERVED DATA", res.text)
        self.assertIn("LAYER 2: AI INTERPRETATION & DIAGNOSIS", res.text)
        self.assertIn("LAYER 3: PRESCRIPTIVE RECOMMENDATIONS", res.text)
        self.assertIn("Strict Truth Discipline", res.text)


if __name__ == "__main__":
    unittest.main()
