"""Shared hashing helpers for execution records."""

import hashlib
import orjson as json
from typing import Any


def calculate_stable_record_hash(data: dict[str, Any]) -> str:
    """Calculate a stable hash for a record, excluding the hash field."""
    body = json.dumps({k: v for k, v in data.items() if k != "hash"}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body).hexdigest()
