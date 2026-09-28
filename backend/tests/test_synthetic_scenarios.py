import unittest
from app.db.database import DB_PATH, get_connection
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset, DATASET_METADATA
from fastapi.testclient import TestClient
from app.main import app


class TestSyntheticDataset(unittest.TestCase):
    """Verifies synthetic dataset seeding, multi-scenario coverage, and debug view."""

    @classmethod
    def setUpClass(cls):
        populate_synthetic_seo_dataset(reset=True)
        cls.client = TestClient(app)

    def test_synthetic_metadata_and_disclaimer(self):
        res = self.client.get("/api/v1/debug/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["metadata"]["is_synthetic"])
        self.assertIn("NOT claim to represent actual Google", data["metadata"]["disclaimer"])
        self.assertEqual(len(data["tracked_queries"]), 3)

    def test_query_1_python_courses_events(self):
        # Find query 1
        summary = self.client.get("/api/v1/debug/summary").json()
        q1 = next(q for q in summary["tracked_queries"] if "python" in q["query"].lower())
        res = self.client.get(f"/api/v1/debug/timeline?query_id={q1['id']}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_events"], 8)
        
        # Verify event types present
        event_types = {e["type"] for e in data["events"]}
        self.assertIn("RANKING_SNAPSHOT", event_types)
        self.assertIn("OPTIMIZATION_ACTION", event_types)
        self.assertIn("COMPETITOR_CHANGE", event_types)
        self.assertIn("CAUSAL_OUTCOME", event_types)

    def test_query_2_fastapi_events(self):
        summary = self.client.get("/api/v1/debug/summary").json()
        q2 = next(q for q in summary["tracked_queries"] if "fastapi" in q["query"].lower())
        res = self.client.get(f"/api/v1/debug/timeline?query_id={q2['id']}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_events"], 6)

    def test_query_3_ai_tools_events(self):
        summary = self.client.get("/api/v1/debug/summary").json()
        q3 = next(q for q in summary["tracked_queries"] if "ai code" in q["query"].lower())
        res = self.client.get(f"/api/v1/debug/timeline?query_id={q3['id']}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_events"], 6)

    def test_debug_html_endpoint(self):
        res = self.client.get("/debug")
        self.assertEqual(res.status_code, 200)
        self.assertIn("RankMind Data Inspector & Debugger", res.text)
        self.assertIn("Synthetic SEO Dataset", res.text)


if __name__ == "__main__":
    unittest.main()
