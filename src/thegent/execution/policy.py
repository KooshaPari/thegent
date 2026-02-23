"""Execution policy and governance.

Domain: Policy
Classes:
- PolicyEngine: Policy evaluation engine
- ProviderScorer: Provider scoring
- TrustBoundaryValidator: Trust boundary validation
- Auditor: Execution auditing
- EvidenceLinter: Evidence linting
- OverrideRegistry: Policy override management
- KPIManager: KPI tracking
"""

from datetime import datetime
from typing import Any


class KPIManager:
    """Manages KPI tracking for executions."""
    
    def __init__(self) -> None:
        self._kpis: dict[str, list[float]] = {}
    
    def record(self, kpi_name: str, value: float) -> None:
        """Record a KPI value."""
        if kpi_name not in self._kpis:
            self._kpis[kpi_name] = []
        self._kpis[kpi_name].append(value)
    
    def get_average(self, kpi_name: str) -> float:
        """Get average for a KPI."""
        values = self._kpis.get(kpi_name, [])
        return sum(values) / len(values) if values else 0.0
    
    def get_stats(self, kpi_name: str) -> dict[str, float]:
        """Get statistics for a KPI."""
        values = self._kpis.get(kpi_name, [])
        if not values:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0}
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }


class PolicyEngine:
    """Evaluates execution policies."""

    def __init__(self) -> None:
        self._policies: list[dict[str, Any]] = []

    def add_policy(self, policy: dict[str, Any]) -> None:
        """Add a policy."""
        self._policies.append(policy)

    def evaluate(self, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate policies against context."""
        results = []
        for policy in self._policies:
            result = self._check_policy(policy, context)
            results.append(result)
        return {
            "passed": all(r["passed"] for r in results),
            "results": results,
        }

    def _check_policy(self, policy: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Check a single policy."""
        rule = policy.get("rule", {})
        field = rule.get("field")
        operator = rule.get("operator")
        value = rule.get("value")

        actual = context.get(field)
        passed = self._compare(actual, operator, value)
        return {
            "policy_id": policy.get("id"),
            "passed": passed,
            "expected": value,
            "actual": actual,
        }

    def _compare(self, actual: Any, operator: str, expected: Any) -> bool:
        """Compare values."""
        ops = {
            "eq": lambda a, e: a == e,
            "ne": lambda a, e: a != e,
            "gt": lambda a, e: a > e,
            "gte": lambda a, e: a >= e,
            "lt": lambda a, e: a < e,
            "lte": lambda a, e: a <= e,
            "in": lambda a, e: a in e,
        }
        return ops.get(operator, lambda a, e: True)(actual, expected)


class ProviderScorer:
    """Scores execution providers."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record_score(self, provider: str, score: float) -> None:
        """Record a provider score."""
        if provider not in self._scores:
            self._scores[provider] = []
        self._scores[provider].append(score)

    def get_average(self, provider: str) -> float:
        """Get average score for provider."""
        scores = self._scores.get(provider, [])
        return sum(scores) / len(scores) if scores else 0.0

    def get_ranking(self) -> list[tuple[str, float]]:
        """Get provider ranking."""
        return sorted(
            [(p, self.get_average(p)) for p in self._scores],
            key=lambda x: x[1],
            reverse=True,
        )


class TrustBoundaryValidator:
    """Validates trust boundaries."""

    def __init__(self) -> None:
        self._boundaries: dict[str, set[str]] = {}

    def add_boundary(self, domain: str, allowed_origins: list[str]) -> None:
        """Add a trust boundary."""
        self._boundaries[domain] = set(allowed_origins)

    def is_valid(self, domain: str, origin: str) -> bool:
        """Check if origin is within boundary."""
        allowed = self._boundaries.get(domain, set())
        return origin in allowed or "*" in allowed


class Auditor:
    """Audits execution operations."""

    def __init__(self) -> None:
        self._logs: list[dict[str, Any]] = []

    def log(self, operation: str, details: dict[str, Any]) -> None:
        """Log an audit entry."""
        self._logs.append({
            "operation": operation,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        })

    def get_logs(self, operation: str | None = None) -> list[dict[str, Any]]:
        """Get audit logs."""
        if operation:
            return [l for l in self._logs if l["operation"] == operation]
        return self._logs.copy()


class EvidenceLinter:
    """Lints execution evidence."""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []

    def add_rule(self, rule: dict[str, Any]) -> None:
        """Add a lint rule."""
        self._rules.append(rule)

    def lint(self, evidence: dict[str, Any]) -> dict[str, Any]:
        """Lint evidence against rules."""
        issues = []
        for rule in self._rules:
            if not self._check_rule(rule, evidence):
                issues.append({
                    "rule_id": rule.get("id"),
                    "message": rule.get("message", "Rule violated"),
                })
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    def _check_rule(self, rule: dict[str, Any], evidence: dict[str, Any]) -> bool:
        """Check a single rule."""
        field = rule.get("field")
        required = rule.get("required", False)
        if required and field not in evidence:
            return False
        return True


class OverrideRegistry:
    """Registry for policy overrides."""

    def __init__(self) -> None:
        self._overrides: dict[str, dict[str, Any]] = {}

    def add_override(self, policy_id: str, override: dict[str, Any]) -> None:
        """Add a policy override."""
        override["created_at"] = datetime.now().isoformat()
        self._overrides[policy_id] = override

    def get_override(self, policy_id: str) -> dict[str, Any] | None:
        """Get override for policy."""
        return self._overrides.get(policy_id)

    def is_overridden(self, policy_id: str) -> bool:
        """Check if policy is overridden."""
        return policy_id in self._overrides


__all__ = [
    "Auditor",
    "EvidenceLinter",
    "KPIManager",
    "OverrideRegistry",
    "PolicyEngine",
    "ProviderScorer",
    "TrustBoundaryValidator",
]
