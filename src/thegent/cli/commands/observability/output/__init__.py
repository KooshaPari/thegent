"""Thegent CLI observability output serializers and writers.

This subpackage encapsulates all health and observability output formatting:
- Health report serializers (JSON, CSV, etc.)
- Health snapshot export writers
- Health trend CSV and JSONL serializers

@trace WL-124: CLI god package decomposition - OBSERVABILITY output domain
"""

from thegent.cli.commands.observability.output.health_export_writers import (
    export_health_snapshot_csv,
    export_health_snapshot_json,
)

from thegent.cli.commands.observability.output.health_serializers import (
    serialize_health_json,
    serialize_health_csv,
)

from thegent.cli.commands.observability.output.health_trend_csv_serializer import (
    serialize_health_trend_csv,
)

from thegent.cli.commands.observability.output.health_trend_jsonl_serializer import (
    serialize_health_trend_jsonl,
)

from thegent.cli.commands.observability.output.health_report_gate_serializers import (
    serialize_health_gate_report,
)

__all__ = [
    "export_health_snapshot_csv",
    "export_health_snapshot_json",
    "serialize_health_json",
    "serialize_health_csv",
    "serialize_health_trend_csv",
    "serialize_health_trend_jsonl",
    "serialize_health_gate_report",
]
