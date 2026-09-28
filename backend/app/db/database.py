import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from app.core.config import DATA_DIR

DB_PATH = DATA_DIR / "rankmind.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- 1. SEARCH QUERY TABLE
CREATE TABLE IF NOT EXISTS search_queries (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    target_keyword TEXT NOT NULL,
    search_intent TEXT NOT NULL DEFAULT 'informational',
    date TEXT NOT NULL,
    location TEXT DEFAULT 'Global'
);
CREATE INDEX IF NOT EXISTS idx_sq_query ON search_queries(query);
CREATE INDEX IF NOT EXISTS idx_sq_keyword ON search_queries(target_keyword);
CREATE INDEX IF NOT EXISTS idx_sq_date ON search_queries(date);

-- 2. WEBSITE TABLE
CREATE TABLE IF NOT EXISTS websites (
    id TEXT PRIMARY KEY,
    domain TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content_topic TEXT NOT NULL DEFAULT 'General',
    seo_observations TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_websites_domain ON websites(domain);

-- 3. RANKING HISTORY TABLE
CREATE TABLE IF NOT EXISTS ranking_history (
    id TEXT PRIMARY KEY,
    website_id TEXT NOT NULL,
    search_query_id TEXT,
    keyword TEXT NOT NULL,
    date TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position >= 1),
    previous_position INTEGER CHECK (previous_position IS NULL OR previous_position >= 1),
    change_in_position INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE,
    FOREIGN KEY (search_query_id) REFERENCES search_queries(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_rh_website_keyword ON ranking_history(website_id, keyword, date);

-- 4. SEO OPTIMIZATIONS TABLE
CREATE TABLE IF NOT EXISTS seo_optimizations (
    id TEXT PRIMARY KEY,
    website_id TEXT NOT NULL,
    date TEXT NOT NULL,
    optimization_type TEXT NOT NULL,
    description TEXT NOT NULL,
    reason_for_optimization TEXT NOT NULL,
    expected_effect TEXT NOT NULL,
    observed_effect TEXT,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_opt_website ON seo_optimizations(website_id);
CREATE INDEX IF NOT EXISTS idx_opt_type ON seo_optimizations(optimization_type);

-- 5. COMPETITOR HISTORY TABLE
CREATE TABLE IF NOT EXISTS competitor_history (
    id TEXT PRIMARY KEY,
    competitor_website_id TEXT NOT NULL,
    keyword TEXT NOT NULL,
    date TEXT NOT NULL,
    content_changes TEXT NOT NULL DEFAULT '[]',
    feature_changes TEXT NOT NULL DEFAULT '[]',
    ranking_changes TEXT NOT NULL DEFAULT '{}',
    notable_seo_changes TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (competitor_website_id) REFERENCES websites(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_comp_website ON competitor_history(competitor_website_id);
CREATE INDEX IF NOT EXISTS idx_comp_keyword ON competitor_history(keyword);

-- 6. OUTCOME TABLE (Causal Attribution)
CREATE TABLE IF NOT EXISTS outcomes (
    id TEXT PRIMARY KEY,
    website_id TEXT NOT NULL,
    optimization_id TEXT NOT NULL,
    previous_ranking INTEGER NOT NULL CHECK (previous_ranking >= 1),
    new_ranking INTEGER NOT NULL CHECK (new_ranking >= 1),
    observed_change TEXT NOT NULL,
    date TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    uncertainty_factors TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE,
    FOREIGN KEY (optimization_id) REFERENCES seo_optimizations(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_outcome_website ON outcomes(website_id);
CREATE INDEX IF NOT EXISTS idx_outcome_optimization ON outcomes(optimization_id);

-- 7. CONTENT / CITATION INFORMATION TABLE (Flexible)
CREATE TABLE IF NOT EXISTS content_citations (
    id TEXT PRIMARY KEY,
    website_id TEXT,
    search_query_id TEXT,
    source_title TEXT NOT NULL,
    source_url TEXT NOT NULL,
    citation_snippet TEXT,
    citation_type TEXT NOT NULL DEFAULT 'authoritative_reference',
    is_used_by_app INTEGER NOT NULL DEFAULT 1,
    citation_metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE SET NULL,
    FOREIGN KEY (search_query_id) REFERENCES search_queries(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_cit_website ON content_citations(website_id);
CREATE INDEX IF NOT EXISTS idx_cit_query ON content_citations(search_query_id);

-- 8. USER INTERACTION TABLE
CREATE TABLE IF NOT EXISTS user_interactions (
    id TEXT PRIMARY KEY,
    search_query_id TEXT,
    query_text TEXT NOT NULL,
    selected_website_id TEXT,
    question_asked TEXT,
    recommendation_requested TEXT,
    recommendation_provided TEXT,
    feedback TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (search_query_id) REFERENCES search_queries(id) ON DELETE SET NULL,
    FOREIGN KEY (selected_website_id) REFERENCES websites(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_ui_query ON user_interactions(search_query_id);
CREATE INDEX IF NOT EXISTS idx_ui_website ON user_interactions(selected_website_id);

-- 9. HINDSIGHT PERSISTENT MEMORY TABLES
CREATE TABLE IF NOT EXISTS hindsight_memories (
    id TEXT PRIMARY KEY,
    bank_id TEXT NOT NULL,
    category TEXT NOT NULL,
    target_keyword TEXT NOT NULL,
    target_domain TEXT,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    tags TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_hm_bank ON hindsight_memories(bank_id);
CREATE INDEX IF NOT EXISTS idx_hm_keyword ON hindsight_memories(target_keyword);
CREATE INDEX IF NOT EXISTS idx_hm_category ON hindsight_memories(category);
CREATE INDEX IF NOT EXISTS idx_hm_domain ON hindsight_memories(target_domain);

CREATE TABLE IF NOT EXISTS hindsight_retain_logs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    bank_id TEXT NOT NULL,
    category TEXT NOT NULL,
    target_keyword TEXT NOT NULL,
    target_domain TEXT,
    content_snippet TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS hindsight_recall_logs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    bank_id TEXT NOT NULL,
    query TEXT NOT NULL,
    target_domain TEXT,
    recalled_count INTEGER NOT NULL,
    recalled_memory_ids TEXT NOT NULL DEFAULT '[]',
    why_relevant_summary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hindsight_retention_decisions (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    bank_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    website TEXT NOT NULL,
    keyword TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    importance_score REAL NOT NULL,
    fingerprint TEXT NOT NULL,
    content_snippet TEXT,
    normalized_data TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_hrd_decision ON hindsight_retention_decisions(decision);
CREATE INDEX IF NOT EXISTS idx_hrd_website ON hindsight_retention_decisions(website);
CREATE INDEX IF NOT EXISTS idx_hrd_fingerprint ON hindsight_retention_decisions(fingerprint);

-- 10. LEARNING LOOP EVENT LIFECYCLE TABLE
CREATE TABLE IF NOT EXISTS learning_loop_events (
    id TEXT PRIMARY KEY,
    website_id TEXT,
    website_domain TEXT NOT NULL,
    keyword TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    stage TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    state_snapshot TEXT NOT NULL DEFAULT '{}',
    details TEXT NOT NULL DEFAULT '{}',
    timestamp TEXT NOT NULL,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_lle_website ON learning_loop_events(website_domain);
CREATE INDEX IF NOT EXISTS idx_lle_keyword ON learning_loop_events(keyword);
CREATE INDEX IF NOT EXISTS idx_lle_stage ON learning_loop_events(stage);
"""


def init_db(db_path: Path = DB_PATH, reset: bool = False):
    """Initializes SQLite schema with foreign key constraints enabled."""
    if reset and db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


def dict_factory(cursor, row):
    """Row factory that converts SQLite rows into dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@contextmanager
def get_connection(db_path: Path = DB_PATH):
    """Context manager yielding SQLite connection with dict_factory and foreign keys."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
