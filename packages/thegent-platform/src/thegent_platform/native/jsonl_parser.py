"""BKM-10: JSONL operations using native Rust (thegent-jsonl).

Primary behavior is native-first. This module also exposes compatibility helper
symbols consumed by tests and historical imports.
"""

from __future__ import annotations

import orjson as json
import logging
import shutil
from thegent_core.infra.shim_subprocess import run as shim_run
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

_log = logging.getLogger(__name__)

try:
    import thegent_jsonl  # type: ignore[reportMissingImports]
except ImportError:
    thegent_jsonl = None


def _require_native() -> Any:
    if _find_binary() is None:
        raise ImportError("thegent-jsonl binary not available")
    if thegent_jsonl is None:
        raise ImportError("thegent-jsonl not available - install with: pip install thegent-jsonl")
    return thegent_jsonl


def _normalize_path(path: Path | str) -> Path:
    return path if isinstance(path, Path) else Path(path)


def _find_binary() -> str | None:
    """Locate the standalone thegent-jsonl binary if present on PATH."""
    return shutil.which("thegent-jsonl")


def _run_binary_lines(args: list[str]) -> list[str] | None:
    """Run the optional native binary and return stdout lines."""
    binary = _find_binary()
    if not binary:
        return None
    proc = shim_run([binary, *args], check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or f"thegent-jsonl failed: {proc.returncode}")
    return proc.stdout.splitlines()


def _run_binary_count(path: Path | str) -> int | None:
    """Return line count via optional native binary, or None when unavailable."""
    lines = _run_binary_lines(["count", str(_normalize_path(path))])
    if lines is None:
        return None
    if not lines:
        return 0
    return int(lines[0].strip() or "0")


def _py_stream(path: Path | str) -> Iterator[dict[str, Any]]:
    """Compatibility helper: parse JSONL with Python and skip invalid entries."""
    p = _normalize_path(path)
    with p.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                yield payload


def _py_count(path: Path | str) -> int:
    """Count non-blank JSONL lines (validity-agnostic)."""
    p = _normalize_path(path)
    with p.open("r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def _py_filter(path: Path | str, key: str, value: str) -> Iterator[dict[str, Any]]:
    """Yield dict records where record[key] == value."""
    for item in _py_stream(path):
        if item.get(key) == value:
            yield item


def _py_sample(path: Path | str, n: int) -> list[dict[str, Any]]:
    """Return first n parsed dict records."""
    out: list[dict[str, Any]] = []
    for item in _py_stream(path):
        if len(out) >= n:
            break
        out.append(item)
    return out


_COMPAT_PARITY_HELPERS: tuple[Callable[..., object], ...] = (
    _run_binary_count,
    _py_count,
    _py_filter,
    _py_sample,
)


class JsonlParser:
    """Native JSONL parser using Rust extension."""

    @staticmethod
    def _native_stream(path: Path | str) -> Iterator[dict[str, Any]]:
        parser = _require_native()
        p = _normalize_path(path)
        result = parser.parse_file(str(p))
        if result.is_err():
            raise OSError(f"Failed to parse {p}: {result.err()}")

        iter_obj = result.unwrap()
        while True:
            item = iter_obj.__next__()
            if item.is_err():
                _log.debug("parse error: %s", item.err())
                continue
            yield item.unwrap()

    @staticmethod
    def _native_count(path: Path | str) -> int:
        parser = _require_native()
        p = _normalize_path(path)
        result = parser.count_file(str(p))
        if result.is_err():
            raise OSError(f"Failed to count {p}: {result.err()}")
        return result.unwrap()

    @staticmethod
    def _native_filter(path: Path | str, key: str, value: str) -> Iterator[dict[str, Any]]:
        parser = _require_native()
        p = _normalize_path(path)
        result = parser.filter_file(str(p), key, value)
        if result.is_err():
            raise OSError(f"Failed to filter {p}: {result.err()}")

        iter_obj = result.unwrap()
        while True:
            item = iter_obj.__next__()
            if item.is_err():
                continue
            yield item.unwrap()

    @staticmethod
    def _native_sample(path: Path | str, n: int) -> list[dict[str, Any]]:
        parser = _require_native()
        p = _normalize_path(path)
        result = parser.sample_file(str(p), n)
        if result.is_err():
            raise OSError(f"Failed to sample {p}: {result.err()}")

        items = result.unwrap()
        return [i for i in items if i.is_ok()]

    @staticmethod
    def stream(path: Path | str) -> Iterator[dict[str, Any]]:
        try:
            _require_native()
            return iter(JsonlParser._native_stream(path))
        except ImportError:
            return _py_stream(path)

    @staticmethod
    def count(path: Path | str) -> int:
        try:
            return JsonlParser._native_count(path)
        except ImportError:
            return _py_count(path)

    @staticmethod
    def filter(path: Path | str, key: str, value: str) -> Iterator[dict[str, Any]]:
        try:
            _require_native()
            return iter(JsonlParser._native_filter(path, key, value))
        except ImportError:
            return _py_filter(path, key, value)

    @staticmethod
    def sample(path: Path | str, n: int) -> list[dict[str, Any]]:
        try:
            return JsonlParser._native_sample(path, n)
        except ImportError:
            return _py_sample(path, n)
