# RankMind Baseline SEO Analyzer (Without Hindsight Memory)
## Version 1.0 — Static On-Page & Technical Heuristic Baseline

> [!IMPORTANT]
> **PURPOSE OF THE BASELINE ANALYZER**  
> This analyzer evaluates isolated on-page signals, search intent alignment, metadata, and content completeness **WITHOUT consulting Hindsight memory**.  
> It intentionally acts as a **standard static SEO tool** (similar to Ahrefs, Semrush, or standard LLM prompts) to establish a rigorous, objective benchmark that we will compare against the memory-powered version in the next phase.

---

### 1. Inputs Accepted

The analyzer accepts both tracked database entities and arbitrary ad-hoc pages:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | `string` | **Yes** | Target search query (e.g. `"best python courses for beginners"`) |
| `website_id` | `string` | Optional | ID of a tracked website from the database (e.g. `site_learnpythonhub`) |
| `url` | `string` | Optional | Target URL if analyzing an external or ad-hoc page |
| `custom_title` | `string` | Optional | Custom HTML title override |
| `custom_meta_description` | `string` | Optional | Custom meta description override |
| `custom_content` | `string` | Optional | Raw page body copy for content analysis |

---

### 2. The 10 Analytical Categories

The analyzer evaluates on-page and technical signals across 10 distinct categories:

1. **Search Intent Alignment**: Detects `commercial`, `informational`, `transactional`, or `navigational` intent and scores content alignment (0–100%).
2. **Title Analysis**: Character count (optimal 45–65), exact keyword matching, keyword placement (`front`, `middle`, `end`), and CTR power words / freshness years.
3. **Meta Description Analysis**: Length (optimal 115–165 chars), keyword presence, call-to-action (CTA) verbs, and truncation risk.
4. **Heading Structure**: H1 uniqueness, keyword in H1, H2/H3 section count, hierarchy validity, and scan-friendliness score.
5. **Content Completeness**: Word count vs intent-specific benchmark (e.g. 3,500 words for commercial guides), completeness percentage, estimated reading time, and reading ease level.
6. **Keyword / Topic Coverage**: Density, prominence score, subtopics detected vs subtopics missing.
7. **Internal Content Structure**: Tabular comparison matrices, curriculum tables, table of contents, bullet list density, and scannability rating.
8. **User Experience Observations**: In-browser interactive tools (code runners, calculators), video preview modules, and estimated dwell-time impact.
9. **Technical SEO Observations**: Canonical status, Schema.org types present (`Course`, `Article`, `FAQPage`, `Credential`), and missing rich snippet opportunities.
10. **Weaknesses & Improvements**: Formatted into distinct problem and opportunity cards.

---

### 3. The 4 Mandatory Structured Output Sections

The output is strictly structured into 4 sections, guaranteed to be machine-readable:

```json
{
  "analysis_id": "base_ana_8d249f01bc",
  "timestamp": "2026-09-27T18:00:00Z",
  "query": "best python courses for beginners",
  "target_domain": "learnpythonhub.io",
  "hindsight_memory_applied": false,
  "data_source_type": "synthetic_database",
  
  "current_observations": { ... },
  "problems": [ ... ],
  "opportunities": [ ... ],
  "recommended_actions": [ ... ],
  "llm_prompt_summary": "..."
}
```

#### Section 1: CURRENT OBSERVATIONS
Factual inventory of current signals:
* Intent: Commercial (Score: 85/100)
* Word Count: 3,650 words (100% of benchmark)
* Interactive Tool: Active (In-browser Python code sandbox)
* Video Preview: Missing
* Schemas: `Article`, `ItemList` (Missing `Course` and `Credential` schemas)

#### Section 2: PROBLEMS
Concrete deficiencies with severity levels (`high`, `medium`, `low`):
* `[HIGH]` **Missing Video Previews**: Search results for this intent cluster reward video snippets. Missing video reduces dwell time and disqualifies page from Video carousel results.
* `[HIGH]` **Missing Course & Credential Schema**: Missing specialized schemas that enable rich course cards.

#### Section 3: OPPORTUNITIES
Growth potential identified by static intent heuristics:
* `[HIGH IMPACT]` **Embed 2-Minute Video Project Previews with VideoObject Schema**.
* `[HIGH IMPACT]` **Implement Course & EducationalCredential Schema Markup**.
* `[MEDIUM IMPACT]` **Expand FAQ Accordion with FAQPage Schema**.

#### Section 4: RECOMMENDED ACTIONS
Prioritized checklist with implementation guides and expected benefits:
1. **Priority 1**: Deploy Course & EducationalCredential Structured Schema.
2. **Priority 2**: Produce & Embed Video Project Walkthroughs.
3. **Priority 3**: Build Filterable Curriculum & Price Comparison Table.
4. **Priority 4**: Optimize Title Tag with Year & High-Intent Click Triggers.

---

### 4. Machine-Readable LLM Summary

The output generates a condensed markdown representation designed for ingestion by an LLM in pair-programming or agent workflows:

```markdown
# BASELINE SEO ANALYSIS REPORT (NO HINDSIGHT MEMORY)
- Target Domain: learnpythonhub.io
- Target Query: "best python courses for beginners"
- Intent Classification: COMMERCIAL (Alignment Score: 85.0/100)
- Word Count: 3650 words (Benchmark: 3500)
- Title Status: optimal ('Best Python Courses for Beginners in 2026 (Curated Interactive Guide)', 71 chars)
- Interactive Widget Present: True
- Video Preview Present: False
- Schema Types: Article, ItemList

## 1. CURRENT OBSERVATIONS
- Headings: H1: 'Best Python Courses for Beginners in 2026' | H2 Count: 6 | H3 Count: 12
- Content Completeness: 100.0% of target benchmark
- Subtopics Covered: Curriculum & Syllabus, Pricing & Free vs Paid, Certification Value
- Subtopics Missing: Hands-on Projects, Beginner Prerequisites
- Scannability Rating: High

## 2. PROBLEMS IDENTIFIED
- [HIGH] Lack of Video Previews or Visual Walkthroughs: Missing video reduces dwell time.
- [HIGH] Missing High-Value Structured Schemas: Course, EducationalOccupationalCredential.

## 3. OPPORTUNITIES
- [HIGH IMPACT] Embed 2-Minute Video Project Previews with VideoObject Schema.
- [HIGH IMPACT] Implement Course and Credential Schema Markup.

## 4. RECOMMENDED ACTIONS
1. [TECHNICAL] Deploy Course & EducationalCredential Structured Schema.
2. [UX] Produce & Embed Video Project Walkthroughs.
3. [CONTENT] Build Filterable Curriculum & Price Comparison Table.
4. [METADATA] Optimize Title Tag with Year & High-Intent Click Triggers.

> NOTE: This is static heuristic advice. It lacks institutional memory of past ranking experiments or competitor counter-moves.
```

---

### 5. Testing the Analyzer

#### Web Testing Interface
Navigate to `http://127.0.0.1:8000/analyzer` in your browser:
* **Preset Buttons**: Click to instantly test Python Courses (`learnpythonhub.io`), Competitor Leader (`coursera.org`), or FastAPI vs Express (`benchmarks-dev.io`).
* **Visual Cards**: 4 responsive panels displaying Current Observations, Problems, Opportunities, and Recommended Actions.
* **One-Click Copy**: "Copy for LLM Prompt" copies the condensed prompt block to your clipboard.
* **Raw JSON Toggle**: Inspect the complete machine-readable payload.

#### REST API Endpoint
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyzer/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "best python courses for beginners",
       "url": "https://learnpythonhub.io/best-python-courses-beginners"
     }'
```
