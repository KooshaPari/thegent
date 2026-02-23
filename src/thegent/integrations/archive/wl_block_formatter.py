"""Formatter for WL block structure normalization.

# @trace WL-264
"""

from __future__ import annotations

import re


_WL_HEADER = re.compile(r"^### \[(WL-\d+)\] (.+)$")
_REQUIRED_META = ("Status", "Priority", "Area", "Effort", "Blocked by")


def normalize_wl_block(block: str) -> str:
    """Normalize a WL markdown block into canonical metadata order."""
    lines = [ln.rstrip() for ln in block.strip().splitlines() if ln.strip()]
    if not lines:
        raise ValueError("WL block is empty")

    m = _WL_HEADER.match(lines[0])
    if not m:
        raise ValueError("WL block must start with '### [WL-<id>] <title>'")

    meta: dict[str, str] = {}
    body: list[str] = []

    for line in lines[1:]:
        if line.startswith("**") and ":**" in line:
            key = line.split(":**", 1)[0].replace("**", "").strip()
            value = line.split(":**", 1)[1].strip()
            meta[key] = value
        else:
            body.append(line)

    missing = [key for key in _REQUIRED_META if key not in meta]
    if missing:
        raise ValueError(f"missing required metadata fields: {', '.join(missing)}")

    normalized = [lines[0]]
    for key in _REQUIRED_META:
        normalized.append(f"**{key}:** {meta[key]}")
    normalized.append("")
    normalized.extend(body)
    return "\n".join(normalized).strip() + "\n"
