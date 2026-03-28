-- Unified Session & Agent Orchestration Schema
-- All sessions from all harnesses in one SQLite database

-- Core sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    harness TEXT NOT NULL,                    -- codex, forge, cursor, claude, droid
    provider TEXT,                            -- Backend: forge, anthropic, openai, etc
    model TEXT,                               -- Model: gpt-4o, claude-3-opus, etc
    project_path TEXT,
    working_directory TEXT,
    
    -- Lifecycle
    state TEXT NOT NULL DEFAULT 'created',   -- created, active, suspended, paused, resumed, closed
    started_at TEXT NOT NULL,
    ended_at TEXT,
    last_activity_at TEXT,
    
    -- Metrics
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    
    -- Content
    messages_json TEXT,                       -- Full message history
    summary TEXT,                             -- AI-generated summary
    goals_json TEXT,                          -- Session goals/objectives
    artifacts_json TEXT,                       -- Files created/modified
    
    -- Coordination
    team_id TEXT,
    parent_session_id TEXT,                   -- For forked sessions
    delegation_chain_json TEXT,               -- Who delegated to whom
    
    -- Audit
    completion_state TEXT DEFAULT 'unknown',  -- optimal, suboptimal, incomplete, failed, unknown
    resolution_notes TEXT,
    metadata_json TEXT,
    
    indexed_at TEXT NOT NULL,
    
    FOREIGN KEY (parent_session_id) REFERENCES sessions(session_id)
);

-- Running agents table (real-time)
CREATE TABLE IF NOT EXISTS running_agents (
    agent_id TEXT PRIMARY KEY,
    harness TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(session_id),
    pid INTEGER,
    started_at TEXT NOT NULL,
    last_heartbeat TEXT,
    status TEXT DEFAULT 'running',           -- running, idle, busy, error, zombie
    current_task TEXT,
    metadata_json TEXT
);

-- Inter-agent messages
CREATE TABLE IF NOT EXISTS agent_messages (
    message_id TEXT PRIMARY KEY,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(session_id),
    message_type TEXT NOT NULL,              -- delegation, status, alert, response, info
    payload_json TEXT,
    priority INTEGER DEFAULT 5,
    sent_at TEXT NOT NULL,
    received_at TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    delivery_status TEXT DEFAULT 'pending'   -- pending, delivered, failed, acknowledged
);

-- Task tracking
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(session_id),
    team_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,              -- 1-10, 1 is highest
    state TEXT DEFAULT 'pending',            -- pending, queued, running, completed, failed, cancelled
    assigned_agent TEXT REFERENCES running_agents(agent_id),
    created_at TEXT NOT NULL,
    updated_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    result_json TEXT,
    error_message TEXT
);

-- Session snapshots (for rollback/fork)
CREATE TABLE IF NOT EXISTS session_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    turn_index INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    messages_json TEXT NOT NULL,
    context_json TEXT,
    description TEXT
);

-- Harness sync status (for incremental indexing)
CREATE TABLE IF NOT EXISTS harness_sync (
    harness TEXT PRIMARY KEY,
    last_sync_at TEXT NOT NULL,
    last_session_at TEXT,
    session_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ok',                -- ok, error, syncing
    error_message TEXT,
    metadata_json TEXT
);

-- Audit log (for sitback monitoring)
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    agent_id TEXT,
    session_id TEXT,
    event_type TEXT NOT NULL,                -- start, stop, message, delegation, error, status_change
    details_json TEXT,
    FOREIGN KEY (agent_id) REFERENCES running_agents(agent_id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Completion state history
CREATE TABLE IF NOT EXISTS completion_history (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    analyzed_at TEXT NOT NULL,
    completion_state TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    factors_json TEXT,                       -- Why this state was assigned
    reviewer_notes TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sessions_harness ON sessions(harness);
CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(state);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_team_id ON sessions(team_id);
CREATE INDEX IF NOT EXISTS idx_sessions_completion ON sessions(completion_state);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity_at DESC);

CREATE INDEX IF NOT EXISTS idx_agents_harness ON running_agents(harness);
CREATE INDEX IF NOT EXISTS idx_agents_status ON running_agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_session ON running_agents(session_id);
CREATE INDEX IF NOT EXISTS idx_agents_heartbeat ON running_agents(last_heartbeat DESC);

CREATE INDEX IF NOT EXISTS idx_messages_from ON agent_messages(from_agent);
CREATE INDEX IF NOT EXISTS idx_messages_to ON agent_messages(to_agent);
CREATE INDEX IF NOT EXISTS idx_messages_type ON agent_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_messages_sent ON agent_messages(sent_at DESC);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_agent);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority ASC);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_agent ON audit_log(agent_id);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);

-- Initial schema version
INSERT INTO schema_version (version, applied_at, description)
VALUES ('1.0.0', datetime('now'), 'Initial unified session orchestration schema');
