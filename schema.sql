-- Stores the sources we scrape from (e.g., Hacker News, a specific RSS feed)
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'hn', 'reddit', 'rss'
    url TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Stores raw data scraped from the internet
CREATE TABLE IF NOT EXISTS discoveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    original_url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    author TEXT,
    collection_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

-- Stores verified problems identified by the LLM
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_summary TEXT NOT NULL,
    severity INTEGER,
    target_audience TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- The many-to-many link between Discoveries and Problems (Evidence)
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    discovery_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(problem_id) REFERENCES problems(id),
    FOREIGN KEY(discovery_id) REFERENCES discoveries(id),
    UNIQUE(problem_id, discovery_id)
);

-- The high-level opportunities based on problems
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER, -- Can be linked to a specific problem
    title TEXT NOT NULL,
    problem_description TEXT NOT NULL,
    score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME,
    FOREIGN KEY(problem_id) REFERENCES problems(id)
);

-- Tracks system runs (processor, delivery, etc)
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type TEXT NOT NULL, -- 'processor' or 'delivery'
    status TEXT NOT NULL, -- 'success', 'failed', 'started'
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    log_message TEXT
);
