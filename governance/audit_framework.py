"""
Comprehensive Audit Framework

Provides automated auditing capabilities for projects with multiple audit types.
"""

import json
import logging
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class AuditType(Enum):
    """Types of audits."""

    CODE_REVIEW = "code_review"
    DEPENDENCY_AUDIT = "dependency_audit"
    SECURITY_AUDIT = "security_audit"
    DOCUMENTATION_AUDIT = "documentation_audit"
    PERFORMANCE_AUDIT = "performance_audit"
    COMPLIANCE_AUDIT = "compliance_audit"
    QUALITY_AUDIT = "quality_audit"
    ARCHITECTURE_AUDIT = "architecture_audit"
    ACCESSIBILITY_AUDIT = "accessibility_audit"
    TESTING_AUDIT = "testing_audit"


class AuditSeverity(Enum):
    """Audit finding severity."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AuditStatus(Enum):
    """Audit status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AuditFinding:
    """Individual audit finding."""

    id: str
    audit_type: AuditType
    severity: AuditSeverity
    title: str
    description: str
    file_path: Path | None = None
    line_number: int | None = None
    rule_id: str | None = None
    recommendation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    resolved: bool = False
    resolved_at: datetime | None = None
    resolved_by: str | None = None


@dataclass
class AuditResult:
    """Result of an audit."""

    audit_type: AuditType
    status: AuditStatus
    started_at: datetime
    completed_at: datetime | None = None
    findings: list[AuditFinding] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_severity_counts(self) -> dict[str, int]:
        """Get counts by severity."""
        counts = defaultdict(int)
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return dict(counts)

    def get_critical_findings(self) -> list[AuditFinding]:
        """Get critical findings."""
        return [f for f in self.findings if f.severity == AuditSeverity.CRITICAL]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "audit_type": self.audit_type.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "findings": [
                {
                    "id": f.id,
                    "severity": f.severity.value,
                    "title": f.title,
                    "description": f.description,
                    "file_path": str(f.file_path) if f.file_path else None,
                    "line_number": f.line_number,
                    "rule_id": f.rule_id,
                    "recommendation": f.recommendation,
                    "detected_at": f.detected_at.isoformat(),
                    "resolved": f.resolved,
                }
                for f in self.findings
            ],
            "summary": {
                **self.summary,
                "severity_counts": self.get_severity_counts(),
                "total_findings": len(self.findings),
                "critical_findings": len(self.get_critical_findings()),
            },
            "metadata": self.metadata,
        }


class AuditFramework:
    """Comprehensive audit framework."""

    def __init__(self, project_path: Path) -> None:
        self.project_path = Path(project_path).resolve()
        self.audit_results: dict[AuditType, list[AuditResult]] = defaultdict(list)
        self.audit_config: dict | None = None
        self._load_config()

    def _load_config(self):
        """Load audit configuration."""
        config_path = self.project_path / "governance" / "audit-config.yaml"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    self.audit_config = yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Error loading audit config: {e}")
                self.audit_config = {}
        else:
            self.audit_config = {}

    def run_audit(self, audit_type: AuditType) -> AuditResult:
        """Run a specific audit."""
        result = AuditResult(
            audit_type=audit_type,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        try:
            if audit_type == AuditType.CODE_REVIEW:
                result = self._run_code_review_audit()
            elif audit_type == AuditType.DEPENDENCY_AUDIT:
                result = self._run_dependency_audit()
            elif audit_type == AuditType.SECURITY_AUDIT:
                result = self._run_security_audit()
            elif audit_type == AuditType.DOCUMENTATION_AUDIT:
                result = self._run_documentation_audit()
            elif audit_type == AuditType.PERFORMANCE_AUDIT:
                result = self._run_performance_audit()
            elif audit_type == AuditType.COMPLIANCE_AUDIT:
                result = self._run_compliance_audit()
            elif audit_type == AuditType.QUALITY_AUDIT:
                result = self._run_quality_audit()
            elif audit_type == AuditType.ARCHITECTURE_AUDIT:
                result = self._run_architecture_audit()
            elif audit_type == AuditType.ACCESSIBILITY_AUDIT:
                result = self._run_accessibility_audit()
            elif audit_type == AuditType.TESTING_AUDIT:
                result = self._run_testing_audit()

            result.status = AuditStatus.COMPLETED
            result.completed_at = datetime.now(tz=UTC)

        except Exception as e:
            logger.error(f"Error running {audit_type.value} audit: {e}")
            result.status = AuditStatus.FAILED
            result.metadata["error"] = str(e)

        self.audit_results[audit_type].append(result)
        return result

    def run_all_audits(self) -> dict[AuditType, AuditResult]:
        """Run all configured audits."""
        results = {}

        if not self.audit_config:
            logger.warning("No audit configuration found")
            return results

        audits = self.audit_config.get("audits", {})
        for audit_name, audit_config in audits.items():
            if not audit_config.get("enabled", False):
                continue

            try:
                audit_type = AuditType(audit_name)
                result = self.run_audit(audit_type)
                results[audit_type] = result
            except ValueError:
                logger.warning(f"Unknown audit type: {audit_name}")

        return results

    def _run_code_review_audit(self) -> AuditResult:
        """Run code review audit."""
        result = AuditResult(
            audit_type=AuditType.CODE_REVIEW,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
        ]

        for py_file in self.project_path.rglob("*.py"):
            self._scan_file_for_secrets(py_file, findings, secret_patterns)

        # Check for TODO/FIXME comments
        for py_file in self.project_path.rglob("*.py"):
            self._scan_file_for_todos(py_file, findings)

        result.findings = findings
        result.summary = {
            "files_scanned": len(list(self.project_path.rglob("*.py"))),
            "findings_count": len(findings),
        }

        return result

    def _scan_file_for_secrets(self, py_file: Path, findings: list[AuditFinding], patterns: list[tuple[str, str]]) -> None:
        """Scan a single file for hardcoded secrets."""
        try:
            content = py_file.read_text()
            for pattern, title in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    findings.append(
                        AuditFinding(
                            id=f"secret-{len(findings)}",
                            audit_type=AuditType.CODE_REVIEW,
                            severity=AuditSeverity.CRITICAL,
                            title=title,
                            description=f"Potential hardcoded secret found in {py_file.name}",
                            file_path=py_file,
                            line_number=line_num,
                            recommendation="Move secrets to environment variables or secret management",
                        )
                    )
        except Exception:
            pass

    def _scan_file_for_todos(self, py_file: Path, findings: list[AuditFinding]) -> None:
        """Scan a single file for TODO/FIXME comments."""
        try:
            content = py_file.read_text()
            for i, line in enumerate(content.split("\n"), 1):
                if re.search(r"TODO|FIXME|XXX|HACK", line, re.IGNORECASE):
                    findings.append(
                        AuditFinding(
                            id=f"todo-{len(findings)}",
                            audit_type=AuditType.CODE_REVIEW,
                            severity=AuditSeverity.LOW,
                            title="TODO/FIXME comment found",
                            description=line.strip(),
                            file_path=py_file,
                            line_number=i,
                            recommendation="Address technical debt items",
                        )
                    )
        except Exception:
            pass

    def _run_dependency_audit(self) -> AuditResult:
        """Run dependency audit."""
        result = AuditResult(
            audit_type=AuditType.DEPENDENCY_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for outdated dependencies
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                # Try to run pip-audit or safety
                proc = subprocess.run(
                    ["pip-audit", "--requirement", str(req_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                if proc.returncode != 0 and "vulnerability" in proc.stdout.lower():
                    findings.append(
                        AuditFinding(
                            id="dep-vuln-1",
                            audit_type=AuditType.DEPENDENCY_AUDIT,
                            severity=AuditSeverity.HIGH,
                            title="Dependency vulnerabilities found",
                            description=proc.stdout[:500],
                            recommendation="Update vulnerable dependencies",
                        )
                    )
            except Exception as e:
                logger.warning(f"Could not run dependency audit: {e}")

        result.findings = findings
        result.summary = {
            "dependencies_checked": req_file.exists(),
        }

        return result

    def _run_security_audit(self) -> AuditResult:
        """Run security audit."""
        result = AuditResult(
            audit_type=AuditType.SECURITY_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for common security issues
        security_checks = [
            (r"eval\s*\(", "Use of eval()", AuditSeverity.HIGH),
            (r"exec\s*\(", "Use of exec()", AuditSeverity.MEDIUM),
            (r"shell\s*=\s*True", "Shell injection risk", AuditSeverity.HIGH),
            (r"pickle\.loads", "Unsafe pickle usage", AuditSeverity.HIGH),
        ]

        for py_file in self.project_path.rglob("*.py"):
            self._scan_file_for_security_risks(py_file, findings, security_checks)

        result.findings = findings
        result.summary = {
            "security_risks_found": len(findings),
        }

        return result

    def _scan_file_for_security_risks(
        self, py_file: Path, findings: list[AuditFinding], checks: list[tuple[str, str, AuditSeverity]]
    ) -> None:
        """Scan a single file for security risks."""
        try:
            content = py_file.read_text()
            for pattern, title, severity in checks:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    findings.append(
                        AuditFinding(
                            id=f"sec-{len(findings)}",
                            audit_type=AuditType.SECURITY_AUDIT,
                            severity=severity,
                            title=title,
                            description=f"Security risk in {py_file.name}",
                            file_path=py_file,
                            line_number=line_num,
                            recommendation="Review and secure this code",
                        )
                    )
        except Exception:
            pass

    def _run_documentation_audit(self) -> AuditResult:
        """Run documentation audit."""
        result = AuditResult(
            audit_type=AuditType.DOCUMENTATION_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for missing README
        if not (self.project_path / "README.md").exists():
            findings.append(
                AuditFinding(
                    id="doc-readme",
                    audit_type=AuditType.DOCUMENTATION_AUDIT,
                    severity=AuditSeverity.HIGH,
                    title="Missing README.md",
                    description="Project lacks a README file",
                    recommendation="Create comprehensive README.md",
                )
            )

        # Check for outdated documentation
        docs_dir = self.project_path / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                self._check_stale_documentation(doc_file, findings)

        result.findings = findings
        result.summary = {
            "docs_checked": docs_dir.exists() or 0,
        }

        return result

    def _check_stale_documentation(self, doc_file: Path, findings: list[AuditFinding]) -> None:
        """Check if documentation is potentially outdated."""
        try:
            stat = doc_file.stat()
            age_days = (datetime.now(tz=timezone.utc) - datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)).days
            if age_days > 180:  # 6 months
                findings.append(
                    AuditFinding(
                        id=f"doc-stale-{len(findings)}",
                        audit_type=AuditType.DOCUMENTATION_AUDIT,
                        severity=AuditSeverity.MEDIUM,
                        title="Potentially outdated documentation",
                        description=f"{doc_file.name} last modified {age_days} days ago",
                        file_path=doc_file,
                        recommendation="Review and update documentation",
                    )
                )
        except Exception:
            pass

    def _run_performance_audit(self) -> AuditResult:
        """Run performance audit."""
        result = AuditResult(
            audit_type=AuditType.PERFORMANCE_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for performance anti-patterns
        perf_patterns = [
            (r"for\s+\w+\s+in\s+range\(len\(", "Inefficient loop", AuditSeverity.LOW),
            (r"\.append\(.*\)\s*for\s+.*\s+in\s+", "List comprehension preferred", AuditSeverity.LOW),
        ]

        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern, title, severity in perf_patterns:
                    if re.search(pattern, content):
                        findings.append(
                            AuditFinding(
                                id=f"perf-{len(findings)}",
                                audit_type=AuditType.PERFORMANCE_AUDIT,
                                severity=severity,
                                title=title,
                                description=f"Performance optimization opportunity in {py_file.name}",
                                file_path=py_file,
                                recommendation="Consider optimization",
                            )
                        )
            except Exception:
                pass

        result.findings = findings
        result.summary = {
            "performance_issues": len(findings),
        }

        return result

    def _run_compliance_audit(self) -> AuditResult:
        """Run compliance audit."""
        result = AuditResult(
            audit_type=AuditType.COMPLIANCE_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for LICENSE
        if not (self.project_path / "LICENSE").exists():
            findings.append(
                AuditFinding(
                    id="compliance-license",
                    audit_type=AuditType.COMPLIANCE_AUDIT,
                    severity=AuditSeverity.HIGH,
                    title="Missing LICENSE file",
                    description="Project lacks a license file",
                    recommendation="Add LICENSE file",
                )
            )

        # Check for CONTRIBUTING
        if not (self.project_path / "CONTRIBUTING.md").exists():
            findings.append(
                AuditFinding(
                    id="compliance-contributing",
                    audit_type=AuditType.COMPLIANCE_AUDIT,
                    severity=AuditSeverity.MEDIUM,
                    title="Missing CONTRIBUTING.md",
                    description="Project lacks contribution guidelines",
                    recommendation="Add CONTRIBUTING.md",
                )
            )

        result.findings = findings
        result.summary = {
            "compliance_items_checked": 2,
        }

        return result

    def _run_quality_audit(self) -> AuditResult:
        """Run quality audit."""
        result = AuditResult(
            audit_type=AuditType.QUALITY_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for test coverage
        test_dir = self.project_path / "tests"
        if not test_dir.exists():
            findings.append(
                AuditFinding(
                    id="quality-tests",
                    audit_type=AuditType.QUALITY_AUDIT,
                    severity=AuditSeverity.HIGH,
                    title="Missing test directory",
                    description="Project lacks test infrastructure",
                    recommendation="Add tests/ directory",
                )
            )

        result.findings = findings
        result.summary = {
            "quality_checks": len(findings),
        }

        return result

    def _run_architecture_audit(self) -> AuditResult:
        """Run architecture audit."""
        result = AuditResult(
            audit_type=AuditType.ARCHITECTURE_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check for architecture documentation
        docs_dir = self.project_path / "docs"
        arch_docs = ["architecture.md", "ARCHITECTURE.md", "design.md", "DESIGN.md"]

        has_arch_doc = False
        if docs_dir.exists():
            for arch_doc in arch_docs:
                if (docs_dir / arch_doc).exists():
                    has_arch_doc = True
                    break

        if not has_arch_doc:
            findings.append(
                AuditFinding(
                    id="arch-docs",
                    audit_type=AuditType.ARCHITECTURE_AUDIT,
                    severity=AuditSeverity.MEDIUM,
                    title="Missing architecture documentation",
                    description="Project lacks architecture documentation",
                    recommendation="Create architecture.md",
                )
            )

        result.findings = findings
        result.summary = {
            "architecture_checks": len(findings),
        }

        return result

    def _run_accessibility_audit(self) -> AuditResult:
        """Run accessibility audit."""
        result = AuditResult(
            audit_type=AuditType.ACCESSIBILITY_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        # Placeholder for accessibility checks
        result.findings = []
        result.summary = {"accessibility_checks": 0}

        return result

    def _run_testing_audit(self) -> AuditResult:
        """Run testing audit."""
        result = AuditResult(
            audit_type=AuditType.TESTING_AUDIT,
            status=AuditStatus.RUNNING,
            started_at=datetime.now(tz=UTC),
        )

        findings = []

        # Check test coverage
        test_files = list(self.project_path.rglob("test_*.py")) + list(self.project_path.rglob("*_test.py"))

        if len(test_files) == 0:
            findings.append(
                AuditFinding(
                    id="test-none",
                    audit_type=AuditType.TESTING_AUDIT,
                    severity=AuditSeverity.HIGH,
                    title="No test files found",
                    description="Project lacks test files",
                    recommendation="Add test files",
                )
            )

        result.findings = findings
        result.summary = {
            "test_files_found": len(test_files),
        }

        return result

    def save_results(self, output_path: Path | None = None):
        """Save audit results."""
        if output_path is None:
            output_path = self.project_path / "governance" / "audit-results.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        all_results = {}
        for audit_type, results in self.audit_results.items():
            all_results[audit_type.value] = [r.to_dict() for r in results]

        with open(output_path, "w") as f:
            json.dump(
                {
                    "project_path": str(self.project_path),
                    "generated_at": datetime.now(tz=UTC).isoformat(),
                    "audit_results": all_results,
                },
                f,
                indent=2,
            )

    def generate_report(self) -> dict:
        """Generate comprehensive audit report."""
        all_findings = []
        for results in self.audit_results.values():
            for result in results:
                all_findings.extend(result.findings)

        severity_counts = defaultdict(int)
        for finding in all_findings:
            severity_counts[finding.severity.value] += 1

        return {
            "generated_at": datetime.now(tz=UTC).isoformat(),
            "total_findings": len(all_findings),
            "severity_counts": dict(severity_counts),
            "critical_findings": len([f for f in all_findings if f.severity == AuditSeverity.CRITICAL]),
            "by_audit_type": {audit_type.value: len(results) for audit_type, results in self.audit_results.items()},
            "recommendations": self._generate_recommendations(all_findings),
        }

    def _generate_recommendations(self, findings: list[AuditFinding]) -> list[str]:
        """Generate recommendations from findings."""
        recommendations = []

        critical = [f for f in findings if f.severity == AuditSeverity.CRITICAL]
        if critical:
            recommendations.append(f"Address {len(critical)} critical findings immediately")

        security = [f for f in findings if f.audit_type == AuditType.SECURITY_AUDIT]
        if security:
            recommendations.append(f"Review {len(security)} security findings")

        return recommendations
