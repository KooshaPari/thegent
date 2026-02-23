"""Default-on guardrail pack and migration utility.

# @trace WL-300
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_DEFAULT_PACK: dict[str, Any] = {
    "input_guardrails_enabled": True,
    "prompt_max_chars": 120_000,
    "deny_dangerous_shell": True,
    "require_explicit_destructive_confirmation": True,
    "mask_pii_in_logs": True,
}


@dataclass(frozen=True)
class GuardrailMigrationResult:
    """Result of migrating legacy guardrail config to default-on pack."""

    merged_config: dict[str, Any]
    added_keys: list[str]


def build_default_guardrail_pack() -> dict[str, Any]:
    """Return a copy of the canonical default-on guardrail pack."""
    return dict(_DEFAULT_PACK)


def migrate_to_default_on_pack(existing: dict[str, Any]) -> GuardrailMigrationResult:
    """Merge missing default keys while preserving explicit existing values."""
    if not isinstance(existing, dict):
        raise ValueError("existing config must be a dict")

    merged = dict(existing)
    added: list[str] = []

    for key, value in _DEFAULT_PACK.items():
        if key in merged:
            continue
        merged[key] = value
        added.append(key)

    return GuardrailMigrationResult(merged_config=merged, added_keys=added)
