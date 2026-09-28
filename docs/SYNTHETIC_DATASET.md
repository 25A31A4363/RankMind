# RankMind Synthetic SEO Dataset & Developer Inspection
## Empirical Historical Demonstration Dataset (v2.0)

> [!IMPORTANT]
> **SYNTHETIC DATASET DISCLAIMER**  
> This dataset is synthetic demonstration data generated specifically for development, testing, and demonstrating historical SEO attribution and Hindsight Memory agents. It does **NOT** claim to represent actual Google search ranking facts or proprietary search engine algorithms.

---

### 1. Dataset Architecture & Scope

The synthetic dataset models **realistic historical SEO causality** rather than random placeholder text. It spans **3 distinct search query ecosystems**, **17 competing websites**, **39 ranking milestone records**, **6 optimization actions**, **6 causal attribution outcomes**, **2 competitor counter-moves**, and **2 user interactions**.

| Dimension | Count | Description |
|---|---|---|
| **Search Queries** | **3** | Distinct intent profiles (Commercial Guide, Technical Benchmark, Software Tooling) |
| **Competing Websites** | **17** | 5 to 7 competing domains per query ecosystem |
| **Ranking Snapshots** | **39** | Multi-cycle historical trajectories spanning 60 to 90 days |
| **SEO Optimizations** | **6** | Documented team interventions with rationale and expected hypotheses |
| **Competitor Shifts** | **2** | Structured competitor changes (content, features, schemas) |
| **Causal Outcomes** | **6** | Pre/post ranking deltas ($\Delta R$) with confidence scores & confounders |
| **Citations** | **2** | Authoritative benchmark sources and official documentation |
| **User Interactions** | **2** | Diagnostic questions asked, recommendations given, and user feedback |

---

### 2. The 3 Historical Scenarios

#### Scenario 1: `"best python courses for beginners"`
* **Search Intent**: Commercial Guide / Education
* **Timeline**: 90 days (Day -90, Day -60, Day -30, Today)
* **Competing Domains (7)**:
  1. `learnpythonhub.io` (**Target Domain**):
     * **Day -90**: Rank #8 (Baseline listicle, 2,400 words, no code runner, no video).
     * **Day -75 (Action 1)**: Team added 1,600 words of passive background text.
     * **Day -60**: Rank #8 (0 delta). **Outcome**: Fluff content has zero causal ranking impact ($\Delta 0$, confidence 0.92).
     * **Day -45 (Action 2)**: Embedded in-browser Python runner widget & interactive curriculum table.
     * **Day -30**: Rank #3 (**+5 position surge!**). **Outcome**: Interactive tools match beginner intent ($\Delta +5$, confidence 0.95).
     * **Day -14 to -10**: Competitor counter-moves (`coursera.org` added credential schemas, `freecodecamp.org` added video previews).
     * **Day 0 (Current)**: Slipped slightly to Rank #4 (-1 position) due to competitor video/credential additions.
  2. `coursera.org`: Stable #1 leader. Deployed `EducationalOccupationalCredential` schema.
  3. `codecademy.com`: Stable #2 leader due to high in-browser dwell time.
  4. `freecodecamp.org`: Shifted #3 $\to$ #4 $\to$ #3 after refreshing video timestamps.
  5. `udemy.com`: Steady #4 $\to$ #5.
  6. `realpython.com`: Steady #5 $\to$ #6.
  7. `edx.org`: Steady #6 $\to$ #7.

#### Scenario 2: `"fastapi vs express performance"`
* **Search Intent**: Informational / Technical Comparison
* **Timeline**: 60 days (Day -60, Day -30, Today)
* **Competing Domains (5)**:
  1. `benchmarks-dev.io` (**Target Domain**):
     * **Day -60**: Rank #6 (Outdated benchmarks, no reproducible code).
     * **Day -45 (Action 1)**: Added open-source reproducible Docker repo + interactive latency chart under 10k req/s.
     * **Day -30**: Rank #2 (**+4 positions!**). **Outcome**: Technical reproducibility builds high trust ($\Delta +4$, confidence 0.96).
     * **Day -15 (Action 2)**: Added Python 3.13 free-threading vs Node 22 benchmarks + `Dataset` Schema.
     * **Day 0 (Current)**: Rank #1 (**Captured Google Featured Snippet!**).
  2. `blog.logrocket.com`: Prior #1 leader displaced to #2.
  3. `k6.io`: Steady #2 $\to$ #3.
  4. `medium.com`: Shifted #3 $\to$ #4.
  5. `dev.to`: Shifted #4 $\to$ #5.

#### Scenario 3: `"ai code generation tools"`
* **Search Intent**: Commercial Software Evaluation
* **Timeline**: 60 days (Day -60, Day -30, Today)
* **Competing Domains (5)**:
  1. `devtools-radar.com` (**Target Domain**):
     * **Day -60**: Rank #9 (Generic affiliate directory list).
     * **Day -40 (Action 1)**: Conducted empirical blind test suite across 12 tools on 50 LeetCode & refactoring tasks with downloadable CSV.
     * **Day -30**: Rank #4 (**+5 positions!**). **Outcome**: Empirical test results provide high E-E-A-T ($\Delta +5$, confidence 0.94).
     * **Day -18 (Action 2)**: Added interactive seat pricing calculator and enterprise zero-retention privacy policy matrix.
     * **Day 0 (Current)**: Rank #2 (**Displaced GitHub Blog and TechRadar!**).
  2. `zapier.com`: Dominant #1 brand authority.
  3. `github.blog`: Displaced #2 $\to$ #3.
  4. `techradar.com`: Shifted #3 $\to$ #4.
  5. `geeksforgeeks.org`: Shifted #4 $\to$ #5.

---

### 3. How to Seed the Dataset

#### Option A: Command Line
```bash
cd backend
python -m app.db.seed_synthetic_data
```

#### Option B: REST API
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/debug/seed?reset=true"
```

---

### 4. Developer Inspection & Debug Views

#### A. Interactive HTML Debug Console
Open your browser to:
`http://127.0.0.1:8000/debug`

Features:
* **Query Scenario Switcher**: Switch between Python Courses, FastAPI vs Express, and AI Code Generation Tools.
* **Unified Chronological Timeline**: Visual cards displaying SERP snapshots, optimization milestones, competitor shifts, and causal outcomes in exact chronological sequence.
* **Competitor vs Target Leaderboard**: Ranks, previous ranks, and deltas for every snapshot.
* **Causal Attribution Breakdown**: Displays confidence scores, attributed actions, and confounding factors.
* **Raw JSON Inspector**: Toggleable formatted JSON viewer for immediate API validation.
* **One-Click Reseed**: Instant reset button to refresh the database.

#### B. Debug REST APIs
* `GET /api/v1/debug/summary`: Returns counts across all 8 entities and tracked query metadata.
* `GET /api/v1/debug/timeline?query_id={id}`: Chronological event stream for any scenario.
