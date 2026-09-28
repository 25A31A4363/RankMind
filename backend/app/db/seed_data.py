from datetime import datetime, timedelta, timezone
from app.db.database import init_db, DB_PATH
from app.repositories.seo_repository import SEORepository
from app.models.domain_schemas import (
    SearchQueryCreate,
    SearchIntent,
    WebsiteCreate,
    RankingHistoryCreate,
    SEOOptimizationCreate,
    OptimizationType,
    CompetitorHistoryCreate,
    OutcomeCreate,
    ContentCitationCreate,
    CitationType,
    UserInteractionCreate,
)


def populate_seed_data(reset: bool = True):
    """Initializes tables and populates realistic sample records for all 8 entities."""
    init_db(reset=reset)
    repo = SEORepository(DB_PATH)

    now = datetime.now(timezone.utc)
    t_90d = now - timedelta(days=90)
    t_75d = now - timedelta(days=75)
    t_60d = now - timedelta(days=60)
    t_45d = now - timedelta(days=45)
    t_30d = now - timedelta(days=30)
    t_14d = now - timedelta(days=14)
    t_10d = now - timedelta(days=10)
    t_2d = now - timedelta(days=2)

    # ----------------------------------------------------
    # 1. SEARCH QUERY RECORDS
    # ----------------------------------------------------
    sq1 = repo.create_search_query(
        SearchQueryCreate(
            query="best python courses for beginners",
            target_keyword="best python courses for beginners",
            search_intent=SearchIntent.COMMERCIAL,
            date=t_90d,
            location="United States",
        )
    )

    sq2 = repo.create_search_query(
        SearchQueryCreate(
            query="learn python from scratch interactive",
            target_keyword="learn python interactive",
            search_intent=SearchIntent.INFORMATIONAL,
            date=t_30d,
            location="Global",
        )
    )

    # ----------------------------------------------------
    # 2. WEBSITE RECORDS
    # ----------------------------------------------------
    target_site = repo.create_website(
        WebsiteCreate(
            id="site_target_learnpython",
            domain="learnpythonhub.io",
            title="Best Python Courses for Beginners in 2026 (Curated Interactive Guide)",
            url="https://learnpythonhub.io/best-python-courses-beginners",
            content_topic="Python Programming Education",
            seo_observations={
                "word_count": 3650,
                "has_interactive_widget": True,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Article", "ItemList"],
                "readability_score": 83.0,
                "citation_density": 4.5,
                "last_crawled": now.isoformat(),
            },
        )
    )

    comp_coursera = repo.create_website(
        WebsiteCreate(
            id="site_comp_coursera",
            domain="coursera.org",
            title="Python for Everybody Specialization | Coursera",
            url="https://www.coursera.org/specializations/python",
            content_topic="Online University Specialization",
            seo_observations={
                "word_count": 3600,
                "has_interactive_widget": True,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Course", "Organization", "EducationalOccupationalCredential"],
                "readability_score": 84.0,
                "citation_density": 4.3,
            },
        )
    )

    comp_codecademy = repo.create_website(
        WebsiteCreate(
            id="site_comp_codecademy",
            domain="codecademy.com",
            title="Learn Python 3 | Codecademy",
            url="https://www.codecademy.com/learn/learn-python-3",
            content_topic="Interactive Coding Platform",
            seo_observations={
                "word_count": 2300,
                "has_interactive_widget": True,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Course", "FAQPage"],
                "readability_score": 86.0,
                "citation_density": 3.4,
            },
        )
    )

    comp_freecodecamp = repo.create_website(
        WebsiteCreate(
            id="site_comp_freecodecamp",
            domain="freecodecamp.org",
            title="Python for Beginners - Full Course (Video & Certificate) | freeCodeCamp.org",
            url="https://www.freecodecamp.org/news/python-for-beginners-full-course/",
            content_topic="Free Open-Source Tech Education",
            seo_observations={
                "word_count": 4900,
                "has_interactive_widget": False,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Article", "VideoObject", "Course"],
                "readability_score": 81.0,
                "citation_density": 5.2,
            },
        )
    )

    # ----------------------------------------------------
    # 3. RANKING HISTORY RECORDS
    # ----------------------------------------------------
    # Target Site trajectory: #8 (T-90d) -> #8 (T-60d) -> #3 (T-30d) -> #4 (Current)
    repo.create_ranking_entry(
        RankingHistoryCreate(
            website_id=target_site.id,
            search_query_id=sq1.id,
            keyword=sq1.target_keyword,
            date=t_90d,
            position=8,
            previous_position=None,
            change_in_position=0,
        )
    )
    repo.create_ranking_entry(
        RankingHistoryCreate(
            website_id=target_site.id,
            search_query_id=sq1.id,
            keyword=sq1.target_keyword,
            date=t_60d,
            position=8,
            previous_position=8,
            change_in_position=0,
        )
    )
    repo.create_ranking_entry(
        RankingHistoryCreate(
            website_id=target_site.id,
            search_query_id=sq1.id,
            keyword=sq1.target_keyword,
            date=t_30d,
            position=3,
            previous_position=8,
            change_in_position=5,
        )
    )
    repo.create_ranking_entry(
        RankingHistoryCreate(
            website_id=target_site.id,
            search_query_id=sq1.id,
            keyword=sq1.target_keyword,
            date=now,
            position=4,
            previous_position=3,
            change_in_position=-1,
        )
    )

    # Coursera history: leader
    repo.create_ranking_entry(
        RankingHistoryCreate(
            website_id=comp_coursera.id,
            search_query_id=sq1.id,
            keyword=sq1.target_keyword,
            date=t_90d,
            position=1,
            previous_position=None,
            change_in_position=0,
        )
    )
    repo.create_ranking_entry(
        RankingHistoryCreate(
            website_id=comp_coursera.id,
            search_query_id=sq1.id,
            keyword=sq1.target_keyword,
            date=now,
            position=1,
            previous_position=1,
            change_in_position=0,
        )
    )

    # ----------------------------------------------------
    # 4. SEO OPTIMIZATIONS
    # ----------------------------------------------------
    opt1 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=target_site.id,
            date=t_75d,
            optimization_type=OptimizationType.CONTENT_DEPTH,
            description="Added 1,600 words of generic descriptive background text on Python history and syntax.",
            reason_for_optimization="Competitors have 3,500+ words; hypothesis was that raw content volume signals topical authority.",
            expected_effect="+3 rank positions into top 5",
            observed_effect="Rank remained static at #8 (0 delta). High passive text length provided zero engagement signal.",
        )
    )

    opt2 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=target_site.id,
            date=t_45d,
            optimization_type=OptimizationType.INTERACTIVE_UX,
            description="Embedded in-browser Python code execution sandbox widget and filterable interactive curriculum table.",
            reason_for_optimization="Beginners want hands-on trial rather than reading passive encyclopedia paragraphs.",
            expected_effect="+4 to +5 positions by elevating on-page dwell time and user utility",
            observed_effect="Rank surged decisively from #8 to #3 (+5 positions) within 15 days.",
        )
    )

    # ----------------------------------------------------
    # 5. COMPETITOR HISTORY
    # ----------------------------------------------------
    repo.create_competitor_history(
        CompetitorHistoryCreate(
            competitor_website_id=comp_coursera.id,
            keyword=sq1.target_keyword,
            date=t_10d,
            content_changes=["Updated course syllabus review modules", "Added pricing transparency guarantee"],
            feature_changes=["Launched instant project preview video players"],
            ranking_changes={"before": 1, "after": 1, "delta": 0},
            notable_seo_changes=["Added EducationalOccupationalCredential schema", "Updated H2 targeting beginners"],
        )
    )

    repo.create_competitor_history(
        CompetitorHistoryCreate(
            competitor_website_id=comp_freecodecamp.id,
            keyword=sq1.target_keyword,
            date=t_14d,
            content_changes=["Refreshed video timestamps and downloadable cheatsheet"],
            feature_changes=["Integrated certificate completion badge preview"],
            ranking_changes={"before": 4, "after": 3, "delta": 1},
            notable_seo_changes=["Implemented Course and VideoObject structured schemas"],
        )
    )

    # ----------------------------------------------------
    # 6. OUTCOMES (Causal Attribution)
    # ----------------------------------------------------
    repo.create_outcome(
        OutcomeCreate(
            website_id=target_site.id,
            optimization_id=opt1.id,
            previous_ranking=8,
            new_ranking=8,
            observed_change="0 positions (no change)",
            date=t_60d,
            confidence=0.92,
            uncertainty_factors=["SERP volatility low during this window", "Competitor content was static"],
        )
    )

    repo.create_outcome(
        OutcomeCreate(
            website_id=target_site.id,
            optimization_id=opt2.id,
            previous_ranking=8,
            new_ranking=3,
            observed_change="+5 positions (#8 to #3)",
            date=t_30d,
            confidence=0.95,
            uncertainty_factors=["No algorithm core updates observed", "Direct correlation with user dwell time"],
        )
    )

    # ----------------------------------------------------
    # 7. CONTENT / CITATION INFORMATION
    # ----------------------------------------------------
    repo.create_citation(
        ContentCitationCreate(
            website_id=target_site.id,
            search_query_id=sq1.id,
            source_title="Python Software Foundation Official 2026 Developer Survey",
            source_url="https://www.python.org/dev/peps/pep-0000/",
            citation_snippet="Python is designated as the most popular entry-level language with 68% beginner preference.",
            citation_type=CitationType.AUTHORITATIVE_REFERENCE,
            is_used_by_app=True,
            citation_metadata={
                "section_referenced": "Executive Summary",
                "authority_score": 98,
                "verified_freshness": "2026-Q1",
            },
        )
    )

    repo.create_citation(
        ContentCitationCreate(
            website_id=comp_coursera.id,
            search_query_id=sq1.id,
            source_title="University of Michigan Python for Everybody Accreditation",
            source_url="https://online.umich.edu/series/python-for-everybody/",
            citation_snippet="Accredited academic credit program recognized across 40+ engineering colleges.",
            citation_type=CitationType.COMPETITOR_REFERENCE,
            is_used_by_app=True,
            citation_metadata={
                "relevance": "Key credibility differentiator holding Coursera at Rank #1",
            },
        )
    )

    # ----------------------------------------------------
    # 8. USER INTERACTION RECORDS
    # ----------------------------------------------------
    repo.create_user_interaction(
        UserInteractionCreate(
            search_query_id=sq1.id,
            query_text="best python courses for beginners",
            selected_website_id=target_site.id,
            question_asked="Why did my rank drop from #3 to #4 last week?",
            recommendation_requested="Identify competitor changes that displaced our page.",
            recommendation_provided="freeCodeCamp and Coursera both deployed video preview players and credential schemas within the last 14 days. Embedding video project walkthroughs is recommended to recapture #3.",
            feedback={"rating": 5, "helpful": True, "comment": "Clear causal explanation that identified the exact competitor change."},
            created_at=t_2d,
        )
    )

    print(f"[Seed] Successfully seeded all 8 entities into SQLite at {DB_PATH}!")
    return {
        "search_queries": 2,
        "websites": 4,
        "ranking_history_entries": 6,
        "seo_optimizations": 2,
        "competitor_events": 2,
        "outcomes": 2,
        "citations": 2,
        "user_interactions": 1,
    }


if __name__ == "__main__":
    populate_seed_data(reset=True)
