import json
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List, Optional

from app.db.database import get_connection, DB_PATH
from app.repositories.seo_repository import SEORepository
from app.db.seed_synthetic_data import populate_synthetic_seo_dataset, DATASET_METADATA

router = APIRouter(prefix="", tags=["Developer Inspection & Debug"])
repo = SEORepository(DB_PATH)


@router.get("/api/v1/debug/summary")
def get_debug_summary() -> Dict[str, Any]:
    """Returns dataset statistics, entity counts, and synthetic metadata."""
    with get_connection(DB_PATH) as conn:
        counts = {
            "search_queries": conn.execute("SELECT COUNT(*) as c FROM search_queries").fetchone()["c"],
            "websites": conn.execute("SELECT COUNT(*) as c FROM websites").fetchone()["c"],
            "ranking_history_entries": conn.execute("SELECT COUNT(*) as c FROM ranking_history").fetchone()["c"],
            "seo_optimizations": conn.execute("SELECT COUNT(*) as c FROM seo_optimizations").fetchone()["c"],
            "competitor_history_entries": conn.execute("SELECT COUNT(*) as c FROM competitor_history").fetchone()["c"],
            "outcomes": conn.execute("SELECT COUNT(*) as c FROM outcomes").fetchone()["c"],
            "citations": conn.execute("SELECT COUNT(*) as c FROM content_citations").fetchone()["c"],
            "user_interactions": conn.execute("SELECT COUNT(*) as c FROM user_interactions").fetchone()["c"],
        }
        queries = conn.execute("SELECT id, query, target_keyword, search_intent, location, date FROM search_queries ORDER BY date ASC").fetchall()

    return {
        "metadata": DATASET_METADATA,
        "counts": counts,
        "tracked_queries": queries,
    }


@router.get("/api/v1/debug/timeline")
def get_debug_timeline(query_id: Optional[str] = None, keyword: Optional[str] = None) -> Dict[str, Any]:
    """Assembles a unified chronological timeline of ranking shifts, optimizations, competitor changes, and outcomes."""
    with get_connection(DB_PATH) as conn:
        # Resolve query
        if not query_id:
            first_q = conn.execute("SELECT * FROM search_queries LIMIT 1").fetchone()
            if not first_q:
                return {"events": [], "query": None}
            target_q = first_q
        else:
            target_q = conn.execute("SELECT * FROM search_queries WHERE id = ?", (query_id,)).fetchone()
            if not target_q:
                raise HTTPException(status_code=404, detail="Query not found")

        q_keyword = keyword or target_q["target_keyword"]
        q_id = target_q["id"]

        events = []

        # 1. Ranking entries
        rank_rows = conn.execute(
            """
            SELECT rh.id, rh.date, rh.position, rh.previous_position, rh.change_in_position, w.domain, w.title
            FROM ranking_history rh
            JOIN websites w ON w.id = rh.website_id
            WHERE rh.search_query_id = ? OR rh.keyword = ?
            ORDER BY rh.date ASC
            """,
            (q_id, q_keyword),
        ).fetchall()

        # Group rankings by date
        date_groups = {}
        for r in rank_rows:
            d = r["date"][:10]
            if d not in date_groups:
                date_groups[d] = []
            date_groups[d].append(r)

        for d, ranks in date_groups.items():
            ranks_sorted = sorted(ranks, key=lambda x: x["position"])
            events.append({
                "date": d,
                "timestamp": ranks[0]["date"],
                "type": "RANKING_SNAPSHOT",
                "badge": "SERP Snapshot",
                "summary": f"Captured leaderboard for '{q_keyword}' ({len(ranks)} domains evaluated)",
                "leaderboard": [
                    {
                        "domain": r["domain"],
                        "rank": r["position"],
                        "prev_rank": r["previous_position"],
                        "delta": r["change_in_position"],
                    }
                    for r in ranks_sorted
                ],
            })

        # 2. SEO Optimizations
        opt_rows = conn.execute(
            """
            SELECT opt.id, opt.date, opt.optimization_type, opt.description, opt.reason_for_optimization, opt.expected_effect, opt.observed_effect, w.domain
            FROM seo_optimizations opt
            JOIN websites w ON w.id = opt.website_id
            WHERE w.id IN (SELECT DISTINCT website_id FROM ranking_history WHERE search_query_id = ? OR keyword = ?)
            ORDER BY opt.date ASC
            """,
            (q_id, q_keyword),
        ).fetchall()

        for o in opt_rows:
            events.append({
                "date": o["date"][:10],
                "timestamp": o["date"],
                "type": "OPTIMIZATION_ACTION",
                "badge": f"Optimization: {o['optimization_type'].replace('_', ' ').title()}",
                "domain": o["domain"],
                "summary": o["description"],
                "reason": o["reason_for_optimization"],
                "expected": o["expected_effect"],
                "observed": o["observed_effect"],
            })

        # 3. Competitor History
        comp_rows = conn.execute(
            """
            SELECT ch.id, ch.date, ch.content_changes, ch.feature_changes, ch.ranking_changes, ch.notable_seo_changes, w.domain
            FROM competitor_history ch
            JOIN websites w ON w.id = ch.competitor_website_id
            WHERE ch.keyword = ?
            ORDER BY ch.date ASC
            """,
            (q_keyword,),
        ).fetchall()

        for c in comp_rows:
            events.append({
                "date": c["date"][:10],
                "timestamp": c["date"],
                "type": "COMPETITOR_CHANGE",
                "badge": "Competitor Shift Detected",
                "domain": c["domain"],
                "content_changes": json.loads(c["content_changes"] or "[]"),
                "feature_changes": json.loads(c["feature_changes"] or "[]"),
                "ranking_changes": json.loads(c["ranking_changes"] or "{}"),
                "notable_changes": json.loads(c["notable_seo_changes"] or "[]"),
            })

        # 4. Outcomes
        outcome_rows = conn.execute(
            """
            SELECT o.id, o.date, o.previous_ranking, o.new_ranking, o.observed_change, o.confidence, o.uncertainty_factors, w.domain, opt.optimization_type, opt.description
            FROM outcomes o
            JOIN websites w ON w.id = o.website_id
            JOIN seo_optimizations opt ON opt.id = o.optimization_id
            WHERE w.id IN (SELECT DISTINCT website_id FROM ranking_history WHERE search_query_id = ? OR keyword = ?)
            ORDER BY o.date ASC
            """,
            (q_id, q_keyword),
        ).fetchall()

        for out in outcome_rows:
            events.append({
                "date": out["date"][:10],
                "timestamp": out["date"],
                "type": "CAUSAL_OUTCOME",
                "badge": f"Causal Attribution: {out['observed_change']}",
                "domain": out["domain"],
                "optimization": out["optimization_type"],
                "action_desc": out["description"],
                "previous_rank": out["previous_ranking"],
                "new_rank": out["new_ranking"],
                "confidence": out["confidence"],
                "uncertainty_factors": json.loads(out["uncertainty_factors"] or "[]"),
            })

        # Sort all chronological events by timestamp
        events_sorted = sorted(events, key=lambda x: x["timestamp"])

        return {
            "query": target_q,
            "metadata": DATASET_METADATA,
            "total_events": len(events_sorted),
            "events": events_sorted,
        }


@router.post("/api/v1/debug/seed")
def reseed_database(reset: bool = Query(True)):
    """Reseeds the synthetic dataset."""
    result = populate_synthetic_seo_dataset(reset=reset)
    return result


@router.get("/debug", response_class=HTMLResponse)
def render_developer_debug_view():
    """Serves a developer inspection & debug dashboard to inspect the synthetic dataset."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RankMind Data Inspector & Debug Console</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card: #111827;
      --card-subtle: #1a2234;
      --border: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(99, 102, 241, 0.4);
      --text: #f3f4f6;
      --muted: #9ca3af;
      --accent: #6366f1;
      --success: #10b981;
      --warning: #f59e0b;
      --cyan: #06b6d4;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }
    .container { max-width: 1300px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 16px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .badge-synth { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-event-rank { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
    .badge-event-opt { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-event-comp { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-event-out { background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }
    
    .stats-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: var(--card);
      border: 1px solid var(--border);
      padding: 12px 16px;
      border-radius: 8px;
    }
    .stat-val { font-size: 1.4rem; font-weight: 800; color: #fff; }
    .stat-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; font-weight: 600; }

    .query-selector {
      background: var(--card);
      border: 1px solid var(--border);
      padding: 14px 18px;
      border-radius: 8px;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }
    select {
      background: var(--card-subtle);
      border: 1px solid var(--border);
      color: #fff;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 0.9rem;
      font-family: inherit;
      min-width: 320px;
    }
    button {
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 8px 14px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
    }
    button.btn-sec {
      background: rgba(255, 255, 255, 0.08);
      color: var(--muted);
      border: 1px solid var(--border);
    }

    .timeline {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .event-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      position: relative;
    }
    .event-card:hover { border-color: var(--border-accent); }
    .event-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      flex-wrap: wrap;
      gap: 8px;
    }
    .event-date { font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: var(--muted); }
    .leaderboard-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      margin-top: 10px;
    }
    .leaderboard-table th, .leaderboard-table td {
      padding: 6px 10px;
      border-bottom: 1px solid var(--border);
      text-align: left;
    }
    .rank-pill {
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.06);
    }
    .delta-pos { color: var(--success); font-weight: 700; }
    .delta-neg { color: #f87171; font-weight: 700; }
    .raw-json {
      background: #05070c;
      border: 1px solid var(--border);
      padding: 12px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      color: #93c5fd;
      max-height: 250px;
      overflow-y: auto;
      margin-top: 10px;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <div style="display:flex; align-items:center; gap:10px;">
          <h1 style="font-size:1.4rem; font-weight:800;">RankMind Data Inspector & Debugger</h1>
          <span class="badge badge-synth">Synthetic SEO Dataset v2.0</span>
        </div>
        <p style="font-size:0.85rem; color:var(--muted); margin-top:4px;">
          Empirical timeline verification console for developers. Validates historical milestones, competitor shifts, and causal attributions.
        </p>
      </div>
      <div>
        <button class="btn-sec" onclick="reseedData()">Reseed Synthetic Dataset</button>
      </div>
    </header>

    <div class="stats-bar" id="statsBar">
      <!-- Populated via JS -->
    </div>

    <div class="query-selector">
      <label style="font-size:0.85rem; font-weight:700; color:var(--muted);">Select Search Query Scenario:</label>
      <select id="querySelect" onchange="loadQueryTimeline()">
        <!-- Populated via JS -->
      </select>
      <button onclick="toggleRaw()">Toggle Raw JSON</button>
    </div>

    <div id="rawContainer" style="display:none; margin-bottom:24px;">
      <pre class="raw-json" id="rawContent"></pre>
    </div>

    <div class="timeline" id="timelineList">
      <!-- Populated via JS -->
    </div>
  </div>

  <script>
    let currentTimelineData = null;

    async function init() {
      await loadSummary();
      await loadQueryTimeline();
    }

    async function loadSummary() {
      const res = await fetch('/api/v1/debug/summary');
      const data = await res.json();

      const sb = document.getElementById('statsBar');
      sb.innerHTML = `
        <div class="stat-card"><div class="stat-label">Queries</div><div class="stat-val">${data.counts.search_queries}</div></div>
        <div class="stat-card"><div class="stat-label">Websites</div><div class="stat-val">${data.counts.websites}</div></div>
        <div class="stat-card"><div class="stat-label">Rankings Logged</div><div class="stat-val">${data.counts.ranking_history_entries}</div></div>
        <div class="stat-card"><div class="stat-label">Optimizations</div><div class="stat-val">${data.counts.seo_optimizations}</div></div>
        <div class="stat-card"><div class="stat-label">Competitor Diffs</div><div class="stat-val">${data.counts.competitor_history_entries}</div></div>
        <div class="stat-card"><div class="stat-label">Causal Outcomes</div><div class="stat-val">${data.counts.outcomes}</div></div>
        <div class="stat-card"><div class="stat-label">Citations</div><div class="stat-val">${data.counts.citations}</div></div>
      `;

      const qs = document.getElementById('querySelect');
      qs.innerHTML = data.tracked_queries.map(q => `
        <option value="${q.id}">"${q.query}" (${q.search_intent})</option>
      `).join('');
    }

    async function loadQueryTimeline() {
      const qid = document.getElementById('querySelect').value;
      const res = await fetch(`/api/v1/debug/timeline?query_id=${qid}`);
      const data = await res.json();
      currentTimelineData = data;

      document.getElementById('rawContent').textContent = JSON.stringify(data, null, 2);

      const list = document.getElementById('timelineList');
      if (!data.events || data.events.length === 0) {
        list.innerHTML = `<div style="color:var(--muted); text-align:center; padding:40px;">No historical events recorded for this query.</div>`;
        return;
      }

      list.innerHTML = data.events.map((ev, idx) => {
        let badgeClass = 'badge-event-rank';
        if (ev.type === 'OPTIMIZATION_ACTION') badgeClass = 'badge-event-opt';
        if (ev.type === 'COMPETITOR_CHANGE') badgeClass = 'badge-event-comp';
        if (ev.type === 'CAUSAL_OUTCOME') badgeClass = 'badge-event-out';

        let innerHtml = '';
        if (ev.type === 'RANKING_SNAPSHOT') {
          innerHtml = `
            <table class="leaderboard-table">
              <thead>
                <tr style="color:var(--muted); font-size:0.75rem;">
                  <th>Rank</th><th>Domain</th><th>Previous Rank</th><th>Delta</th>
                </tr>
              </thead>
              <tbody>
                ${ev.leaderboard.map(item => `
                  <tr>
                    <td><span class="rank-pill">#${item.rank}</span></td>
                    <td style="font-weight:600;">${item.domain}</td>
                    <td style="color:var(--muted);">${item.prev_rank ? '#' + item.prev_rank : 'Baseline'}</td>
                    <td class="${item.delta > 0 ? 'delta-pos' : item.delta < 0 ? 'delta-neg' : ''}">${item.delta > 0 ? '+' + item.delta : item.delta}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
        } else if (ev.type === 'OPTIMIZATION_ACTION') {
          innerHtml = `
            <div style="font-size:0.9rem; font-weight:700; color:#fff; margin-bottom:4px;">Domain: ${ev.domain}</div>
            <div style="font-size:0.86rem; color:var(--text); margin-bottom:6px;">${ev.summary}</div>
            <div style="font-size:0.8rem; color:var(--muted); background:rgba(0,0,0,0.25); padding:8px; border-radius:6px;">
              <strong>Strategic Reason:</strong> ${ev.reason}<br>
              <strong>Expected Hypothesis:</strong> ${ev.expected}<br>
              ${ev.observed ? `<strong>Observed Outcome:</strong> ${ev.observed}` : ''}
            </div>
          `;
        } else if (ev.type === 'COMPETITOR_CHANGE') {
          innerHtml = `
            <div style="font-size:0.9rem; font-weight:700; color:#fff; margin-bottom:4px;">Competitor: ${ev.domain}</div>
            <div style="font-size:0.82rem; color:var(--muted); line-height:1.5;">
              ${ev.content_changes.length ? `• <strong>Content:</strong> ${ev.content_changes.join(', ')}<br>` : ''}
              ${ev.feature_changes.length ? `• <strong>Features:</strong> ${ev.feature_changes.join(', ')}<br>` : ''}
              ${ev.notable_changes.length ? `• <strong>SEO/Schemas:</strong> ${ev.notable_changes.join(', ')}` : ''}
            </div>
          `;
        } else if (ev.type === 'CAUSAL_OUTCOME') {
          innerHtml = `
            <div style="font-size:0.92rem; font-weight:700; color:#fff; margin-bottom:4px;">
              ${ev.domain}: #${ev.previous_rank} → #${ev.new_rank} (${ev.badge})
            </div>
            <div style="font-size:0.85rem; color:var(--muted); margin-bottom:6px;">
              Attributed to: <em>"${ev.action_desc}"</em>
            </div>
            <div style="font-size:0.8rem; background:rgba(0,0,0,0.25); padding:8px; border-radius:6px; color:var(--cyan);">
              Confidence Score: <strong>${(ev.confidence * 100).toFixed(0)}%</strong> • Confounders: ${ev.uncertainty_factors.join(', ') || 'None observed'}
            </div>
          `;
        }

        return `
          <div class="event-card">
            <div class="event-header">
              <span class="badge ${badgeClass}">${ev.badge}</span>
              <span class="event-date">Date: ${ev.date} (${ev.timestamp.slice(0, 10)})</span>
            </div>
            ${innerHtml}
          </div>
        `;
      }).join('');
    }

    function toggleRaw() {
      const el = document.getElementById('rawContainer');
      el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }

    async function reseedData() {
      if (!confirm('Reseed the synthetic dataset back to initial 3-scenario baseline?')) return;
      await fetch('/api/v1/debug/seed?reset=true', { method: 'POST' });
      await init();
      alert('Synthetic dataset successfully reseeded!');
    }

    window.onload = init;
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
