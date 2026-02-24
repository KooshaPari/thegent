"""DAG session management facade (WL-120).

Re-exports split modules:
- dag_impl_helpers: parse, validate, serialize
- dag_impl_ops: list, ready, run, sync, recover
"""

from thegent.cli.commands.dag_impl_helpers import (
    DagDocument,
    TASK_ID_RE,
    _parse_dag_full,
    _escape_cell,
    _serialize_dag,
    _atomic_write,
    _parse_dag_session,
    _validate_task_id,
    _validate_agent,
    _check_dag_cycles,
    _validate_dag,
    _ensure_evidence_header,
    _ensure_contract_version_header,
    _dag_update_task,
)
from thegent.cli.commands.dag_impl_ops import (
    _dag_path,
    _ensure_dag_file,
    _session_status_for,
    _parse_depends_on,
    _get_ready_task_ids,
    _resolve_prompt,
    dag_list_impl,
    dag_raw_impl,
    dag_ready_impl,
    dag_run_impl,
    dag_status_impl,
    rules_sync_impl,
    dag_sync_impl,
    dag_recover_impl,
)

__all__ = [
    "DagDocument",
    "TASK_ID_RE",
    "_parse_dag_full",
    "_escape_cell",
    "_serialize_dag",
    "_atomic_write",
    "_parse_dag_session",
    "_validate_task_id",
    "_validate_agent",
    "_check_dag_cycles",
    "_validate_dag",
    "_ensure_evidence_header",
    "_ensure_contract_version_header",
    "_dag_update_task",
    "_dag_path",
    "_ensure_dag_file",
    "_session_status_for",
    "_parse_depends_on",
    "_get_ready_task_ids",
    "_resolve_prompt",
    "dag_list_impl",
    "dag_raw_impl",
    "dag_ready_impl",
    "dag_run_impl",
    "dag_status_impl",
    "rules_sync_impl",
    "dag_sync_impl",
    "dag_recover_impl",
]
