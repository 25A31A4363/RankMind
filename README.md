# RankMind 🧠
### Empirical AI-Powered SEO & Search Intelligence Agent with Persistent Hindsight Memory

RankMind is an advanced search intelligence agent designed for technical SEO leads and organic growth strategists. Unlike generic SEO chatbots and static audit checklists that give the same cookie-cutter advice every month, **RankMind operates on persistent institutional memory ("Hindsight Memory")**.

RankMind tracks and learns from:
1. **Historical Ranking Trajectories** across multiple evaluation cycles.
2. **Optimization Action Ledgers** (what exact changes the team deployed).
3. **Competitor Counter-Moves** (what competitors updated between snapshots).
4. **Causal Attribution & Lessons** (which specific actions moved the needle vs. which ones produced zero measurable effect).

---

## 🏛️ The 7 Foundational Pillars

### 1. User Persona
- **Alex Vance** — Head of SEO & Organic Growth at a mid-market SaaS or digital agency managing high-value conversion queries.
- **Problem**: Loses institutional memory of past experiments; standard SEO tools don't track *causality* or competitor counter-moves.

### 2. Primary Workflow: The Empirical SERP Audit Loop
1. Input target keyword and target domain.
2. Ingest live SERP ranking positions and deep feature signals.
3. Query Hindsight Memory Store for historical snapshots, logged actions, and competitor diffs.
4. Triangulate current observations against historical memory.
5. Deliver a 4-tier intelligence report distinguishing **Current Observations**, **Historical Memory**, **Recommendations**, and **Observed Outcomes**.
6. Commit planned optimizations to the Action Ledger to track in the next evaluation cycle.

### 3. MVP Scope
- **Core Query**: Flagship seed scenario `"best python courses for beginners"` tracking `learnpythonhub.io` against top competitors (`coursera.org`, `codecademy.com`, `freecodecamp.org`, `udemy.com`).
- **Persistent Hindsight Store**: Records snapshots across 4 cycles, actions taken, competitor diffs, and causal lessons.
- **Evidence-Tiered Recommendations**: Every recommendation is explicitly tagged as `[Historically Proven]`, `[Competitor Trend]`, or `[Theoretical Hypothesis]`.

### 4. Core Screens
1. **Query Intelligence & Status Header**: Tracks Current Rank (#4), Historical Peak (#3), 30d Velocity (-1), and Memory Nodes.
2. **Historical Hindsight Trajectory**: Interactive timeline visualizer showing multi-cycle rank shifts and milestone markers.
3. **Triangulated Recommendations Panel**: Tabbed/split intelligence interface distinguishing Current Observations, Historical Precedents, and Prescriptive Next Steps.
4. **Causal Attribution Memory Ledger**: "What Worked vs What Failed" ledger displaying empirical rank deltas, attribution verdicts, and agent-distilled lessons.
5. **Live SERP Leaderboard**: Top 10 matrix with feature comparison (Interactive widgets, video previews, curriculum matrices, schema types, word counts).
6. **Action Logger Modal**: Interface to register new optimization experiments.

### 5. Information The System Needs
- **SERP Rankings**: Position, URL, Title, Snippet.
- **Page Feature Vectors**: Interactive widgets, video previews, structured syllabus tables, Schema.org types, word counts, readability.
- **Diff Data**: Feature shifts and rank deltas between consecutive snapshots.
- **Action Logs**: Category, title, description, hypothesis, target URL, and pre-action rank baseline.
- **Attribution Records**: Rank delta ($\Delta R$), latency window, confounding factor analysis, confidence score.

### 6. What Hindsight Memory Remembers
- **`serp_snapshots`**: Time-series SERP records.
- **`competitor_diffs`**: What competitors changed between cycles.
- **`optimization_actions`**: Experiments logged by the team.
- **`memory_nodes`**: Empirical causal rules (e.g. *Interactive tools yielded +5 rank improvement; passive word count expansion produced 0 delta*).

### 7. The Learning Loop
$$\text{Action Logged } \to \text{ Latency Window } \to \text{ New SERP Snapshot } \to \text{ Diff Analysis } \to \text{ Attribution Evaluation } \to \text{ Memory Updated } \to \text{ Empirical Recommendations}$$

---

## 🚀 Quickstart Guide

### Backend (FastAPI + Python)
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
# Server runs on http://127.0.0.1:8000
# API docs available at http://127.0.0.1:8000/docs
```

### Frontend (React + Vite + TypeScript)
```bash
cd frontend
npm install
npm run dev
# Web console runs on http://localhost:3000
```
