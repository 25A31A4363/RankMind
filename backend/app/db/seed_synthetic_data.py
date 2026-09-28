import json
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

DATASET_METADATA = {
    "is_synthetic": True,
    "version": "2.0.0",
    "disclaimer": "This is synthetic demonstration data generated for developing historical SEO attribution agents. It does NOT claim to represent actual Google search ranking facts.",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "scenarios_count": 3,
}


def populate_synthetic_seo_dataset(reset: bool = True) -> dict:
    """Seeds a realistic synthetic SEO history dataset across multiple search queries and dates.
    
    Includes realistic historical patterns:
    1. Query 1: 'best python courses for beginners' (7 competing domains, 4 time milestones)
       - Target: learnpythonhub.io (#8 -> #8 fluff -> #3 interactive tool -> #4 competitor counter-attack)
    2. Query 2: 'fastapi vs express performance' (5 competing domains, 3 time milestones)
       - Target: benchmarks-dev.io (#6 -> #2 reproducible docker benchmark -> #1 memory leak test)
    3. Query 3: 'ai code generation tools' (5 competing domains, 3 time milestones)
       - Target: devtools-radar.com (#9 -> #4 blind evaluation study -> #2 interactive pricing matrix)
    """
    init_db(reset=reset)
    repo = SEORepository(DB_PATH)

    now = datetime.now(timezone.utc)

    # Time milestones for Query 1 (90-day timeline)
    q1_t0 = now - timedelta(days=90)
    q1_t1 = now - timedelta(days=60)
    q1_t2 = now - timedelta(days=30)
    q1_t3 = now

    # =========================================================================
    # SCENARIO 1: "best python courses for beginners"
    # =========================================================================
    sq1 = repo.create_search_query(
        SearchQueryCreate(
            query="best python courses for beginners",
            target_keyword="best python courses for beginners",
            search_intent=SearchIntent.COMMERCIAL,
            date=q1_t0,
            location="United States",
        )
    )

    # 1.1 Websites for Scenario 1
    w_learnpython = repo.create_website(
        WebsiteCreate(
            id="site_learnpythonhub",
            domain="learnpythonhub.io",
            title="Best Python Courses for Beginners in 2026 (Curated Interactive Guide)",
            url="https://learnpythonhub.io/best-python-courses-beginners",
            content_topic="Python Programming Education",
            seo_observations={
                "is_synthetic": True,
                "word_count": 3650,
                "has_interactive_widget": True,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Article", "ItemList"],
                "readability_score": 83.0,
                "citation_density": 4.5,
                "domain_authority_sim": 54,
            },
        )
    )

    w_coursera = repo.create_website(
        WebsiteCreate(
            id="site_coursera",
            domain="coursera.org",
            title="Python for Everybody Specialization | Coursera",
            url="https://www.coursera.org/specializations/python",
            content_topic="Online University Specialization",
            seo_observations={
                "is_synthetic": True,
                "word_count": 3600,
                "has_interactive_widget": True,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Course", "Organization", "EducationalOccupationalCredential"],
                "readability_score": 84.0,
                "citation_density": 4.3,
                "domain_authority_sim": 92,
            },
        )
    )

    w_codecademy = repo.create_website(
        WebsiteCreate(
            id="site_codecademy",
            domain="codecademy.com",
            title="Learn Python 3 | Codecademy",
            url="https://www.codecademy.com/learn/learn-python-3",
            content_topic="Interactive Coding Platform",
            seo_observations={
                "is_synthetic": True,
                "word_count": 2300,
                "has_interactive_widget": True,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Course", "FAQPage"],
                "readability_score": 86.0,
                "citation_density": 3.4,
                "domain_authority_sim": 88,
            },
        )
    )

    w_freecodecamp = repo.create_website(
        WebsiteCreate(
            id="site_freecodecamp",
            domain="freecodecamp.org",
            title="Python for Beginners - Full Course (Video & Certificate) | freeCodeCamp.org",
            url="https://www.freecodecamp.org/news/python-for-beginners-full-course/",
            content_topic="Free Open-Source Tech Education",
            seo_observations={
                "is_synthetic": True,
                "word_count": 4900,
                "has_interactive_widget": False,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Article", "VideoObject", "Course"],
                "readability_score": 81.0,
                "citation_density": 5.2,
                "domain_authority_sim": 89,
            },
        )
    )

    w_udemy = repo.create_website(
        WebsiteCreate(
            id="site_udemy",
            domain="udemy.com",
            title="2026 Complete Python Bootcamp From Zero to Hero | Udemy",
            url="https://www.udemy.com/course/complete-python-bootcamp/",
            content_topic="Online Marketplace Courses",
            seo_observations={
                "is_synthetic": True,
                "word_count": 2950,
                "has_interactive_widget": False,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Course", "AggregateRating"],
                "readability_score": 80.0,
                "citation_density": 2.8,
                "domain_authority_sim": 90,
            },
        )
    )

    w_realpython = repo.create_website(
        WebsiteCreate(
            id="site_realpython",
            domain="realpython.com",
            title="Python Basics: A Practical Introduction | Real Python",
            url="https://realpython.com/learning-paths/python-basics/",
            content_topic="In-depth Python Tutorials",
            seo_observations={
                "is_synthetic": True,
                "word_count": 4100,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Article", "BreadcrumbList"],
                "readability_score": 85.0,
                "citation_density": 6.1,
                "domain_authority_sim": 78,
            },
        )
    )

    w_edx = repo.create_website(
        WebsiteCreate(
            id="site_edx",
            domain="edx.org",
            title="CS50: Introduction to Computer Science & Python | edX",
            url="https://www.edx.org/course/introduction-to-computer-science-and-programming-using-python",
            content_topic="University Online Education",
            seo_observations={
                "is_synthetic": True,
                "word_count": 2600,
                "has_interactive_widget": False,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Course"],
                "readability_score": 76.0,
                "citation_density": 4.5,
                "domain_authority_sim": 91,
            },
        )
    )

    # 1.2 Ranking Milestones for Scenario 1
    # Day -90 (Baseline)
    ranks_t0 = [
        (w_coursera.id, 1, None),
        (w_codecademy.id, 2, None),
        (w_freecodecamp.id, 3, None),
        (w_udemy.id, 4, None),
        (w_realpython.id, 5, None),
        (w_edx.id, 6, None),
        (w_learnpython.id, 8, None),
    ]
    for wid, pos, prev in ranks_t0:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq1.id,
                keyword=sq1.target_keyword,
                date=q1_t0,
                position=pos,
                previous_position=prev,
                change_in_position=0,
            )
        )

    # Day -75: User executed Optimization 1 (fluff expansion)
    opt1_q1 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=w_learnpython.id,
            date=now - timedelta(days=75),
            optimization_type=OptimizationType.CONTENT_DEPTH,
            description="Expanded article by adding 1,600 words of background text on Python history and general concepts.",
            reason_for_optimization="Competitors have 3,500+ words; team assumed raw word volume signals higher topical authority.",
            expected_effect="+3 rank positions into top 5",
            observed_effect="Rank remained static at #8 (0 delta). High passive text length provided zero engagement signal.",
        )
    )

    # Day -60: Evaluation after fluff expansion (No change for target site)
    ranks_t1 = [
        (w_coursera.id, 1, 1),
        (w_codecademy.id, 2, 2),
        (w_freecodecamp.id, 3, 3),
        (w_udemy.id, 4, 4),
        (w_realpython.id, 5, 5),
        (w_edx.id, 6, 6),
        (w_learnpython.id, 8, 8),
    ]
    for wid, pos, prev in ranks_t1:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq1.id,
                keyword=sq1.target_keyword,
                date=q1_t1,
                position=pos,
                previous_position=prev,
                change_in_position=prev - pos,
            )
        )

    # Outcome 1: Causal record for fluff expansion
    repo.create_outcome(
        OutcomeCreate(
            website_id=w_learnpython.id,
            optimization_id=opt1_q1.id,
            previous_ranking=8,
            new_ranking=8,
            observed_change="0 positions (no change)",
            date=q1_t1,
            confidence=0.92,
            uncertainty_factors=["SERP volatility low during this window", "Competitors were static"],
        )
    )

    # Day -45: User executed Optimization 2 (Interactive Code Sandbox & Matrix)
    opt2_q1 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=w_learnpython.id,
            date=now - timedelta(days=45),
            optimization_type=OptimizationType.INTERACTIVE_UX,
            description="Embedded in-browser Python code execution sandbox widget and filterable interactive curriculum table.",
            reason_for_optimization="Beginners want hands-on trial rather than reading passive encyclopedia paragraphs.",
            expected_effect="+4 to +5 positions by elevating on-page dwell time and user utility",
            observed_effect="Rank surged decisively from #8 to #3 (+5 positions) within 15 days.",
        )
    )

    # Day -30: Evaluation after interactive tool (Rank surged #8 -> #3!)
    ranks_t2 = [
        (w_coursera.id, 1, 1),
        (w_codecademy.id, 2, 2),
        (w_learnpython.id, 3, 8),  # Surged!
        (w_freecodecamp.id, 4, 3),
        (w_udemy.id, 5, 4),
        (w_realpython.id, 6, 5),
        (w_edx.id, 7, 6),
    ]
    for wid, pos, prev in ranks_t2:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq1.id,
                keyword=sq1.target_keyword,
                date=q1_t2,
                position=pos,
                previous_position=prev,
                change_in_position=prev - pos,
            )
        )

    # Outcome 2: Causal record for interactive widget
    repo.create_outcome(
        OutcomeCreate(
            website_id=w_learnpython.id,
            optimization_id=opt2_q1.id,
            previous_ranking=8,
            new_ranking=3,
            observed_change="+5 positions (#8 to #3)",
            date=q1_t2,
            confidence=0.95,
            uncertainty_factors=["No algorithm core updates observed", "Direct correlation with user dwell time"],
        )
    )

    # Day -14 to -10: Competitor counter-moves
    repo.create_competitor_history(
        CompetitorHistoryCreate(
            competitor_website_id=w_coursera.id,
            keyword=sq1.target_keyword,
            date=now - timedelta(days=10),
            content_changes=["Updated course syllabus review modules", "Added pricing transparency guarantee"],
            feature_changes=["Launched instant project preview video players"],
            ranking_changes={"before": 1, "after": 1, "delta": 0},
            notable_seo_changes=["Added EducationalOccupationalCredential schema", "Updated H2 targeting beginners"],
        )
    )

    repo.create_competitor_history(
        CompetitorHistoryCreate(
            competitor_website_id=w_freecodecamp.id,
            keyword=sq1.target_keyword,
            date=now - timedelta(days=14),
            content_changes=["Refreshed video timestamps and downloadable cheatsheet"],
            feature_changes=["Integrated certificate completion badge preview"],
            ranking_changes={"before": 4, "after": 3, "delta": 1},
            notable_seo_changes=["Implemented Course and VideoObject structured schemas"],
        )
    )

    # Day 0 (Current): Target dropped to #4 due to competitor additions
    ranks_t3 = [
        (w_coursera.id, 1, 1),
        (w_codecademy.id, 2, 2),
        (w_freecodecamp.id, 3, 4),  # Re-overtook #3
        (w_learnpython.id, 4, 3),   # Slipped to #4
        (w_udemy.id, 5, 5),
        (w_realpython.id, 6, 6),
        (w_edx.id, 7, 7),
    ]
    for wid, pos, prev in ranks_t3:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq1.id,
                keyword=sq1.target_keyword,
                date=q1_t3,
                position=pos,
                previous_position=prev,
                change_in_position=prev - pos,
            )
        )

    # Citations for Scenario 1
    repo.create_citation(
        ContentCitationCreate(
            website_id=w_learnpython.id,
            search_query_id=sq1.id,
            source_title="Python Software Foundation Official 2026 Developer Survey",
            source_url="https://www.python.org/dev/peps/pep-0000/",
            citation_snippet="Python is designated as the most popular entry-level language with 68% beginner preference.",
            citation_type=CitationType.AUTHORITATIVE_REFERENCE,
            is_used_by_app=True,
            citation_metadata={
                "authority_score": 98,
                "verified_freshness": "2026-Q1",
            },
        )
    )

    # User Interaction for Scenario 1
    repo.create_user_interaction(
        UserInteractionCreate(
            search_query_id=sq1.id,
            query_text=sq1.query,
            selected_website_id=w_learnpython.id,
            question_asked="Why did my rank drop from #3 to #4 last week?",
            recommendation_requested="Identify competitor changes that displaced our page.",
            recommendation_provided="freeCodeCamp and Coursera both deployed video preview players and credential schemas within the last 14 days. Embedding video project walkthroughs is recommended to recapture #3.",
            feedback={"rating": 5, "helpful": True, "comment": "Clear causal explanation that identified the exact competitor change."},
            created_at=now - timedelta(days=2),
        )
    )

    # =========================================================================
    # SCENARIO 2: "fastapi vs express performance"
    # =========================================================================
    q2_t0 = now - timedelta(days=60)
    q2_t1 = now - timedelta(days=30)
    q2_t2 = now

    sq2 = repo.create_search_query(
        SearchQueryCreate(
            query="fastapi vs express performance",
            target_keyword="fastapi vs express performance",
            search_intent=SearchIntent.INFORMATIONAL,
            date=q2_t0,
            location="Global",
        )
    )

    w_benchmarks = repo.create_website(
        WebsiteCreate(
            id="site_benchmarks_dev",
            domain="benchmarks-dev.io",
            title="FastAPI vs Express.js 2026 Benchmark (Throughput & Latency)",
            url="https://benchmarks-dev.io/fastapi-vs-express-benchmark",
            content_topic="Backend Performance Engineering",
            seo_observations={
                "is_synthetic": True,
                "word_count": 3200,
                "has_interactive_widget": True,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["TechArticle", "Dataset"],
                "readability_score": 79.0,
                "citation_density": 5.8,
            },
        )
    )

    w_logrocket = repo.create_website(
        WebsiteCreate(
            id="site_logrocket",
            domain="blog.logrocket.com",
            title="Node vs Python: Express vs FastAPI Performance Comparison",
            url="https://blog.logrocket.com/fastapi-vs-express-performance/",
            content_topic="Developer Blog",
            seo_observations={
                "is_synthetic": True,
                "word_count": 2800,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Article"],
                "readability_score": 82.0,
                "citation_density": 3.9,
            },
        )
    )

    w_devto = repo.create_website(
        WebsiteCreate(
            id="site_devto",
            domain="dev.to",
            title="Benchmarking FastAPI against Express: Real-World Latency",
            url="https://dev.to/benchmarks/fastapi-vs-express",
            content_topic="Community Engineering Posts",
            seo_observations={
                "is_synthetic": True,
                "word_count": 1900,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": False,
                "schema_types": ["SocialMediaPosting"],
                "readability_score": 80.0,
                "citation_density": 2.1,
            },
        )
    )

    w_medium = repo.create_website(
        WebsiteCreate(
            id="site_medium_eng",
            domain="medium.com",
            title="Why We Migrated From Express to FastAPI: Benchmarks Included",
            url="https://medium.com/engineering-deepdive/migrated-express-fastapi",
            content_topic="Architecture Case Studies",
            seo_observations={
                "is_synthetic": True,
                "word_count": 2400,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Article"],
                "readability_score": 77.0,
                "citation_density": 3.2,
            },
        )
    )

    w_k6 = repo.create_website(
        WebsiteCreate(
            id="site_k6_io",
            domain="k6.io",
            title="Load Testing FastAPI and Node.js with k6",
            url="https://k6.io/blog/load-testing-fastapi-vs-express/",
            content_topic="Load Testing & Observability",
            seo_observations={
                "is_synthetic": True,
                "word_count": 3100,
                "has_interactive_widget": False,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Article", "SoftwareSourceCode"],
                "readability_score": 83.0,
                "citation_density": 4.8,
            },
        )
    )

    # Rankings Day -60 (Baseline)
    q2_ranks_t0 = [
        (w_logrocket.id, 1, None),
        (w_k6.id, 2, None),
        (w_medium.id, 3, None),
        (w_devto.id, 4, None),
        (w_benchmarks.id, 6, None),  # Target site starts at #6
    ]
    for wid, pos, prev in q2_ranks_t0:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq2.id,
                keyword=sq2.target_keyword,
                date=q2_t0,
                position=pos,
                previous_position=prev,
                change_in_position=0,
            )
        )

    # Day -45: Action 1 for Scenario 2 (Added Reproducible Docker Repo + Interactive Chart)
    opt1_q2 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=w_benchmarks.id,
            date=now - timedelta(days=45),
            optimization_type=OptimizationType.TECHNICAL_SPEED,
            description="Added open-source GitHub Docker reproduction repo link and interactive client-side chart comparing p95 latency under 10k req/s load.",
            reason_for_optimization="Technical readers demand reproducible methodology; Google rewards verifiable technical documentation.",
            expected_effect="+3 to +4 positions into top 3",
            observed_effect="Rank moved from #6 to #2 (+4 positions) within 15 days.",
        )
    )

    # Rankings Day -30: Target surged to #2
    q2_ranks_t1 = [
        (w_logrocket.id, 1, 1),
        (w_benchmarks.id, 2, 6),  # Surged!
        (w_k6.id, 3, 2),
        (w_medium.id, 4, 3),
        (w_devto.id, 5, 4),
    ]
    for wid, pos, prev in q2_ranks_t1:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq2.id,
                keyword=sq2.target_keyword,
                date=q2_t1,
                position=pos,
                previous_position=prev,
                change_in_position=prev - pos,
            )
        )

    # Outcome 1 for Scenario 2
    repo.create_outcome(
        OutcomeCreate(
            website_id=w_benchmarks.id,
            optimization_id=opt1_q2.id,
            previous_ranking=6,
            new_ranking=2,
            observed_change="+4 positions (#6 to #2)",
            date=q2_t1,
            confidence=0.96,
            uncertainty_factors=["High organic backlink gain from Reddit/HackerNews post"],
        )
    )

    # Day -15: Action 2 for Scenario 2 (Added Python 3.13 / Node 22 JIT deep-dive & Dataset schema)
    opt2_q2 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=w_benchmarks.id,
            date=now - timedelta(days=15),
            optimization_type=OptimizationType.SCHEMA_MARKUP,
            description="Implemented Dataset Schema with raw JSON latency exports and updated tests for Python 3.13 free-threading vs Node 22 Maglev.",
            reason_for_optimization="Capture Google Dataset search snippet and target featured snippet answer box.",
            expected_effect="+1 position to take #1 rank",
            observed_effect="Captured featured snippet answer box; achieved Rank #1.",
        )
    )

    # Rankings Day 0 (Current): Target captured #1
    q2_ranks_t2 = [
        (w_benchmarks.id, 1, 2),  # #1 Rank!
        (w_logrocket.id, 2, 1),
        (w_k6.id, 3, 3),
        (w_medium.id, 4, 4),
        (w_devto.id, 5, 5),
    ]
    for wid, pos, prev in q2_ranks_t2:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq2.id,
                keyword=sq2.target_keyword,
                date=q2_t2,
                position=pos,
                previous_position=prev,
                change_in_position=prev - pos,
            )
        )

    # Outcome 2 for Scenario 2
    repo.create_outcome(
        OutcomeCreate(
            website_id=w_benchmarks.id,
            optimization_id=opt2_q2.id,
            previous_ranking=2,
            new_ranking=1,
            observed_change="+1 position (#2 to #1 - Captured Snippet)",
            date=q2_t2,
            confidence=0.94,
            uncertainty_factors=["Dataset rich snippet captured in search result"],
        )
    )

    # Citations for Scenario 2
    repo.create_citation(
        ContentCitationCreate(
            website_id=w_benchmarks.id,
            search_query_id=sq2.id,
            source_title="TechEmpower Web Framework Benchmarks Round 22",
            source_url="https://www.techempower.com/benchmarks/",
            citation_snippet="Standardized JSON serialization and database query throughput testing harness.",
            citation_type=CitationType.DATASET_SOURCE,
            is_used_by_app=True,
            citation_metadata={"round": 22, "hardware": "Dedicated Dell R440"},
        )
    )

    # =========================================================================
    # SCENARIO 3: "ai code generation tools"
    # =========================================================================
    q3_t0 = now - timedelta(days=60)
    q3_t1 = now - timedelta(days=30)
    q3_t2 = now

    sq3 = repo.create_search_query(
        SearchQueryCreate(
            query="ai code generation tools",
            target_keyword="ai code generation tools",
            search_intent=SearchIntent.COMMERCIAL,
            date=q3_t0,
            location="Global",
        )
    )

    w_radar = repo.create_website(
        WebsiteCreate(
            id="site_devtools_radar",
            domain="devtools-radar.com",
            title="Best AI Code Generation Tools in 2026 (Benchmark & Privacy Matrix)",
            url="https://devtools-radar.com/ai-code-generation-tools",
            content_topic="AI Developer Tooling",
            seo_observations={
                "is_synthetic": True,
                "word_count": 3800,
                "has_interactive_widget": True,
                "has_video_preview": True,
                "has_curriculum_table": True,
                "schema_types": ["Article", "Product"],
                "readability_score": 82.0,
                "citation_density": 6.0,
            },
        )
    )

    w_zapier = repo.create_website(
        WebsiteCreate(
            id="site_zapier",
            domain="zapier.com",
            title="The Best AI Code Generators and Coding Assistants in 2026",
            url="https://zapier.com/blog/best-ai-code-tools/",
            content_topic="Software Review Blog",
            seo_observations={
                "is_synthetic": True,
                "word_count": 4200,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Article"],
                "readability_score": 87.0,
                "citation_density": 4.1,
            },
        )
    )

    w_github_blog = repo.create_website(
        WebsiteCreate(
            id="site_github_blog",
            domain="github.blog",
            title="How Generative AI and Copilot are Transforming Developer Productivity",
            url="https://github.blog/ai-code-generation/",
            content_topic="Engineering Research",
            seo_observations={
                "is_synthetic": True,
                "word_count": 2900,
                "has_interactive_widget": False,
                "has_video_preview": True,
                "has_curriculum_table": False,
                "schema_types": ["Article"],
                "readability_score": 81.0,
                "citation_density": 5.0,
            },
        )
    )

    w_techradar = repo.create_website(
        WebsiteCreate(
            id="site_techradar",
            domain="techradar.com",
            title="Best AI Coding Assistant in 2026: Tested by Coders",
            url="https://www.techradar.com/best/ai-coding-assistant",
            content_topic="Consumer Tech Hardware & Software",
            seo_observations={
                "is_synthetic": True,
                "word_count": 3500,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": True,
                "schema_types": ["Review", "Product"],
                "readability_score": 79.0,
                "citation_density": 3.2,
            },
        )
    )

    w_geeks = repo.create_website(
        WebsiteCreate(
            id="site_geeksforgeeks",
            domain="geeksforgeeks.org",
            title="Top 10 AI Tools for Code Generation",
            url="https://www.geeksforgeeks.org/top-ai-tools-for-code-generation/",
            content_topic="Educational Programming Portal",
            seo_observations={
                "is_synthetic": True,
                "word_count": 2100,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": False,
                "schema_types": ["Article"],
                "readability_score": 75.0,
                "citation_density": 2.0,
            },
        )
    )

    # Rankings Day -60 (Baseline)
    q3_ranks_t0 = [
        (w_zapier.id, 1, None),
        (w_github_blog.id, 2, None),
        (w_techradar.id, 3, None),
        (w_geeks.id, 4, None),
        (w_radar.id, 9, None),  # Target site starts at #9
    ]
    for wid, pos, prev in q3_ranks_t0:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq3.id,
                keyword=sq3.target_keyword,
                date=q3_t0,
                position=pos,
                previous_position=prev,
                change_in_position=0,
            )
        )

    # Action 1 for Scenario 3: Blind Benchmark Test Suite
    opt1_q3 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=w_radar.id,
            date=now - timedelta(days=40),
            optimization_type=OptimizationType.CONTENT_DEPTH,
            description="Published empirical blind evaluation testing 12 tools across 50 LeetCode & refactoring tasks with downloadable CSV results.",
            reason_for_optimization="Generic 'top 10' lists lack testing evidence; empirical scores establish decisive E-E-A-T signals.",
            expected_effect="+4 to +5 positions",
            observed_effect="Rank surged from #9 to #4 (+5 positions).",
        )
    )

    # Rankings Day -30: Target surged to #4
    q3_ranks_t1 = [
        (w_zapier.id, 1, 1),
        (w_github_blog.id, 2, 2),
        (w_techradar.id, 3, 3),
        (w_radar.id, 4, 9),  # Surged!
        (w_geeks.id, 5, 4),
    ]
    for wid, pos, prev in q3_ranks_t1:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq3.id,
                keyword=sq3.target_keyword,
                date=q3_t1,
                position=pos,
                previous_position=prev,
                change_in_position=prev - pos,
            )
        )

    repo.create_outcome(
        OutcomeCreate(
            website_id=w_radar.id,
            optimization_id=opt1_q3.id,
            previous_ranking=9,
            new_ranking=4,
            observed_change="+5 positions (#9 to #4)",
            date=q3_t1,
            confidence=0.94,
            uncertainty_factors=["High natural citation pickup across tech newsletters"],
        )
    )

    # Action 2 for Scenario 3: Interactive Pricing & Privacy Matrix
    opt2_q3 = repo.create_optimization(
        SEOOptimizationCreate(
            website_id=w_radar.id,
            date=now - timedelta(days=18),
            optimization_type=OptimizationType.INTERACTIVE_UX,
            description="Embedded interactive seat-cost pricing calculator and privacy policy audit matrix (zero-data retention verification).",
            reason_for_optimization="Enterprise developers evaluate compliance and pricing; calculator matches high-intent search needs.",
            expected_effect="+2 positions to reach #2",
            observed_effect="Rank improved from #4 to #2, displacing GitHub Blog and TechRadar.",
        )
    )

    # Rankings Day 0 (Current): Target reached #2
    q3_ranks_t2 = [
        (w_zapier.id, 1, 1),
        (w_radar.id, 2, 4),  # Reached #2!
        (w_github_blog.id, 3, 2),
        (w_techradar.id, 4, 3),
        (w_geeks.id, 5, 5),
    ]
    for wid, pos, prev in q3_ranks_t2:
        repo.create_ranking_entry(
            RankingHistoryCreate(
                website_id=wid,
                search_query_id=sq3.id,
                keyword=sq3.target_keyword,
                date=q3_t2,
                position=pos,
                previous_position=prev,
                change_in_position=prev - pos,
            )
        )

    repo.create_outcome(
        OutcomeCreate(
            website_id=w_radar.id,
            optimization_id=opt2_q3.id,
            previous_ranking=4,
            new_ranking=2,
            observed_change="+2 positions (#4 to #2)",
            date=q3_t2,
            confidence=0.89,
            uncertainty_factors=["Zapier retains high brand authority at #1"],
        )
    )

    # User Interaction for Scenario 3
    repo.create_user_interaction(
        UserInteractionCreate(
            search_query_id=sq3.id,
            query_text=sq3.query,
            selected_website_id=w_radar.id,
            question_asked="How can we overtake Zapier for the #1 position?",
            recommendation_requested="Identify remaining gap holding Zapier at #1.",
            recommendation_provided="Zapier maintains #1 due to massive brand domain authority and deep integration guides. Adding hands-on workflow video tutorials for enterprise IDE integration is recommended to compete for the featured snippet.",
            feedback={"rating": 5, "helpful": True, "comment": "Actionable enterprise gap identified."},
            created_at=now - timedelta(days=1),
        )
    )

    summary = {
        "status": "success",
        "metadata": DATASET_METADATA,
        "counts": {
            "search_queries": 3,
            "websites": 17,
            "ranking_history_entries": 39,
            "seo_optimizations": 6,
            "competitor_events": 2,
            "outcomes": 6,
            "citations": 2,
            "user_interactions": 2,
        },
    }
    print(f"[Seed] Successfully seeded synthetic SEO dataset: {summary['counts']}")
    return summary


if __name__ == "__main__":
    populate_synthetic_seo_dataset(reset=True)
