"""Canonical workstream entity operations for CLI, MCP, and API surfaces."""

from __future__ import annotations

import contextlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson as json

from thegent.config import ThegentSettings
from thegent.planning.workstream_db import WorkstreamDB
from thegent.planning.workstream_db_schema import SCHEMA_TABLE_SQL

_TABLE_NAME_RE = re.compile(r"CREATE TABLE IF NOT EXISTS\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_JSON_PREFIXES = ("{", "[")


@dataclass(frozen=True)
class EntityTableSpec:
    """Canonical table metadata for safe generic CRUD."""

    table: str
    pk_columns: tuple[str, ...]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _available_tables() -> set[str]:
    return {match.group(1) for sql in SCHEMA_TABLE_SQL if (match := _TABLE_NAME_RE.search(sql))}


_SUPPORTED_TABLES = _available_tables()


def _normalize_entity_type(entity_type: str) -> str:
    entity = entity_type.strip()
    if not entity:
        raise ValueError("entity_type is required")

    aliases = {
        "workstream_item": "workstream_items",
        "workstream_items": "workstream_items",
        "session": "sessions",
        "sessions": "sessions",
        "launch": "launches",
        "launches": "launches",
        "backlog_item": "backlog_items",
        "backlog_items": "backlog_items",
        "deferred_task": "deferred_tasks",
        "deferred_tasks": "deferred_tasks",
        "dependency": "dependencies",
        "dependencies": "dependencies",
        "team_task": "team_tasks",
        "team_tasks": "team_tasks",
        "cost_tracking": "cost_tracking",
        "event": "auto_launch_events",
        "auto_launch_event": "auto_launch_events",
        "auto_launch_events": "auto_launch_events",
        "evidence_link": "evidence_links",
        "evidence_links": "evidence_links",
        "policy_override": "policy_overrides",
        "policy_overrides": "policy_overrides",
        "process_tracking": "process_tracking",
        "siem_event": "siem_events",
        "siem_events": "siem_events",
        "constitutional_violation": "constitutional_violations",
        "constitutional_violations": "constitutional_violations",
        "reputation_entry": "reputation_entries",
        "reputation_entries": "reputation_entries",
    }
    normalized = aliases.get(entity, entity)
    if normalized not in _SUPPORTED_TABLES:
        raise ValueError(f"Unsupported entity_type: {entity_type}")
    return normalized


def _connect(db: WorkstreamDB) -> sqlite3.Connection:
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _table_info(db: WorkstreamDB, table: str) -> list[dict[str, Any]]:
    return db.execute_query(f'PRAGMA table_info("{table}")')


def _table_spec(db: WorkstreamDB, table: str) -> EntityTableSpec:
    columns = _table_info(db, table)
    pk_columns = tuple(row["name"] for row in sorted(columns, key=lambda row: row["pk"]) if row.get("pk", 0))
    return EntityTableSpec(table=table, pk_columns=pk_columns)


def _quote(identifier: str) -> str:
    if not _IDENTIFIER_RE.match(identifier):
        raise ValueError(f"Invalid identifier: {identifier}")
    return f'"{identifier}"'


def _decode_value(value: Any) -> Any:
    if not isinstance(value, str) or not value:
        return value
    if value.startswith(_JSON_PREFIXES):
        with contextlib.suppress(Exception):
            return json.loads(value)
    return value


def _row_to_dict(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    payload = dict(row)
    return {key: _decode_value(value) for key, value in payload.items()}


def _serialize_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value).decode()
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _coerce_properties(properties: dict[str, Any] | None) -> dict[str, Any]:
    return {key: _serialize_value(value) for key, value in (properties or {}).items()}


def _entity_key_values(
    spec: EntityTableSpec,
    entity_id: str | None,
    properties: dict[str, Any] | None,
) -> dict[str, Any]:
    props = dict(properties or {})
    if spec.pk_columns and entity_id:
        if len(spec.pk_columns) == 1:
            props.setdefault(spec.pk_columns[0], entity_id)
        else:
            parts = [part.strip() for part in entity_id.split("|")]
            if len(parts) != len(spec.pk_columns):
                raise ValueError(f"entity_id for {spec.table} must contain {len(spec.pk_columns)} pipe-separated parts")
            for column, part in zip(spec.pk_columns, parts, strict=True):
                props.setdefault(column, part)
    return props


def _read_existing(
    conn: sqlite3.Connection, spec: EntityTableSpec, entity_id: str | None, properties: dict[str, Any] | None
) -> dict[str, Any] | None:
    cursor = conn.cursor()
    if spec.pk_columns:
        criteria = _entity_key_values(spec, entity_id, properties)
        if not all(column in criteria for column in spec.pk_columns):
            return None
        where_clause = " AND ".join(f"{_quote(column)} = ?" for column in spec.pk_columns)
        cursor.execute(
            f"SELECT * FROM {_quote(spec.table)} WHERE {where_clause} LIMIT 1",  # noqa: S608
            [criteria[column] for column in spec.pk_columns],
        )
        row = cursor.fetchone()
        return _row_to_dict(row) if row else None
    if entity_id:
        cursor.execute(f"SELECT * FROM {_quote(spec.table)} LIMIT 1")  # noqa: S608
        row = cursor.fetchone()
        return _row_to_dict(row) if row else None
    return None


def _list_table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA table_info("{table}")')
    return [row[1] for row in cursor.fetchall()]


def _build_like_clause(columns: list[str]) -> str:
    return " OR ".join(f"LOWER(COALESCE(CAST({_quote(column)} AS TEXT), '')) LIKE ?" for column in columns)


def _ensure_db(db_path: Path | None = None, settings: ThegentSettings | None = None) -> WorkstreamDB:
    if db_path is not None:
        return WorkstreamDB(db_path=db_path, settings=settings)
    if settings is None:
        settings = ThegentSettings()
    return WorkstreamDB(settings=settings)


def list_entities(
    entity_type: str,
    *,
    limit: int = 50,
    offset: int = 0,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """List canonical records for a supported workstream entity table."""
    db = _ensure_db(db_path=db_path, settings=settings)
    table = _normalize_entity_type(entity_type)
    spec = _table_spec(db, table)
    conn = _connect(db)
    try:
        columns = _list_table_columns(conn, table)
        order_candidates = list(spec.pk_columns) + [
            column for column in ("created_at", "last_synced_at", "updated_at") if column in columns
        ]
        order_clause = ", ".join(f"{_quote(column)}" for column in order_candidates) if order_candidates else '"rowid"'
        rows = [
            dict(row)
            for row in conn.execute(  # noqa: S608
                f"SELECT * FROM {_quote(table)} ORDER BY {order_clause} LIMIT ? OFFSET ?",  # noqa: S608
                (limit, offset),
            ).fetchall()
        ]
        return {
            "entity_type": table,
            "count": len(rows),
            "limit": limit,
            "offset": offset,
            "items": [_row_to_dict(row) for row in rows],
        }
    finally:
        conn.close()


def read_entity(
    entity_type: str,
    entity_id: str,
    *,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    db = _ensure_db(db_path=db_path, settings=settings)
    table = _normalize_entity_type(entity_type)
    spec = _table_spec(db, table)
    conn = _connect(db)
    try:
        existing = _read_existing(conn, spec, entity_id, None)
        if existing is None:
            raise LookupError(f"{table} entity not found: {entity_id}")
        return {"entity_type": table, "item": existing}
    finally:
        conn.close()


def search_entities(
    entity_type: str,
    query: str,
    *,
    limit: int = 20,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    db = _ensure_db(db_path=db_path, settings=settings)
    table = _normalize_entity_type(entity_type)
    conn = _connect(db)
    try:
        columns = _list_table_columns(conn, table)
        if not columns:
            raise ValueError(f"{table} has no columns to search")
        text_columns = columns
        clause = _build_like_clause(text_columns)
        pattern = f"%{query.lower()}%"
        rows = [
            dict(row)
            for row in conn.execute(  # noqa: S608
                f"SELECT * FROM {_quote(table)} WHERE {clause} LIMIT ?",  # noqa: S608
                (*([pattern] * len(text_columns)), limit),
            ).fetchall()
        ]
        return {
            "entity_type": table,
            "count": len(rows),
            "query": query,
            "items": [_row_to_dict(row) for row in rows],
        }
    finally:
        conn.close()


def upsert_entity(
    entity_type: str,
    *,
    entity_id: str | None = None,
    properties: dict[str, Any] | None = None,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    db = _ensure_db(db_path=db_path, settings=settings)
    table = _normalize_entity_type(entity_type)
    spec = _table_spec(db, table)
    props = _coerce_properties(properties)
    conn = _connect(db)
    try:
        existing = _read_existing(conn, spec, entity_id, props)
        merged = dict(existing or {})
        merged.update(props)
        merged = _entity_key_values(spec, entity_id, merged)

        columns = _list_table_columns(conn, table)
        if "created_at" in columns and not merged.get("created_at") and existing is None:
            merged["created_at"] = _now_iso()
        if "updated_at" in columns:
            merged["updated_at"] = _now_iso()
        if "last_synced_at" in columns:
            merged["last_synced_at"] = _now_iso()

        insert_columns = [column for column in columns if column in merged or column in spec.pk_columns]
        if not insert_columns:
            insert_columns = columns

        values = [merged.get(column) for column in insert_columns]
        placeholders = ", ".join("?" for _ in insert_columns)
        quoted_columns = ", ".join(_quote(column) for column in insert_columns)
        pk_clause = ", ".join(_quote(column) for column in spec.pk_columns)

        if spec.pk_columns and all(merged.get(column) is not None for column in spec.pk_columns):
            update_columns = [column for column in insert_columns if column not in spec.pk_columns]
            update_clause = ", ".join(f"{_quote(column)} = excluded.{column}" for column in update_columns)
            sql = f"INSERT INTO {_quote(table)} ({quoted_columns}) VALUES ({placeholders})"  # noqa: S608
            if update_clause:
                sql += f" ON CONFLICT({pk_clause}) DO UPDATE SET {update_clause}"
            else:
                sql += f" ON CONFLICT({pk_clause}) DO NOTHING"
            conn.execute(sql, values)  # noqa: S608
        else:
            conn.execute(  # noqa: S608
                f"INSERT INTO {_quote(table)} ({quoted_columns}) VALUES ({placeholders})",  # noqa: S608
                values,
            )

        conn.commit()
        if spec.pk_columns:
            key_filter = {column: merged.get(column) for column in spec.pk_columns}
            if not all(key_filter.values()):
                raise ValueError(f"Unable to resolve primary key for {table}")
            readback = _read_existing(conn, spec, None, key_filter)
            if readback is None:
                raise LookupError(f"Failed to reload {table} after upsert")
            return {"entity_type": table, "item": readback}

        rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"entity_type": table, "item": {"rowid": rowid, **merged}}
    finally:
        conn.close()


def delete_entity(
    entity_type: str,
    entity_id: str,
    *,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    db = _ensure_db(db_path=db_path, settings=settings)
    table = _normalize_entity_type(entity_type)
    spec = _table_spec(db, table)
    conn = _connect(db)
    try:
        if not spec.pk_columns:
            raise ValueError(f"{table} does not expose a primary key")
        criteria = _entity_key_values(spec, entity_id, None)
        if not all(criteria.get(column) for column in spec.pk_columns):
            raise ValueError(f"Unable to resolve delete key for {table}")
        where_clause = " AND ".join(f"{_quote(column)} = ?" for column in spec.pk_columns)
        cursor = conn.execute(  # noqa: S608
            f"DELETE FROM {_quote(table)} WHERE {where_clause}",  # noqa: S608
            [criteria[column] for column in spec.pk_columns],
        )
        conn.commit()
        return {"entity_type": table, "deleted": cursor.rowcount > 0, "entity_id": entity_id}
    finally:
        conn.close()


def import_entities(
    entity_type: str,
    records: list[dict[str, Any]],
    *,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    count = 0
    items: list[dict[str, Any]] = []
    for record in records:
        entity_id = str(record.get("entity_id") or record.get("id") or record.get("item_id") or "").strip() or None
        properties = dict(record.get("properties") or {})
        for key, value in record.items():
            if key not in {"entity_type", "entity_id", "id", "properties"}:
                properties.setdefault(key, value)
        result = upsert_entity(
            entity_type,
            entity_id=entity_id,
            properties=properties,
            settings=settings,
            db_path=db_path,
        )
        items.append(result["item"])
        count += 1
    return {"entity_type": _normalize_entity_type(entity_type), "count": count, "items": items}


def export_entities(
    entity_type: str,
    *,
    limit: int = 100,
    offset: int = 0,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    payload = list_entities(entity_type, limit=limit, offset=offset, settings=settings, db_path=db_path)
    return payload


def sync_entities_from_sources(
    *,
    source: str = "all",
    cd: Path | None = None,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Sync canonical tables from markdown, AgilePlus, and queue sources."""
    db = _ensure_db(db_path=db_path, settings=settings)
    settings = settings or ThegentSettings()
    project_dir = Path(cd).expanduser().resolve() if cd else Path.cwd()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    counts: dict[str, int] = {}

    if source in {"markdown", "all"}:
        work_stream_path = project_dir / "docs" / "reference" / "WORK_STREAM.md"
        if work_stream_path.exists():
            from thegent.cli.services import run_workstream_helpers

            data = run_workstream_helpers.parse_work_stream_md(work_stream_path)
            db.sync_workstream(data)
            counts["markdown"] = len(data.get("backlog", []))
        else:
            counts["markdown"] = 0

    if source in {"agileplus", "all"}:
        counts["agileplus"] = db.sync_from_agileplus(session_dir)

    if source in {"queues", "all"}:
        counts["queues"] = db.sync_from_queues(session_dir)

    return {
        "source": source,
        "project_dir": str(project_dir),
        "session_dir": str(session_dir),
        "counts": counts,
        "total": sum(counts.values()),
    }


def entity_operation(
    operation: str,
    entity_type: str,
    *,
    entity_id: str | None = None,
    properties: dict[str, Any] | None = None,
    records: list[dict[str, Any]] | None = None,
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
    source: str = "all",
    cd: Path | None = None,
    settings: ThegentSettings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Dispatch workstream entity operations through one canonical API."""
    action = operation.strip().lower()
    if action == "list":
        return list_entities(entity_type, limit=limit, offset=offset, settings=settings, db_path=db_path)
    if action == "read":
        if not entity_id:
            raise ValueError("entity_id is required for read")
        return read_entity(entity_type, entity_id, settings=settings, db_path=db_path)
    if action == "search":
        if not query:
            raise ValueError("query is required for search")
        return search_entities(entity_type, query, limit=limit, settings=settings, db_path=db_path)
    if action == "upsert":
        return upsert_entity(
            entity_type,
            entity_id=entity_id,
            properties=properties,
            settings=settings,
            db_path=db_path,
        )
    if action == "delete":
        if not entity_id:
            raise ValueError("entity_id is required for delete")
        return delete_entity(entity_type, entity_id, settings=settings, db_path=db_path)
    if action == "import":
        if records is None:
            raise ValueError("records are required for import")
        return import_entities(entity_type, records, settings=settings, db_path=db_path)
    if action == "export":
        return export_entities(entity_type, limit=limit, offset=offset, settings=settings, db_path=db_path)
    if action == "sync":
        return sync_entities_from_sources(source=source, cd=cd, settings=settings, db_path=db_path)
    raise ValueError(f"Unsupported operation: {operation}")
