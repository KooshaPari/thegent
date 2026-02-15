"""Universal operation interfaces for thegent orchestration.

Stable operation-based taxonomy per Kush docs deep dive (D-B).
Maps CLI commands to operations: orchestrate, govern, recover, observe, plan.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Operation(str, Enum):
    """Canonical operation types for thegent capabilities."""

    ORCHESTRATE = "orchestrate"  # Execute agents, run, bg, dag run
    GOVERN = "govern"  # Policy, override, audit, compliance
    RECOVER = "recover"  # Rollback, retry, fallback, oversight
    OBSERVE = "observe"  # Status, logs, cockpit, inspect, metrics
    PLAN = "plan"  # DAG, validate, ready, route resolution


@dataclass
class OperationEntry:
    """A command or capability mapped to an operation."""

    operation: Operation
    command: str
    description: str
    mcp_tool: str | None = None
    constraints: dict[str, Any] = field(default_factory=dict)


# Command -> operation mapping (authoritative)
OPERATION_MAP: list[OperationEntry] = [
    # Orchestrate
    OperationEntry(Operation.ORCHESTRATE, "run", "Run foreground agent invocation", "thegent_run"),
    OperationEntry(Operation.ORCHESTRATE, "bg", "Start background run and register session", "thegent_bg"),
    OperationEntry(Operation.ORCHESTRATE, "dag run", "Execute DAG tasks", None),
    OperationEntry(Operation.ORCHESTRATE, "dag sync", "Sync DAG task status", None),
    OperationEntry(Operation.ORCHESTRATE, "dag add", "Add DAG task", None),
    OperationEntry(Operation.ORCHESTRATE, "dag update", "Update DAG task", None),
    OperationEntry(Operation.ORCHESTRATE, "dag remove", "Remove DAG task", None),
    OperationEntry(Operation.ORCHESTRATE, "dag cancel", "Cancel DAG task", None),
    # Govern
    OperationEntry(Operation.GOVERN, "policy show", "Show active governance policies", None),
    OperationEntry(
        Operation.GOVERN, "session-contracts", "Audit session routing contract metadata", "thegent_session_contracts"
    ),
    OperationEntry(
        Operation.GOVERN,
        "session-contract-health-gate",
        "Evaluate session contract health gate",
        "thegent_session_contract_health_gate",
    ),
    OperationEntry(
        Operation.GOVERN,
        "session-contract-health-report",
        "Session contract health report",
        "thegent_session_contract_health_report",
    ),
    OperationEntry(
        Operation.GOVERN,
        "session-contract-health-trend",
        "Session contract health trend",
        "thegent_session_contract_health_trend",
    ),
    OperationEntry(Operation.GOVERN, "history verify", "Verify run registry integrity", None),
    OperationEntry(Operation.GOVERN, "closure-pack", "Generate closure pack", None),
    # Recover
    OperationEntry(
        Operation.RECOVER, "dag recover", "Recovery actions (retry-failed, clear-stuck, reset-retries)", None
    ),
    OperationEntry(Operation.RECOVER, "dag rollback", "Rollback to checkpoint", None),
    OperationEntry(Operation.RECOVER, "dag reconcile", "Reconcile stuck DAG tasks", None),
    OperationEntry(Operation.RECOVER, "stop", "Stop background session", "thegent_stop"),
    OperationEntry(Operation.RECOVER, "archive", "Archive old sessions", None),
    # Observe
    OperationEntry(Operation.OBSERVE, "ps", "List background sessions", "thegent_ps"),
    OperationEntry(Operation.OBSERVE, "status", "Session status", "thegent_status"),
    OperationEntry(Operation.OBSERVE, "logs", "Session logs", "thegent_logs"),
    OperationEntry(Operation.OBSERVE, "inspect", "Status and logs for sessions", "thegent_inspect"),
    OperationEntry(Operation.OBSERVE, "cockpit", "Operator cockpit summary", None),
    OperationEntry(Operation.OBSERVE, "history list", "Execution history", None),
    OperationEntry(Operation.OBSERVE, "history events", "Raw telemetry events", None),
    OperationEntry(Operation.OBSERVE, "benchmark", "Orchestration performance metrics", None),
    OperationEntry(Operation.OBSERVE, "feedback", "Provide feedback for run", None),
    OperationEntry(Operation.OBSERVE, "list-agents", "List available agents", "thegent_list_agents"),
    OperationEntry(Operation.OBSERVE, "list-droids", "List droids", "thegent_list_droids"),
    OperationEntry(Operation.OBSERVE, "list-models", "List models by provider", "thegent_list_models"),
    OperationEntry(Operation.OBSERVE, "wait", "Wait for session completion", "thegent_wait"),
    # Plan
    OperationEntry(Operation.PLAN, "dag list", "List DAG tasks", "thegent_dag_list"),
    OperationEntry(Operation.PLAN, "dag validate", "Validate DAG", None),
    OperationEntry(Operation.PLAN, "dag ready", "List ready tasks", None),
    OperationEntry(Operation.PLAN, "dag status", "DAG status", None),
    OperationEntry(Operation.PLAN, "dag checkpoint", "Create checkpoint", None),
    OperationEntry(Operation.PLAN, "dag checkpoints", "List checkpoints", None),
    OperationEntry(Operation.PLAN, "dag probe", "Probe DAG against baseline", None),
    OperationEntry(Operation.PLAN, "plan analyze", "PERT, resource contention, continuity risk overlays", None),
    OperationEntry(Operation.PLAN, "resolve-model-route", "Resolve model route", "thegent_resolve_model_route"),
    OperationEntry(Operation.PLAN, "models contract", "Model contract schema", None),
    OperationEntry(Operation.PLAN, "modes", "List multi-agent orchestration modes", "thegent_list_modes"),
]


def get_operations_by_type(op: Operation) -> list[OperationEntry]:
    """Return all entries for an operation type."""
    return [e for e in OPERATION_MAP if e.operation == op]


def list_operations() -> dict[str, list[dict[str, Any]]]:
    """Return operations grouped by type for CLI/MCP."""
    result: dict[str, list[dict[str, Any]]] = {}
    for op in Operation:
        entries = get_operations_by_type(op)
        result[op.value] = [
            {"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries
        ]
    return result
