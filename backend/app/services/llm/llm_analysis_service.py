import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.services.seo_analyzer import seo_analyzer
from app.models.analyzer_schemas import BaselineAnalysisRequest
from app.models.llm_schemas import (
    LLMAnalysisRequest,
    LLMAnalysisResponse,
    ObservedDataSummary,
    AIInterpretation,
    WeaknessItem,
    LLMRecommendationItem,
)
from app.services.llm.providers import get_llm_provider, BaseLLMProvider
from app.repositories.seo_repository import SEORepository
from app.db.database import DB_PATH


SYSTEM_PROMPT = """You are RankMind's Advanced Search Intelligence & SEO Reasoning Agent.

CRITICAL INSTRUCTIONS & TRUTH DISCIPLINE:
1. STRICT TRUTH DISCIPLINE: You do NOT have access to historical ranking data or past optimization experiments for this analysis.
2. ABSOLUTELY DO NOT INVENT OR HALLUCINATE HISTORICAL RANK RESULTS (e.g. NEVER say "Last month your rank dropped by 3 positions" or "In past cycles this action improved rank by 5").
3. You must rigorously distinguish between:
   - OBSERVED DATA: Factual on-page signals, technical attributes, and competitor features provided in the input.
   - AI INTERPRETATION: Your heuristic hypothesis based on search engine guidelines and user intent expectations.
   - RECOMMENDATIONS: Specific, forward-looking optimizations.
4. When evidence is insufficient to make firm claims (e.g. missing server response times, backlink profile, or dwell time analytics), you MUST explicitly ask clarifying QUESTIONS and list MISSING EVIDENCE instead of guessing.
5. Provide actionable, high-depth recommendations with clear heuristic reasoning and expected direction of improvement.

RESPONSE FORMAT:
You MUST respond with valid JSON matching this exact structure:
{
  "seo_diagnosis": "High-level diagnostic summary of current search performance readiness...",
  "intent_fit_assessment": "Assessment of how well the page satisfies user query intent...",
  "main_weaknesses": [
    {
      "weakness": "Title of weakness",
      "category": "technical | content | ux | metadata",
      "severity": "high | medium | low",
      "evidence": "Observed evidence supporting this finding"
    }
  ],
  "evidence_sufficiency_rating": "Sufficient | Moderate | Insufficient",
  "missing_evidence_or_questions": [
    "Question or missing data point needed for higher certainty..."
  ],
  "recommendations": [
    {
      "id": "rec_01",
      "priority": 1,
      "title": "Clear action title",
      "category": "technical | content | ux | metadata",
      "reasoning": "Heuristic rationale for why this recommendation matters",
      "expected_direction_of_improvement": "Expected direction of improvement (e.g. Higher CTR and Course Carousel qualification)",
      "implementation_steps": [
        "Step 1...",
        "Step 2..."
      ]
    }
  ]
}
"""


class LLMAnalysisService:
    """Orchestrates LLM-powered SEO analysis over structured SEO analyzer signals."""

    def __init__(self, db_path=DB_PATH):
        self.repo = SEORepository(db_path)

    async def run_analysis(self, req: LLMAnalysisRequest) -> LLMAnalysisResponse:
        # 1. Step 1: Run deterministic SEO Analyzer to get factual baseline observations
        base_req = BaselineAnalysisRequest(
            query=req.query,
            website_id=req.website_id,
            url=req.url,
            custom_title=req.custom_title,
            custom_content=req.custom_content,
        )
        base_res = seo_analyzer.analyze(base_req)
        obs = base_res.current_observations

        # 2. Step 2: Fetch Competitor Context if available (without historical ranking memory)
        competitor_context = self._fetch_competitor_context(req.query, base_res.target_domain)

        # 3. Step 3: Construct the Verified Observed Data Summary
        observed_data = ObservedDataSummary(
            target_query=base_res.query,
            target_domain=base_res.target_domain,
            target_url=base_res.target_url,
            search_intent_detected=obs.search_intent_detected,
            intent_match_score=obs.intent_match_score,
            word_count=obs.content_completeness.word_count,
            title_text=obs.title.title_text,
            meta_description=obs.meta_description.description_text,
            h1_text=obs.headings.h1_text,
            h2_count=obs.headings.h2_count,
            has_interactive_widget=obs.user_experience.has_interactive_widget,
            has_video_preview=obs.user_experience.has_video_preview,
            has_comparison_table=obs.internal_structure.has_comparison_table,
            schema_types_present=obs.technical_seo.schema_types_present,
            missing_schemas_detected=obs.technical_seo.missing_high_value_schemas,
            competitor_context_available=competitor_context,
        )

        # 4. Step 4: Construct the Prompt
        user_prompt = self._build_user_prompt(observed_data)

        # 5. Step 5: Resolve Provider & Execute with Retry Handling
        provider = get_llm_provider(provider_name=req.provider, api_key=req.api_key)
        
        try:
            raw_response = await provider.generate_json(prompt=user_prompt, system_prompt=SYSTEM_PROMPT)
        except Exception as e:
            # Fallback to local deterministic reasoning if external provider fails
            fallback_provider = get_llm_provider(provider_name="local")
            raw_response = await fallback_provider.generate_json(prompt=user_prompt, system_prompt=SYSTEM_PROMPT)

        # 6. Step 6: Parse into Structured Schema
        interpretation = self._parse_interpretation(raw_response)
        recommendations = self._parse_recommendations(raw_response)

        return LLMAnalysisResponse(
            analysis_id=f"llm_ana_{uuid.uuid4().hex[:10]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            provider_used=provider.name,
            query=base_res.query,
            target_domain=base_res.target_domain,
            hindsight_memory_applied=False,
            observed_data=observed_data,
            ai_interpretation=interpretation,
            recommendations=recommendations,
            raw_prompt_sent=user_prompt,
        )

    def _fetch_competitor_context(self, query: str, target_domain: str) -> Optional[List[Dict[str, Any]]]:
        """Fetches known competitor on-page signals for the query without historical ranking trajectory."""
        sites = self.repo.list_websites()
        competitors = [s for s in sites if s.domain.lower() != target_domain.lower()]
        if not competitors:
            return None

        comp_summaries = []
        for c in competitors[:3]:
            obs = c.seo_observations or {}
            comp_summaries.append({
                "domain": c.domain,
                "title": c.title,
                "word_count": obs.get("word_count", 0),
                "has_interactive_widget": obs.get("has_interactive_widget", False),
                "has_video_preview": obs.get("has_video_preview", False),
                "has_curriculum_table": obs.get("has_curriculum_table", False),
                "schema_types": obs.get("schema_types", []),
            })
        return comp_summaries if comp_summaries else None

    def _build_user_prompt(self, obs: ObservedDataSummary) -> str:
        prompt_parts = [
            f"Analyze the following verifiable SEO observations for target query '{obs.target_query}':",
            "",
            "=== TARGET WEBSITE CURRENT OBSERVATIONS ===",
            f"- Domain: {obs.target_domain}",
            f"- Target URL: {obs.target_url}",
            f"- Search Intent Detected: {obs.search_intent_detected.upper()} (Intent Match Score: {obs.intent_match_score}/100)",
            f"- Title Tag: \"{obs.title_text}\" ({len(obs.title_text)} characters)",
            f"- Meta Description: \"{obs.meta_description}\" ({len(obs.meta_description)} characters)",
            f"- Primary H1: \"{obs.h1_text}\" | Total H2 Headings: {obs.h2_count}",
            f"- Content Length: {obs.word_count} words",
            f"- Interactive Tool Present: {obs.has_interactive_widget}",
            f"- Video Preview Present: {obs.has_video_preview}",
            f"- Tabular Comparison / Syllabus Matrix: {obs.has_comparison_table}",
            f"- Structured Schema Types: {', '.join(obs.schema_types_present)}",
            f"- Detected Schema Deficiencies: {', '.join(obs.missing_schemas_detected) if obs.missing_schemas_detected else 'None'}",
        ]

        if obs.competitor_context_available:
            prompt_parts.append("")
            prompt_parts.append("=== COMPETITOR CURRENT OBSERVATIONS ===")
            for c in obs.competitor_context_available:
                prompt_parts.append(
                    f"- Competitor {c['domain']}: {c['word_count']}w, Interactive Widget: {c['has_interactive_widget']}, "
                    f"Video Preview: {c['has_video_preview']}, Schemas: [{', '.join(c['schema_types'])}]"
                )

        prompt_parts.append("")
        prompt_parts.append("Generate a comprehensive diagnosis, main weaknesses, evidence sufficiency rating, questions on missing data, and prioritized recommendations following the required JSON schema.")
        return "\n".join(prompt_parts)

    def _parse_interpretation(self, raw: Dict[str, Any]) -> AIInterpretation:
        weaknesses = []
        for w in raw.get("main_weaknesses", []):
            weaknesses.append(
                WeaknessItem(
                    weakness=w.get("weakness", "Identified Weakness"),
                    category=w.get("category", "content"),
                    severity=w.get("severity", "medium"),
                    evidence=w.get("evidence", "Observed signal"),
                )
            )

        return AIInterpretation(
            seo_diagnosis=raw.get("seo_diagnosis", "Diagnostic analysis completed."),
            intent_fit_assessment=raw.get("intent_fit_assessment", "Intent evaluated against current signals."),
            main_weaknesses=weaknesses,
            evidence_sufficiency_rating=raw.get("evidence_sufficiency_rating", "Moderate"),
            missing_evidence_or_questions=raw.get("missing_evidence_or_questions", []),
        )

    def _parse_recommendations(self, raw: Dict[str, Any]) -> List[LLMRecommendationItem]:
        recs = []
        for idx, r in enumerate(raw.get("recommendations", []), start=1):
            recs.append(
                LLMRecommendationItem(
                    id=r.get("id", f"rec_{idx:02d}"),
                    priority=r.get("priority", idx),
                    title=r.get("title", f"Recommendation {idx}"),
                    category=r.get("category", "technical"),
                    reasoning=r.get("reasoning", "Standard SEO best practice recommendation."),
                    expected_direction_of_improvement=r.get(
                        "expected_direction_of_improvement", "Expected to improve click-through and search engagement."
                    ),
                    implementation_steps=r.get("implementation_steps", ["Audit and implement change."]),
                )
            )
        return recs


llm_analysis_service = LLMAnalysisService()
