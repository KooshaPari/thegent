"""Observe-summary payload constants — split from observability_impl (WL-124)."""

from __future__ import annotations

OBSERVE_SUMMARY_SCHEMA_VERSION = "observe-summary-schema-v1"
OBSERVE_SUMMARY_PAYLOAD_TYPES = ("observe_summary",)

__all__ = ["OBSERVE_SUMMARY_SCHEMA_VERSION", "OBSERVE_SUMMARY_PAYLOAD_TYPES"]
