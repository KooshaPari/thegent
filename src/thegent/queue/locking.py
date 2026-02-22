"""Advisory file locking for queue operations (atomic claim, release, extend_lease)."""

import fcntl
import json
import logging
from pathlib import Path

_log = logging.getLogger(__name__)


def _supports_flock() -> bool:
    """Check if fcntl.flock is available (Unix)."""
    return hasattr(fcntl, "flock")


class QueueLock:
    """Advisory exclusive lock on the queue file for atomic multi-line updates.
    Provides read/write through the locked file handle so all I/O uses the same fd.
    """

    def __init__(self, queue_path: Path) -> None:
        self.queue_path = queue_path
        self._file = None

    def __enter__(self) -> "QueueLock":
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.queue_path.exists():
            self.queue_path.touch()
        self._file = open(self.queue_path, "r+", encoding="utf-8")
        if _supports_flock():
            fcntl.flock(self._file.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        try:
            if self._file:
                if _supports_flock():
                    fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
                self._file.close()
        finally:
            self._file = None

    def read_entries(self) -> list[dict]:
        """Read entries from the locked file. Call only while holding the lock."""
        assert self._file is not None, "read_entries called outside lock context"
        self._file.seek(0)
        entries = []
        for line in self._file:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
        return entries

    def write_entries(self, entries: list[dict]) -> None:
        """Write entries to the locked file (truncate + rewrite). Call only while holding the lock."""
        self._file.seek(0)
        self._file.truncate()
        for entry in entries:
            self._file.write(json.dumps(entry) + "\n")
        self._file.flush()
