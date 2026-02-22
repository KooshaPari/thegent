CREATE TABLE IF NOT EXISTS docs (
    path TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    title TEXT NOT NULL,
    layer INTEGER NOT NULL,
    date TEXT NOT NULL,
    author TEXT DEFAULT 'agent',
    session_id TEXT DEFAULT '',
    git_commit TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    relates_to TEXT DEFAULT '[]',
    traces_to TEXT DEFAULT '[]',
    indexed_at TEXT NOT NULL,
    content_hash TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS relations (
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    PRIMARY KEY (source_path, target_path, relation_type)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    doc_path TEXT,
    git_ref TEXT DEFAULT '',
    timestamp TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_docs_type ON docs(type);
CREATE INDEX IF NOT EXISTS idx_docs_status ON docs(status);
CREATE INDEX IF NOT EXISTS idx_docs_layer ON docs(layer);
CREATE INDEX IF NOT EXISTS idx_docs_date ON docs(date);
