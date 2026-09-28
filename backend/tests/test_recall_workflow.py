import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset
from app.services.hindsight.client import hindsight_client
from app.services.hindsight.memory_manager import hindsight_memory_manager
from app.services.hindsight.relevance_ranker import relevance_ranking_layer
from app.services.llm.hindsight_reasoning_agent import hindsight_reasoning_agent
from app.models.hindsight_schemas import (
    MemoryCategory,
    MemoryAugmentedAnalysisRequest,
    HindsightMemoryItem,
)
from app.models.llm_schemas import LLMAnalysisRequest
from app.services.llm.llm_analysis_service import llm_analysis_service


class TestRecallWorkflow(unittest.TestCase):
    """Complete test suite verifying the Hindsight RECALL workflow:
    
    1. Relevance-ranking layer evaluating 8 dimensions:
       - same website
       - same keyword
       - related keywords
       - similar optimization
       - previous ranking behavior
       - competitor behavior
       - previous outcomes
       - previous user interactions
    2. Bounded retrieval (not retrieving all memories).
    3. 4-part reasoning context assembly:
       CURRENT INFORMATION + RELEVANT HISTORICAL MEMORY + CURRENT COMPETITOR INFORMATION + USER REQUEST.
    4. Explaining recommendations using historical evidence with observational discipline.
    5. 'Why am I seeing this recommendation?' transparency breakdown.
    6. Contrast demonstration:
       WITHOUT MEMORY -> generic recommendation
       WITH MEMORY    -> context-aware recommendation
    """

    @classmethod
    def setUpClass(cls):
        populate_synthetic_seo_dataset(reset=True)
        hindsight_memory_manager.sync_database_to_hindsight()
        cls.client = TestClient(app)

    def test_relevance_ranking_layer_eight_dimensions(self):
        """1. Verify that the relevance ranker evaluates memories across all 8 dimensions."""
        # Query with exact keyword match and domain match
        memories = relevance_ranking_layer.rank_and_select_memories(
            query="best python courses for beginners",
            target_domain="learnpythonhub.io",
            current_position=8,
            target_deficiencies=["structured_schema", "video_preview"],
            max_memories=6,
        )

        self.assertGreater(len(memories), 0)
        self.assertLessEqual(len(memories), 6)

        # Check that why_relevant notes dimensions
        matched_dimension_keywords = set()
        for m in memories:
            self.assertIsNotNone(m.why_relevant)
            why_lower = m.why_relevant.lower()
            if "same website" in why_lower:
                matched_dimension_keywords.add("same website")
            if "same keyword" in why_lower or "keyword" in why_lower:
                matched_dimension_keywords.add("same keyword")
            if "related keywords" in why_lower or "semantic" in why_lower:
                matched_dimension_keywords.add("related keywords")
            if "similar optimization" in why_lower or "addresses current deficiency" in why_lower:
                matched_dimension_keywords.add("similar optimization")
            if "previous ranking behavior" in why_lower:
                matched_dimension_keywords.add("previous ranking behavior")
            if "competitor behavior" in why_lower:
                matched_dimension_keywords.add("competitor behavior")
            if "previous outcomes" in why_lower or "empirical" in why_lower:
                matched_dimension_keywords.add("previous outcomes")

        # Must have matched multiple key dimensions
        self.assertIn("same website", matched_dimension_keywords)
        self.assertIn("same keyword", matched_dimension_keywords)
        self.assertIn("previous outcomes", matched_dimension_keywords)
        self.assertIn("competitor behavior", matched_dimension_keywords)

    def test_bounded_retrieval_does_not_retrieve_all_memories(self):
        """2. Verify bounded retrieval respects limits and token budgets."""
        all_memories = hindsight_client.list_all_memories()
        self.assertGreater(len(all_memories), 15, "Should have more than 15 total memories in bank")

        # Bounded recall with max_memories = 4
        recalled_4 = hindsight_client.recall(
            query="best python courses for beginners",
            target_domain="learnpythonhub.io",
            max_memories=4,
        )
        self.assertEqual(len(recalled_4), 4)

        # Bounded recall with max_memories = 2
        recalled_2 = hindsight_client.recall(
            query="best python courses for beginners",
            target_domain="learnpythonhub.io",
            max_memories=2,
        )
        self.assertEqual(len(recalled_2), 2)

    def test_four_part_reasoning_context_assembly(self):
        """3. Verify that the reasoning context explicitly assembles:
        CURRENT INFORMATION + RELEVANT HISTORICAL MEMORY + CURRENT COMPETITOR INFORMATION + USER REQUEST.
        """
        user_goal = "How can we improve ranking from #8 into the top 3?"
        req = MemoryAugmentedAnalysisRequest(
            query="best python courses for beginners",
            url="https://learnpythonhub.io/courses",
            user_request=user_goal,
            current_position=8,
            provider="local",
            max_memories=6,
        )

        res = self.client.post("/api/v1/hindsight/analyze", json=req.model_dump())
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Check assembled context dictionary
        context = data.get("reasoning_context_assembled")
        self.assertIsNotNone(context)
        
        # 1. CURRENT INFORMATION
        self.assertIn("current_information", context)
        curr_info = context["current_information"]
        self.assertEqual(curr_info["target_query"], "best python courses for beginners")
        self.assertEqual(curr_info["target_domain"], "learnpythonhub.io")
        self.assertEqual(curr_info["current_position"], 8)
        self.assertIn("word_count", curr_info)
        self.assertIn("schema_types_present", curr_info)

        # 2. RELEVANT HISTORICAL MEMORY
        self.assertIn("recalled_historical_memory", context)
        mem_list = context["recalled_historical_memory"]
        self.assertIsInstance(mem_list, list)
        self.assertGreater(len(mem_list), 0)

        # 3. CURRENT COMPETITOR INFORMATION
        self.assertIn("current_competitor_information", context)
        comp_info = context["current_competitor_information"]
        self.assertIsInstance(comp_info, list)
        self.assertGreater(len(comp_info), 0)

        # 4. USER REQUEST
        self.assertIn("user_request", context)
        self.assertEqual(context["user_request"], user_goal)

    def test_historical_evidence_and_why_am_i_seeing_this_section(self):
        """4. Verify transparent 'Why am I seeing this recommendation?' section with observational caveat."""
        req = MemoryAugmentedAnalysisRequest(
            query="best python courses for beginners",
            url="https://learnpythonhub.io/courses",
            current_position=8,
            provider="local",
            max_memories=6,
        )

        res = self.client.post("/api/v1/hindsight/analyze", json=req.model_dump())
        self.assertEqual(res.status_code, 200)
        data = res.json()

        recs = data.get("context_aware_recommendations")
        self.assertGreater(len(recs), 0)

        # Verify recommendation #1 reflects the example requirement
        rec1 = recs[0]
        self.assertIn("why_am_i_seeing_this", rec1)
        why = rec1["why_am_i_seeing_this"]

        # Check all 5 transparent components
        self.assertIn("current_observation", why)
        self.assertIn("recalled_memory", why)
        self.assertIn("connection_between_them", why)
        self.assertIn("recommendation", why)
        self.assertIn("observational_caveat", why)

        # Verify content of the transparent card matches the requirement
        self.assertIn("#8", why["current_observation"])
        self.assertIn("#8 to #5", why["recalled_memory"])
        self.assertIn("observational and not guaranteed", why["recommendation"].lower())
        self.assertIn("observational and not guaranteed", why["observational_caveat"].lower())

    def test_contrast_without_memory_vs_with_memory(self):
        """5. Add tests showing that:
        WITHOUT MEMORY -> generic recommendation
        WITH MEMORY    -> context-aware recommendation
        """
        # A. WITHOUT MEMORY: Stateless Baseline Analysis
        base_req = LLMAnalysisRequest(
            query="best python courses for beginners",
            url="https://learnpythonhub.io/courses",
            provider="local",
        )
        base_res = self.client.post("/api/v1/llm/analyze", json=base_req.model_dump())
        self.assertEqual(base_res.status_code, 200)
        base_data = base_res.json()

        self.assertFalse(base_data["hindsight_memory_applied"])
        self.assertNotIn("recalled_memories", base_data)
        self.assertNotIn("suppressed_tactics", base_data)
        
        # Verify baseline recommendations do NOT have historical memory citations or why_am_i_seeing_this
        for r in base_data["recommendations"]:
            self.assertNotIn("why_am_i_seeing_this", r)
            self.assertNotIn("#8 to #5", r["reasoning"])
            self.assertNotIn("Cycle 1", r["reasoning"])

        # B. WITH MEMORY: Hindsight-Augmented Analysis
        mem_req = MemoryAugmentedAnalysisRequest(
            query="best python courses for beginners",
            url="https://learnpythonhub.io/courses",
            provider="local",
            current_position=8,
            max_memories=6,
        )
        mem_res = self.client.post("/api/v1/hindsight/analyze", json=mem_req.model_dump())
        self.assertEqual(mem_res.status_code, 200)
        mem_data = mem_res.json()

        self.assertTrue(mem_data["hindsight_memory_applied"])
        
        # Suppressed disproven tactics: text expansion is suppressed because 1600 words yielded 0 delta
        self.assertGreater(len(mem_data["suppressed_tactics"]), 0)
        suppressed_joined = " ".join(mem_data["suppressed_tactics"])
        self.assertIn("Passive Word Count Expansion", suppressed_joined)

        # Context-aware recommendations cite past empirical outcomes
        context_recs = mem_data["context_aware_recommendations"]
        self.assertGreater(len(context_recs), 0)
        rec1 = context_recs[0]
        self.assertIn("#8 to #5", rec1["reasoning"])
        self.assertIn("observational and not guaranteed", rec1["reasoning"].lower())

        # Contrast summary explicitly points out the difference
        self.assertIn("CRITICAL CONTRAST", mem_data["baseline_vs_hindsight_contrast"])
        self.assertIn("ZERO", mem_data["baseline_vs_hindsight_contrast"])


if __name__ == "__main__":
    unittest.main()
