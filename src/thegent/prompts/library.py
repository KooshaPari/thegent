from __future__ import annotations

"""GW-73: Prompt library — store, version, and retrieve named prompts.

In-memory versioned prompt store. Prompts are stored by name; each update
creates a new version (auto-incrementing integer starting at 1). Thread-safe.

# @trace FR-PROMPT-073
"""

import logging
import threading
import time
from dataclasses import dataclass, field

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class PromptEntry:
    name: str
    version: int
    content: str  # the prompt text
    description: str = ""  # optional human description
    tags: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# PromptLibrary
# ---------------------------------------------------------------------------


class PromptLibrary:
    """Thread-safe in-memory versioned prompt store."""

    def __init__(self) -> None:
        # _store[name] = list of PromptEntry (oldest first, newest last)
        self._store: dict[str, list[PromptEntry]] = {}
        self._lock = threading.Lock()

    def add(
        self,
        name: str,
        content: str,
        *,
        description: str = "",
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> PromptEntry:
        """Add or update a prompt. Returns the new PromptEntry with auto-assigned version."""
        with self._lock:
            existing = self._store.get(name, [])
            version = len(existing) + 1
            entry = PromptEntry(
                name=name,
                version=version,
                content=content,
                description=description,
                tags=tags if tags is not None else [],
                metadata=metadata if metadata is not None else {},
            )
            if name not in self._store:
                self._store[name] = []
            self._store[name].append(entry)
            _log.debug("add prompt: name=%r version=%d", name, version)
            return entry

    def get(self, name: str, version: int | None = None) -> PromptEntry | None:
        """Get prompt by name and optional version. Returns latest if version=None."""
        with self._lock:
            versions = self._store.get(name)
            if not versions:
                return None
            if version is None:
                return versions[-1]
            # versions are 1-indexed; list is 0-indexed
            idx = version - 1
            if idx < 0 or idx >= len(versions):
                return None
            return versions[idx]

    def get_all_versions(self, name: str) -> list[PromptEntry]:
        """Return all versions of a named prompt, oldest first."""
        with self._lock:
            return list(self._store.get(name, []))

    def list_names(self) -> list[str]:
        """Return sorted list of all prompt names."""
        with self._lock:
            return sorted(self._store.keys())

    def delete(self, name: str) -> bool:
        """Remove all versions of a prompt. Returns True if existed."""
        with self._lock:
            if name in self._store:
                del self._store[name]
                _log.debug("delete prompt: name=%r", name)
                return True
            return False

    def search(self, query: str) -> list[PromptEntry]:
        """Return latest version of all prompts whose name or content contains query (case-insensitive)."""
        lower_query = query.lower()
        results: list[PromptEntry] = []
        with self._lock:
            for name, versions in self._store.items():
                if not versions:
                    continue
                latest = versions[-1]
                if lower_query in name.lower() or lower_query in latest.content.lower():
                    results.append(latest)
        return results


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_library: PromptLibrary | None = None
_library_lock = threading.Lock()


def get_prompt_library() -> PromptLibrary:
    """Return the module-level PromptLibrary singleton, creating it if needed."""
    global _library  # noqa: PLW0603
    with _library_lock:
        if _library is None:
            _library = PromptLibrary()
        return _library


def reset_prompt_library() -> None:
    """Replace the singleton with a fresh PromptLibrary. Intended for tests."""
    global _library  # noqa: PLW0603
    with _library_lock:
        _library = PromptLibrary()
