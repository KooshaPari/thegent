"""Schema constants for workstream DB initialization."""

SCHEMA_TABLE_SQL: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        agent TEXT,
        prompt TEXT,
        status TEXT,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        exit_code INTEGER,
        workstream_item_id TEXT,
        owner_tag TEXT,
        lane TEXT,
        model TEXT,
        cost_usd REAL,
        tokens_total INTEGER,
        team_id TEXT,
        task_id TEXT,
        evidence_hash TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS workstream_items (
        item_id TEXT PRIMARY KEY,
        title TEXT,
        source TEXT,
        source_system TEXT,
        priority TEXT,
        status TEXT,
        claimed_at TIMESTAMP,
        completed_at TIMESTAMP,
        agent_id TEXT,
        notes TEXT,
        created_at TIMESTAMP,
        last_synced_at TIMESTAMP,
        last_attempted_at TIMESTAMP,
        retry_count INTEGER DEFAULT 0,
        last_error TEXT,
        tags TEXT,
        category TEXT,
        metadata TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS dependencies (
        item_id TEXT,
        depends_on_item_id TEXT,
        satisfied_at TIMESTAMP,
        PRIMARY KEY (item_id, depends_on_item_id),
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id),
        FOREIGN KEY (depends_on_item_id) REFERENCES workstream_items(item_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS launches (
        launch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        session_id TEXT,
        launched_at TIMESTAMP,
        completed_at TIMESTAMP,
        exit_code INTEGER,
        trigger_type TEXT,
        lane TEXT,
        model TEXT,
        estimated_cost_usd REAL,
        actual_cost_usd REAL,
        route_category TEXT,
        deferral_reason TEXT,
        evidence_hash TEXT,
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id),
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS auto_launch_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        session_id TEXT,
        item_id TEXT,
        timestamp TIMESTAMP,
        payload TEXT,
        evidence_hash TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id),
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evidence_links (
        link_id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_hash TEXT,
        entity_type TEXT,
        entity_id TEXT,
        timestamp TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cost_tracking (
        cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        owner_tag TEXT,
        date DATE,
        cost_usd REAL,
        tokens_total INTEGER,
        model TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS deferred_tasks (
        deferral_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        deferred_at TIMESTAMP,
        reason TEXT,
        load_level REAL,
        priority TEXT,
        resumed_at TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS team_tasks (
        team_task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id TEXT,
        task_id TEXT,
        session_id TEXT,
        agent_id TEXT,
        status TEXT,
        created_at TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS kpi_metrics (
        metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP,
        throughput REAL,
        reliability REAL,
        availability REAL,
        finance REAL,
        fatigue REAL,
        integrity REAL,
        continuity REAL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS backlog_items (
        backlog_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        finding_id TEXT,
        dimension TEXT,
        severity REAL,
        description TEXT,
        attempts INTEGER DEFAULT 0,
        last_attempted_at TIMESTAMP,
        created_at TIMESTAMP,
        status TEXT,
        deferred_reason TEXT,
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS teammate_delegations (
        delegation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        teammate_id TEXT,
        parent_run_id TEXT,
        prompt TEXT,
        status TEXT,
        created_at TIMESTAMP,
        completed_at TIMESTAMP,
        result_summary TEXT,
        artifact_path TEXT,
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS policy_overrides (
        override_id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id TEXT,
        reason TEXT,
        by TEXT,
        expires_at TIMESTAMP,
        created_at TIMESTAMP,
        metadata TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS process_tracking (
        process_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        pid INTEGER,
        name TEXT,
        started_at TIMESTAMP,
        cleanup_on_exit BOOLEAN,
        timeout REAL,
        memory_mb REAL,
        cpu_percent REAL,
        num_threads INTEGER,
        open_files INTEGER,
        connections INTEGER,
        num_fds INTEGER,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS siem_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        item_id TEXT,
        severity TEXT,
        event_type TEXT,
        source TEXT,
        payload TEXT,
        timestamp TIMESTAMP,
        egressed BOOLEAN DEFAULT FALSE,
        egressed_at TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id),
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rbac_audit (
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        permission TEXT,
        operation TEXT,
        lane TEXT,
        allowed BOOLEAN,
        reason TEXT,
        timestamp TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS memory_cache (
        cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cache_key TEXT UNIQUE,
        cache_value TEXT,
        l1_hit BOOLEAN DEFAULT FALSE,
        l2_hit BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP,
        accessed_at TIMESTAMP,
        ttl_seconds INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS constitutional_violations (
        violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        session_id TEXT,
        principle_id TEXT,
        reason TEXT,
        remediation TEXT,
        timestamp TIMESTAMP,
        resolved BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (item_id) REFERENCES workstream_items(item_id),
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reputation (
        agent_id TEXT PRIMARY KEY,
        trust_score REAL DEFAULT 1.0,
        entries_count INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reputation_entries (
        reputation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        reviewer_id TEXT,
        task_id TEXT,
        rating REAL,
        feedback_hash TEXT,
        timestamp TIMESTAMP,
        FOREIGN KEY (agent_id) REFERENCES reputation(agent_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_hierarchy (
        hierarchy_id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        run_id TEXT,
        role TEXT,
        team_id TEXT,
        parent_id TEXT,
        coordination_mode TEXT,
        created_at TIMESTAMP,
        status TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sync_tracking (
        sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
        component TEXT,
        status TEXT,
        message TEXT,
        duration REAL,
        details TEXT,
        timestamp TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS config_cache (
        config_id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key TEXT UNIQUE,
        config_value TEXT,
        system_name TEXT,
        source_path TEXT,
        cached_at TIMESTAMP,
        ttl_seconds INTEGER DEFAULT 300
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS plan_tasks (
        plan_task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT,
        phase_number INTEGER,
        description TEXT,
        status TEXT,
        depends_on TEXT,
        completed_at TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS alert_fatigue (
        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kind TEXT,
        suppressed BOOLEAN,
        timestamp TIMESTAMP
    )
    """,
)

SCHEMA_INDEX_SQL: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_workstream_item ON sessions(workstream_item_id)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_lane ON sessions(lane)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_team ON sessions(team_id)",
    "CREATE INDEX IF NOT EXISTS idx_workstream_status ON workstream_items(status)",
    "CREATE INDEX IF NOT EXISTS idx_dependencies_satisfied ON dependencies(satisfied_at)",
    "CREATE INDEX IF NOT EXISTS idx_launches_item ON launches(item_id)",
    "CREATE INDEX IF NOT EXISTS idx_launches_session ON launches(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_launches_lane ON launches(lane)",
    "CREATE INDEX IF NOT EXISTS idx_cost_tracking_date ON cost_tracking(date)",
    "CREATE INDEX IF NOT EXISTS idx_cost_tracking_owner ON cost_tracking(owner_tag)",
    "CREATE INDEX IF NOT EXISTS idx_deferred_tasks_item ON deferred_tasks(item_id)",
    "CREATE INDEX IF NOT EXISTS idx_team_tasks_team ON team_tasks(team_id)",
    "CREATE INDEX IF NOT EXISTS idx_kpi_metrics_timestamp ON kpi_metrics(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_backlog_items_status ON backlog_items(status)",
    "CREATE INDEX IF NOT EXISTS idx_teammate_delegations_status ON teammate_delegations(status)",
    "CREATE INDEX IF NOT EXISTS idx_policy_overrides_policy ON policy_overrides(policy_id)",
    "CREATE INDEX IF NOT EXISTS idx_policy_overrides_expires ON policy_overrides(expires_at)",
    "CREATE INDEX IF NOT EXISTS idx_process_tracking_pid ON process_tracking(pid)",
    "CREATE INDEX IF NOT EXISTS idx_process_tracking_session ON process_tracking(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_siem_events_severity ON siem_events(severity)",
    "CREATE INDEX IF NOT EXISTS idx_siem_events_egressed ON siem_events(egressed)",
    "CREATE INDEX IF NOT EXISTS idx_rbac_audit_role ON rbac_audit(role)",
    "CREATE INDEX IF NOT EXISTS idx_rbac_audit_timestamp ON rbac_audit(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_memory_cache_key ON memory_cache(cache_key)",
    "CREATE INDEX IF NOT EXISTS idx_constitutional_violations_item ON constitutional_violations(item_id)",
    "CREATE INDEX IF NOT EXISTS idx_reputation_entries_agent ON reputation_entries(agent_id)",
    "CREATE INDEX IF NOT EXISTS idx_agent_hierarchy_agent ON agent_hierarchy(agent_id)",
    "CREATE INDEX IF NOT EXISTS idx_agent_hierarchy_team ON agent_hierarchy(team_id)",
    "CREATE INDEX IF NOT EXISTS idx_sync_tracking_component ON sync_tracking(component)",
    "CREATE INDEX IF NOT EXISTS idx_config_cache_key ON config_cache(config_key)",
    "CREATE INDEX IF NOT EXISTS idx_plan_tasks_phase ON plan_tasks(phase_number)",
    "CREATE INDEX IF NOT EXISTS idx_alert_fatigue_kind ON alert_fatigue(kind)",
    "CREATE INDEX IF NOT EXISTS idx_alert_fatigue_timestamp ON alert_fatigue(timestamp)",
)
