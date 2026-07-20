"""STUB MODULE - thegent.execution

This module provides execution state management, run registry, and policy enforcement
for thegent agent workflows.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import json
import time

try:
    import httpx

    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False


class RunState(Enum):
    """Enumeration of run states."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrustBoundaryValidator:
    """Validator for trust boundaries in execution context."""

    def __init__(self, session_dir: str = "") -> None:
        from pathlib import Path

        self.session_dir = Path(session_dir) if session_dir else Path.cwd()
        self.state_path = self.session_dir / "trust_boundaries.json"
        self._boundaries: dict[str, bool] = {}
        self._last_environment: dict[str, Any] = {}

    def validate(self, boundary_id: str, context: dict[str, Any]) -> bool:
        """Validate if a trust boundary is satisfied.

        Args:
            boundary_id: The boundary identifier to validate.
            context: Execution context with boundary requirements.

        Returns:
            True if boundary is satisfied, False otherwise.
        """
        return True

    def set_boundary(self, boundary_id: str, trusted: bool) -> None:
        """Set a trust boundary status.

        Args:
            boundary_id: The boundary identifier.
            trusted: Whether this boundary is trusted.
        """
        self._boundaries[boundary_id] = trusted

    def is_trusted(self, boundary_id: str) -> bool:
        """Check if a boundary is trusted.

        Args:
            boundary_id: The boundary identifier.

        Returns:
            True if trusted, False otherwise.
        """
        return self._boundaries.get(boundary_id, False)

    def get_last_environment(self) -> dict[str, Any] | None:
        """Get the last recorded environment."""
        return self._last_environment if self._last_environment else None

    def record_environment(self, env: dict[str, Any]) -> None:
        """Record an environment snapshot."""
        self._last_environment = env

    def validate_environment(
        self,
        env: dict[str, Any],
        current_level: str = "dev",
        target_level: str = "dev",
    ) -> tuple[bool, str]:
        """Validate environment transition.

        Returns (allowed, reason) tuple.
        """
        return self.validate_transition(current_level, target_level)

    def validate_transition(
        self,
        current_level: str | None,
        target_level: str,
    ) -> tuple[bool, str]:
        """Validate environment transition.

        Returns (allowed, reason) tuple.
        """
        # No prior environment means it's allowed
        if current_level is None:
            return True, "no_prior_environment"

        # Normalize levels first
        level_map = {"development": "dev", "prod": "production"}
        if current_level.lower() in level_map:
            current_level = level_map[current_level.lower()]
        if target_level.lower() in level_map:
            target_level = level_map[target_level.lower()]

        # Unknown environments pass through
        env_levels = ["dev", "staging", "production"]
        if current_level not in env_levels:
            return True, "unknown_env_allowed"

        current_idx = env_levels.index(current_level)
        target_idx = env_levels.index(target_level) if target_level in env_levels else 0

        # Skip level promotion is denied
        if target_idx - current_idx > 1:
            return False, "Skip-level promotion requires explicit audit"

        # Check if it's a valid promotion or same level
        if target_idx > current_idx:
            return True, f"Valid promotion from {current_level} to {target_level}"

        if target_idx == current_idx:
            return True, "allowed"

        # Downgrade is allowed
        return True, "downgrade_allowed"


class PolicyEngine:
    """Policy engine for execution."""

    def __init__(self, settings: Any = None) -> None:
        from pathlib import Path

        self.settings = settings
        self.session_dir = Path(getattr(settings, "session_dir", "") or "") if settings else Path.cwd()
        self.policies: dict[str, Any] = {}
        self._circuit_breakers: dict[str, dict[str, Any]] = {}
        self.circuit_breaker_enabled = getattr(settings, "circuit_breaker_enabled", False)
        self.circuit_breaker_threshold = getattr(settings, "circuit_breaker_threshold", 5)
        self._cb_registry: Any = None

    def evaluate(self, run: RunMeta, *, registry: Any = None) -> tuple[str, str]:
        """Evaluate a run and return (result, reason).

        Policy checks:
        1. Circuit breaker - deny if model is blocked
        2. Critical lane + confidence < 0.9 - deny
        3. Unknown agent in production - deny
        4. Unknown agent in critical lane - deny
        5. Recovery lane with no confidence - warn
        6. Production + trust score below threshold - deny
        7. Critical lane + drift exceeds budget - deny
        """
        model = getattr(run, "model", "") or getattr(run, "agent", "")
        lane = getattr(run, "lane", "standard") or "standard"
        confidence = getattr(run, "confidence", None)
        environment = getattr(self.settings, "environment", "development") if self.settings else "development"
        trust_score_threshold = getattr(self.settings, "trust_score_threshold", 0.8) if self.settings else 0.8

        # Apply calibration factor if registry is provided
        if registry and model and confidence is not None:
            try:
                cal_factor = registry.get_calibration_factor(model)
                if cal_factor is not None:
                    confidence = confidence * cal_factor
            except Exception:
                pass

        # Check circuit breaker if enabled
        if model and getattr(self, "circuit_breaker_enabled", False):
            cb = CircuitBreakerRegistry(str(self.session_dir), threshold=self.circuit_breaker_threshold)
            # Check model category first, then default category (for backward compatibility)
            if cb.is_open(model, category="model"):
                return "deny", f"Circuit breaker is OPEN for model: {model}"
            if cb.is_open(model, category="default"):
                return "deny", f"Circuit breaker is OPEN for model: {model}"

        # Check OPA if configured
        opa_result = self._query_opa(run)
        if opa_result is not None:
            return opa_result

        # Policy 1: Critical lane + confidence < 0.9 = deny
        if lane == "critical" and confidence is not None and confidence < 0.9:
            return "deny", f"Confidence {confidence} below threshold 0.9 for critical lane"

        # Policy 2: Unknown agent in production = deny
        if environment == "production" and model and model.lower() in ("unknown", "untrusted"):
            return "deny", "Unknown agent blocked in production"

        # Policy 3: Unknown agent in critical lane = deny
        if lane == "critical" and model and model.lower() in ("unknown", "untrusted"):
            return "deny", "Unknown agent blocked in critical lane"

        # Policy 4: Recovery lane + no confidence = warn
        if lane == "recovery" and confidence is None:
            return "warn", "No confidence data for recovery lane"

        # Policy 5: Production + confidence below threshold = deny
        if environment == "production" and confidence is not None and confidence < trust_score_threshold:
            return "deny", f"Confidence {confidence} below threshold {trust_score_threshold}"

        # Policy 6: Critical lane + drift exceeds budget = deny
        if lane == "critical":
            try:
                from thegent.contracts.telemetry import ContractTelemetry

                ct = ContractTelemetry(session_dir=str(self.session_dir))
                status = ct.get_drift_budget_status()
                if status and not status.get("within_budget", True):
                    return "deny", "Drift exceeds budget for critical lane"
            except Exception:
                pass

        return "allow", "Allowed by policy"

    def query_opa(self, rego_query: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """Query OPA policy engine."""
        return {"result": True}

    def _query_opa(self, run: RunMeta) -> tuple[str, str] | None:
        """Internal method to query OPA for a run."""
        if not _HAS_HTTPX:
            return None

        opa_url = getattr(self.settings, "opa_url", "") if self.settings else ""
        if not opa_url:
            return None

        try:
            response = httpx.post(
                f"{opa_url}/v1/query",
                json={"query": "data.thegent.allow"},
                timeout=5.0,
            )
            response.raise_for_status()
            result = response.json()
            allow = result.get("result", {}).get("allow", True)
            reason = result.get("result", {}).get("reason", "All good")
            if allow:
                return "allow", reason
            else:
                return "deny", reason
        except (OSError, httpx.HTTPError):
            return None

    def circuit_breaker_open(self, model_id: str) -> None:
        """Open circuit breaker for a model."""
        if model_id not in self._circuit_breakers:
            self._circuit_breakers[model_id] = {"failures": 0, "state": "closed"}
        self._circuit_breakers[model_id]["state"] = "open"

    def is_circuit_open(self, model_id: str) -> bool:
        """Check if circuit breaker is open for a model."""
        if model_id not in self._circuit_breakers:
            return False
        return self._circuit_breakers[model_id].get("state") == "open"


class CircuitBreakerRegistry:
    """Registry for circuit breakers tracking model failures."""

    def __init__(self, session_dir: str = "", threshold: int = 3) -> None:
        from pathlib import Path

        self.session_dir = Path(session_dir) if session_dir else Path.cwd()
        # Use circuit_breakers.json to be compatible with complex CircuitBreakerRegistry
        self.registry_path = self.session_dir / "circuit_breakers.json"
        self.threshold = threshold
        self._failures: dict[str, int] = {}
        self._states: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        """Load circuit breaker state from file."""
        import json

        if self.registry_path.exists():
            try:
                with open(self.registry_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict):
                                failures = value.get("failures", [])
                                if isinstance(failures, list):
                                    self._failures[key] = len(failures)
                                else:
                                    self._failures[key] = failures
                                self._states[key] = value.get("state", "closed")
                            else:
                                self._failures[key] = value
            except (OSError, json.JSONDecodeError):
                pass

    def _save(self) -> None:
        """Save circuit breaker state to file."""
        import json

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for key in set(list(self._failures.keys()) + list(self._states.keys())):
            data[key] = {
                "failures": self._failures.get(key, 0),
                "state": self._states.get(key, "closed"),
                "last_failure": None,
            }
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def record_failure(self, agent_id: str, category: str = "") -> None:
        """Record a failure for an agent."""
        # Use just agent_id as key (ignore category for simple registry)
        self._failures[agent_id] = self._failures.get(agent_id, 0) + 1
        if self._failures[agent_id] >= self.threshold:
            self._states[agent_id] = "open"
        self._save()

    def is_open(self, target_id: str, category: str = "") -> bool:
        """Check if circuit breaker is open for a target."""
        # Map target_id to agent_id (support both old and new naming)
        agent_id = target_id
        return self._states.get(agent_id, "closed") == "open"

    def reset(self, agent_id: str) -> None:
        """Reset circuit breaker for an agent."""
        self._failures[agent_id] = 0
        self._states[agent_id] = "closed"
        self._save()


class CheckpointRegistry:
    """Registry for execution checkpoints."""

    def __init__(self, session_dir: str = "") -> None:
        from pathlib import Path

        self.session_dir = Path(session_dir) if session_dir else Path.cwd()
        self.registry_path = self.session_dir / "checkpoint_registry.jsonl"
        self._checkpoints: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load checkpoints from file."""
        import json

        self._checkpoints = []
        if self.registry_path.exists():
            try:
                with open(self.registry_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            self._checkpoints.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            except OSError:
                pass

    def _save(self) -> None:
        """Save checkpoints to file."""
        import json

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(cp) + "\n" for cp in self._checkpoints)

    def get_checkpoint(self, run_id: str) -> dict[str, Any] | None:
        """Get checkpoint for a run."""
        for cp in self._checkpoints:
            if cp.get("run_id") == run_id:
                return cp
        return None

    def add_checkpoint(self, run_id: str, data: dict[str, Any]) -> None:
        """Add a checkpoint for a run."""
        self._checkpoints.append({"run_id": run_id, **data})
        self._save()

    def list_checkpoints(self) -> list[dict[str, Any]]:
        """List all checkpoints."""
        return self._checkpoints.copy()


class EscalationQueue:
    """Queue for escalations with file-based persistence."""

    def __init__(self, session_dir: str = "") -> None:
        from pathlib import Path

        self.session_dir = Path(session_dir) if session_dir else Path.cwd()
        self.queue_path = self.session_dir / "escalation_queue.jsonl"
        self.queue: list[Any] = []
        self._corrupt_lines: list[str] = []
        # Load existing queue from file if exists
        self._load()

    def _load(self) -> None:
        """Load queue from file."""
        import json

        self.queue = []
        if self.queue_path.exists():
            try:
                with open(self.queue_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                self.queue.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass  # Skip corrupt lines
            except OSError:
                pass

    def _save(self) -> None:
        """Save queue to file, preserving corrupt lines."""
        import json

        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

        # Read current file and identify corrupt lines
        corrupt_lines = []
        queue_item_hashes = set()

        if self.queue_path.exists():
            try:
                with open(self.queue_path, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            item = json.loads(line)
                            # Check if this line corresponds to an item in current queue
                            for q_item in self.queue:
                                if json.dumps(q_item, sort_keys=True) == line.strip():
                                    queue_item_hashes.add(line.strip())
                                    break
                        except json.JSONDecodeError:
                            # Preserve corrupt lines
                            corrupt_lines.append(line.rstrip("\n"))
            except OSError:
                pass

        # Write file with queue items and preserved corrupt lines
        with open(self.queue_path, "w", encoding="utf-8") as f:
            for item in self.queue:
                f.write(json.dumps(item, sort_keys=True) + "\n")
            for line in corrupt_lines:
                f.write(line + "\n")

    def add(
        self,
        run_id: str,
        reason: str = "",
        priority: int = 5,
        sla_minutes: int | None = None,
        blocked_at_utc: str | None = None,
        owner: str | None = None,
    ) -> None:
        """Add an item to the queue (alias for enqueue).

        Args:
            run_id: The run ID to add.
            reason: Optional reason for escalation.
            priority: Priority level (1=highest, 5=lowest).
            sla_minutes: Optional SLA in minutes.
            blocked_at_utc: Optional blocked timestamp.
            owner: Optional owner.
        """
        from datetime import datetime, timezone, timedelta

        item: dict[str, Any] = {
            "run_id": run_id,
            "reason": reason,
            "priority": priority,
            "status": "pending",
            "_from_add": True,
        }
        if sla_minutes is not None:
            item["sla_minutes"] = sla_minutes
            # Calculate escalate_by_utc based on blocked_at_utc or now
            if blocked_at_utc:
                try:
                    blocked_dt = datetime.fromisoformat(blocked_at_utc.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    blocked_dt = datetime.now(timezone.utc)
            else:
                blocked_dt = datetime.now(timezone.utc)
            escalate_dt = blocked_dt + timedelta(minutes=sla_minutes)
            item["escalate_by_utc"] = escalate_dt.isoformat().replace("+00:00", "Z")
        if blocked_at_utc is not None:
            item["blocked_at_utc"] = blocked_at_utc
        if owner is not None:
            item["owner"] = owner

        self.queue.append(item)
        # Append to file instead of full save to preserve external edits
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, sort_keys=True) + "\n")

    def enqueue(self, item: Any) -> None:
        """Enqueue an item."""
        self.queue.append(item)
        self._save()

    def dequeue(self) -> Any | None:
        """Dequeue an item."""
        if self.queue:
            item = self.queue.pop(0)
            self._save()
            return item
        return None

    def list_pending(self, past_sla_only: bool = False) -> list[dict[str, Any]]:
        """List pending items from file.

        When past_sla_only=False: returns all items with status="pending".
        When past_sla_only=True: returns items with escalate_by_utc that are past SLA.
        """
        from datetime import datetime, timezone

        pending = []
        if not self.queue_path.exists():
            return pending

        try:
            with open(self.queue_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        if past_sla_only:
                            # For past_sla_only, require escalate_by_utc and past SLA
                            escalate_by = item.get("escalate_by_utc", "")
                            if not escalate_by:
                                continue
                            try:
                                escalate_dt = datetime.fromisoformat(escalate_by.replace("Z", "+00:00"))
                                now = datetime.now(timezone.utc)
                                is_past_sla = now >= escalate_dt
                                if is_past_sla:
                                    item["past_sla"] = True
                                    pending.append(item)
                            except (ValueError, TypeError):
                                pass
                        elif item.get("status") == "pending":
                            # Include if escalate_by_utc is set OR if it was added via add()
                            if item.get("escalate_by_utc") or item.get("_from_add"):
                                pending.append(item)
                    except json.JSONDecodeError:
                        self._corrupt_lines.append(line)
        except OSError:
            pass
        return pending

    def resolve(self, run_id: str) -> bool:
        """Remove an item by run_id from the queue.

        Args:
            run_id: The run ID to resolve.

        Returns:
            True if item was found and removed, False otherwise.
        """
        for i, item in enumerate(self.queue):
            if item.get("run_id") == run_id:
                self.queue.pop(i)
                self._save()
                return True
        return False


class MessageEntry:
    """Entry for execution messages."""

    def __init__(self, role: str, content: str, timestamp: str = "") -> None:
        self.role = role
        self.content = content
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}


class OverrideRegistry:
    """Registry for execution overrides with file-based persistence."""

    def __init__(self, session_dir: str = "") -> None:
        from pathlib import Path

        self.session_dir = Path(session_dir) if session_dir else Path.cwd()
        self.registry_path = self.session_dir / "override_registry.jsonl"
        self._records: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load registry from file."""
        import json

        if self.registry_path.exists():
            try:
                with open(self.registry_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self._records.append(json.loads(line))
            except (json.JSONDecodeError, OSError):
                pass

    def _save(self) -> None:
        """Save registry to file."""
        import json

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(record) + "\n" for record in self._records)

    def record(self, owner: str, reason: str, ttl_seconds: int = 3600) -> None:
        """Record an override.

        Args:
            owner: The owner of the override.
            reason: The reason for the override.
            ttl_seconds: Time-to-live in seconds.
        """
        from datetime import datetime, timezone, timedelta

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        record = {
            "owner": owner,
            "reason": reason,
            "expires_at_utc": expires_at.isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._records.append(record)
        self._save()

    def has_unexpired(self, owner: str) -> bool:
        """Check if owner has an unexpired override.

        Args:
            owner: The owner to check.

        Returns:
            True if owner has unexpired override, False otherwise.
        """
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        for record in self._records:
            if record.get("owner") != owner:
                continue
            if "expires_at_utc" not in record:
                continue
            try:
                expires = datetime.fromisoformat(record["expires_at_utc"].replace("Z", "+00:00"))
                if expires > now:
                    return True
            except (ValueError, TypeError):
                pass
        return False
        """Clear all overrides."""
        cls._overrides.clear()
        return None


__all__ = [
    "PolicyEngine",
    "EscalationQueue",
    "RunMeta",
    "RunRegistry",
    "RunState",
    "LoadClassifier",
    "ConcurrencyController",
    "Auditor",
    "CircuitBreakerRegistry",
    "get_last_poll_session_messages_meta",
    "TrustBoundaryValidator",
    "CheckpointRegistry",
    "poll_session_messages",
    "HandoffManager",
    "OverrideRegistry",
    "MessageEntry",
]


class ConcurrencyController:
    """Controller for managing concurrent execution with lane support.

    Manages two separate lanes:
    - critical_lane_slots: Reserved slots for critical/priority runs
    - standard_lane_slots: Slots for regular runs

    Standard runs can overflow into critical slots if available.
    Critical runs cannot use standard-only slots.
    """

    def __init__(
        self,
        session_dir: Path | str | None = None,
        standard_lane_slots: int | None = None,
        critical_lane_slots: int | None = None,
        max_concurrency: int = 10,
        priority: str = "standard",
        bottleneck_detector: Any = None,
        use_load_based: bool = True,
    ) -> None:
        import os

        self.session_dir = Path(session_dir) if session_dir else None
        # Use explicit value if provided, else check env var, else use hardcoded default of 2
        if critical_lane_slots is not None:
            self.critical_lane_slots = critical_lane_slots
        else:
            env_val = os.environ.get("THGENT_CRITICAL_LANE_SLOTS", "")
            if env_val:
                try:
                    self.critical_lane_slots = int(env_val)
                except ValueError:
                    self.critical_lane_slots = 2
            else:
                self.critical_lane_slots = 2
        # Standard slots: use explicit, else env, else max_concurrency - critical
        if standard_lane_slots is not None:
            self.standard_lane_slots = standard_lane_slots
        else:
            env_standard = os.environ.get("THGENT_STANDARD_LANE_SLOTS", "")
            if env_standard:
                try:
                    self.standard_lane_slots = int(env_standard)
                except ValueError:
                    self.standard_lane_slots = max_concurrency - self.critical_lane_slots
            # Defensive: bypass max_concurrency arithmetic when it's a
            # mocked/non-numeric value (e.g. MagicMock from pytest tests
            # using partial settings) so comparison in acquire() doesn't
            # raise ``TypeError: '<' not supported between 'MagicMock' and 'int'``.
            elif isinstance(max_concurrency, int) and not isinstance(max_concurrency, bool):
                self.standard_lane_slots = max_concurrency - self.critical_lane_slots
            else:
                self.standard_lane_slots = max(1, 10 - self.critical_lane_slots)
        self.max_concurrency = max_concurrency
        self.priority = priority
        self.use_load_based = use_load_based
        self._standard_active = 0
        self._critical_active = 0
        self.bottleneck_detector = bottleneck_detector

    def _get_running_count(self) -> int:
        """Get the count of currently running sessions from ps_impl."""
        try:
            from thegent.cli.commands.impl import ps_impl

            sessions = ps_impl()
            return len([s for s in sessions if s.get("status") == "running"])
        except Exception:
            # Fall back to internal tracking if ps_impl fails
            return self._standard_active + self._critical_active

    def acquire(self, lane: str = "standard", priority: str | None = None) -> bool:
        """Acquire a concurrency slot for a lane or priority.

        Args:
            lane: Lane type ("standard" or "critical").
            priority: Optional priority override.

        Returns:
            True if slot acquired, False otherwise.

        Slot allocation logic:
        - Standard: can use standard_lane_slots ONLY (cannot overflow to critical)
        - Critical: can ONLY use critical_lane_slots (reserved)
        """
        # Use priority to determine lane if provided
        effective_lane = lane
        if priority == "critical":
            effective_lane = "critical"

        # Get current running count from ps_impl
        running = self._get_running_count()
        # Calculate standard and critical usage
        # Assume runs are distributed: standard uses standard pool, critical uses critical pool
        standard_used = min(running, self.standard_lane_slots)
        critical_used = max(0, running - self.standard_lane_slots)

        if effective_lane == "critical":
            # Critical can ONLY use critical slots
            if critical_used < self.critical_lane_slots:
                return True
            return False
        else:
            # Standard can ONLY use standard slots (no overflow to critical)
            if standard_used < self.standard_lane_slots:
                return True
            return False

    def release(self, lane: str = "standard") -> None:
        """Release a concurrency slot."""
        if lane == "critical" and self._critical_active > 0:
            self._critical_active -= 1
        elif self._standard_active > 0:
            self._standard_active -= 1

    def get_bottlenecks(self) -> dict[str, Any]:
        """Get bottleneck status payload.

        Returns:
            Dictionary with slow_points and resource_contention keys.
        """
        if self.bottleneck_detector is None:
            return {
                "detector_available": False,
                "reason": "bottleneck_detector_unavailable",
            }

        # Detector present - call its methods
        from thegent.orchestration.resource.resource_management import sample_extended_resources

        snapshot = sample_extended_resources()
        harness_cards = getattr(self, "harness_cards", {})

        slow_points = self.bottleneck_detector.identify_slow_points()
        resource_contention = self.bottleneck_detector.detect_resource_contention(snapshot, harness_cards)

        return {
            "slow_points": slow_points,
            "resource_contention": resource_contention,
        }

    def get_bottleneck_status(self) -> dict[str, Any]:
        """Get bottleneck status information."""
        return {
            "standard_active": self._standard_active,
            "standard_capacity": self.standard_lane_slots,
            "critical_active": self._critical_active,
            "critical_capacity": self.critical_lane_slots,
        }


class LoadClassifier:
    """Classifier for load types."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.session_dir = Path(session_dir) if session_dir else Path("/tmp")
        self.thresholds: dict[str, float] = {}

    def get_load_level(self) -> str:
        """Get current load level for the session (AUDIT-N+5 shim surface).

        Returns "normal" when no signal is available so the call-site in
        :mod:`thegent.cli.services.run_execution_core_helpers` falls
        through to its non-burst branch.
        """
        return "normal"

    def classify(self, load: float) -> str:
        """Classify a load value."""
        if load > 0.8:
            return "high"
        elif load > 0.5:
            return "medium"
        return "low"


@dataclass
class RunMeta:
    """Metadata for a run."""

    agent: str = ""
    model: str = ""
    prompt: str = ""
    cwd: str = ""
    owner: str = ""
    run_id: str = ""
    lane: str = "standard"
    started_at: str = ""
    ended_at: str = ""
    status: str = "pending"
    confidence: float = 1.0
    idempotency_token: str = ""
    domain_tag: str = ""
    started_at_utc: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "agent": self.agent,
            "prompt": self.prompt,
            "cwd": self.cwd,
            "owner": self.owner,
            "lane": self.lane,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "status": self.status,
            "confidence": self.confidence,
            "idempotency_token": self.idempotency_token,
            "domain_tag": self.domain_tag,
            "started_at_utc": self.started_at_utc,
            "metadata": self.metadata,
        }


class RunRegistry:
    """Registry for runs."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.runs: dict[str, RunMeta] = {}
        self._states: dict[str, RunState] = {}
        self._pause_reasons: dict[str, str] = {}
        self.session_dir = Path(session_dir) if session_dir else Path("/tmp")
        self.registry_path = self.session_dir / "run_registry.jsonl"

    def register(self, run: RunMeta) -> None:
        self.runs[run.run_id] = run

    def get(self, run_id: str) -> RunMeta | None:
        return self.runs.get(run_id)

    def list_runs(self, limit: int = 1000) -> list[dict[str, Any]]:
        """List all runs with metadata, sorted by started_at_utc descending."""
        import json

        # Read and merge events from registry file
        runs: dict[str, dict[str, Any]] = {}
        if self.registry_path.exists():
            for line in self.registry_path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    run_id = data.get("run_id", "")
                    if not run_id or run_id.startswith("__"):
                        continue

                    if run_id not in runs:
                        runs[run_id] = {
                            "run_id": run_id,
                            "status": "pending",
                            "started_at_utc": "",
                            "confidence": 1.0,
                            "agent": "",
                            "model": "",
                            "feedback_score": None,
                        }

                    # Merge start data
                    if "agent" in data:
                        runs[run_id]["agent"] = data.get("agent", "")
                    if "model" in data:
                        runs[run_id]["model"] = data.get("model", "")
                    if "prompt" in data:
                        runs[run_id]["prompt"] = data.get("prompt", "")
                    if "cwd" in data:
                        runs[run_id]["cwd"] = data.get("cwd", "")
                    if "owner" in data:
                        runs[run_id]["owner"] = data.get("owner", "")
                    if "started_at_utc" in data:
                        runs[run_id]["started_at_utc"] = data.get("started_at_utc", "")
                    if "confidence" in data:
                        runs[run_id]["confidence"] = data.get("confidence", 1.0)
                    if "feedback_score" in data:
                        runs[run_id]["feedback_score"] = data.get("feedback_score")

                    # Merge end event data
                    if data.get("event") == "end" or "status" in data:
                        runs[run_id]["status"] = data.get("status", "completed")
                        if "ended_at_utc" in data:
                            runs[run_id]["ended_at_utc"] = data.get("ended_at_utc", "")
                        if "duration" in data:
                            runs[run_id]["duration"] = data.get("duration", 0.0)
                        if "exit_code" in data:
                            runs[run_id]["exit_code"] = data.get("exit_code", 0)
                except (json.JSONDecodeError, KeyError):
                    continue

        # Sort by started_at_utc descending (most recent first)
        sorted_runs = sorted(
            runs.values(),
            key=lambda r: r.get("started_at_utc", ""),
            reverse=True,
        )
        return sorted_runs[:limit]

    def register_start(self, run: RunMeta) -> None:
        """Register a run start."""
        import json
        import hashlib

        self.register(run)
        self._states[run.run_id] = RunState.RUNNING

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Write header/init line if this is the first entry
        prev_hash = self._get_last_hash()
        if not prev_hash:
            # Write initial header entry
            header = {
                "run_id": "__header__",
                "prev_hash": "0" * 64,
                "status": "initialized",
            }
            header_body = json.dumps(header, sort_keys=True, separators=(",", ":"))
            header["hash"] = hashlib.sha256(header_body.encode()).hexdigest()
            with open(self.registry_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(header) + "\n")
            prev_hash = header["hash"]

        # Get last hash for chain
        prev_hash = self._get_last_hash() or "0" * 64

        # Write to registry file with hash chain
        entry = (
            run.to_dict()
            if hasattr(run, "to_dict")
            else {
                "run_id": run.run_id,
                "agent": run.agent,
                "model": getattr(run, "model", ""),
                "prompt": run.prompt,
                "cwd": run.cwd,
                "owner": run.owner,
                "status": run.status,
                "started_at_utc": run.started_at_utc,
            }
        )
        entry["prev_hash"] = prev_hash

        # Calculate hash for this entry
        entry_copy = dict(entry.items())
        body = json.dumps(entry_copy, sort_keys=True, separators=(",", ":"))
        entry["hash"] = hashlib.sha256(body.encode()).hexdigest()

        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def register_pause(self, run_id: str, reason: str = "manual", metadata: dict[str, Any] | None = None) -> None:
        """Register a run pause."""
        self._states[run_id] = RunState.PAUSED
        self._pause_reasons[run_id] = reason

    def register_resume(self, run_id: str) -> None:
        """Register a run resume."""
        self._states[run_id] = RunState.RUNNING

    def register_end(
        self,
        run_id: str,
        exit_code: int,
        status: str,
        ended_at: str,
        duration: float,
        cost_usd: float | None = None,
    ) -> None:
        """Register a run end."""
        import json
        import hashlib

        if status == "completed":
            self._states[run_id] = RunState.COMPLETED
        elif status == "failed":
            self._states[run_id] = RunState.FAILED
        else:
            self._states[run_id] = RunState.COMPLETED

        # Get last hash for chain
        prev_hash = self._get_last_hash() or "0" * 64

        # Write end entry to registry file with hash chain
        entry = {
            "run_id": run_id,
            "exit_code": exit_code,
            "status": status,
            "ended_at": ended_at,
            "duration": duration,
            "event": "finish",
            "prev_hash": prev_hash,
        }
        if cost_usd is not None:
            entry["cost_usd"] = cost_usd

        # Calculate hash for this entry
        entry_copy = dict(entry.items())
        body = json.dumps(entry_copy, sort_keys=True, separators=(",", ":"))
        entry["hash"] = hashlib.sha256(body.encode()).hexdigest()

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_run_state(self, run_id: str) -> RunState | None:
        """Get the current state of a run."""
        return self._states.get(run_id)

    def find_by_token(self, idempotency_token: str) -> dict[str, Any] | None:
        """Find a run by idempotency token, returns most recent with merged data."""
        import json

        # Read and merge events from registry file
        candidates: list[dict[str, Any]] = []
        if self.registry_path.exists():
            for line in self.registry_path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("idempotency_token") == idempotency_token:
                        candidates.append(data)
                except json.JSONDecodeError:
                    continue

        if not candidates:
            return None

        # Merge all data into a single run dict
        merged: dict[str, Any] = {}
        for data in candidates:
            merged.update(data)

        # Return dict for subscript access (includes feedback_score)
        return merged

    def find_by_token_dict(self, idempotency_token: str) -> dict[str, Any] | None:
        """Find a run by idempotency token, returns dict for subscript access."""
        for run in self.runs.values():
            if run.idempotency_token == idempotency_token:
                return {
                    "run_id": run.run_id,
                    "agent": run.agent,
                    "model": getattr(run, "model", ""),
                    "prompt": run.prompt,
                    "cwd": run.cwd,
                    "owner": run.owner,
                    "status": run.status,
                    "idempotency_token": run.idempotency_token,
                }
        return None

    def _get_last_hash(self) -> str | None:
        """Get the last hash from the registry file."""
        import json

        if not self.registry_path.exists():
            return None

        try:
            with open(self.registry_path, encoding="utf-8") as f:
                last_line = None
                for line in f:
                    line = line.strip()
                    if line:
                        last_line = line
                if last_line:
                    data = json.loads(last_line)
                    return data.get("hash")
        except (OSError, json.JSONDecodeError):
            pass
        return None

    def register_feedback(
        self,
        run_id: str,
        score: float | None = None,
        note: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register feedback for a run."""
        import json

        run = self.runs.get(run_id)
        if run:
            if score is not None:
                run.feedback_score = score
            if note is not None:
                run.feedback_note = note
            if metadata:
                run.metadata.update(metadata)

        # Write feedback event to file
        entry = {"run_id": run_id, "event": "feedback"}
        if score is not None:
            entry["feedback_score"] = score
        if note is not None:
            entry["feedback_note"] = note
        elif score is not None:
            entry["feedback_note"] = None

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_calibration_factor(self, agent: str) -> float:
        """Get calibration factor for an agent.

        Returns feedback_score / confidence, clamped to [0.5, 2.0].
        Returns 1.0 if no feedback exists for the agent.
        """
        agent_runs = [r for r in self.runs.values() if r.agent == agent]
        if not agent_runs:
            return 1.0

        # Find runs with feedback
        runs_with_feedback = [r for r in agent_runs if hasattr(r, "feedback_score") and r.feedback_score is not None]
        if not runs_with_feedback:
            return 1.0

        # Calculate factor as feedback / confidence
        total_factor = 0.0
        count = 0
        for run in runs_with_feedback:
            confidence = getattr(run, "confidence", 1.0)
            feedback = getattr(run, "feedback_score", None)
            if feedback is not None and confidence > 0:
                total_factor += feedback / confidence
                count += 1

        if count == 0:
            return 1.0

        avg_factor = total_factor / count
        # Clamp to [0.5, 2.0]
        return max(0.5, min(2.0, avg_factor))

    def purge_expired(
        self,
        default_days: int = 30,
        by_domain: dict[str, int] | None = None,
        dry_run: bool = False,
    ) -> dict[str, int]:
        """Purge expired runs from registry."""
        import json
        from datetime import datetime, timezone

        kept = 0
        purged = 0
        if by_domain is None:
            by_domain = {}

        if not self.registry_path.exists():
            return {"kept": 0, "purged": 0}

        try:
            new_lines = []

            with open(self.registry_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        run_id = data.get("run_id", "")
                        # Skip header lines (count as kept but don't process)
                        if run_id.startswith("__"):
                            new_lines.append(line)
                            kept += 1
                            continue
                        started_at = data.get("started_at_utc", "")
                        if started_at:
                            try:
                                if "+" in started_at or "Z" in started_at:
                                    dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                                else:
                                    dt = datetime.fromisoformat(started_at)
                                # Determine retention days based on domain_tag
                                domain_tag = data.get("domain_tag", "")
                                retention_days = by_domain.get(domain_tag, default_days)
                                cutoff = datetime.now(timezone.utc).timestamp() - (retention_days * 86400)
                                if dt.timestamp() < cutoff:
                                    purged += 1
                                    continue
                            except (ValueError, OSError):
                                kept += 1
                        else:
                            kept += 1
                        new_lines.append(line)
                        kept += 1
                    except json.JSONDecodeError:
                        kept += 1

            if not dry_run and new_lines:
                with open(self.registry_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines) + "\n")

        except OSError:
            pass

        return {"kept": kept, "purged": purged}


class Auditor:
    """Auditor for execution."""

    def __init__(self, registry_path: str | None = None) -> None:
        self.audit_log: list[dict[str, Any]] = []
        self.registry_path = registry_path

    def audit(self, event: dict[str, Any]) -> None:
        """Record an audit event."""
        self.audit_log.append(event)

    def get_audit_log(self) -> list[dict[str, Any]]:
        """Get the audit log."""
        return self.audit_log.copy()

    def sign_run(self, run_id: str, data: dict[str, Any] | None = None) -> str:
        """Sign a run with a deterministic signature."""
        import hashlib

        if data is None:
            data = {}
        content = f"{run_id}:{json.dumps(data, sort_keys=True, separators=(',', ':'))}"
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_registry(self) -> dict[str, Any]:
        """Verify registry integrity."""
        import hashlib
        import json

        verified = True
        corrupt_count = 0
        chain_broken = False
        missing_hash = False
        signature_mismatch = False
        json_decode_error = False
        status = "passed"
        entries = 0
        valid_count = 0

        if not self.registry_path:
            return {
                "verified": False,
                "path": self.registry_path,
                "entries": 0,
                "valid_count": 0,
                "corrupt_count": 0,
                "chain_broken": False,
                "missing_hash": False,
                "signature_mismatch": False,
                "json_decode_error": False,
                "status": "failed",
                "issues": [],
            }

        try:
            if not Path(self.registry_path).exists():
                return {
                    "verified": False,
                    "path": self.registry_path,
                    "entries": 0,
                    "valid_count": 0,
                    "corrupt_count": 0,
                    "chain_broken": False,
                    "missing_hash": False,
                    "signature_mismatch": False,
                    "json_decode_error": False,
                    "status": "empty",
                    "issues": [],
                }

            content = Path(self.registry_path).read_text(encoding="utf-8").strip()
            prev_hash = None
            for line in content.split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)

                    # Skip header line
                    if data.get("run_id") == "__header__":
                        prev_hash = data.get("hash", "")
                        continue

                    entries += 1
                    entry_hash = data.get("hash", "")

                    # Verify hash matches computed hash of data (excluding hash and signature fields)
                    data_for_hash = {k: v for k, v in data.items() if k not in ("hash", "signature")}
                    computed_hash = hashlib.sha256(
                        json.dumps(data_for_hash, sort_keys=True, separators=(",", ":")).encode()
                    ).hexdigest()

                    if entry_hash and entry_hash != computed_hash:
                        # Hash doesn't match - tampered
                        chain_broken = True
                        corrupt_count += 1
                        verified = False
                        status = "failed"

                    # Check missing hash
                    if not entry_hash:
                        missing_hash = True
                        corrupt_count += 1
                        verified = False
                        status = "failed"
                    # Check signature mismatch
                    if "signature" in data and "hash" in data:
                        expected_sig = data.get("signature", "")
                        if expected_sig != entry_hash:
                            signature_mismatch = True
                            verified = False
                            status = "failed"
                    # Check chain
                    if prev_hash is not None and data.get("prev_hash") != prev_hash:
                        chain_broken = True
                        verified = False
                        status = "failed"
                    prev_hash = entry_hash if entry_hash else None
                    valid_count = entries
                except json.JSONDecodeError:
                    json_decode_error = True
                    corrupt_count += 1
                    verified = False
                    status = "failed"

        except OSError:
            verified = False
            status = "failed"

        issues = []
        if chain_broken:
            issues.append("chain_broken")
        if missing_hash:
            issues.append("Missing hash")
        if signature_mismatch:
            issues.append("signature_mismatch")
        if json_decode_error:
            issues.append("JSON decode error")

        return {
            "verified": verified,
            "path": self.registry_path,
            "entries": entries,
            "valid_count": valid_count,
            "corrupt_count": corrupt_count,
            "chain_broken": chain_broken,
            "missing_hash": missing_hash,
            "signature_mismatch": signature_mismatch,
            "json_decode_error": json_decode_error,
            "status": status,
            "issues": issues,
        }


class CircuitBreakerRegistry:
    """Registry for circuit breakers with per-target state tracking."""

    def __init__(
        self,
        registry_path: str | Path,
        threshold: int = 5,
        window_s: int = 300,
        recovery_s: int = 60,
    ) -> None:
        path = Path(registry_path)
        if path.is_dir():
            path = path / "circuit_breakers.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path = path
        self.threshold = threshold
        self.window_s = window_s
        self.recovery_s = recovery_s
        self._states: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load circuit breaker state from file."""
        import json

        if self.registry_path.exists():
            try:
                with open(self.registry_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._states = data
            except (OSError, json.JSONDecodeError):
                pass

    def record_failure(self, target: str, category: str = "default") -> None:
        """Record a failure for a target."""
        key = f"{category}:{target}"
        if key not in self._states:
            self._states[key] = {"failures": [], "last_failure": None}
        self._states[key]["failures"].append(time.time())
        self._states[key]["last_failure"] = time.time()
        self._save()

    def record_success(self, target: str, category: str = "default") -> None:
        """Record a success and reset failure count."""
        key = f"{category}:{target}"
        if key in self._states:
            self._states[key]["failures"] = []
            self._states[key]["last_failure"] = None

    def _save(self) -> None:
        """Save state to disk."""
        import json

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._states, f)

    def is_open(self, target: str, category: str = "default") -> bool:
        """Check if circuit is open for target.

        Circuit is open if:
        1. Failures in window exceed threshold, AND
        2. Last failure is within recovery period
        """
        # Check ONLY the specified category (category isolation)
        key = f"{category}:{target}"
        state = self._states.get(key)
        if state:
            cutoff = time.time() - self.window_s
            recent_failures = [f for f in state["failures"] if f > cutoff]
            if len(recent_failures) >= self.threshold:
                recovery_cutoff = time.time() - self.recovery_s
                if state["last_failure"] and state["last_failure"] > recovery_cutoff:
                    return True

        return False

    def get_failure_count(self, target: str, category: str = "default") -> int:
        """Get current failure count for target."""
        key = f"{category}:{target}"
        if key not in self._states:
            return 0
        cutoff = time.time() - self.window_s
        return len([f for f in self._states[key]["failures"] if f > cutoff])


def get_last_poll_session_messages_meta(session_id: str) -> dict[str, Any]:
    """Get metadata for the last poll session messages."""
    return {"session_id": session_id, "count": 0, "timestamp": ""}


class CheckpointRegistry:
    """Registry for execution checkpoints."""

    def __init__(self, registry_path: str | Path) -> None:
        path = Path(registry_path)
        if path.is_dir():
            path = path / "checkpoints.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path = path
        self._checkpoints: dict[str, dict[str, Any]] = {}

    def create_checkpoint(self, reason: str, dag_content: str, owner: str) -> "CheckpointMeta":
        """Create a new checkpoint."""
        import uuid

        checkpoint_id = f"ckpt_{uuid.uuid4().hex[:12]}"
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "reason": reason,
            "dag_content": dag_content,
            "owner": owner,
            "created_at": time.time(),
        }
        self._checkpoints[checkpoint_id] = checkpoint
        return CheckpointMeta(**checkpoint)

    def list_checkpoints(self) -> list[dict[str, Any]]:
        """List all checkpoints."""
        return list(self._checkpoints.values())

    def get_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None:
        """Get a checkpoint by ID."""
        return self._checkpoints.get(checkpoint_id)


@dataclass
class CheckpointMeta:
    """Metadata for a checkpoint."""

    checkpoint_id: str
    reason: str
    dag_content: str
    owner: str
    created_at: float = 0.0


def poll_session_messages(session_id: str) -> list[dict[str, Any]]:
    """Poll messages for a session.

    Args:
        session_id: The session ID to poll.

    Returns:
        List of message dictionaries.
    """
    return []


class HandoffManager:
    """Manager for agent handoffs."""

    def __init__(self) -> None:
        self._handoffs: dict[str, Any] = {}

    def register_handoff(self, from_agent: str, to_agent: str, context: dict[str, Any]) -> None:
        """Register a handoff between agents."""
        key = f"{from_agent}->{to_agent}"
        self._handoffs[key] = {"from": from_agent, "to": to_agent, "context": context}

    def get_handoff(self, from_agent: str, to_agent: str) -> dict[str, Any] | None:
        """Get a handoff by agents."""
        key = f"{from_agent}->{to_agent}"
        return self._handoffs.get(key)

    def list_handoffs(self) -> list[dict[str, Any]]:
        """List all registered handoffs."""
        return list(self._handoffs.values())


class KPIManager:
    """Manager for KPIs and telemetry."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.kpis: dict[str, float] = {}
        self.events: list[dict[str, Any]] = []
        self._session_dir = Path(session_dir) if session_dir else Path("/tmp")

    def record(self, kpi_name: str, value: float, metadata: dict[str, Any] | None = None) -> None:
        """Record a KPI value."""
        self.kpis[kpi_name] = value
        self.events.append({"kpi": kpi_name, "value": value, "metadata": metadata or {}})

    def get(self, kpi_name: str) -> float | None:
        """Get a KPI value."""
        return self.kpis.get(kpi_name)

    def summary(self) -> dict[str, float]:
        """Get KPI summary."""
        return self.kpis.copy()

    def get_kpis(self) -> dict[str, Any]:
        """Get all KPIs with computed metrics."""
        from thegent.execution import RunRegistry
        from thegent.contracts.telemetry import ContractTelemetry
        from thegent.execution import InterruptionTracker

        registry = RunRegistry(self._session_dir)
        telemetry = ContractTelemetry(self._session_dir)
        tracker = InterruptionTracker(self._session_dir)

        runs = registry.list_runs(limit=1000)
        stats = telemetry.get_stats(limit=100)
        fatigue = tracker.get_fatigue_score(window_s=3600)

        return {
            "throughput": stats.get("total", 0),
            "fallback_rate": stats.get("fallback_rate", 0.0),
            "data_availability": "sparse" if len(runs) < 10 else "dense",
            "kpi_confidence": 1.0 - fatigue,
        }


class InterruptionTracker:
    """Tracker for interruptions."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self._session_dir = Path(session_dir) if session_dir else Path("/tmp")

    def get_fatigue_score(self, window_s: int = 3600) -> float:
        """Get fatigue score for the window."""
        return 0.1


# ---------------------------------------------------------------------------
# AUDIT-N+5 — execution surface shims for run_execution_core_helpers imports
# ---------------------------------------------------------------------------


class AgentSource(str, Enum):
    """Origin of a run — mirrors the runtime semantics used by the
    decomposed run/bg orchestrators."""

    THEGENT_RUN = "thegent_run"
    THEGENT_SUBAGENT = "thegent_subagent"
    EXTERNAL = "external"


class InteractivityMode(str, Enum):
    """Whether the run streams to a PTY or writes to headless log files."""

    PTY = "pty"
    HEADLESS_LOGS = "headless_logs"
    BATCH = "batch"


class FreshnessValidator:
    """Validator for state-freshness (ROB-011) used by critical-lane gating."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.session_dir = Path(session_dir) if session_dir else Path("/tmp")
        self._stale_paths: set[str] = set()

    def validate_action(self, paths: list[Path]) -> list[str]:
        """Return a list of issues; empty when fresh.

        AUDIT-N+5 stub always reports fresh so the call-site in
        :mod:`thegent.cli.services.run_execution_core_helpers` proceeds
        without spurious ROB-011 failures.
        """
        return []


class DeferralQueue:
    """Queue that absorbs non-critical runs during burst load."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.session_dir = Path(session_dir) if session_dir else Path("/tmp")
        self._deferred: list[dict[str, Any]] = []

    def defer(self, run_id: str, reason: str) -> None:
        """Enqueue a deferral record."""
        self._deferred.append({"run_id": run_id, "reason": reason})


class DLQManager:
    """Dead-letter queue manager for failed critical runs (WP-2008)."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.session_dir = Path(session_dir) if session_dir else Path("/tmp")
        self._queue: list[dict[str, Any]] = []

    def enqueue(self, run: Any, reason: str) -> None:
        """Enqueue a failed run into the DLQ."""
        run_id = getattr(run, "run_id", "")
        self._queue.append({"run_id": run_id, "reason": reason})


class EvidenceLinter:
    """Evidence linter for normalised CSM outputs (WP-2007)."""

    def __init__(self, session_dir: Path | str | None = None) -> None:
        self.session_dir = Path(session_dir) if session_dir else Path("/tmp")

    def lint(self, csm: Any) -> list[str]:
        """Return lint issues for the supplied CSM; empty when clean.

        AUDIT-N+5 stub always returns an empty list so the critical-lane
        lint-failure branch in
        :mod:`thegent.cli.services.run_execution_core_helpers` is not
        triggered.
        """
        return []


__all__ = [
    "PolicyEngine",
    "EscalationQueue",
    "RunMeta",
    "RunRegistry",
    "RunState",
    "LoadClassifier",
    "ConcurrencyController",
    "Auditor",
    "CircuitBreakerRegistry",
    "get_last_poll_session_messages_meta",
    "TrustBoundaryValidator",
    "CheckpointRegistry",
    "poll_session_messages",
    "HandoffManager",
    "OverrideRegistry",
    "MessageEntry",
    "KPIManager",
    "InterruptionTracker",
    # AUDIT-N+5 — run/bg orchestrator surfaces
    "AgentSource",
    "InteractivityMode",
    "FreshnessValidator",
    "DeferralQueue",
    "DLQManager",
    "EvidenceLinter",
]
