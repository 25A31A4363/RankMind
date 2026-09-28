import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset
from app.models.hindsight_schemas import (
    RawSEOEvent,
    RetentionDecisionEnum,
    MemoryCategory,
)
from app.services.hindsight.event_processor import event_processing_layer
from app.services.hindsight.client import hindsight_client


class TestRetainWorkflowAndMemoryQuality(unittest.TestCase):
    """Test suite verifying the RETAIN workflow, memory-quality gatekeeper,
    deduplication engine, and correlational truth discipline.
    """

    @classmethod
    def setUpClass(cls):
        populate_synthetic_seo_dataset(reset=True)
        cls.client = TestClient(app)
        cls.processor = event_processing_layer

    def test_1_new_ranking_event_remembered(self):
        """1. New ranking event -> remembered (significant shift >= 2 positions)."""
        event = RawSEOEvent(
            event_type="ranking_change",
            website="testrankhub.com",
            keyword="react state management",
            date="2026-09-21T10:00:00Z",
            details={
                "position": 3,
                "previous_position": 9,
                "delta": 6,
            },
        )
        res = self.processor.process_and_evaluate_event(event)

        self.assertEqual(res.decision, RetentionDecisionEnum.REMEMBER)
        self.assertGreaterEqual(res.importance_score, 0.75)
        self.assertTrue("Significant" in res.reason or "milestone" in res.reason.lower())
        self.assertIsNotNone(res.normalized_memory)
        self.assertEqual(res.normalized_memory.website, "testrankhub.com")
        self.assertEqual(res.normalized_memory.keyword, "react state management")
        self.assertIsNotNone(res.retained_memory_item)
        self.assertEqual(res.retained_memory_item.category, MemoryCategory.RANKING_HISTORY)

    def test_2_important_optimization_remembered(self):
        """2. Important optimization -> remembered (structured schemas, interactive tools, etc.)."""
        event = RawSEOEvent(
            event_type="optimization_performed",
            website="testrankhub.com",
            keyword="react state management",
            date="2026-09-22T10:00:00Z",
            details={
                "optimization_type": "structured_schema",
                "description": "Deployed Course and CodeRepository JSON-LD schema markup",
                "reason": "Qualify for Google Course Carousel and code snippet rich cards",
                "expected_effect": "Anticipated +25% organic CTR boost",
            },
        )
        res = self.processor.process_and_evaluate_event(event)

        self.assertEqual(res.decision, RetentionDecisionEnum.REMEMBER)
        self.assertGreaterEqual(res.importance_score, 0.80)
        self.assertIn("Strategic optimization", res.reason)
        self.assertIsNotNone(res.normalized_memory)
        self.assertIn("[STRUCTURED_SCHEMA]", res.normalized_memory.action)
        self.assertIsNotNone(res.retained_memory_item)
        self.assertEqual(res.retained_memory_item.category, MemoryCategory.OPTIMIZATION_HISTORY)

    def test_3_meaningless_duplicate_event_ignored(self):
        """3. Meaningless duplicate event -> ignored / suppressed."""
        # Submit the exact same event as test #2
        duplicate_event = RawSEOEvent(
            event_type="optimization_performed",
            website="testrankhub.com",
            keyword="react state management",
            date="2026-09-22T10:00:00Z",
            details={
                "optimization_type": "structured_schema",
                "description": "Deployed Course and CodeRepository JSON-LD schema markup",
                "reason": "Qualify for Google Course Carousel and code snippet rich cards",
                "expected_effect": "Anticipated +25% organic CTR boost",
            },
        )
        res = self.processor.process_and_evaluate_event(duplicate_event)

        self.assertEqual(res.decision, RetentionDecisionEnum.DO_NOT_REMEMBER)
        self.assertEqual(res.importance_score, 0.0)
        self.assertIn("Meaningless duplicate event", res.reason)
        self.assertIsNone(res.retained_memory_item)
        self.assertIsNone(res.normalized_memory)

    def test_4_new_outcome_remembered_with_correlational_language(self):
        """4. New outcome -> remembered, strictly using correlational language.
        Must use language such as:
        'After this change, the observed ranking moved from X to Y.'
        Must NOT say:
        'This change definitely caused the ranking improvement.'
        """
        event = RawSEOEvent(
            event_type="outcome_observed",
            website="testrankhub.com",
            keyword="react state management",
            date="2026-09-27T10:00:00Z",
            details={
                "optimization_title": "Deployed Course and CodeRepository JSON-LD schema markup",
                "optimization_type": "structured_schema",
                "rank_before": 9,
                "rank_after": 3,
                "observed_result": "Rank moved from #9 to #3 (+6 positions)",
                "time_period_days": 21,
                "confidence": 0.88,
                "uncertainty_factors": [
                    "External search engine algorithm core update occurred during evaluation window"
                ],
            },
        )
        res = self.processor.process_and_evaluate_event(event)

        self.assertEqual(res.decision, RetentionDecisionEnum.REMEMBER)
        self.assertGreaterEqual(res.importance_score, 0.90)
        self.assertIn("Empirical outcome recorded", res.reason)
        self.assertIsNotNone(res.normalized_memory)

        result_text = res.normalized_memory.result
        # MUST use disciplined correlational language
        self.assertIn("After this change", result_text)
        self.assertIn("the observed ranking moved from #9 to #3", result_text)

        # MUST NEVER claim definitive causation
        self.assertNotIn("definitely caused", result_text.lower())
        self.assertNotIn("caused the ranking improvement", result_text.lower())

        # Confidence and uncertainty factors
        self.assertEqual(res.normalized_memory.confidence, 0.88)
        self.assertGreater(len(res.normalized_memory.uncertainty_factors), 0)
        self.assertIsNotNone(res.retained_memory_item)
        self.assertEqual(res.retained_memory_item.category, MemoryCategory.OUTCOME_HISTORY)

    def test_5_micro_fluctuation_noise_ignored(self):
        """Low-signal ranking micro-fluctuations (delta <= 1 outside tier thresholds) -> ignored."""
        event = RawSEOEvent(
            event_type="ranking_change",
            website="testrankhub.com",
            keyword="react state management",
            details={
                "position": 14,
                "previous_position": 15,
                "delta": 1,
            },
        )
        res = self.processor.process_and_evaluate_event(event)

        self.assertEqual(res.decision, RetentionDecisionEnum.DO_NOT_REMEMBER)
        self.assertIn("micro-fluctuation", res.reason.lower())
        self.assertIsNone(res.retained_memory_item)

    def test_6_trivial_typo_optimization_ignored(self):
        """Trivial cosmetic optimizations (typo fixes, minor whitespace) -> ignored."""
        event = RawSEOEvent(
            event_type="optimization_performed",
            website="testrankhub.com",
            keyword="react state management",
            details={
                "optimization_type": "typo_fix",
                "description": "Fixed minor spelling typo in sidebar footer",
                "reason": "Cosmetic text hygiene",
            },
        )
        res = self.processor.process_and_evaluate_event(event)

        self.assertEqual(res.decision, RetentionDecisionEnum.DO_NOT_REMEMBER)
        self.assertIn("Trivial cosmetic", res.reason)
        self.assertIsNone(res.retained_memory_item)

    def test_7_http_api_endpoints(self):
        """Verify POST /process-event, GET /decisions, and GET /logs endpoints."""
        payload = {
            "event_type": "ranking_change",
            "website": "api-test-site.io",
            "keyword": "fastapi microservices",
            "details": {
                "position": 2,
                "previous_position": 8,
                "delta": 6,
            },
        }

        # 1. Process Event
        res_post = self.client.post("/api/v1/hindsight/process-event", json=payload)
        self.assertEqual(res_post.status_code, 200)
        data = res_post.json()
        self.assertEqual(data["decision"], "REMEMBER")
        self.assertTrue("Significant" in data["reason"] or "milestone" in data["reason"].lower())

        # 2. Duplicate submission via API
        res_dup = self.client.post("/api/v1/hindsight/process-event", json=payload)
        self.assertEqual(res_dup.status_code, 200)
        data_dup = res_dup.json()
        self.assertEqual(data_dup["decision"], "DO NOT REMEMBER")
        self.assertIn("duplicate", data_dup["reason"].lower())

        # 3. List Decisions via API
        res_dec = self.client.get("/api/v1/hindsight/decisions?limit=10")
        self.assertEqual(res_dec.status_code, 200)
        dec_list = res_dec.json()
        self.assertGreater(len(dec_list), 0)

        # 4. Audit logs including decisions
        res_logs = self.client.get("/api/v1/hindsight/logs?log_type=decisions")
        self.assertEqual(res_logs.status_code, 200)
        log_data = res_logs.json()
        self.assertIn("retention_decisions", log_data)
        self.assertGreater(len(log_data["retention_decisions"]), 0)


if __name__ == "__main__":
    unittest.main()
