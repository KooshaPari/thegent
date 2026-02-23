"""Shared hashing helpers for execution records."""

import hashlib
import orjson
from orjson import OPT_SORT_KEYS
from typing import Any


def calculate_stable_record_hash(data: dict[str, Any]) -> str:
    """Calculate a stable hash for a record, excluding the hash field."""
    filtered = {k: v for k, v in data.items() if k != "hash"}
    body = orjson.dumps(filtered, option=OPT_SORT_KEYS)
    return hashlib.sha256(body).hexdigest()
