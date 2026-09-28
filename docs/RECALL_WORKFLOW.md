# RankMind RECALL Workflow: Institutional SEO Memory Retrieval & Evidence-Driven Reasoning

The **RECALL workflow** is the institutional intelligence engine of RankMind. When a user queries a keyword or requests SEO recommendations, RankMind does not simply run an isolated on-page heuristic check. Instead, it queries its **Hindsight Persistent Memory Layer**, scores candidate memories across **8 distinct dimensions**, bounds retrieval within token budgets, assembles a **4-part reasoning context**, and directs the LLM to explain every recommendation with empirical historical evidence and strict observational discipline.

---

## 1. High-Level Architecture

```
User Search / Optimization Request
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  SEO Analyzer (Deterministic Current On-Page Baseline) │
└────────────────────────┬───────────────────────────────┘
                         │ Current Signals & Detected Weaknesses
                         ▼
┌────────────────────────────────────────────────────────┐
│    Hindsight Relevance-Ranking Layer (8 Dimensions)    │
│  - Evaluates all candidate memories in bank            │
│  - Scores across 8 distinct dimensions                 │
│  - Bounded retrieval (token budget & category quotas)  │
└────────────────────────┬───────────────────────────────┘
                         │ Top Scored Empirical Memories
                         ▼
┌────────────────────────────────────────────────────────┐
│           4-Part Reasoning Context Assembly            │
│  1. CURRENT INFORMATION                                │
│  2. RELEVANT HISTORICAL MEMORY                         │
│  3. CURRENT COMPETITOR INFORMATION                     │
│  4. USER REQUEST                                       │
└────────────────────────┬───────────────────────────────┘
                         │ Assembled Multi-Layer Prompt
                         ▼
┌────────────────────────────────────────────────────────┐
│  LLM Search Intelligence Agent                         │
│  - Explains recommendations citing past evidence       │
│  - Suppresses empirically disproven tactics            │
│  - Enforces observational causal discipline            │
└────────────────────────┬───────────────────────────────┘
                         │ Structured JSON
                         ▼
┌────────────────────────────────────────────────────────┐
│  Transparent Output Layer                              │
│  "Why am I seeing this recommendation?"                │
│  - Current Observation                                 │
│  - Recalled Memory                                     │
│  - Connection Between Them                             │
│  - Recommendation                                      │
│  - Observational Caveat                                │
└────────────────────────────────────────────────────────┘
```

---

## 2. The 8-Dimension Relevance Ranking Layer

RankMind rejects naive "retrieve all memories" approaches that pollute LLM context windows with low-signal data. The `RelevanceRankingLayer` (`backend/app/services/hindsight/relevance_ranker.py`) scores candidate memories across 8 distinct dimensions:

| Dimension | Max Weight | Evaluation Logic |
|---|---|---|
| **1. Same Website** | `+0.35` | Target domain directly matches the memory's `target_domain`. |
| **2. Same Keyword** | `+0.40` | Exact query match (`+0.40`) or phrase containment (`+0.30`). |
| **3. Related Keywords** | `+0.25` | Semantic token overlap across query terms, content, and metadata tags (`+0.08` per token hit, capped at `+0.25`). |
| **4. Similar Optimization** | `+0.20` | Memory matches high-value optimization types (`structured_schema`, `interactive_widget`, `video_preview`, `content_structure`, etc.) or directly addresses one of the target site's current deficiencies (`+0.18`). |
| **5. Previous Ranking Behavior** | `+0.15` | Baseline ranking proximity (e.g. target site is at `#8` and memory records an optimization starting from `#8` or within `±2` positions), or historical SERP transition milestones. |
| **6. Competitor Behavior** | `+0.25` | Rival counter-actions, competitor feature launches, or schema deployments (`competitor_history` category). |
| **7. Previous Outcomes** | `+0.30` | Verified empirical outcome attributions (`outcome_history` category or `causal` tags) recording positive or neutral ranking deltas. |
| **8. Previous User Interactions** | `+0.15` | Historical feedback, accepted/rejected recommendations, or past user questions. |

### Bounded Retrieval & Category-Stratified Diversity
- Candidate memories scoring below the quality threshold (`score < 0.20`) are pruned.
- Candidate memories are ranked by `(relevance_score, timestamp DESC)`.
- **Stratified Diversity Selection**: RankMind guarantees balanced context by taking up to 2 items from priority categories (`OUTCOME_HISTORY`, `COMPETITOR_HISTORY`, `OPTIMIZATION_HISTORY`, `RANKING_HISTORY`) before filling the remaining quota up to `max_memories` (default: 6) and token budgets (default: 4096 tokens).

---

## 3. The 4-Part Reasoning Context Assembly

Before prompting the LLM, RankMind strictly synthesizes 4 explicit layers into the reasoning context (`reasoning_context_assembled`):

```json
{
  "reasoning_context_assembled": {
    "current_information": {
      "target_query": "best python courses for beginners",
      "target_domain": "learnpythonhub.io",
      "current_position": 8,
      "word_count": 2450,
      "interactive_widget": true,
      "video_preview": false,
      "schema_types_present": ["Article", "ItemList"],
      "missing_schemas_detected": ["Course", "VideoObject"]
    },
    "recalled_historical_memory": [
      {
        "category": "outcome_history",
        "content": "Observed SEO Outcome: After this change ('Optimize content structure with interactive sandbox exercises'), the observed ranking moved from #8 to #5 over a 21-day latency window.",
        "relevance_score": 0.95,
        "why_relevant": "Same website: Direct history for 'learnpythonhub.io'; Same keyword; Previous outcomes: Empirical causal outcome record"
      }
    ],
    "current_competitor_information": [
      {
        "domain": "coursera.org",
        "current_position": 1,
        "word_count": 4800,
        "has_video_preview": true,
        "schema_types": ["Course", "ItemList", "VideoObject"]
      }
    ],
    "user_request": "How can we improve ranking from #8 into the top 3?"
  }
}
```

---

## 4. Historical Evidence Citation & Observational Discipline

### Core Operational Mandates
1. **Explain Recommendations Using Historical Evidence**: Recommendations must cite past empirical outcomes rather than abstract SEO mantras.
2. **Observational Causal Discipline**: The system strictly forbids claiming absolute causality when the available data reflects correlation. Language strictly adheres to:
   > *"After this change, the observed ranking moved from #8 to #5. Consider a similar optimization, while clearly stating that the historical relationship is observational and not guaranteed."*
3. **Suppress Disproven Tactics**: If past experiments proved a tactic ineffective (e.g. Cycle 1: adding 1,600 words of passive text resulted in 0 ranking delta `#8 -> #8`), the tactic is explicitly blacklisted in `suppressed_tactics`.

---

## 5. "Why Am I Seeing This Recommendation?" Transparent Breakdown

Each recommendation generated by RankMind includes a transparent reasoning card exposed to the end-user:

```json
{
  "id": "rec_mem_01",
  "priority": 1,
  "title": "Optimize Content-Structure with Interactive Practice Code Modules",
  "category": "content",
  "reasoning": "Current observation: Website is ranking #8. Historical memory: A similar content-structure optimization was previously followed by an observed movement from #8 to #5. Recommendation: Consider a similar optimization, while clearly stating that the historical relationship is observational and not guaranteed.",
  "expected_direction_of_improvement": "Observed historical movement from #8 to #5 upon interactive structure deployment.",
  "why_am_i_seeing_this": {
    "current_observation": "Website is ranking #8.",
    "recalled_memory": "A similar content-structure optimization was previously followed by an observed movement from #8 to #5.",
    "connection_between_them": "Empirical evidence demonstrates that passive text depth alone is insufficient to penetrate top-5 SERPs, whereas interactive content-structure optimizations previously correlated with immediate ranking advancement from #8 to #5.",
    "recommendation": "Consider a similar optimization, while clearly stating that the historical relationship is observational and not guaranteed.",
    "observational_caveat": "Historical relationship is observational and not guaranteed; external SERP algorithm shifts remain confounding variables."
  }
}
```

---

## 6. Contrast Demonstration: WITHOUT MEMORY vs WITH MEMORY

| Attribute | WITHOUT MEMORY (Stateless Baseline) | WITH MEMORY (Hindsight-Augmented) |
|---|---|---|
| **Memory Applied** | `False` | `True` |
| **Historical Awareness** | Zero awareness of past experiments or competitor moves. | Recalls 6 verified historical events scored across 8 dimensions. |
| **Content Advice** | Observes competitors have 4,800 words and generically advises *"Add 1,500+ words of text depth"*. | **Suppresses text bloat**: cites Cycle 1 empirical outcome where adding 1,600 words produced **ZERO** ranking movement (`#8 -> #8`). |
| **Prescription Basis** | Generic heuristic checklists. | Empirical trajectory: prescribes interactive practice structure (`#8 -> #5`) and Course/Video schemas to counter Coursera and freeCodeCamp. |
| **Transparency** | None. | Dedicated **"Why am I seeing this recommendation?"** breakdown with observational caveats on every recommendation. |

---

## 7. Automated Test Verification

The RECALL workflow is validated by a dedicated test suite (`backend/tests/test_recall_workflow.py`):

1. `test_relevance_ranking_layer_eight_dimensions`: Validates scoring across same website, same keyword, related keywords, similar optimizations, ranking behavior, competitor behavior, and causal outcomes.
2. `test_bounded_retrieval_does_not_retrieve_all_memories`: Verifies that retrieval respects token budgets and `max_memories` limits.
3. `test_four_part_reasoning_context_assembly`: Validates that `CURRENT INFORMATION + RELEVANT HISTORICAL MEMORY + CURRENT COMPETITOR INFORMATION + USER REQUEST` are correctly assembled in `reasoning_context_assembled`.
4. `test_historical_evidence_and_why_am_i_seeing_this_section`: Validates the structure and observational caveats of the `"Why am I seeing this recommendation?"` section.
5. `test_contrast_without_memory_vs_with_memory`: Demonstrates that baseline stateless advice lacks memory and suppressed tactics, whereas Hindsight memory suppresses failed tactics and provides empirical evidence.

Run the test suite:
```bash
python -m unittest tests/test_recall_workflow.py
```
Total project test suite:
```bash
python -m unittest discover tests
# 38 tests passing across 6 test suites
```
