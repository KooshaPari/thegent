"""BKM-10: Thin Python wrapper for thegent-jsonl native binary.

Streams JSON objects from JSONL (newline-delimited JSON) files without loading
entire files into memory.  Two execution strategies (tried in order):

1. ``thegent-jsonl`` binary (Rust, streaming BufReader backend) — zero heap for
   entire-file load.
2. Pure Python fallback — ``json.loads`` line-by-line — always available.

The fallback is intentionally kept as a standalone, fully functional path so
the module works even when the Rust binary has not been compiled.

FR-JSONL-001  @trace FR-JSONL-001
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path  # TC003 -- Path() used as constructor at runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

_log = logging.getLogger(__name__)

_BINARY_NAME = "thegent-jsonl"


# ---------------------------------------------------------------------------
# Binary discovery
# ---------------------------------------------------------------------------


def _find_binary() -> str | None:
    """Return absolute path to the thegent-jsonl binary, or None."""
    return shutil.which(_BINARY_NAME)


def _run_binary_lines(args: list[str]) -> Iterator[dict] | None:
    """Run thegent-jsonl with *args* and yield parsed JSON dicts.

    Returns ``None`` if the binary is unavailable or exits non-zero.
    """
    binary = _find_binary()
    if binary is None:
        return None

    try:
        proc = subprocess.Popen(
            [binary, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        _log.debug("thegent-jsonl launch failed: %s", exc)
        return None

    def _iter() -> Iterator[dict]:
        if proc.stdout is None:
            return
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                _log.debug("thegent-jsonl output parse error: %s", exc)
        proc.wait()
        if proc.returncode not in (0, None):
            stderr_text = proc.stderr.read() if proc.stderr else ""
            _log.debug(
                "thegent-jsonl exited %d: %s",
                proc.returncode,
                stderr_text,
            )

    return _iter()


def _run_binary_count(file: Path) -> int | None:
    """Run ``thegent-jsonl count`` and return integer, or None on failure."""
    binary = _find_binary()
    if binary is None:
        return None
    try:
        result = subprocess.run(
            [binary, "count", str(file)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            _log.debug(
                "thegent-jsonl count exited %d: %s",
                result.returncode,
                result.stderr.strip(),
            )
            return None
        return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError, OSError) as exc:
        _log.debug("thegent-jsonl count failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Pure-Python fallback helpers
# ---------------------------------------------------------------------------


def _py_stream(path: Path) -> Iterator[dict]:
    """Yield parsed JSON dicts from *path* line-by-line (pure Python)."""
    with path.open(encoding="utf-8", errors="replace") as fh:
        for lineno, raw in enumerate(fh, start=1):
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
                if isinstance(obj, dict):
                    yield obj
                else:
                    _log.debug("line %d: non-object JSON value skipped", lineno)
            except json.JSONDecodeError as exc:
                _log.debug("line %d: JSON parse error: %s", lineno, exc)


def _py_count(path: Path) -> int:
    """Count non-blank lines in *path* (pure Python, O(1) memory)."""
    count = 0
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                count += 1
    return count


def _py_filter(path: Path, key: str, value: str) -> Iterator[dict]:
    """Yield records from *path* where ``record[key] == value``."""
    for record in _py_stream(path):
        field = record.get(key)
        if field is None:
            continue
        if str(field) == value or field == value:
            yield record


def _py_sample(path: Path, n: int) -> list[dict]:
    """Return up to *n* records from the start of *path*."""
    results: list[dict] = []
    for record in _py_stream(path):
        results.append(record)
        if len(results) >= n:
            break
    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class JsonlParser:
    """Streaming JSONL parser.

    Tries the ``thegent-jsonl`` Rust binary first; falls back to pure Python.

    All methods operate lazily (generators) except :meth:`count` and
    :meth:`sample` which need to materialise results.
    """

    def stream(self, path: Path) -> Iterator[dict]:
        """Yield every JSON object in *path* without loading the file fully.

        Args:
            path: Path to a JSONL file.

        Yields:
            Parsed JSON objects as Python dicts.  Non-dict values and
            malformed lines are silently skipped.
        """
        path = Path(path)
        native = _run_binary_lines(["stream", str(path)])
        if native is not None:
            _log.debug("JsonlParser.stream via binary: %s", path)
            yield from native
            return
        _log.debug("JsonlParser.stream falling back to Python: %s", path)
        yield from _py_stream(path)

    def count(self, path: Path) -> int:
        """Return the number of non-blank lines in *path*.

        Args:
            path: Path to a JSONL file.

        Returns:
            Integer record count.
        """
        path = Path(path)
        native = _run_binary_count(path)
        if native is not None:
            _log.debug("JsonlParser.count via binary: %s -> %d", path, native)
            return native
        _log.debug("JsonlParser.count falling back to Python: %s", path)
        return _py_count(path)

    def filter(self, path: Path, key: str, value: str) -> Iterator[dict]:
        """Yield records from *path* where ``record[key] == value``.

        Args:
            path:  Path to a JSONL file.
            key:   Top-level JSON field name.
            value: String value to match (coerced via ``str()``).

        Yields:
            Matching JSON objects.
        """
        path = Path(path)
        native = _run_binary_lines(["filter", str(path), "--key", key, "--value", value])
        if native is not None:
            _log.debug("JsonlParser.filter via binary: %s key=%s value=%s", path, key, value)
            yield from native
            return
        _log.debug("JsonlParser.filter falling back to Python: %s", path)
        yield from _py_filter(path, key, value)

    def sample(self, path: Path, n: int) -> list[dict]:
        """Return up to *n* records from the start of *path*.

        Args:
            path: Path to a JSONL file.
            n:    Maximum number of records to return.

        Returns:
            List of up to *n* parsed JSON dicts.
        """
        path = Path(path)
        native = _run_binary_lines(["sample", str(path), "--n", str(n)])
        if native is not None:
            _log.debug("JsonlParser.sample via binary: %s n=%d", path, n)
            return list(native)
        _log.debug("JsonlParser.sample falling back to Python: %s", path)
        return _py_sample(path, n)
