"""Session contract listing and audit implementation.

Extracted from session_health_impl.py as part of WL-120 LOC Reduction Program.
Contains:
- _extract_blocked_ratio: helper for blocked ratio extraction
- list_session_contracts_impl: list sessions with contract metadata and quality signal
- session_contract_audit_impl: session contract audit rows with filtering and summary
"""

from __future__ import annotations

import contextlib
import logging
from typing import Any

_log = logging.getLogger(__name__)

__all__ = [
    "_extract_blocked_ratio",
    "list_session_contracts_impl",
    "session_contract_audit_impl",
]


def _extract_blocked_ratio(ratios: list[float], snap: dict[str, Any] | None) -> None:
    """Extract blocked ratio from a single snapshot safely."""
    with contextlib.suppress(TypeError, ValueError):
        ratios.append(float((snap or {}).get("blocked_ratio", 0.0)))


def list_session_contracts_impl(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
) -> list[dict[str, Any]]:
    """
    Return sessions with route-request/route-contract metadata and contract quality signal.
    """
    from phenotype_thegent_cli.cli.commands import impl as cli_impl

    def _alignment_issues(
        route_request: dict[str, Any] | None,
        route_contract: dict[str, Any] | None,
    ) -> list[str]:
        if not strict or not route_request or not route_contract:
            return []

        issues: list[str] = []
        requested_provider = route_request.get("requested_provider_hint")
        contract_provider = route_contract.get("provider")
        if requested_provider is not None and contract_provider is not None and requested_provider != contract_provider:
            issues.append("misalign:provider_hint")

        requested_alias = route_request.get("resolved_model_alias") or route_request.get("resolved_alias")
        contract_alias = route_contract.get("model_alias")
        if requested_alias is not None and contract_alias is not None and requested_alias != contract_alias:
            issues.append("misalign:resolved_alias")

        resolved_agent = route_request.get("resolved_agent")
        if resolved_agent is not None and contract_provider is not None and resolved_agent != contract_provider:
            issues.append("misalign:resolved_agent")

        return issues

    rows = cli_impl.ps_impl(owner=owner, all=all, include_contract=True)
    contracts: list[dict[str, Any]] = []

    for row in rows:
        route_request = row.get("route_request")
        route_contract = row.get("route_contract")
        request_obj = route_request if isinstance(route_request, dict) else None
        contract_obj = route_contract if isinstance(route_contract, dict) else None
        request_present = request_obj is not None
        contract_present = contract_obj is not None

        contract_issues: list[str] = []
        if contract_obj is not None:
            required_contract_fields = ("provider", "model_alias", "backend_type", "priority")
            for key in required_contract_fields:
                if contract_obj.get(key) is None:
                    contract_issues.append(f"missing_contract:{key}")
            if contract_obj.get("schema_version") is None:
                contract_issues.append("missing_contract:schema_version")
        if request_obj is not None:
            if not request_obj.get("requested_model"):
                contract_issues.append("missing_request:requested_model")
            if request_obj.get("policy") not in {"prefer_direct", "prefer_proxy", "failover"}:
                contract_issues.append("missing_request:policy")

        if not request_present and not contract_present:
            state = "untracked"
        elif request_present and not contract_present:
            state = "request_only"
        elif contract_present and not request_present:
            state = "contract_only"
        elif contract_issues:
            state = "partial"
        else:
            state = "complete"

        alignment_issues = _alignment_issues(request_obj, contract_obj)
        contract_issues.extend(alignment_issues)

        if not request_present or not contract_present:
            contract_health = "missing"
        elif any(issue.startswith("misalign:") for issue in alignment_issues):
            contract_health = "error"
        elif contract_issues:
            contract_health = "warning"
        else:
            contract_health = "healthy"

        contracts.append(
            {
                "session_id": row.get("id", ""),
                "agent": row.get("agent", ""),
                "owner": row.get("owner", ""),
                "pid": row.get("pid", 0),
                "status": row.get("status", "unknown"),
                "started_at_utc": row.get("started_at_utc", ""),
                "route_request": request_obj,
                "route_contract": contract_obj,
                "contract_state": state,
                "route_request_present": request_present,
                "route_contract_present": contract_present,
                "contract_health": contract_health,
                "strict_checks_enabled": strict,
                "contract_issues": contract_issues,
                "requested_model": request_obj.get("requested_model") if request_obj is not None else None,
                "requested_provider_hint": request_obj.get("requested_provider_hint")
                if request_obj is not None
                else None,
                "resolved_model_alias": (request_obj.get("resolved_model_alias") or request_obj.get("resolved_alias"))
                if request_obj is not None
                else None,
                "policy": request_obj.get("policy") if request_obj is not None else None,
            }
        )

    return contracts


def session_contract_audit_impl(
    owner: str | None = None,
    all: bool = False,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    """
    Return session contract audit rows with optional filtering and summary.
    """
    rows = list_session_contracts_impl(owner=owner, all=all, strict=strict)
    if missing_only:
        rows = [row for row in rows if row.get("contract_state") != "complete"]

    states: dict[str, int] = {}
    for row in rows:
        state = str(row.get("contract_state", "unknown"))
        states[state] = states.get(state, 0) + 1

    health: dict[str, int] = {"healthy": 0, "warning": 0, "error": 0, "missing": 0}
    for row in rows:
        key = str(row.get("contract_health", "warning"))
        health[key] = health.get(key, 0) + 1

    summary = {
        "total": len(rows),
        "complete": states.get("complete", 0),
        "partial": states.get("partial", 0),
        "request_only": states.get("request_only", 0),
        "contract_only": states.get("contract_only", 0),
        "untracked": states.get("untracked", 0),
        "strict_checks_enabled": strict,
        "health": health,
    }
    if summary_only:
        return {"rows": [], "summary": summary}
    return {"rows": rows, "summary": summary}
