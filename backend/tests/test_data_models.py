import os
import unittest
from pathlib import Path
from datetime import datetime, timezone
import tempfile

from app.db.database import init_db, get_connection
from app.repositories.seo_repository import SEORepository
from app.models.domain_schemas import (
    SearchQueryCreate,
    SearchQueryUpdate,
    SearchIntent,
    WebsiteCreate,
    WebsiteUpdate,
    RankingHistoryCreate,
    SEOOptimizationCreate,
    SEOOptimizationUpdate,
    OptimizationType,
    CompetitorHistoryCreate,
    OutcomeCreate,
    OutcomeUpdate,
    ContentCitationCreate,
    ContentCitationUpdate,
    CitationType,
    UserInteractionCreate,
    UserInteractionUpdate,
)
from pydantic import ValidationError


class TestSEODataModels(unittest.TestCase):
    """Test suite verifying Create, Read, Update, and Retrieve operations on all 8 entities."""

    def setUp(self):
        # Create a fresh temporary SQLite database for test isolation
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_rankmind.db"
        init_db(self.db_path, reset=True)
        self.repo = SEORepository(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    # ----------------------------------------------------
    # 1. SEARCH QUERY TESTS
    # ----------------------------------------------------
    def test_search_query_crud(self):
        # Create
        sq = self.repo.create_search_query(
            SearchQueryCreate(
                query="best python bootcamps online",
                target_keyword="best python bootcamps",
                search_intent=SearchIntent.COMMERCIAL,
                location="United States",
            )
        )
        self.assertIsNotNone(sq.id)
        self.assertEqual(sq.query, "best python bootcamps online")
        self.assertEqual(sq.search_intent, SearchIntent.COMMERCIAL)

        # Read
        retrieved = self.repo.get_search_query(sq.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.target_keyword, "best python bootcamps")

        # Update
        updated = self.repo.update_search_query(
            sq.id,
            SearchQueryUpdate(location="North America", search_intent=SearchIntent.TRANSACTIONAL),
        )
        self.assertEqual(updated.location, "North America")
        self.assertEqual(updated.search_intent, SearchIntent.TRANSACTIONAL)

        # List
        all_queries = self.repo.list_search_queries()
        self.assertEqual(len(all_queries), 1)

    # ----------------------------------------------------
    # 2. WEBSITE TESTS
    # ----------------------------------------------------
    def test_website_crud(self):
        # Create
        site = self.repo.create_website(
            WebsiteCreate(
                domain="pythonmastery.io",
                title="Python Mastery Academy",
                url="https://pythonmastery.io/course",
                content_topic="Programming",
                seo_observations={"word_count": 2800, "has_code_widget": True},
            )
        )
        self.assertIsNotNone(site.id)
        self.assertEqual(site.domain, "pythonmastery.io")
        self.assertEqual(site.seo_observations["word_count"], 2800)

        # Read by Domain
        retrieved = self.repo.get_website_by_domain("pythonmastery.io")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, site.id)

        # Update
        updated = self.repo.update_website(
            site.id,
            WebsiteUpdate(title="Python Mastery Academy 2026", seo_observations={"word_count": 3200}),
        )
        self.assertEqual(updated.title, "Python Mastery Academy 2026")
        self.assertEqual(updated.seo_observations["word_count"], 3200)

        # List
        sites = self.repo.list_websites()
        self.assertEqual(len(sites), 1)

    # ----------------------------------------------------
    # 3. RANKING HISTORY TESTS
    # ----------------------------------------------------
    def test_ranking_history_crud(self):
        site = self.repo.create_website(
            WebsiteCreate(domain="ranktest.io", title="Rank Test", url="https://ranktest.io")
        )

        # Create Baseline entry (#8)
        rh1 = self.repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=site.id,
                keyword="python testing",
                position=8,
                previous_position=None,
            )
        )
        self.assertEqual(rh1.position, 8)
        self.assertEqual(rh1.change_in_position, 0)

        # Create Subsequent entry with improvement (#3, previous was #8 -> change +5)
        rh2 = self.repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=site.id,
                keyword="python testing",
                position=3,
                previous_position=8,
            )
        )
        self.assertEqual(rh2.position, 3)
        self.assertEqual(rh2.change_in_position, 5)

        # Validation: Position cannot be less than 1
        with self.assertRaises(ValidationError):
            RankingHistoryCreate(
                website_id=site.id,
                keyword="python testing",
                position=0,
            )

        # List History
        history = self.repo.list_ranking_history(site.id, keyword="python testing")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].position, 8)
        self.assertEqual(history[1].position, 3)

    # ----------------------------------------------------
    # 4. SEO OPTIMIZATION TESTS
    # ----------------------------------------------------
    def test_seo_optimization_crud(self):
        site = self.repo.create_website(
            WebsiteCreate(domain="optwebsite.com", title="Opt Site", url="https://optwebsite.com")
        )

        # Create
        opt = self.repo.create_optimization(
            SEOOptimizationCreate(
                website_id=site.id,
                optimization_type=OptimizationType.INTERACTIVE_UX,
                description="Deployed live interactive code execution console.",
                reason_for_optimization="Boost beginner dwell time and reduce bounce rate.",
                expected_effect="+3 positions into top 3",
            )
        )
        self.assertIsNotNone(opt.id)
        self.assertEqual(opt.optimization_type, OptimizationType.INTERACTIVE_UX)
        self.assertIsNone(opt.observed_effect)

        # Update observed effect
        updated = self.repo.update_optimization(
            opt.id,
            SEOOptimizationUpdate(observed_effect="Rank surged +4 positions within 12 days."),
        )
        self.assertEqual(updated.observed_effect, "Rank surged +4 positions within 12 days.")

        # List
        opts = self.repo.list_optimizations(site.id)
        self.assertEqual(len(opts), 1)

    # ----------------------------------------------------
    # 5. COMPETITOR HISTORY TESTS
    # ----------------------------------------------------
    def test_competitor_history_crud(self):
        comp = self.repo.create_website(
            WebsiteCreate(domain="competitor-alpha.com", title="Comp Alpha", url="https://competitor-alpha.com")
        )

        # Create
        ch = self.repo.create_competitor_history(
            CompetitorHistoryCreate(
                competitor_website_id=comp.id,
                keyword="python courses",
                content_changes=["Added 10 practice projects"],
                feature_changes=["Launched code editor"],
                ranking_changes={"before": 2, "after": 1, "delta": 1},
                notable_seo_changes=["Added CourseSchema"],
            )
        )
        self.assertIsNotNone(ch.id)
        self.assertEqual(ch.content_changes[0], "Added 10 practice projects")

        # Read & List
        histories = self.repo.list_competitor_history(competitor_website_id=comp.id)
        self.assertEqual(len(histories), 1)
        self.assertEqual(histories[0].ranking_changes["delta"], 1)

    # ----------------------------------------------------
    # 6. OUTCOME (Causal Attribution) TESTS
    # ----------------------------------------------------
    def test_outcome_crud_and_attribution_link(self):
        site = self.repo.create_website(
            WebsiteCreate(domain="outcomesite.com", title="Outcome Site", url="https://outcomesite.com")
        )
        opt = self.repo.create_optimization(
            SEOOptimizationCreate(
                website_id=site.id,
                optimization_type=OptimizationType.SCHEMA_MARKUP,
                description="Implemented Course schema with credential metadata.",
                reason_for_optimization="Eligible for rich carousel results.",
                expected_effect="+2 positions",
            )
        )

        # Create Outcome
        outcome = self.repo.create_outcome(
            OutcomeCreate(
                website_id=site.id,
                optimization_id=opt.id,
                previous_ranking=6,
                new_ranking=4,
                observed_change="+2 positions (#6 to #4)",
                confidence=0.94,
                uncertainty_factors=["Minor SERP fluctuation"],
            )
        )
        self.assertIsNotNone(outcome.id)
        self.assertEqual(outcome.previous_ranking, 6)
        self.assertEqual(outcome.new_ranking, 4)
        self.assertEqual(outcome.confidence, 0.94)

        # Verify that parent optimization's observed_effect was automatically populated
        opt_refreshed = self.repo.get_optimization(opt.id)
        self.assertIn("#6 to #4", opt_refreshed.observed_effect)

        # Validation: Confidence must be between 0.0 and 1.0
        with self.assertRaises(ValidationError):
            OutcomeCreate(
                website_id=site.id,
                optimization_id=opt.id,
                previous_ranking=6,
                new_ranking=4,
                observed_change="test",
                confidence=1.5,
            )

        # Update Outcome
        updated_out = self.repo.update_outcome(outcome.id, OutcomeUpdate(confidence=0.98))
        self.assertEqual(updated_out.confidence, 0.98)

    # ----------------------------------------------------
    # 7. CONTENT / CITATION INFORMATION TESTS
    # ----------------------------------------------------
    def test_content_citation_crud(self):
        site = self.repo.create_website(
            WebsiteCreate(domain="citationsite.org", title="Cite Site", url="https://citationsite.org")
        )

        # Create
        cit = self.repo.create_citation(
            ContentCitationCreate(
                website_id=site.id,
                source_title="IEEE Software 2026 Developer Report",
                source_url="https://ieee.org/python-report",
                citation_snippet="Python accounts for 54% of entry-level developer learning tracks.",
                citation_type=CitationType.AUTHORITATIVE_REFERENCE,
                is_used_by_app=True,
                citation_metadata={"citations_count": 142, "authority_tier": "A+"},
            )
        )
        self.assertIsNotNone(cit.id)
        self.assertEqual(cit.citation_metadata["authority_tier"], "A+")

        # Update
        updated = self.repo.update_citation(
            cit.id,
            ContentCitationUpdate(citation_snippet="Updated snippet with verified 2026 data."),
        )
        self.assertEqual(updated.citation_snippet, "Updated snippet with verified 2026 data.")

        # List active citations
        active_cits = self.repo.list_citations(website_id=site.id, only_used=True)
        self.assertEqual(len(active_cits), 1)

    # ----------------------------------------------------
    # 8. USER INTERACTION TESTS
    # ----------------------------------------------------
    def test_user_interaction_crud(self):
        site = self.repo.create_website(
            WebsiteCreate(domain="interactive-qa.com", title="QA Site", url="https://interactive-qa.com")
        )

        # Create
        ui = self.repo.create_user_interaction(
            UserInteractionCreate(
                query_text="best python courses for beginners",
                selected_website_id=site.id,
                question_asked="Why did competitor X overtake us?",
                recommendation_requested="Analyze competitor feature differences",
                recommendation_provided="Competitor added interactive quizzes and CourseSchema.",
                feedback={"rating": 5, "helpful": True},
            )
        )
        self.assertIsNotNone(ui.id)
        self.assertEqual(ui.feedback["rating"], 5)

        # Update feedback
        updated = self.repo.update_user_interaction(
            ui.id,
            UserInteractionUpdate(feedback={"rating": 5, "helpful": True, "comment": "Excellent attribution detail"}),
        )
        self.assertEqual(updated.feedback["comment"], "Excellent attribution detail")

        # List
        interactions = self.repo.list_user_interactions(query_text="python courses")
        self.assertEqual(len(interactions), 1)


if __name__ == "__main__":
    unittest.main()
