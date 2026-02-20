"""SY-002: System Audit Framework for thegent.
Audit configuration, dependencies, security, and performance.
"""

import logging
import platform
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class AuditSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditIssue:
    """A single issue found during an audit."""

    id: str
    title: str
    description: str
    severity: str = AuditSeverity.MEDIUM
    component: str = "system"
    remediation: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "component": self.component,
            "remediation": self.remediation,
            "data": self.data,
            "timestamp": self.timestamp,
        }


@dataclass
class AuditResult:
    """Result of a full system audit."""

    issues: list[AuditIssue] = field(default_factory=list)
    start_time: float = field(default_factory=lambda: datetime.now(UTC).timestamp())
    end_time: float | None = None
    summary: dict[str, Any] = field(default_factory=dict)

    def add_issue(self, issue: AuditIssue):
        self.issues.append(issue)

    def complete(self):
        self.end_time = datetime.now(UTC).timestamp()
        self.summary = {
            "total_issues": len(self.issues),
            "critical": len([i for i in self.issues if i.severity == AuditSeverity.CRITICAL]),
            "high": len([i for i in self.issues if i.severity == AuditSeverity.HIGH]),
            "medium": len([i for i in self.issues if i.severity == AuditSeverity.MEDIUM]),
            "low": len([i for i in self.issues if i.severity == AuditSeverity.LOW]),
            "duration": self.end_time - self.start_time,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "issues": [i.to_dict() for i in self.issues],
            "start_time": datetime.fromtimestamp(self.start_time, UTC).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time, UTC).isoformat() if self.end_time else None,
        }


class AuditType(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    async def run(self, fix: bool = False) -> list[AuditIssue]:
        pass


class DoctorAuditType(AuditType):
    @property
    def name(self) -> str:
        return "doctor"

    @property
    def description(self) -> str:
        return "Run thegent doctor health checks."

    async def run(self, fix: bool = False) -> list[AuditIssue]:
        from thegent.doctor import (
            _check_configuration,
            _check_connectivity,
            _check_dependencies,
            _check_environment,
            _check_headless,
            _check_isolation,
            _check_mcp_tools,
            _check_nix,
            _check_process_leaks,
            _check_project_hints,
            _check_providers,
            _check_runtime_infrastructure,
            _check_sessions,
            _check_shell,
            _check_shim_binaries,
            run_doctor,
        )

        all_checks = [
            _check_dependencies,
            _check_configuration,
            _check_isolation,
            _check_connectivity,
            _check_environment,
            _check_shim_binaries,
            _check_shell,
            _check_nix,
            _check_providers,
            _check_headless,
            _check_runtime_infrastructure,
            _check_process_leaks,
            _check_mcp_tools,
            _check_sessions,
            _check_project_hints,
        ]

        issues = []

        def _run_check(check_func: callable) -> list[AuditIssue]:
            """Run a single doctor check and return any issues found."""
            check_issues = []
            try:
                results = check_func()
                for r in results:
                    if r.status in ("fail", "warn"):
                        severity = AuditSeverity.HIGH if r.status == "fail" else AuditSeverity.MEDIUM
                        check_issues.append(
                            AuditIssue(
                                id=f"doctor-{r.category}-{r.name}",
                                title=r.name,
                                description=r.message,
                                severity=severity,
                                component=r.category,
                                remediation=r.fix_hint,
                                data={"details": r.details},
                            )
                        )
            except Exception as e:
                _log.error(f"Doctor check {check_func.__name__} failed: {e}")
            return check_issues

        for check_func in all_checks:
            issues.extend(_run_check(check_func))

        if fix:
            run_doctor(fix=True)
        return issues


class ConfigAuditType(AuditType):
    @property
    def name(self) -> str:
        return "config"

    @property
    def description(self) -> str:
        return "Audit configuration drift and presence of necessary files."

    async def run(self, fix: bool = False) -> list[AuditIssue]:
        issues = []
        required_files = [
            ("CLAUDE.md", "Agent instructions source of truth"),
            ("AGENTS.md", "Platform-specific rules"),
            ("CONSTITUTION.yaml", "Agent governance rules"),
            ("mcp_servers.json", "MCP server configuration"),
        ]
        for file_name, desc in required_files:
            if not Path(file_name).exists():
                issues.append(
                    AuditIssue(
                        id=f"config-missing-{file_name}",
                        title=f"Missing configuration file: {file_name}",
                        description=f"{file_name} is required for {desc}.",
                        severity=AuditSeverity.HIGH,
                        component="config",
                        remediation=f"Create {file_name} from template or default values.",
                    )
                )
        return issues


class AuditRegistry:
    def __init__(self) -> None:
        self.audits: dict[str, AuditType] = {}

    def register(self, audit: AuditType):
        self.audits[audit.name] = audit

    def get_all_audits(self) -> list[AuditType]:
        return list(self.audits.values())


class SystemAuditFramework:
    def __init__(self, registry: AuditRegistry | None = None) -> None:
        self.registry = registry or global_audit_registry

    async def run_audit(self, names: list[str] | None = None, fix: bool = False) -> AuditResult:
        result = AuditResult()
        target_audits = (
            [a for a in self.registry.get_all_audits() if a.name in names] if names else self.registry.get_all_audits()
        )

        async def _run_audit(audit: AuditType) -> list[AuditIssue]:
            """Run a single audit and return issues."""
            try:
                return await audit.run(fix=fix)
            except Exception as e:
                return [
                    AuditIssue(
                        id=f"audit-failure-{audit.name}",
                        title=f"Audit Execution Failure: {audit.name}",
                        description=str(e),
                        severity=AuditSeverity.HIGH,
                        component=audit.name,
                    )
                ]

        for audit in target_audits:
            issues = await _run_audit(audit)
            for issue in issues:
                result.add_issue(issue)
        result.complete()
        return result


class PlanAuditType(AuditType):
    @property
    def name(self) -> str:
        return "plan"

    @property
    def description(self) -> str:
        return "Audit planning simulation overlays (PERT, resources, continuity)."

    async def run(self, fix: bool = False) -> list[AuditIssue]:
        from thegent.cli.commands.impl import plan_analyze_impl

        issues = []
        try:
            result = plan_analyze_impl(pert=True, resources=True, continuity=True)
            if "error" in result:
                return [
                    AuditIssue(
                        id="plan-error",
                        title="Plan Analysis Error",
                        description=result["error"],
                        severity=AuditSeverity.HIGH,
                        component="plan",
                    )
                ]

            if result.get("continuity", {}).get("risk_score", 0) > 0.7:
                issues.append(
                    AuditIssue(
                        id="plan-continuity-high-risk",
                        title="High Handoff Continuity Risk",
                        description=f"Continuity risk score is {result['continuity']['risk_score']}",
                        severity=AuditSeverity.HIGH,
                        component="plan",
                        remediation="Review handoff factors and score risk manually.",
                    )
                )

            # Add more issue mapping as needed
        except Exception as e:
            _log.error(f"Plan audit failed: {e}")

        return issues


class DagAuditType(AuditType):
    @property
    def name(self) -> str:
        return "dag"

    @property
    def description(self) -> str:
        return "Audit DAG for cycles, orphans, and stale state."

    async def run(self, fix: bool = False) -> list[AuditIssue]:
        from thegent.cli.commands.impl import _parse_dag_full, _resolve_cwd, _validate_dag

        issues = []
        try:
            cwd = _resolve_cwd(None)
            dag_path = cwd / ".factory" / "dag-session.md"
            if not dag_path.exists():
                return []

            doc = _parse_dag_full(dag_path)
            errors = _validate_dag(doc)
            for e in errors:
                issues.append(
                    AuditIssue(
                        id=f"dag-validation-{hash(e)}",
                        title="DAG Validation Error",
                        description=e,
                        severity=AuditSeverity.CRITICAL,
                        component="dag",
                        remediation="Run 'thegent plan validate' for more details.",
                    )
                )
        except Exception as e:
            _log.error(f"DAG audit failed: {e}")

        return issues


class InitiativeAuditType(AuditType):
    @property
    def name(self) -> str:
        return "initiative"

    @property
    def description(self) -> str:
        return "Audit initiative progress and alignment with PLAN.md."

    async def run(self, fix: bool = False) -> list[AuditIssue]:
        from thegent.cli.commands.cli_initiative import parse_plan_initiatives

        initiatives = parse_plan_initiatives(Path("PLAN.md"))
        issues = []

        if not initiatives:
            issues.append(
                AuditIssue(
                    id="initiative-missing-plan",
                    title="PLAN.md Not Found",
                    description="Master plan is missing or unparseable.",
                    severity=AuditSeverity.MEDIUM,
                    component="initiative",
                )
            )

        return issues


global_audit_registry = AuditRegistry()
global_audit_registry.register(DoctorAuditType())
global_audit_registry.register(ConfigAuditType())
global_audit_registry.register(PlanAuditType())
global_audit_registry.register(DagAuditType())
global_audit_registry.register(InitiativeAuditType())
