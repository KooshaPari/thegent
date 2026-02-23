"""Restore verifier for checkpoint/rollback output parity.

# @trace WL-296
"""

from __future__ import annotations

import hashlib
import orjson as json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RestoreVerificationResult:
    """Result for restore parity check."""

    matches: bool
    expected_hash: str
    restored_hash: str


def _stable_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":").decode())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_restore_output(
    expected_checkpoint: dict[str, Any],
    restored_output: dict[str, Any],
) -> RestoreVerificationResult:
    """Verify restored output matches expected checkpoint semantics.

    Keys must match exactly; values are compared via canonical JSON hashing.
    """
    expected_hash = _stable_hash(expected_checkpoint)
    restored_hash = _stable_hash(restored_output)
    return RestoreVerificationResult(
        matches=expected_hash == restored_hash,
        expected_hash=expected_hash,
        restored_hash=restored_hash,
    )
