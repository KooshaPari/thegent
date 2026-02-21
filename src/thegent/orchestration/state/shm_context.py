"""WP-21002: Zero-Copy Context Sharing (Shared Memory).
MTSP-09/11: Efficiently share large context blocks across multi-tenant agent runs.
"""

import logging
import mmap
import os
import tempfile
from pathlib import Path

_log = logging.getLogger(__name__)


class ZeroCopyContext:
    """Provides high-performance shared memory context for agent processes."""

    def __init__(self, size: int = 1024 * 1024) -> None:  # Default 1MB
        self.size = size
        fd_num, temp_path = tempfile.mkstemp()
        self.fd = os.fdopen(fd_num, "w+b")
        self.fd.write(b"\0" * size)
        self.fd.flush()
        self.mm = mmap.mmap(self.fd.fileno(), size)
        self.path = Path(temp_path)
        _log.info("ZeroCopyContext initialized at: %s (Size: %d bytes)", self.path, size)

    def write_context(self, data: bytes, offset: int = 0):
        """Write context data directly to memory-mapped file."""
        if len(data) + offset > self.size:
            raise ValueError("Context data exceeds shared memory size")
        self.mm[offset : offset + len(data)] = data
        self.mm.flush()
        _log.debug("Wrote %d bytes to shared context", len(data))

    def read_context(self, size: int, offset: int = 0) -> bytes:
        """Read context data directly from memory-mapped file."""
        return self.mm[offset : offset + size]

    def close(self):
        """Clean up resources."""
        self.mm.close()
        self.fd.close()
        if self.path.exists():
            self.path.unlink()
        _log.info("ZeroCopyContext closed and cleaned up")


class ContextSharer:
    """Manages context sharing across multiple agent runs (Multi-Tenancy)."""

    def __init__(self) -> None:
        self.shared_contexts: dict[str, ZeroCopyContext] = {}

    def get_context(self, session_id: str) -> ZeroCopyContext:
        """Retrieve or create a shared context for a session."""
        if session_id not in self.shared_contexts:
            self.shared_contexts[session_id] = ZeroCopyContext()
        return self.shared_contexts[session_id]

    def release_context(self, session_id: str):
        """Clean up session context."""
        if session_id in self.shared_contexts:
            self.shared_contexts[session_id].close()
            del self.shared_contexts[session_id]
