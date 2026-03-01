"""Auto-launch system for workstream items.

Event-driven system that automatically launches workstream items when:
- Agent sessions complete
- Dependencies are cleared
- Capacity becomes available

Harmonized with all thegent components: WorkStreamManager, EvidenceLedger,
LaneModel, CostEstimator, DeferralManager, TaskRouter, TeamCoordinator, etc.
"""

import orjson as json
import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent_core.config import ThegentSettings
from thegent_routing.cost.aggregator import CostAggregator, CostEstimator
from thegent_audit.economy.reputation import ReputationManager
from thegent_audit.governance.agent_hierarchy import AgentHierarchyManager
from thegent_audit.governance.backlog import BacklogManager
from thegent_audit.governance.constitution import ConstitutionManager
from thegent_audit.governance.evidence_ledger import EvidenceLedger
from thegent_audit.governance.overrides import OverrideManager
from thegent_audit.governance.teammates import TeammateManager
from thegent_core.infra.process_registry import ProcessRegistry
from thegent_core.infra.subprocess_manager import SubprocessManager
from thegent_planning.integration.plan_system import PlanSystemIntegration
from thegent_planning.integration.unified_config import UnifiedConfigManager
from thegent_core.memory.manager import MemoryManager
from thegent_observability.observability.analytics import AnalyticsIntegration
from thegent_observability.observability.egress import EgressEvent, SIEMEgress
from thegent_execution.orchestration.execution.lanes import Lane, LaneModel
from thegent_execution.orchestration.execution.worker_pool import PersistentWorkerPool
from thegent_execution.orchestration.resilience.deferral import DeferralManager
from thegent_execution.orchestration.resource.load_based_limits import (
    compute_dynamic_limit,
    sample_resources,
)
from thegent_execution.orchestration.state.session_watcher import SessionEventWatcher
from thegent_planning.planning.work_stream import WorkStreamManager
from thegent_planning.planning.workstream_db import WorkstreamDB
from thegent_core.utils.routing_impl.task_router import TaskRouter
from thegent_audit.security.rbac import Permission, RBACManager, Role
from thegent_sync.sync import SyncOrchestrator, SyncRegistry
from thegent_agents.team.coordination import TeamCoordinator
from thegent_cli.ux.alerts import AlertFatigueController, InterruptionKind

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Agent throttle API (FR-ORCH-001)
# ---------------------------------------------------------------------------

from dataclasses import dataclass as _dataclass


@_dataclass
class _ThrottleResult:
    """Result of agent throttle check."""

    action: str  # "ok", "warn", "throttle", "hard_stop"
    count: int
    limit: int
    message: str


def get_active_agent_count() -> int:
    """Return count of currently active agent processes."""
    import psutil

    count = 0
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            name = proc.info.get("name", "") or ""
            if any(agent in name for agent in ("cursor-agent", "thegent", "claude", "codex", "droid")):
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):  # noqa: PERF203 - intentional per-item error handling
            pass
    return count


def check_agent_throttle(
    count: int | None = None,
    warn_at: int = 20,
    throttle_at: int = 50,
    hard_stop_at: int = 80,
) -> _ThrottleResult:
    """Check current agent count against throttle thresholds.

    Returns a _ThrottleResult with action in: "ok", "warn", "throttle", "hard_stop".
    """
    if count is None:
        count = get_active_agent_count()
    if count >= hard_stop_at:
        return _ThrottleResult(
            action="hard_stop", count=count, limit=hard_stop_at, message=f"Hard stop: {count} agents >= {hard_stop_at}"
        )
    if count >= throttle_at:
        return _ThrottleResult(
            action="throttle", count=count, limit=throttle_at, message=f"Throttle: {count} agents >= {throttle_at}"
        )
    if count >= warn_at:
        return _ThrottleResult(
            action="warn", count=count, limit=warn_at, message=f"Warning: {count} agents >= {warn_at}"
        )
    return _ThrottleResult(
        action="ok", count=count, limit=warn_at, message=f"OK: {count} agents below warn threshold {warn_at}"
    )


class AutoLaunchSystem:
    """Event-driven auto-launch system for workstream items."""

    def __init__(self, settings: ThegentSettings | None = None) -> None:
        """Initialize auto-launch system with all component integrations.

        Args:
            settings: ThegentSettings instance. Defaults to ThegentSettings().
        """
        self.settings = settings or ThegentSettings()

        # Core components
        self.workstream_manager = WorkStreamManager(self.settings, base_dir=Path.cwd())
        self.db = WorkstreamDB(settings=self.settings)
        self.evidence_ledger = EvidenceLedger(self.settings.session_dir)
        self.event_watcher = SessionEventWatcher(self.settings.session_dir)

        # Register completion callback
        self.event_watcher.on_complete(self.handle_completion)

        # Extended integrations
        self.worker_pool = PersistentWorkerPool.get_instance()
        self.lane_model = LaneModel()
        self.cost_estimator = CostEstimator()
        self.cost_aggregator = CostAggregator(self.settings.session_dir)
        self.deferral_manager = DeferralManager(self.settings)
        self.task_router = TaskRouter(config=self.settings)
        self.team_coordinator = TeamCoordinator(self.settings.session_dir)
        self.backlog_manager = BacklogManager(self.settings.session_dir)
        # TeammateManager expects a file path, create if needed
        # TeammateManager expects a file path for storage
        # It creates AgentHierarchyManager with storage_path / "hierarchy"
        # So we need to ensure storage_path is a file, not a directory
        teammates_file = self.settings.session_dir / "teammates.json"
        # Ensure parent directory exists
        teammates_file.parent.mkdir(parents=True, exist_ok=True)
        # Create empty file if it doesn't exist
        if not teammates_file.exists():
            teammates_file.write_text("{}")
        # Pass file path - TeammateManager will create hierarchy subdirectory
        # But first ensure the hierarchy parent directory exists
        hierarchy_dir = teammates_file.parent / "teammates_hierarchy"
        hierarchy_dir.mkdir(parents=True, exist_ok=True)
        # Create a custom hierarchy manager with proper directory
        hierarchy_mgr = AgentHierarchyManager(hierarchy_dir)
        self.teammate_manager = TeammateManager(teammates_file, hierarchy_manager=hierarchy_mgr)
        self.override_manager = OverrideManager(self.settings)
        self.process_registry = ProcessRegistry()
        self.subprocess_manager = SubprocessManager()
        self.rbac_manager = RBACManager()

        # Phase 0+ integrations
        self.memory_manager = MemoryManager(l1_size=1000, l2_dir=str(self.settings.session_dir / "cache" / "l2"))
        self.constitution_manager = ConstitutionManager(Path("CONSTITUTION.yaml"))
        self.reputation_manager = ReputationManager(db_path=self.db.db_path)
        self.sync_orchestrator = SyncOrchestrator(SyncRegistry())
        self.unified_config = UnifiedConfigManager()
        self.plan_integration = PlanSystemIntegration()
        self.alert_fatigue = AlertFatigueController(self.settings)
        self.analytics = AnalyticsIntegration(provider="plausible", site_id=self.settings.analytics_site_id)
        self.siem_egress = SIEMEgress(endpoint_url=self.settings.siem_endpoint_url)
        self._background_tasks: set[Any] = set()

        # Start event watcher
        self.event_watcher.start()

        _log.info("Auto-launch system initialized")

    def record_event(
        self,
        event_type: str,
        session_id: str | None = None,
        item_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Record an auto-launch event in the database.

        Args:
            event_type: Type of event
            session_id: Associated session ID
            item_id: Associated workstream item ID
            payload: Optional event payload
        """
        import json

        evidence_hash = self.evidence_ledger.record(
            event_type=f"auto_launch_{event_type}",
            cycle_id=f"auto-launch-{datetime.now(UTC).isoformat()}",
            payload={
                "event_type": event_type,
                "session_id": session_id,
                "item_id": item_id,
                "payload": payload,
            },
        )

        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO auto_launch_events
            (event_type, session_id, item_id, timestamp, payload, evidence_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_type,
                session_id,
                item_id,
                datetime.now(UTC).isoformat(),
                json.dumps(payload).decode() if payload else None,
                evidence_hash,
            ),
        )
        conn.commit()
        conn.close()

    def handle_completion(self, session_id: str, exit_code: int) -> None:
        """Handle session completion event.

        Args:
            session_id: Completed session ID
            exit_code: Session exit code
        """
        _log.info(f"Session {session_id} completed with exit code {exit_code}")

        # Record in evidence ledger
        self.evidence_ledger.record(
            event_type="auto_launch_completion",
            cycle_id=f"auto-launch-{datetime.now(UTC).isoformat()}",
            payload={"session_id": session_id, "exit_code": exit_code},
        )

        # Record auto-launch event
        self.record_event("session_completed", session_id=session_id, payload={"exit_code": exit_code})

        # Update database
        session = self.db.execute_query("SELECT * FROM sessions WHERE session_id = ? LIMIT 1", (session_id,))
        if session:
            self.db.mark_session_complete(session_id, exit_code)

            # Award XP for successful completion
            if exit_code == 0:
                self._award_xp(session[0])

            # Update workstream item status
            item_id = session[0].get("workstream_item_id")
            if item_id:
                # Mark as complete in WorkStreamManager (updates markdown)
                try:
                    self.workstream_manager.complete(item_id, "auto-launch")
                except Exception as e:
                    _log.warning(f"Failed to complete {item_id} in WorkStreamManager: {e}")

                # Update status in DB workstream_items table
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                now_iso = datetime.now(UTC).isoformat()
                cursor.execute(
                    "UPDATE workstream_items SET status = 'completed', completed_at = ? WHERE item_id = ?",
                    (now_iso, item_id),
                )
                # Update dependencies table
                cursor.execute(
                    "UPDATE dependencies SET satisfied_at = ? WHERE depends_on_item_id = ?", (now_iso, item_id)
                )
                conn.commit()
                conn.close()

            # Update cost tracking
            s = session[0]
            if s.get("model"):
                cost = self.cost_estimator.estimate(
                    model=s["model"],
                    tokens_total=s.get("tokens_total", 0),
                )
                self.db.record_cost(session_id, cost, tokens_total=s.get("tokens_total", 0), model=s.get("model"))
                _log.debug(f"Recorded cost for {session_id}: ${cost:.4f}")

        # Check team coordination
        if session and session[0].get("team_id"):
            self.team_coordinator.handle_task_completed(
                session[0]["team_id"],
                session[0].get("task_id", session_id),
                f"Exit code: {exit_code}",
            )

        # Emit SIEM event
        self.siem_egress.push_event(
            EgressEvent(
                id=f"completion-{session_id}",
                severity="low" if exit_code == 0 else "medium",
                event_type="session_completed",
                source="auto-launch-system",
                payload={
                    "session_id": session_id,
                    "exit_code": exit_code,
                    "item_id": session[0].get("workstream_item_id") if session else None,
                },
            )
        )

        # Track analytics
        self.analytics.track_page_view(f"/session/complete/{session_id}")

        # Handle failure retry
        if exit_code != 0 and session:
            item_id = session[0].get("workstream_item_id")
            if item_id:
                _log.warning(f"Session {session_id} for {item_id} failed with code {exit_code}")
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE workstream_items SET status = 'failed', retry_count = retry_count + 1, last_error = ? WHERE item_id = ?",
                    (f"Exit code {exit_code}", item_id),
                )
                conn.commit()
                conn.close()

        # Sync database with markdown before checking for next items
        self.sync_database()

        # Send notification

        try:
            shim_run(
                [
                    "bash",
                    "hooks/notify-agent-event.sh",
                    "--event",
                    "sessionend",
                    "--title",
                    f"Session {session_id} Complete",
                    "--message",
                    f"Exit code: {exit_code}",
                    "--severity",
                    "info" if exit_code == 0 else "error",
                ],
                check=False,
            )
        except Exception as e:
            _log.warning(f"Failed to send notification for {session_id}: {e}")

        # Get next items and launch if capacity available
        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            task = loop.create_task(self._try_launch_next())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        else:
            loop.run_until_complete(self._try_launch_next())

    def sync_database(self) -> None:
        """Sync workstream database with WORK_STREAM.md."""
        try:
            from thegent_cli.cli.commands.impl import _parse_work_stream_md

            work_stream_path = Path("docs/reference/WORK_STREAM.md")
            if work_stream_path.exists():
                data = _parse_work_stream_md(work_stream_path)
                self.db.sync_workstream(data)
                _log.debug("Workstream database synced with markdown")
        except Exception as e:
            _log.error(f"Failed to sync workstream database: {e}")

    async def _try_launch_next(self) -> None:
        """Try to launch next workstream items if capacity available."""
        # Use database-backed dependency resolution
        ready_items = self.db.get_ready_items()
        if not ready_items:
            return

        # Check dynamic limit
        current_running = self.db.get_running_count()
        snapshot = sample_resources()
        dynamic_limit, _ = compute_dynamic_limit(snapshot)
        available = dynamic_limit - current_running

        if available <= 0:
            return

        # Filter and launch items
        items_to_launch = ready_items[:available]
        await self.launch_batch(items_to_launch, role=Role.OPERATOR)

    async def launch_batch(self, items: list[dict[str, Any]], role: Role = Role.OPERATOR) -> None:
        """Launch batch of items with lane-aware routing, RBAC, and resource management.

        Args:
            items: List of workstream items to launch
            role: RBAC role for permission checking
        """
        # Check RBAC permissions
        if not self.rbac_manager.has_permission(role, Permission.RUN_AGENT):
            _log.warning(f"Role {role} lacks RUN_AGENT permission, skipping launch")
            return

        # Check for active overrides
        override = self.override_manager.get_override("auto_launch_limit")
        if override and override.is_active():
            _log.info(f"Auto-launch limit override active: {override.reason}")

        # Check alert fatigue
        if self.alert_fatigue.record_alert(InterruptionKind.POLICY_DENY):
            _log.warning("Alert fatigue threshold reached, suppressing auto-launch")
            return

        # Check memory cache for recent launch decisions
        cache_key = f"auto_launch_batch_{hash(tuple((i.get('item_id') or i.get('id')) for i in items))}"
        cached = await self.memory_manager.get_knowledge(cache_key)
        if cached:
            _log.debug("Using cached launch decision for batch")
            return

        # Sort by lane priority and group by source
        sorted_items = self.lane_model.sort_tasks(items)
        sorted_items.sort(key=lambda x: (x.get("priority", "P2"), x.get("source", "")))

        # Check dynamic limit
        current_running = self.db.get_running_count()
        snapshot = sample_resources()
        dynamic_limit, _ = compute_dynamic_limit(snapshot)
        load_level = current_running / dynamic_limit if dynamic_limit > 0 else 0.0

        # Sync components before launch if needed
        try:
            import asyncio

            asyncio.get_event_loop().run_until_complete(self.sync_orchestrator.sync_all())
        except Exception as e:
            _log.warning(f"Component sync failed before launch: {e}")

        for item in sorted_items:
            # item_id normalized from DB or workstream
            item_id = item.get("item_id") or item.get("id")
            if not item_id:
                continue

            if len([i for i in items if (i.get("item_id") or i.get("id")) == item_id]) == 0:
                continue

            priority = item.get("priority", "P2")
            lane = self._determine_lane(item)

            # Check deferral
            if self.deferral_manager.should_defer(priority, load_level):
                self.deferral_manager.defer_task(
                    item_id,
                    f"High load ({load_level:.1%}), priority {priority}",
                )
                continue

            # Check lane capacity
            lane_counts = self.db.get_running_count_by_lane()
            if not self.lane_model.check_capacity(lane, lane_counts.get(lane, 0), dynamic_limit):
                continue

            # Constitutional AI critique
            action = {"prompt": item.get("prompt", ""), "item_id": item_id}
            violations = self.constitution_manager.critique_action(action)
            if violations:
                _log.warning(f"Constitutional violations detected for {item_id}: {[v.reason for v in violations]}")
                # Record violation in DB and backlog
                for violation in violations:
                    self.db.record_constitutional_violation(item_id, None, violation)
                    self.backlog_manager.add(
                        finding_id=f"constitutional-{item_id}",
                        dimension="safety",
                        severity=0.8,
                        description=f"{violation.reason}. Remediation: {violation.remediation}",
                    )
                continue

            # Route task to optimal model
            metadata = self.task_router.classify(item.get("prompt", ""))
            category = metadata.category
            fallbacks = self.task_router.get_fallback_chain(category)
            model = fallbacks[0] if fallbacks else "gemini-3-flash"

            # Check agent reputation
            trust_score = self.reputation_manager.get_trust_score(model)
            if trust_score < 0.3:
                _log.warning(f"Low trust score ({trust_score:.2f}) for model {model}, skipping")
                continue

            # Estimate cost
            estimated_cost = self.cost_estimator.estimate(model=model, prompt_length=len(item.get("prompt", "")))

            # Check if should delegate to teammate
            if self._should_delegate_to_teammate(item):
                teammate = self._select_teammate(str(category))
                if teammate:
                    try:
                        self.teammate_manager.delegate(
                            teammate_id=teammate.id, parent_run_id="auto-launch", prompt=item.get("prompt", "")
                        )
                        _log.info(f"Delegated {item_id} to teammate {teammate.id}")
                        continue
                    except Exception as e:
                        _log.warning(f"Teammate delegation failed for {item_id}: {e}")

            # Launch item
            await self._launch_item(item, lane, model, estimated_cost)

            # Emit SIEM event
            from thegent_observability.observability.egress import EgressEvent

            self.siem_egress.push_event(
                EgressEvent(
                    id=f"launch-{item_id}",
                    severity="low",
                    event_type="auto_launch_started",
                    source="auto-launch-system",
                    payload={
                        "item_id": item_id,
                        "lane": lane,
                        "model": model,
                        "estimated_cost": estimated_cost,
                        "trust_score": trust_score,
                    },
                )
            )

            # Track analytics
            self.analytics.track_page_view(f"/auto-launch/{item_id}")

        # Cache launch decision
        await self.memory_manager.store_knowledge(
            cache_key, {"launched": True, "timestamp": datetime.now(UTC).isoformat()}
        )

    def _determine_lane(self, item: dict[str, Any]) -> str:
        """Determine lane for item based on priority and context.

        Args:
            item: Workstream item dict

        Returns:
            Lane name (critical, standard, recovery, background)
        """
        priority = item.get("priority", "P2")
        if priority == "P0":
            return Lane.CRITICAL
        if priority == "P1":
            return Lane.STANDARD
        if item.get("source") == "gardening":
            return Lane.RECOVERY
        return Lane.BACKGROUND

    async def _launch_item(self, item: dict[str, Any], lane: str, model: str, estimated_cost: float) -> None:
        """Launch a single workstream item."""
        # Claim item first
        item_id = item.get("item_id") or item.get("id")
        if not item_id:
            return

        agent_id = "auto-launch"
        from thegent_cli.cli.commands.impl import work_stream_claim_impl

        claim_result = work_stream_claim_impl(item_id, agent_id, cd=Path.cwd())
        if not claim_result.get("success", False):
            payload = {
                "surface": "auto_launch.claim_start",
                "item_id": item_id,
                "governance_blocked": bool(claim_result.get("governance_blocked")),
                "remediation": claim_result.get("remediation"),
                "governance_block": claim_result.get("governance_block"),
                "error": claim_result.get("error"),
            }
            self.record_event("claim_failed", item_id=item_id, payload=payload)
            _log.warning("Auto-launch claim blocked for %s: %s", item_id, claim_result.get("error", "claim failed"))
            return

        # Use bg_impl directly for the specific item
        from thegent_cli.cli.commands.impl import bg_impl

        prompt = item.get("prompt_suggestion") or item.get("prompt") or item.get("title", item_id)

        # Use gpt-4o-mini as default for auto-launch if model not specified
        launch_model = model or "gpt-4o-mini"

        result = bg_impl(
            agent=None,  # Will be resolved from model
            model=launch_model,
            prompt=prompt,
            cd=Path.cwd(),
            mode="write",
            timeout=self.settings.default_timeout,
            full=False,
            owner=self.settings.owner_tag,
            lane=lane,
            override_reason="auto-launch",
            task_id=item_id,
        )

        # Record launch in database
        if result.get("session_id") and result.get("session_id") != "failed":
            session_id = result["session_id"]
            self.db.record_launch(
                item_id=item_id,
                session_id=session_id,
                lane=lane,
                model=launch_model,
                estimated_cost=estimated_cost,
                trigger_type="auto_launch",
            )

            # Record session in database
            self.db.record_session(
                session_id=session_id,
                agent=launch_model,
                prompt=prompt,
                status="running",
                workstream_item_id=item_id,
                lane=lane,
                model=launch_model,
                owner_tag=self.settings.owner_tag,
            )

            # Update last_attempted_at in workstream_items
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE workstream_items SET last_attempted_at = ?, status = 'running' WHERE item_id = ?",
                (datetime.now(UTC).isoformat(), item_id),
            )
            conn.commit()
            conn.close()

            _log.info(
                f"Launched {item_id} as {session_id} via {launch_model} (lane: {lane}, cost: ${estimated_cost:.4f})"
            )

            # Record auto-launch event
            self.record_event(
                "item_launched",
                item_id=item_id,
                session_id=session_id,
                payload={"lane": lane, "model": launch_model, "estimated_cost": estimated_cost},
            )

    def _should_delegate_to_teammate(self, item: dict[str, Any]) -> bool:
        """Decide if an item should be delegated to a teammate."""
        tags = item.get("tags")
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except json.JSONDecodeError:
                tags = []
        elif tags is None:
            tags = []

        # Policy: delegate if explicitly requested or if it's a specific category
        if "delegate" in tags:
            return True

        # Or if it's a high-complexity task (heuristic)
        if len(item.get("prompt", "")) > 1000:
            return True

        return False

    def _select_teammate(self, category: str) -> Any | None:
        """Select the best teammate for a category."""
        try:
            personas = self.teammate_manager.list_personas()
            # Filter by capability if teammate manager supports it
            # For now, just pick the first available or matching
            for t in personas:
                if category in t.capabilities:
                    return t

            # Fallback to any teammate
            if personas:
                return personas[0]
        except Exception as e:
            _log.error(f"Error selecting teammate: {e}")

        return None

    async def run_gardening_cycle(self) -> None:
        """Run a gardening cycle to identify and queue maintenance tasks."""
        _log.info("Starting gardening cycle")

        # 1. Scan for backlog items from BacklogManager
        pending_backlog = self.backlog_manager.get_pending()
        for item in pending_backlog:
            # Check if already in workstream
            existing = self.db.execute_query(
                "SELECT item_id FROM workstream_items WHERE item_id = ? OR title LIKE ?",
                (f"garden-{item.item_id}", f"%{item.finding_id}%"),
            )
            if not existing:
                # Add to workstream
                item_id = f"garden-{item.item_id}"
                self.db.execute_query(
                    """
                    INSERT INTO workstream_items (item_id, title, source, priority, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item_id,
                        f"Gardening: {item.description[:50]}...",
                        "gardening",
                        "P2" if item.severity < 0.7 else "P1",
                        "pending",
                        datetime.now(UTC).isoformat(),
                    ),
                )
                _log.info(f"Queued gardening task {item_id}")

        # 2. Check for stalled items
        stalled_limit = datetime.now(UTC).timestamp() - 3600  # 1 hour
        stalled_items = self.db.execute_query(
            "SELECT item_id FROM workstream_items WHERE status = 'running' AND last_attempted_at < ?",
            (datetime.fromtimestamp(stalled_limit, UTC).isoformat(),),
        )
        for item in stalled_items:
            _log.warning(f"Item {item['item_id']} stalled, resetting to failed for retry")
            self.db.execute_query(
                "UPDATE workstream_items SET status = 'failed', last_error = 'stalled' WHERE item_id = ?",
                (item["item_id"],),
            )

        # 3. Clean up old costs and logs
        # Implementation...

    def start(self) -> None:
        """Start the auto-launch system."""
        # Initial sync with markdown
        work_stream_path = Path("docs/reference/WORK_STREAM.md")
        try:
            self.db.sync_with_markdown(work_stream_path)
            _log.info(f"Initial sync with {work_stream_path} completed")
        except Exception as e:
            _log.warning(f"Initial sync failed: {e}")

        # Start periodic sync and gardening tasks
        import threading

        def periodic_tasks():
            import asyncio
            import time

            count = 0
            while True:
                time.sleep(60)  # Check every minute
                count += 1

                # Sync every 5 minutes
                if count % 5 == 0:
                    try:
                        self.db.sync_with_markdown(work_stream_path)
                        _log.debug("Periodic sync completed")
                    except Exception as e:
                        _log.warning(f"Periodic sync failed: {e}")

                # Garden every 30 minutes
                if count % 30 == 0:
                    try:
                        # Use a new event loop or the current one if it exists
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            task = loop.create_task(self.run_gardening_cycle())
                            self._background_tasks.add(task)
                            task.add_done_callback(self._background_tasks.discard)
                        else:
                            loop.run_until_complete(self.run_gardening_cycle())
                        _log.debug("Periodic gardening completed")
                    except Exception as e:
                        _log.warning(f"Periodic gardening failed: {e}")

        self.worker_thread = threading.Thread(target=periodic_tasks, daemon=True)
        self.worker_thread.start()

        self.event_watcher.start()
        _log.info("Auto-launch system started")

    def stop(self) -> None:
        """Stop the auto-launch system."""
        self.event_watcher.stop()
        _log.info("Auto-launch system stopped")

    def _award_xp(self, session: dict[str, Any]) -> None:
        """Award XP for a successful session completion."""

        agent = session.get("agent", "unknown")
        item_id = session.get("workstream_item_id", "unknown")

        # Determine XP based on lane and priority
        lane = session.get("lane", "standard")
        xp_amount = {"critical": 50, "standard": 20, "recovery": 30, "background": 10}.get(lane, 20)

        _log.info(f"Awarding {xp_amount} XP to {agent} for {item_id}")

        try:
            shim_run(
                [
                    "bash",
                    "hooks/gardener-xp.sh",
                    "--agent",
                    agent,
                    "--amount",
                    str(xp_amount),
                    "--reason",
                    f"auto-launch-complete:{item_id}",
                ],
                check=False,
            )
        except Exception as e:
            _log.warning(f"Failed to award XP: {e}")
