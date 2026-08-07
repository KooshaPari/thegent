"""Shared I/O helpers for the mesh consensus package.

All three protocol sub-modules (:mod:`protocol`, :mod:`influence`,
:mod:`escalation`) previously embedded small private copies of
``_load_json``. WL705 L1 Architecture hardening consolidates the
duplicated read/write primitives into this single ``_io`` module so
that safe-load semantics + directory-permission conventions live in
exactly one place.

The leading underscore in the module name signals private-to-package
status; consumers should import the public classes from
:mod:`thegent.mesh.consensus` directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_silent(path: Path) -> dict[str, Any] | None:
    """Load a JSON file, returning ``None`` on missing file or malformed JSON.

    This is the canonical safe-load primitive for the consensus package —
    all three sub-modules route their ``_load_json`` private copies
    through here. Used by every read path that must not raise on
    transient filesystem / parse issues.
    """
    if not path.exists():
        return None
    try:
        with path.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON file with the canonical ``open(..., "w")`` semantics.

    The original ``mesh/consensus.py`` module used the ``open(path, "w")`` +
    ``json.dump(...)`` pattern at every write site (proposals, votes,
    decisions, escalation records, human-escalation queue). This helper
    centralises that pattern so future hardening (e.g. tmp-file +
    ``os.replace`` for atomic durability) can be applied uniformly.

    Caller is responsible for ensuring the parent directory exists; use
    :func:`ensure_dir` first when creating a new directory tree.
    """
    with path.open("w") as f:
        json.dump(payload, f)


def ensure_dir(path: Path, mode: int = 0o1777) -> None:
    """Create ``path`` (with parents) using the canonical sticky-bit mode.

    The consensus package writes into shared mesh directories whose
    permissions must be ``0o1777`` (sticky + rwx for all) so multiple
    agents on the same mesh can drop files without colliding. This
    helper absorbs the repeated ``mkdir(parents=True, exist_ok=True,
    mode=0o1777)`` pattern from the legacy single-file module.
    """
    path.mkdir(parents=True, exist_ok=True, mode=mode)


__all__ = [
    "load_json_silent",
    "write_json_atomic",
    "ensure_dir",
]
