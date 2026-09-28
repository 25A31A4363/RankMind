import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from app.db.database import DB_PATH
from app.repositories.seo_repository import SEORepository
from app.models.analyzer_schemas import (
    BaselineAnalysisRequest,
    BaselineAnalysisResult,
    CurrentObservations,
    TitleAnalysis,
    MetaDescriptionAnalysis,
    HeadingStructureAnalysis,
    ContentCompleteness,
    KeywordTopicCoverage,
    InternalContentStructure,
    UserExperienceObservations,
    TechnicalSEOObservations,
    ProblemItem,
    OpportunityItem,
    RecommendedActionItem,
)


class SEOAnalyzer:
    """Baseline Static SEO Analyzer (v1.0 - Zero Hindsight Memory).
    
    Evaluates on-page signals, search intent alignment, technical features, 
    and content architecture purely on static heuristic rules.
    Does NOT consult past ranking memory or competitor causal timelines.
    """

    def __init__(self, db_path=DB_PATH):
        self.repo = SEORepository(db_path)

    def analyze(self, request: BaselineAnalysisRequest) -> BaselineAnalysisResult:
        query = request.query.strip()
        target_keyword = query.lower()

        # 1. Resolve Target Website & Data Source
        website_data, source_type = self._resolve_website(request)

        # 2. Extract Signals
        obs = website_data.get("seo_observations", {})
        title_text = request.custom_title or website_data.get("title", "")
        domain = website_data.get("domain", "")
        url = request.url or website_data.get("url", f"https://{domain}")
        word_count = obs.get("word_count", 2500)

        # Fallback meta description if not explicitly set
        meta_desc = request.custom_meta_description or obs.get(
            "meta_description",
            f"Comprehensive {target_keyword} evaluated on pricing, features, curriculum depth, and real-world student outcomes.",
        )

        # 3. Intent Detection & Alignment
        intent, intent_match_score = self._evaluate_search_intent(query, obs, title_text)

        # 4. Perform Granular Analyses
        title_analysis = self._analyze_title(title_text, target_keyword)
        meta_analysis = self._analyze_meta_description(meta_desc, target_keyword)
        headings_analysis = self._analyze_headings(title_text, obs, target_keyword)
        completeness_analysis = self._analyze_content_completeness(word_count, intent, obs)
        coverage_analysis = self._analyze_topic_coverage(target_keyword, title_text, obs)
        structure_analysis = self._analyze_internal_structure(obs)
        ux_analysis = self._analyze_user_experience(obs)
        technical_analysis = self._analyze_technical_seo(obs, intent)

        current_obs = CurrentObservations(
            search_intent_detected=intent,
            intent_match_score=intent_match_score,
            title=title_analysis,
            meta_description=meta_analysis,
            headings=headings_analysis,
            content_completeness=completeness_analysis,
            keyword_coverage=coverage_analysis,
            internal_structure=structure_analysis,
            user_experience=ux_analysis,
            technical_seo=technical_analysis,
        )

        # 5. Extract Problems, Opportunities & Recommended Actions
        problems = self._identify_problems(current_obs, domain)
        opportunities = self._identify_opportunities(current_obs, domain)
        recommended_actions = self._generate_recommended_actions(problems, opportunities, intent)

        # 6. Generate Machine-Readable LLM Prompt Summary
        llm_summary = self._generate_llm_summary(
            query=query,
            domain=domain,
            intent=intent,
            intent_score=intent_match_score,
            current_obs=current_obs,
            problems=problems,
            opportunities=opportunities,
            recommendations=recommended_actions,
        )

        return BaselineAnalysisResult(
            analysis_id=f"base_ana_{uuid.uuid4().hex[:10]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            query=query,
            target_keyword=target_keyword,
            target_domain=domain,
            target_url=url,
            hindsight_memory_applied=False,
            data_source_type=source_type,
            current_observations=current_obs,
            problems=problems,
            opportunities=opportunities,
            recommended_actions=recommended_actions,
            llm_prompt_summary=llm_summary,
        )

    # =========================================================================
    # Internal Signal Extractors
    # =========================================================================

    def _resolve_website(self, req: BaselineAnalysisRequest) -> tuple[Dict[str, Any], str]:
        """Resolves website data from database or constructs an ad-hoc record."""
        if req.website_id:
            site = self.repo.get_website(req.website_id)
            if site:
                return site.model_dump(), "synthetic_database"

        if req.url:
            parsed = urlparse(req.url)
            domain = parsed.netloc.lower() or parsed.path.lower()
            site = self.repo.get_website_by_domain(domain)
            if site:
                return site.model_dump(), "synthetic_database"
            # Ad-hoc URL input
            return {
                "id": f"adhoc_{uuid.uuid4().hex[:8]}",
                "domain": domain or "custom-site.com",
                "title": req.custom_title or f"Guide to {req.query}",
                "url": req.url,
                "content_topic": "General Web",
                "seo_observations": {
                    "word_count": len(req.custom_content.split()) if req.custom_content else 2400,
                    "has_interactive_widget": False,
                    "has_video_preview": False,
                    "has_curriculum_table": False,
                    "schema_types": ["Article"],
                    "readability_score": 78.0,
                },
            }, "ad_hoc_input"

        # Match query keywords against website domains or content topics
        sites = self.repo.list_websites()
        if sites:
            q_lower = req.query.lower()
            tokens = [w for w in q_lower.split() if len(w) > 3]
            for s in sites:
                s_topic = s.content_topic.lower()
                s_dom = s.domain.lower()
                if any(t in s_dom or t in s_topic for t in tokens):
                    return s.model_dump(), "synthetic_database"
            return sites[0].model_dump(), "synthetic_database"

        return {
            "id": "adhoc_default",
            "domain": "example-site.com",
            "title": f"Complete Guide to {req.query}",
            "url": f"https://example-site.com/{req.query.replace(' ', '-')}",
            "content_topic": "Technology",
            "seo_observations": {
                "word_count": 2500,
                "has_interactive_widget": False,
                "has_video_preview": False,
                "has_curriculum_table": False,
                "schema_types": ["Article"],
                "readability_score": 75.0,
            },
        }, "ad_hoc_input"

    def _evaluate_search_intent(self, query: str, obs: Dict[str, Any], title: str) -> tuple[str, float]:
        q = query.lower()
        if any(w in q for w in ["best", "vs", "versus", "top", "review", "compare", "comparison"]):
            intent = "commercial"
            score = 75.0
            if obs.get("has_curriculum_table") or obs.get("has_comparison_table"):
                score += 15.0
            if obs.get("has_interactive_widget"):
                score += 10.0
        elif any(w in q for w in ["how to", "what is", "learn", "guide", "tutorial", "code", "explain"]):
            intent = "informational"
            score = 80.0
            if obs.get("word_count", 0) >= 3000:
                score += 10.0
            if obs.get("has_interactive_widget"):
                score += 10.0
        elif any(w in q for w in ["buy", "order", "price", "cost", "enroll", "signup"]):
            intent = "transactional"
            score = 70.0
        else:
            intent = "informational"
            score = 75.0

        return intent, min(score, 98.0)

    def _analyze_title(self, title: str, keyword: str) -> TitleAnalysis:
        char_len = len(title)
        is_optimal_len = 45 <= char_len <= 65

        # Check keyword presence & position
        t_lower = title.lower()
        contains_kw = keyword in t_lower
        
        # Word-level check if full phrase doesn't match verbatim
        kw_tokens = keyword.split()
        matched_tokens = [w for w in kw_tokens if w in t_lower]
        partial_match = len(matched_tokens) >= max(2, len(kw_tokens) - 1)

        if contains_kw:
            pos_idx = t_lower.find(keyword)
            if pos_idx < 15:
                kw_pos = "front"
            elif pos_idx > len(t_lower) - len(keyword) - 15:
                kw_pos = "end"
            else:
                kw_pos = "middle"
        elif partial_match:
            kw_pos = "middle"
            contains_kw = True
        else:
            kw_pos = "missing"

        has_power_words = any(w in t_lower for w in ["2026", "best", "curated", "guide", "review", "benchmark", "complete", "interactive"])

        if is_optimal_len and contains_kw and has_power_words:
            status = "optimal"
        elif not contains_kw or char_len < 30 or char_len > 70:
            status = "critical_issue"
        else:
            status = "needs_optimization"

        return TitleAnalysis(
            title_text=title,
            char_length=char_len,
            is_length_optimal=is_optimal_len,
            contains_target_keyword=contains_kw,
            keyword_position=kw_pos,
            has_power_words_or_year=has_power_words,
            title_status=status,
        )

    def _analyze_meta_description(self, desc: str, keyword: str) -> MetaDescriptionAnalysis:
        char_len = len(desc)
        is_optimal = 115 <= char_len <= 165
        t_lower = desc.lower()
        contains_kw = any(w in t_lower for w in keyword.split()[:2])
        has_cta = any(w in t_lower for w in ["compare", "discover", "learn", "find", "explore", "read", "evaluate", "start"])
        truncation_risk = char_len > 165

        status = "optimal" if is_optimal and contains_kw and has_cta else "needs_optimization"
        if char_len < 80:
            status = "too_short"

        return MetaDescriptionAnalysis(
            description_text=desc,
            char_length=char_len,
            is_length_optimal=is_optimal,
            contains_target_keyword=contains_kw,
            has_call_to_action=has_cta,
            truncation_risk=truncation_risk,
            meta_status=status,
        )

    def _analyze_headings(self, title: str, obs: Dict[str, Any], keyword: str) -> HeadingStructureAnalysis:
        h1_text = title.split("|")[0].split("-")[0].strip()
        h1_match = any(w in h1_text.lower() for w in keyword.split()[:2])
        h2_count = obs.get("h2_count", 6)
        h3_count = obs.get("h3_count", 12)
        has_hierarchy = h2_count >= 3 and h3_count >= 4
        score = 85.0 if has_hierarchy and h1_match else 68.0

        return HeadingStructureAnalysis(
            h1_text=h1_text,
            h1_count=1,
            h1_contains_keyword=h1_match,
            h2_count=h2_count,
            h3_count=h3_count,
            has_logical_hierarchy=has_hierarchy,
            scan_friendliness_score=score,
        )

    def _analyze_content_completeness(self, word_count: int, intent: str, obs: Dict[str, Any]) -> ContentCompleteness:
        benchmark = 3500 if intent in ["commercial", "informational"] else 2200
        comp_pct = round(min((word_count / benchmark) * 100.0, 100.0), 1)
        read_time = max(1, round(word_count / 220))
        readability = obs.get("readability_score", 81.0)
        ease = "Easy" if readability >= 80 else "Standard" if readability >= 65 else "Complex"

        return ContentCompleteness(
            word_count=word_count,
            intent_benchmark_word_count=benchmark,
            completeness_percentage=comp_pct,
            estimated_read_time_minutes=read_time,
            readability_score=readability,
            reading_ease_level=ease,
        )

    def _analyze_topic_coverage(self, keyword: str, title: str, obs: Dict[str, Any]) -> KeywordTopicCoverage:
        # Determine relevant subtopics based on keyword domain
        if "python" in keyword:
            expected = ["Curriculum & Syllabus", "Pricing & Free vs Paid", "Hands-on Projects", "Certification Value", "Beginner Prerequisites"]
        elif "fastapi" in keyword or "express" in keyword:
            expected = ["Latency Benchmarks (p95/p99)", "RPS Throughput", "Memory Consumption", "Async Concurrency", "Reproducible Repository"]
        else:
            expected = ["Feature Comparison", "Pricing Models", "Security & Data Privacy", "API Integrations", "Pros & Cons"]

        # Simulate detected subtopics based on available features
        detected = [expected[0], expected[1]]
        if obs.get("has_curriculum_table"):
            detected.append(expected[2] if len(expected) > 2 else expected[0])
        if obs.get("has_interactive_widget"):
            detected.append(expected[3] if len(expected) > 3 else expected[1])

        missing = [t for t in expected if t not in detected]
        cov_score = round((len(detected) / len(expected)) * 100.0, 1)

        return KeywordTopicCoverage(
            target_keyword=keyword,
            keyword_density_percentage=1.8,
            keyword_prominence_score=85.0,
            subtopics_detected=detected,
            subtopics_missing=missing,
            topic_coverage_score=cov_score,
        )

    def _analyze_internal_structure(self, obs: Dict[str, Any]) -> InternalContentStructure:
        has_table = obs.get("has_curriculum_table", False) or obs.get("has_comparison_table", False)
        return InternalContentStructure(
            has_comparison_table=has_table,
            has_curriculum_or_syllabus=has_table,
            has_table_of_contents=True,
            bullet_list_count=obs.get("bullet_list_count", 8),
            scannability_rating="High" if has_table else "Medium",
        )

    def _analyze_user_experience(self, obs: Dict[str, Any]) -> UserExperienceObservations:
        has_widget = obs.get("has_interactive_widget", False)
        has_video = obs.get("has_video_preview", False)

        if has_widget and has_video:
            dwell = "High"
            ux_score = 92.0
        elif has_widget or has_video:
            dwell = "Moderate"
            ux_score = 78.0
        else:
            dwell = "Low"
            ux_score = 55.0

        return UserExperienceObservations(
            has_interactive_widget=has_widget,
            interactive_widget_type="In-Browser Interactive Sandbox / Calculator" if has_widget else None,
            has_video_preview=has_video,
            estimated_dwell_impact=dwell,
            ux_engagement_score=ux_score,
        )

    def _analyze_technical_seo(self, obs: Dict[str, Any], intent: str) -> TechnicalSEOObservations:
        present = obs.get("schema_types", ["Article"])
        missing = []
        if intent == "commercial" and "Course" not in present:
            missing.append("Course")
        if "EducationalOccupationalCredential" not in present and intent in ["commercial", "education"]:
            missing.append("EducationalOccupationalCredential")
        if "FAQPage" not in present:
            missing.append("FAQPage")

        readiness = "Ready" if len(present) >= 3 else "Partial" if len(present) >= 1 else "Missing"

        return TechnicalSEOObservations(
            canonical_specified=True,
            schema_types_present=present,
            missing_high_value_schemas=missing,
            rich_snippet_readiness=readiness,
        )

    # =========================================================================
    # Problem, Opportunity & Recommendation Generators
    # =========================================================================

    def _identify_problems(self, obs: CurrentObservations, domain: str) -> List[ProblemItem]:
        problems: List[ProblemItem] = []

        # 1. Video Deficiency
        if not obs.user_experience.has_video_preview:
            problems.append(
                ProblemItem(
                    id="prob_missing_video",
                    severity="high",
                    category="ux",
                    problem="Lack of Video Previews or Visual Walkthroughs",
                    impact="Search results for this intent cluster reward video snippets. Missing video reduces dwell time and disqualifies page from Google Video carousel results.",
                )
            )

        # 2. Schema Gap
        if obs.technical_seo.missing_high_value_schemas:
            missing_str = ", ".join(obs.technical_seo.missing_high_value_schemas)
            problems.append(
                ProblemItem(
                    id="prob_missing_schema",
                    severity="high",
                    category="technical",
                    problem=f"Missing High-Value Structured Schemas: {missing_str}",
                    impact=f"Page is missing specialized schemas ({missing_str}) that enable rich result cards, student rating badges, and credential carousels.",
                )
            )

        # 3. Interactive UX Widget
        if not obs.user_experience.has_interactive_widget:
            problems.append(
                ProblemItem(
                    id="prob_no_interactive_tool",
                    severity="medium",
                    category="ux",
                    problem="No Tactile / Interactive Utility Tools",
                    impact="Passive text copy leads to higher bounce rates compared to competitors providing hands-on calculators, sandboxes, or interactive filters.",
                )
            )

        # 4. Meta Description or Title
        if not obs.title.is_length_optimal:
            problems.append(
                ProblemItem(
                    id="prob_title_length",
                    severity="low",
                    category="metadata",
                    problem=f"Page Title Length Suboptimal ({obs.title.char_length} characters)",
                    impact="Title may be truncated in search results if >60 characters, or fail to maximize keyword prominence if <45 characters.",
                )
            )

        # 5. Missing Subtopics
        if obs.keyword_coverage.subtopics_missing:
            problems.append(
                ProblemItem(
                    id="prob_missing_subtopics",
                    severity="medium",
                    category="content",
                    problem=f"Incomplete Subtopic Coverage: Missing {', '.join(obs.keyword_coverage.subtopics_missing)}",
                    impact="Search engines evaluating topical breadth will penalize pages that skip fundamental subtopics expected by query intent.",
                )
            )

        return problems

    def _identify_opportunities(self, obs: CurrentObservations, domain: str) -> List[OpportunityItem]:
        opps: List[OpportunityItem] = []

        opps.append(
            OpportunityItem(
                id="opp_video_curriculum",
                impact_potential="high",
                category="ux",
                opportunity="Embed 2-Minute Video Project Previews with VideoObject Schema",
                rationale="Beginner learners prefer watching an instructor demonstrate code before committing. Adding short video previews captures visual SERP real estate.",
            )
        )

        opps.append(
            OpportunityItem(
                id="opp_accreditation_schema",
                impact_potential="high",
                category="technical",
                opportunity="Implement Course and Credential Schema Markup",
                rationale="Signals formal course curriculum structure to Googlebot, enabling the coveted rich course carousel at the top of the SERP.",
            )
        )

        opps.append(
            OpportunityItem(
                id="opp_interactive_matrix",
                impact_potential="medium",
                category="content",
                opportunity="Deploy Filterable Interactive Comparison Table",
                rationale="Allows users to filter by cost (free vs paid), difficulty, and project count, driving up on-page session duration.",
            )
        )

        opps.append(
            OpportunityItem(
                id="opp_faq_schema",
                impact_potential="medium",
                category="technical",
                opportunity="Expand Targeted FAQ Accordion with FAQPage Schema",
                rationale="Directly answers long-tail conversational search queries and expands page pixel footprint in mobile search results.",
            )
        )

        return opps

    def _generate_recommended_actions(
        self, problems: List[ProblemItem], opportunities: List[OpportunityItem], intent: str
    ) -> List[RecommendedActionItem]:
        actions: List[RecommendedActionItem] = [
            RecommendedActionItem(
                id="act_01",
                priority=1,
                category="technical",
                action_title="Deploy Course & EducationalCredential Structured Schema",
                implementation_guide="Add JSON-LD script containing @type: 'Course' and 'EducationalOccupationalCredential' detailing course provider, prerequisites, and certificate status.",
                expected_benefit="Eligible for Google Course Rich Snippet carousel; anticipated +15-25% CTR boost.",
            ),
            RecommendedActionItem(
                id="act_02",
                priority=2,
                category="ux",
                action_title="Produce & Embed Video Project Walkthroughs",
                implementation_guide="Record 90-second video overviews of student capstone projects. Host on YouTube/Wistia and embed with structured VideoObject schema.",
                expected_benefit="Addresses primary user engagement gap; drives higher dwell time and captures Video SERP tab.",
            ),
            RecommendedActionItem(
                id="act_03",
                priority=3,
                category="content",
                action_title="Build Filterable Curriculum & Price Comparison Table",
                implementation_guide="Insert an HTML comparison matrix above the fold featuring instant filtering by price, estimated hours, and certificate availability.",
                expected_benefit="Satisfies commercial comparison intent immediately; lowers initial bounce rate.",
            ),
            RecommendedActionItem(
                id="act_04",
                priority=4,
                category="metadata",
                action_title="Optimize Title Tag with Year & High-Intent Click Triggers",
                implementation_guide="Refactor title to: '[Primary Keyword] (2026 Interactive Guide & Comparison)'. Keep between 52-58 characters.",
                expected_benefit="Maximizes desktop and mobile snippet readability without truncation.",
            ),
        ]
        return actions

    def _generate_llm_summary(
        self,
        query: str,
        domain: str,
        intent: str,
        intent_score: float,
        current_obs: CurrentObservations,
        problems: List[ProblemItem],
        opportunities: List[OpportunityItem],
        recommendations: List[RecommendedActionItem],
    ) -> str:
        """Produces a dense, structured markdown summary designed for LLM prompt consumption."""
        lines = [
            f"# BASELINE SEO ANALYSIS REPORT (NO HINDSIGHT MEMORY)",
            f"- Target Domain: {domain}",
            f"- Target Query: \"{query}\"",
            f"- Intent Classification: {intent.upper()} (Alignment Score: {intent_score}/100)",
            f"- Word Count: {current_obs.content_completeness.word_count} words (Benchmark: {current_obs.content_completeness.intent_benchmark_word_count})",
            f"- Title Status: {current_obs.title.title_status} ('{current_obs.title.title_text}', {current_obs.title.char_length} chars)",
            f"- Interactive Widget Present: {current_obs.user_experience.has_interactive_widget}",
            f"- Video Preview Present: {current_obs.user_experience.has_video_preview}",
            f"- Schema Types: {', '.join(current_obs.technical_seo.schema_types_present)}",
            "",
            "## 1. CURRENT OBSERVATIONS",
            f"- Headings: H1: '{current_obs.headings.h1_text}' | H2 Count: {current_obs.headings.h2_count} | H3 Count: {current_obs.headings.h3_count}",
            f"- Content Completeness: {current_obs.content_completeness.completeness_percentage}% of target benchmark",
            f"- Subtopics Covered: {', '.join(current_obs.keyword_coverage.subtopics_detected)}",
            f"- Subtopics Missing: {', '.join(current_obs.keyword_coverage.subtopics_missing)}",
            f"- Scannability Rating: {current_obs.internal_structure.scannability_rating}",
            "",
            "## 2. PROBLEMS IDENTIFIED",
        ]
        for p in problems:
            lines.append(f"- [{p.severity.upper()}] {p.problem}: {p.impact}")

        lines.append("")
        lines.append("## 3. OPPORTUNITIES")
        for o in opportunities:
            lines.append(f"- [{o.impact_potential.upper()} IMPACT] {o.opportunity}: {o.rationale}")

        lines.append("")
        lines.append("## 4. RECOMMENDED ACTIONS")
        for a in recommendations:
            lines.append(f"{a.priority}. [{a.category.upper()}] {a.action_title} -> Benefit: {a.expected_benefit}")

        lines.append("")
        lines.append("> NOTE: This is static heuristic advice. It lacks institutional memory of past ranking experiments or competitor counter-moves.")

        return "\n".join(lines)


seo_analyzer = SEOAnalyzer()
