"""JSON export for VitePress data loaders.

# @trace FR-DOCS-008
"""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from docs_engine.db.queries import DocQueries
from thegent.integrations.confidential_report import ConfidentialReportFilter

ARTIFACT_SCHEMA_VERSION = "wl277.artifact.v1"
SUPPORTED_ARTIFACT_SCHEMA_VERSIONS = {ARTIFACT_SCHEMA_VERSION}


class JsonExporter:
    """Export SQLite index snapshots to JSON for VitePress loaders."""

    def __init__(self, db_path: Path, out_dir: Path) -> None:
        self._queries = DocQueries(db_path)
        self._out = out_dir
        self._out.mkdir(parents=True, exist_ok=True)
        self.schema_version = ARTIFACT_SCHEMA_VERSION

    def _wrap_payload(self, payload_type: str, records: Any) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "payload_type": payload_type,
            "generated_at": datetime.now(UTC).isoformat(),
            "records": ConfidentialReportFilter.redact_artifact_payload(records),
        }

    def _write_artifact(self, out_path: Path, payload_type: str, records: Any) -> Path:
        payload = self._wrap_payload(payload_type, records)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out_path

    @staticmethod
    def validate_artifact_schema(payload: dict[str, Any]) -> None:
        schema_version = payload.get("schema_version")
        if not isinstance(schema_version, str) or not schema_version:
            raise ValueError("Artifact payload missing required schema_version")
        if schema_version not in SUPPORTED_ARTIFACT_SCHEMA_VERSIONS:
            raise ValueError(f"Unsupported artifact schema_version: {schema_version}")

    @classmethod
    def load_artifact(cls, artifact_path: Path) -> dict[str, Any]:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Artifact payload must be an object")
        cls.validate_artifact_schema(payload)
        return payload

    def export_audit_log(self) -> Path:
        """Export worklog + completion-report docs as audit-log.json."""
        rows: list[dict] = []
        for doc_type in ("worklog", "completion-report", "test-log"):
            rows.extend(self._queries.get_by_type(doc_type))
        rows.sort(key=lambda r: r.get("date", ""), reverse=True)
        out = self._out / "audit-log.json"
        return self._write_artifact(out, "audit-log", rows)

    def export_kb_graph(self) -> Path:
        """Export kb-extract docs as graph nodes."""
        nodes = self._queries.get_by_type("kb-extract")
        out = self._out / "kb-graph.json"
        return self._write_artifact(out, "kb-graph", {"nodes": nodes, "edges": []})

    def export_sprint_board(self) -> Path:
        """Export sprint-plan + sprint-retro docs."""
        sprints: list[dict] = []
        for doc_type in ("sprint-plan", "sprint-retro"):
            sprints.extend(self._queries.get_by_type(doc_type))
        sprints.sort(key=lambda r: r.get("date", ""))
        out = self._out / "sprint-board.json"
        return self._write_artifact(out, "sprint-board", sprints)

    def export_all(self) -> None:
        """Export all three snapshots."""
        self.export_audit_log()
        self.export_kb_graph()
        self.export_sprint_board()
