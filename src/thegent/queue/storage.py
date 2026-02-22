"""WP-7001: Unified prompt queue storage."""

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from thegent.queue.locking import QueueLock

_log = logging.getLogger(__name__)

DEFAULT_LEASE_SECONDS = 300


def _parse_entries(queue_path: Path) -> list[tuple[int, dict[str, Any]]]:
    """Read queue file, return [(line_index, entry), ...]. Skips invalid lines."""
    if not queue_path.exists():
        return []
    entries = []
    with queue_path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append((idx, data))
            except Exception:
                continue
    return entries




class PromptQueue:
    """Manages a unified queue of deferred agent prompts."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.queue_path = session_dir / "prompt_queue.jsonl"

    def append(self, prompt: str, project: str, agent: str | None = None) -> int:
        """Append a new prompt to the queue."""
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "prompt": prompt,
            "project": str(project),
            "agent": agent,
            "claimed_by": None,
            "lease_expires_at": None,
            "status": "pending",
        }
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with self.queue_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return self.get_pending_count()

    def list_pending(self) -> list[dict[str, Any]]:
        """List all pending (unclaimed) items."""
        items = []
        for _idx, data in _parse_entries(self.queue_path):
            if data.get("status") == "pending":
                items.append(data)
        return items

    def list_all(
        self,
        include_done: bool = False,
        include_expired: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """List queue items with optional filters. Each item gets an 'id' (0-based position)."""
        now = datetime.now(UTC)
        result = []
        for pos, (_idx, data) in enumerate(_parse_entries(self.queue_path)):
            status = data.get("status", "pending")
            if status == "done" and not include_done:
                continue
            lease = data.get("lease_expires_at")
            if lease and status == "claimed":
                try:
                    expires = datetime.fromisoformat(lease)
                    if expires < now and not include_expired:
                        continue
                except Exception:
                    pass
            item = dict(data)
            item["id"] = pos
            result.append(item)
            if limit is not None and len(result) >= limit:
                break
        return result

    def get_pending_count(self) -> int:
        """Return count of pending items."""
        return len(self.list_pending())

    def claim(
        self,
        claimer_id: str,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
        project: str | None = None,
    ) -> dict[str, Any] | None:
        """Atomically claim the first pending item. Returns claimed item or None."""
        with QueueLock(self.queue_path) as lock:
            entries = lock.read_entries()
            for pos, entry in enumerate(entries):
                if entry.get("status") != "pending":
                    continue
                if project and entry.get("project") != project:
                    continue
                expires = datetime.now(UTC) + timedelta(seconds=lease_seconds)
                entry["claimed_by"] = claimer_id
                entry["lease_expires_at"] = expires.isoformat()
                entry["status"] = "claimed"
                lock.write_entries(entries)
                out = dict(entry)
                out["id"] = pos
                return out
        return None

    def done(self, item_id: int) -> bool:
        """Mark item by id as done. Returns True if found and updated."""
        with QueueLock(self.queue_path) as lock:
            entries = lock.read_entries()
            if item_id < 0 or item_id >= len(entries):
                return False
            entries[item_id]["status"] = "done"
            lock.write_entries(entries)
            return True

    def release(self, item_id: int) -> bool:
        """Release a claim by item id. Returns True if found and updated."""
        with QueueLock(self.queue_path) as lock:
            entries = lock.read_entries()
            if item_id < 0 or item_id >= len(entries):
                return False
            entry = entries[item_id]
            if entry.get("status") != "claimed":
                return False
            entry["claimed_by"] = None
            entry["lease_expires_at"] = None
            entry["status"] = "pending"
            lock.write_entries(entries)
            return True

    def extend_lease(self, item_id: int, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> bool:
        """Extend lease for a claimed item. Returns True if found and updated."""
        with QueueLock(self.queue_path) as lock:
            entries = lock.read_entries()
            if item_id < 0 or item_id >= len(entries):
                return False
            entry = entries[item_id]
            if entry.get("status") != "claimed":
                return False
            expires = datetime.now(UTC) + timedelta(seconds=lease_seconds)
            entry["lease_expires_at"] = expires.isoformat()
            lock.write_entries(entries)
            return True

    def edit(self, item_id: int, prompt: str) -> bool:
        """Edit prompt for an item. Only pending or claimed items. Returns True if updated."""
        with QueueLock(self.queue_path) as lock:
            entries = lock.read_entries()
            if item_id < 0 or item_id >= len(entries):
                return False
            entry = entries[item_id]
            if entry.get("status") == "done":
                return False
            entry["prompt"] = prompt
            lock.write_entries(entries)
            return True
