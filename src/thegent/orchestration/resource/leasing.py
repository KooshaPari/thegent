import orjson as json
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# MTSP-14: In-memory singleton for zero-latency coordination (no disk I/O on every acquire/release)
_LEASE_MANAGER: Optional["EditLeaseManager"] = None
_LEASE_MANAGER_LOCK = threading.Lock()


def _read_json_file(path: Path) -> object:
    return json.loads(path.read_bytes())


def _write_json_file(path: Path, payload: object) -> None:
    path.write_bytes(json.dumps(payload, option=json.OPT_INDENT_2))


def get_lease_manager(state_dir: Path) -> "EditLeaseManager":
    """Return shared in-memory EditLeaseManager. MTSP-14: zero-latency lock coordination."""
    global _LEASE_MANAGER
    with _LEASE_MANAGER_LOCK:
        if _LEASE_MANAGER is None:
            _LEASE_MANAGER = EditLeaseManager(state_dir)
        return _LEASE_MANAGER


@dataclass
class EditLease:
    path: str
    agent_id: str
    expires_at: float
    metadata: dict[str, str] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class EditLeaseManager:
    """MTSP-11: Centralized edit lease management for multi-tenant agent environments.
    Prevents agent-on-agent edit collisions by providing advisory locks with TTL.
    """

    def __init__(self, state_dir: Path) -> None:
        self.state_file = state_dir / "edit_leases.json"
        self.leases: dict[str, EditLease] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        if self.state_file.exists():
            try:
                data = _read_json_file(self.state_file)
                if isinstance(data, dict):
                    for path, lease_data in data.items():
                        if not isinstance(lease_data, dict):
                            continue
                        lease = EditLease(
                            path=lease_data["path"],
                            agent_id=lease_data["agent_id"],
                            expires_at=lease_data["expires_at"],
                            metadata=lease_data.get("metadata", {}),
                        )
                        if not lease.is_expired():
                            self.leases[path] = lease
            except Exception as e:
                logger.error(f"Failed to load edit leases: {e}")

    def _save(self):
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                path: {
                    "path": lease.path,
                    "agent_id": lease.agent_id,
                    "expires_at": lease.expires_at,
                    "metadata": lease.metadata,
                }
                for path, lease in self.leases.items()
                if not lease.is_expired()
            }
            _write_json_file(self.state_file, data)
        except Exception as e:
            logger.error(f"Failed to save edit leases: {e}")

    def acquire(self, path: str, agent_id: str, duration: float = 300.0, force: bool = False) -> bool:
        """Acquire an advisory lease on a file path."""
        with self._lock:
            now = time.time()
            existing = self.leases.get(path)

            if existing and not existing.is_expired():
                if existing.agent_id == agent_id:
                    # Renew lease
                    existing.expires_at = now + duration
                    self._save()
                    return True
                if not force:
                    logger.warning(f"Path {path} is leased by agent {existing.agent_id}")
                    return False

            # New lease or force takeover
            self.leases[path] = EditLease(path=path, agent_id=agent_id, expires_at=now + duration)
            self._save()
            return True

    def release(self, path: str, agent_id: str) -> bool:
        """Release a lease if held by the agent."""
        with self._lock:
            existing = self.leases.get(path)
            if existing:
                if existing.agent_id == agent_id or existing.is_expired():
                    del self.leases[path]
                    self._save()
                    return True
                return False
            return True

    def check(self, path: str, agent_id: str | None = None) -> EditLease | None:
        """Check if a path is currently leased by another agent."""
        with self._lock:
            lease = self.leases.get(path)
            if lease and not lease.is_expired():
                if agent_id and lease.agent_id == agent_id:
                    return None
                return lease
            return None

    def prune(self) -> None:
        """Remove all expired leases."""
        with self._lock:
            pre_count = len(self.leases)
            self.leases = {p: l for p, l in self.leases.items() if not l.is_expired()}
            if len(self.leases) < pre_count:
                self._save()
