"""Workstream database for auto-launch system.

SQLite database for tracking sessions, workstream items, launches, and all related data.
Harmonized with EvidenceLedger, RunRegistry, and other thegent components.
"""

import json
import logging
import sqlite3
import threading
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class WorkstreamDB:
    """SQLite database for workstream tracking and auto-launch observability."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: Path | None = None, settings: ThegentSettings | None = None) -> None:
        """Initialize workstream database.

        Args:
            db_path: Path to SQLite database file. Defaults to session_dir/workstream.db
            settings: ThegentSettings instance. Required if db_path not provided.
        """
        if db_path is None:
            if settings is None:
                settings = ThegentSettings()
            db_path = settings.session_dir / "workstream.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._stats_cache: dict[str, Any] = {}
        self._cache_lock = threading.Lock()
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Check if schema exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        )
        if cursor.fetchone():
            # Schema exists, check version
            cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row and row[0] >= self.SCHEMA_VERSION:
                conn.close()
                return

        # Create schema version table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Sessions table (harmonized with RunRegistry, extended with lanes/cost/team)
        cursor.execute(
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
            """
        )

        # Workstream items table (harmonized with WORK_STREAM.md)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workstream_items (
                item_id TEXT PRIMARY KEY,
                title TEXT,
                source TEXT,
                priority TEXT,
                status TEXT,
                claimed_at TIMESTAMP,
                completed_at TIMESTAMP,
                agent_id TEXT,
                notes TEXT,
                created_at TIMESTAMP,
                last_synced_at TIMESTAMP,
                retry_count INTEGER DEFAULT 0,
                last_error TEXT
            )
            """
        )

        # Dependencies table (normalized, supports auto-resolution)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dependencies (
                item_id TEXT,
                depends_on_item_id TEXT,
                satisfied_at TIMESTAMP,
                PRIMARY KEY (item_id, depends_on_item_id),
                FOREIGN KEY (item_id) REFERENCES workstream_items(item_id),
                FOREIGN KEY (depends_on_item_id) REFERENCES workstream_items(item_id)
            )
            """
        )

        # Launches table (tracking auto-launch decisions, extended with lanes/cost/routing)
        cursor.execute(
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
            """
        )

        # Auto-launch events (for audit trail)
        cursor.execute(
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
            """
        )

        # Evidence links (harmonized with EvidenceLedger)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS evidence_links (
                link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_hash TEXT,
                entity_type TEXT,
                entity_id TEXT,
                timestamp TIMESTAMP
            )
            """
        )

        # Cost tracking (harmonized with CostAggregator)
        cursor.execute(
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
            """
        )

        # Deferral tracking (harmonized with DeferralManager)
        cursor.execute(
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
            """
        )

        # Team coordination (harmonized with TeamCoordinator)
        cursor.execute(
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
            """
        )

        # KPI metrics (harmonized with KPIDashboard)
        cursor.execute(
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
            """
        )

        # Backlog tracking (harmonized with BacklogManager)
        cursor.execute(
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
            """
        )

        # Teammate delegations (harmonized with TeammateManager)
        cursor.execute(
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
            """
        )

        # Policy overrides (harmonized with OverrideManager)
        cursor.execute(
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
            """
        )

        # Process tracking (harmonized with ProcessRegistry)
        cursor.execute(
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
            """
        )

        # SIEM events (harmonized with SIEMEgress)
        cursor.execute(
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
            """
        )

        # RBAC audit log (harmonized with RBACManager)
        cursor.execute(
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
            """
        )

        # Memory cache tracking (harmonized with MemoryManager)
        cursor.execute(
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
            """
        )

        # Constitutional violations (harmonized with ConstitutionManager)
        cursor.execute(
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
            """
        )

        # Reputation tracking (harmonized with ReputationManager)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reputation_entries (
                reputation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                reviewer_id TEXT,
                task_id TEXT,
                rating REAL,
                feedback_hash TEXT,
                timestamp TIMESTAMP
            )
            """
        )

        # Agent hierarchy (harmonized with AgentHierarchyManager)
        cursor.execute(
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
            """
        )

        # Sync tracking (harmonized with SyncOrchestrator)
        cursor.execute(
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
            """
        )

        # Unified config cache (harmonized with UnifiedConfigManager)
        cursor.execute(
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
            """
        )

        # Plan integration tracking (harmonized with PlanSystemIntegration)
        cursor.execute(
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
            """
        )

        # Alert fatigue tracking (harmonized with AlertFatigueController)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_fatigue (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT,
                suppressed BOOLEAN,
                timestamp TIMESTAMP
            )
            """
        )

        # Create indexes for performance
        indexes = [
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
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        # Record schema version
        cursor.execute(
            "INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,)
        )

        conn.commit()
        conn.close()
        _log.info(f"Initialized workstream database at {self.db_path}")

    def get_running_count(self) -> int:
        """Get count of running sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'running'")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_running_count_by_lane(self) -> dict[str, int]:
        """Get count of running sessions by lane."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT lane, COUNT(*) 
            FROM sessions 
            WHERE status = 'running' 
            GROUP BY lane
            """
        )
        result = {row[0] or "standard": row[1] for row in cursor.fetchall()}
        conn.close()
        return result

    def mark_session_complete(self, session_id: str, exit_code: int) -> None:
        """Mark a session as complete."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE sessions 
            SET status = 'exited', completed_at = ?, exit_code = ?
            WHERE session_id = ?
            """,
            (datetime.now(UTC).isoformat(), exit_code, session_id),
        )
        conn.commit()
        conn.close()

    def record_launch(
        self,
        item_id: str,
        session_id: str,
        lane: str,
        model: str,
        estimated_cost: float,
        trigger_type: str = "auto_launch",
        pid: int | None = None,
    ) -> int:
        """Record a launch in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO launches 
            (item_id, session_id, launched_at, lane, model, estimated_cost_usd, trigger_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                session_id,
                datetime.now(UTC).isoformat(),
                lane,
                model,
                estimated_cost,
                trigger_type,
            ),
        )
        launch_id = cursor.lastrowid

        # Record process tracking if pid provided
        if pid:
            cursor.execute(
                """
                INSERT INTO process_tracking 
                (session_id, pid, name, started_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, pid, f"auto-launch-{item_id}", datetime.now(UTC).isoformat()),
            )

        conn.commit()
        conn.close()
        return launch_id

    def record_cost(self, session_id: str, cost_usd: float, tokens_total: int = 0, model: str | None = None) -> None:
        """Record cost for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session info if model not provided
        if not model:
            cursor.execute("SELECT model, owner_tag FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            model = row[0] if row else "unknown"
            owner_tag = row[1] if row else "unknown"
        else:
            cursor.execute("SELECT owner_tag FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            owner_tag = row[0] if row else "unknown"

        cursor.execute(
            """
            INSERT INTO cost_tracking 
            (session_id, owner_tag, date, cost_usd, tokens_total, model)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, owner_tag, datetime.now(UTC).date().isoformat(), cost_usd, tokens_total, model),
        )
        
        # Update session record
        cursor.execute(
            "UPDATE sessions SET cost_usd = ?, tokens_total = ? WHERE session_id = ?",
            (cost_usd, tokens_total, session_id),
        )
        
        # Update launch record if exists
        cursor.execute(
            "UPDATE launches SET actual_cost_usd = ? WHERE session_id = ?",
            (cost_usd, session_id),
        )
        
        conn.commit()
        conn.close()

    def record_resource_usage(self, session_id: str, usage: dict[str, Any]) -> None:
        """Record resource usage for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE process_tracking 
            SET memory_mb = ?, cpu_percent = ?, num_threads = ?, open_files = ?, connections = ?, num_fds = ?
            WHERE session_id = ?
            """,
            (
                usage.get("memory_mb"),
                usage.get("cpu_percent"),
                usage.get("num_threads"),
                usage.get("open_files"),
                usage.get("connections"),
                usage.get("num_fds"),
                session_id,
            ),
        )
        conn.commit()
        conn.close()

    def record_constitutional_violation(self, item_id: str, session_id: str | None, violation: Any) -> None:
        """Record a constitutional violation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO constitutional_violations 
            (item_id, session_id, principle_id, reason, remediation, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                session_id,
                getattr(violation, "principle_id", "unknown"),
                getattr(violation, "reason", str(violation)),
                getattr(violation, "remediation", ""),
                datetime.now(UTC).isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    def sync_workstream(self, workstream_data: dict[str, Any]) -> None:
        """Sync workstream data from markdown parser to database.
        
        Args:
            workstream_data: Dict with 'backlog', 'claimed', 'completed' keys.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Update workstream_items
        backlog = workstream_data.get("backlog", [])
        claimed = workstream_data.get("claimed", set())
        completed = workstream_data.get("completed", set())
        
        # Upsert items from backlog
        for item in backlog:
            item_id = item["id"]
            status = "pending"
            if item_id in claimed:
                status = "claimed"
            elif item_id in completed:
                status = "completed"
                
            cursor.execute(
                """
                INSERT INTO workstream_items (item_id, title, source, priority, status, last_synced_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    title=excluded.title,
                    source=excluded.source,
                    priority=excluded.priority,
                    status=excluded.status,
                    last_synced_at=excluded.last_synced_at
                """,
                (
                    item_id,
                    item.get("title", ""),
                    item.get("source", ""),
                    item.get("priority", "P2"),
                    status,
                    datetime.now(UTC).isoformat(),
                ),
            )
            
            # Update dependencies
            depends = item.get("depends", [])
            # First remove existing dependencies for this item
            cursor.execute("DELETE FROM dependencies WHERE item_id = ?", (item_id,))
            for dep_id in depends:
                cursor.execute(
                    "INSERT OR IGNORE INTO dependencies (item_id, depends_on_item_id) VALUES (?, ?)",
                    (item_id, dep_id),
                )
        
        # Upsert items that are only in claimed/completed but not in backlog
        # (Shouldn't happen often but for robustness)
        for item_id in (claimed | completed):
            cursor.execute("SELECT 1 FROM workstream_items WHERE item_id = ?", (item_id,))
            if not cursor.fetchone():
                status = "claimed" if item_id in claimed else "completed"
                cursor.execute(
                    """
                    INSERT INTO workstream_items (item_id, status, last_synced_at)
                    VALUES (?, ?, ?)
                    """,
                    (item_id, status, datetime.now(UTC).isoformat()),
                )

        conn.commit()
        conn.close()

    def get_ready_items(self, max_retries: int = 3) -> list[dict[str, Any]]:
        """Get items that are pending and have all dependencies satisfied."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Items with no unsatisfied dependencies
        cursor.execute(
            """
            SELECT wi.* FROM workstream_items wi
            WHERE (wi.status IN ('pending', 'backlog') OR (wi.status = 'failed' AND wi.retry_count < ?))
            AND NOT EXISTS (
                SELECT 1 FROM dependencies d
                JOIN workstream_items wi2 ON d.depends_on_item_id = wi2.item_id
                WHERE d.item_id = wi.item_id
                AND wi2.status != 'completed'
            )
            ORDER BY 
                CASE wi.priority 
                    WHEN 'P0' THEN 1 
                    WHEN 'P1' THEN 2 
                    WHEN 'P2' THEN 3 
                    ELSE 4 
                END
            """,
            (max_retries,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_statistics(self) -> dict[str, Any]:
        """Get workstream statistics."""
        # Use cache for performance in TUI refresh loops
        with self._cache_lock:
            if "last_stats_refresh" in self._stats_cache:
                dt = datetime.fromisoformat(self._stats_cache["last_stats_refresh"])
                if (datetime.now(UTC) - dt).total_seconds() < 1.0:
                    return self._stats_cache["stats"]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Running count
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'running'")
        running = cursor.fetchone()[0]

        # Completed count
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'exited'")
        completed = cursor.fetchone()[0]

        # Success rate
        cursor.execute(
            "SELECT COUNT(*) FROM sessions WHERE status = 'exited' AND exit_code = 0"
        )
        successful = cursor.fetchone()[0]
        success_rate = (successful / completed * 100) if completed > 0 else 0.0

        # Average duration
        cursor.execute(
            """
            SELECT AVG((julianday(completed_at) - julianday(started_at)) * 86400)
            FROM sessions
            WHERE completed_at IS NOT NULL AND started_at IS NOT NULL
            """
        )
        avg_duration = cursor.fetchone()[0] or 0.0

        # Deferred count
        cursor.execute("SELECT COUNT(*) FROM deferred_tasks WHERE resumed_at IS NULL")
        deferred = cursor.fetchone()[0]

        conn.close()

        stats = {
            "running": running,
            "completed": completed,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "deferred": deferred,
        }
        
        # Cache results
        with self._cache_lock:
            self._stats_cache["stats"] = stats
            self._stats_cache["last_stats_refresh"] = datetime.now(UTC).isoformat()
            
        return stats

    @lru_cache(maxsize=32)
    def get_recent_costs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent cost tracking entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                date as period,
                SUM(cost_usd) as cost_usd,
                COUNT(*) as task_count,
                AVG(cost_usd) as avg_per_task
            FROM cost_tracking
            GROUP BY date
            ORDER BY date DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "period": row[0],
                "cost_usd": row[1],
                "task_count": row[2],
                "avg_per_task": row[3],
            }
            for row in rows
        ]

    def execute_query(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as list of dicts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get session by ID."""
        results = self.execute_query("SELECT * FROM sessions WHERE session_id = ? LIMIT 1", (session_id,))
        return results[0] if results else None

    def get_running_sessions(self) -> list[dict[str, Any]]:
        """Get all running sessions."""
        return self.execute_query("SELECT * FROM sessions WHERE status = 'running' ORDER BY started_at DESC")

    def get_active_items(self) -> list[dict[str, Any]]:
        """Get active workstream items."""
        return self.execute_query(
            "SELECT * FROM workstream_items WHERE status IN ('backlog', 'claimed') ORDER BY priority ASC"
        )

    def record_session(
        self,
        session_id: str,
        agent: str,
        prompt: str,
        status: str,
        workstream_item_id: str | None = None,
        lane: str | None = None,
        model: str | None = None,
        owner_tag: str | None = None,
        team_id: str | None = None,
        task_id: str | None = None,
    ) -> None:
        """Record or update a session in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO sessions 
            (session_id, agent, prompt, status, started_at, workstream_item_id, lane, model, owner_tag, team_id, task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                agent,
                prompt,
                status,
                datetime.now(UTC).isoformat(),
                workstream_item_id,
                lane,
                model,
                owner_tag,
                team_id,
                task_id,
            ),
        )
        conn.commit()
        conn.close()

    def sync_with_markdown(self, work_stream_path: Path) -> None:
        """Sync WORK_STREAM.md with the database.
        
        Bidirectional sync:
        1. Parse WORK_STREAM.md
        2. Update database workstream_items and dependencies
        3. (Optional) Could update markdown from DB if needed
        """
        if not work_stream_path.exists():
            _log.warning(f"Work stream file not found: {work_stream_path}")
            return

        from thegent.integration.work_stream import WorkStreamIntegration
        integration = WorkStreamIntegration(work_stream_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now(UTC).isoformat()
        
        # 1. Sync items
        for section, status in [("pending", "backlog"), ("claimed", "claimed"), ("completed", "completed")]:
            items = integration.work_stream_data.get(section, [])
            for item in items:
                item_id = item.get("ID")
                if not item_id:
                    continue
                
                title = item.get("Title", "")
                source = item.get("Source", "")
                priority = item.get("Priority", "P2")
                agent_id = item.get("Agent", "")
                
                cursor.execute(
                    """
                    INSERT INTO workstream_items (item_id, title, source, priority, status, agent_id, last_synced_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(item_id) DO UPDATE SET
                        title=excluded.title,
                        source=excluded.source,
                        priority=excluded.priority,
                        status=excluded.status,
                        agent_id=excluded.agent_id,
                        last_synced_at=excluded.last_synced_at
                    """,
                    (item_id, title, source, priority, status, agent_id, now)
                )
                
                # 2. Sync dependencies
                depends_on = item.get("Depends", "")
                if depends_on and depends_on != "—" and depends_on != "-":
                    # Split by comma or semicolon
                    dep_ids = [d.strip() for d in depends_on.replace(";", ",").split(",")]
                    for dep_id in dep_ids:
                        if not dep_id or dep_id.startswith("✅"):
                            continue
                        
                        cursor.execute(
                            "INSERT OR IGNORE INTO dependencies (item_id, depends_on_item_id) VALUES (?, ?)",
                            (item_id, dep_id)
                        )

        conn.commit()
        conn.close()
        _log.info(f"Synced database with {work_stream_path}")
