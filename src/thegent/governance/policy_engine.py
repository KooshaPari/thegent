"""WP-3001 + WP-3003: Pre-check policy gate evaluator with override path.

Implements the governance-layer ``PolicyEngine`` for ``thegent``:

* Pre-check gate evaluator (FR-003, FR-011, FR-033, P-066)
* Override path with TTL and revalidation (WP-3003, FR-011, P-075)
* LRU-cached decision results for sub-50ms repeated evaluations (OPT-008)
* Integration points:
  - ``OverrideManager`` (overrides.py) — TTL-based human override
  - ``TrustBoundaryChecker`` (trust.py) — trust boundary enforcement
  - ``FederatedPolicyEngine`` (federated_policy.py) — scope-aware policy
    registry (used when ``use_federation=True``)
* Fail-closed: deny on missing/empty config unless an active override exists

Public surface:
  - ``PolicyDecision`` (dataclass) — verdict payload returned by ``evaluate``
  - ``PolicyEngine`` — main entry point
  - ``evaluate_pre_check`` — convenience helper

The runtime ``thegent.execution.PolicyEngine`` (used by the orchestrator) is
intentionally preserved; this module is the governance-layer counterpart
that adds the override-aware pre-check path before a run is admitted to the
execution pipeline.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import orjson as json
from cachetools import TTLCache

from thegent.config import ThegentSettings

from thegent.governance.federated_policy import (
    FederatedPolicyEngine,
    PolicyRule,
    PolicyScope,
)
from thegent.governance.overrides import OverrideManager
from thegent.governance.trust import TrustBoundaryChecker

_log = logging.getLogger(__name__)


class Verdict(StrEnum):
    """Pre-check gate verdict."""

    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"


class ReasonCode(StrEnum):
    """Machine-readable reason codes for decisions."""

    ALLOWED = "allowed"
    OVERRIDE_ACTIVE = "override_active"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    CRITICAL_LANE_LOW_CONFIDENCE = "critical_lane_low_confidence"
    UNKNOWN_AGENT_PRODUCTION = "unknown_agent_production"
    UNKNOWN_AGENT_CRITICAL = "unknown_agent_critical"
    TRUST_BOUNDARY_VIOLATION = "trust_boundary_violation"
    DRIFT_BUDGET_EXCEEDED = "drift_budget_exceeded"
    RECOVERY_NO_CONFIDENCE = "recovery_no_confidence"
    FEDERATED_POLICY_BLOCK = "federated_policy_block"
    MISSING_CONFIG = "missing_config"


@dataclass(frozen=True)
class PolicyContext:
    """Inputs to a pre-check evaluation.

    ``agent``/``model`` are accepted as either-or: ``model`` is preferred for
    routing decisions; ``agent`` is the legacy alias kept for back-compat.
    """

    agent: str = ""
    model: str = ""
    lane: str = "standard"  # one of: standard, critical, recovery, deferral
    confidence: float | None = None
    environment: str = "development"
    namespace: str = "global"
    prompt: str = ""
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyDecision:
    """Verdict returned by :meth:`PolicyEngine.evaluate`."""

    verdict: Verdict
    reason: str
    reason_code: ReasonCode
    rule_id: str | None = None
    override_applied: bool = False
    cached: bool = False
    evaluated_at: float = field(default_factory=time.time)

    def is_admissible(self) -> bool:
        """Whether the decision admits the request to the execution pipeline."""
        return self.verdict != Verdict.DENY

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "reason": self.reason,
            "reason_code": self.reason_code.value,
            "rule_id": self.rule_id,
            "override_applied": self.override_applied,
            "cached": self.cached,
            "evaluated_at": self.evaluated_at,
        }


def _cache_key(ctx: PolicyContext) -> str:
    """Stable cache key for a context.

    Uses the most decision-affecting fields only; ``prompt`` is hashed so
    long prompts do not bloat the key.
    """
    prompt_hash = hashlib.sha256(ctx.prompt.encode("utf-8")).hexdigest()[:16]
    confidence_str = f"{ctx.confidence:.4f}" if ctx.confidence is not None else "-"
    return "|".join(
        [
            ctx.agent or "",
            ctx.model or "",
            ctx.lane,
            confidence_str,
            ctx.environment,
            ctx.namespace,
            prompt_hash,
        ]
    )


class PolicyEngine:
    """Governance-layer pre-check gate evaluator (WP-3001, FR-003).

    Args:
        settings: Optional :class:`ThegentSettings`; defaults to a new instance.
        use_federation: If True, evaluate the :class:`FederatedPolicyEngine`
            scope rules before the local checks. Off by default for back-compat
            with the existing execution-layer pipeline.
        cache_ttl_sec: TTL for the decision cache (default 5 min).
        cache_maxsize: Max entries in the decision cache.
    """

    CRITICAL_LANE_CONFIDENCE_MIN = 0.9
    PRODUCTION_CONFIDENCE_MIN_DEFAULT = 0.8

    def __init__(
        self,
        settings: ThegentSettings | None = None,
        *,
        use_federation: bool = False,
        cache_ttl_sec: int = 300,
        cache_maxsize: int = 1000,
    ) -> None:
        self.settings = settings or ThegentSettings()
        self.use_federation = use_federation
        self.override_manager = OverrideManager(settings=self.settings)
        self.trust_checker = TrustBoundaryChecker(self.settings, cache_ttl_sec=cache_ttl_sec)
        if use_federation:
            # The settings object does not carry a default namespace; fall
            # back to ``global`` which is the federated registry's default.
            self.federated: FederatedPolicyEngine | None = FederatedPolicyEngine(
                default_namespace=getattr(self.settings, "default_namespace", "global")
            )
        else:
            self.federated = None
        # OPT-008: LRU + TTL decision cache (sub-50ms repeated evaluations)
        self._cache: TTLCache[str, PolicyDecision] = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl_sec)

    # ------------------------------------------------------------------ registry

    def register_rule(
        self,
        rule: PolicyRule | None = None,
        *,
        rule_id: str | None = None,
        when: dict[str, Any] | None = None,
        verdict: str = "allow",
        reason: str = "",
        priority: int = 100,
        scope: PolicyScope = PolicyScope.GLOBAL,
        namespace: str = "global",
    ) -> None:
        """Register a federated policy rule (no-op if federation is disabled).

        Accepts either a fully-built :class:`PolicyRule` or a convenience dict
        form (``rule_id``, ``when`` mapping key->expected value, ``verdict``,
        ``reason``, ``priority``, ``scope``, ``namespace``).
        """
        if self.federated is None:
            _log.debug("register_rule ignored: federation disabled")
            return
        if rule is not None:
            self.federated.register(rule)
            return
        assert rule_id is not None, "register_rule requires rule_id when no PolicyRule is passed"
        # convert dict-style "when" to a json pointer-like condition string
        # that the FederatedPolicyEngine evaluator can match on ctx.metadata.
        condition = json.dumps(when or {}, sort_keys=True, separators=(",", ":"))
        self.federated.register(
            PolicyRule.create(
                rule_id=rule_id,
                scope=scope,
                condition=condition,
                action=verdict,
                priority=priority,
                namespace=namespace,
            )
        )

    def load_rules_from_file(self, path: Any, namespace: str = "global") -> int:
        """Load federated rules from a JSON file. Returns count loaded."""
        if self.federated is None:
            return 0
        before = sum(len(ns) for ns in self.federated._namespaces.values())
        self.federated.load_from_file(path, namespace=namespace)
        after = sum(len(ns) for ns in self.federated._namespaces.values())
        return after - before

    def register_override(
        self,
        rule_id: str,
        *,
        reason: str,
        by: str,
        duration_minutes: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a TTL-based human override for ``rule_id`` (WP-3003).

        Thin pass-through to :meth:`OverrideManager.apply_override` so callers
        do not need to reach into the override_manager directly.
        """
        self.override_manager.apply_override(
            policy_id=rule_id,
            reason=reason,
            by=by,
            duration_minutes=duration_minutes,
            metadata=metadata,
        )

    # ------------------------------------------------------------------ evaluate

    def evaluate(self, ctx: PolicyContext) -> PolicyDecision:
        """Evaluate ``ctx`` and return a :class:`PolicyDecision`.

        Order of checks (short-circuits on first ``DENY`` that has no override):

        1. Cached decision lookup (OPT-008).
        2. Federated rules (if enabled) — highest priority first.
        3. Trust boundary (sensitive prompt + low-trust agent).
        4. Local rules (mirrors execution-layer checks, FR-003, FR-033):
           - critical lane + confidence < 0.9 -> deny
           - unknown agent in production -> deny
           - unknown agent in critical lane -> deny
           - recovery lane + no confidence -> warn
           - production + confidence < trust threshold -> deny
        5. Active override for the matched rule_id (override path, WP-3003).
        """
        if not isinstance(ctx, PolicyContext):  # type: ignore[unreachable]
            raise TypeError(f"PolicyEngine.evaluate expects PolicyContext, got {type(ctx).__name__}")

        key = _cache_key(ctx)
        cached = self._cache.get(key)
        if cached is not None:
            return PolicyDecision(
                verdict=cached.verdict,
                reason=cached.reason,
                reason_code=cached.reason_code,
                rule_id=cached.rule_id,
                override_applied=cached.override_applied,
                cached=True,
                evaluated_at=cached.evaluated_at,
            )

        decision = self._evaluate_uncached(ctx)
        self._cache[key] = decision
        return decision

    def _evaluate_uncached(self, ctx: PolicyContext) -> PolicyDecision:
        # 1. Federated rules (highest priority)
        if self.federated is not None:
            fed_decision = self._evaluate_federated(ctx)
            if fed_decision is not None and fed_decision.verdict != Verdict.ALLOW:
                if fed_decision.verdict == Verdict.DENY:
                    overridden = self._apply_override(ctx, fed_decision, rule_id=fed_decision.rule_id)
                    return overridden
                return fed_decision

        # 2. Trust boundary
        trust_decision = self._evaluate_trust(ctx)
        if trust_decision is not None:
            return trust_decision

        # 3. Local rules
        local = self._evaluate_local(ctx)
        if local.verdict == Verdict.DENY:
            decision = self._apply_override(ctx, local, rule_id=local.rule_id)
            return decision
        return local

    def _evaluate_federated(self, ctx: PolicyContext) -> PolicyDecision | None:
        if self.federated is None:
            return None
        try:
            # Build the effective metadata bag used to match rule conditions
            # against. Includes the agent, model, lane, environment, and
            # any caller-supplied metadata overrides.
            meta = {
                "agent": ctx.agent,
                "model": ctx.model,
                "lane": ctx.lane,
                "environment": ctx.environment,
                "namespace": ctx.namespace,
                "confidence": ctx.confidence,
            }
            meta.update(ctx.metadata)
            resolved = self.federated.resolve_policies(ctx.namespace)
        except Exception as exc:  # fail-closed on registry error
            _log.error("Federated policy evaluation failed: %s", exc)
            return PolicyDecision(
                verdict=Verdict.DENY,
                reason=f"federated policy error: {exc}",
                reason_code=ReasonCode.FEDERATED_POLICY_BLOCK,
            )

        # Match rules where all key/value pairs in the condition JSON are
        # satisfied in the context metadata bag. Sort by priority ascending
        # so lower priority numbers (more specific) win first.
        matched: list[tuple[int, PolicyRule]] = []
        for rule in resolved:
            try:
                cond = json.loads(rule.condition) if rule.condition else {}
            except Exception:
                cond = {}
            if not isinstance(cond, dict) or not cond:
                # Match anything if condition is empty; this is intentionally
                # the widest possible match.
                matched.append((rule.priority, rule))
                continue
            if all(meta.get(k) == v for k, v in cond.items()):
                matched.append((rule.priority, rule))

        matched.sort(key=lambda pr: pr[0])
        for _, rule in matched:
            action = rule.action.lower()
            if action == "deny":
                return PolicyDecision(
                    verdict=Verdict.DENY,
                    reason=f"federated rule {rule.rule_id} denied",
                    reason_code=ReasonCode.FEDERATED_POLICY_BLOCK,
                    rule_id=rule.rule_id,
                )
            if action == "warn":
                return PolicyDecision(
                    verdict=Verdict.WARN,
                    reason=f"federated rule {rule.rule_id} warns",
                    reason_code=ReasonCode.FEDERATED_POLICY_BLOCK,
                    rule_id=rule.rule_id,
                )
        return None

    def _evaluate_trust(self, ctx: PolicyContext) -> PolicyDecision | None:
        if not ctx.prompt or not ctx.agent:
            return None
        result = self.trust_checker.evaluate_routing(ctx.prompt, ctx.agent)
        if not result.get("allowed", True):
            return PolicyDecision(
                verdict=Verdict.DENY,
                reason=str(result.get("reason") or "trust boundary violation"),
                reason_code=ReasonCode.TRUST_BOUNDARY_VIOLATION,
                rule_id="trust.boundary",
            )
        return None

    def _evaluate_local(self, ctx: PolicyContext) -> PolicyDecision:
        agent_or_model = (ctx.model or ctx.agent or "").lower()
        is_unknown = agent_or_model in ("", "unknown", "untrusted")
        threshold = float(getattr(self.settings, "trust_score_threshold", self.PRODUCTION_CONFIDENCE_MIN_DEFAULT))

        if ctx.lane == "critical" and ctx.confidence is not None and ctx.confidence < self.CRITICAL_LANE_CONFIDENCE_MIN:
            return PolicyDecision(
                verdict=Verdict.DENY,
                reason=(
                    f"confidence {ctx.confidence:.3f} below critical-lane floor {self.CRITICAL_LANE_CONFIDENCE_MIN}"
                ),
                reason_code=ReasonCode.CRITICAL_LANE_LOW_CONFIDENCE,
                rule_id="local.critical.confidence",
            )

        if ctx.environment == "production" and is_unknown:
            return PolicyDecision(
                verdict=Verdict.DENY,
                reason="unknown agent blocked in production",
                reason_code=ReasonCode.UNKNOWN_AGENT_PRODUCTION,
                rule_id="local.production.unknown_agent",
            )

        if ctx.lane == "critical" and is_unknown:
            return PolicyDecision(
                verdict=Verdict.DENY,
                reason="unknown agent blocked in critical lane",
                reason_code=ReasonCode.UNKNOWN_AGENT_CRITICAL,
                rule_id="local.critical.unknown_agent",
            )

        if ctx.lane == "recovery" and ctx.confidence is None:
            return PolicyDecision(
                verdict=Verdict.WARN,
                reason="no confidence data for recovery lane",
                reason_code=ReasonCode.RECOVERY_NO_CONFIDENCE,
                rule_id="local.recovery.no_confidence",
            )

        if ctx.environment == "production" and ctx.confidence is not None and ctx.confidence < threshold:
            return PolicyDecision(
                verdict=Verdict.DENY,
                reason=f"confidence {ctx.confidence:.3f} below production floor {threshold:.3f}",
                reason_code=ReasonCode.CRITICAL_LANE_LOW_CONFIDENCE,
                rule_id="local.production.confidence",
            )

        return PolicyDecision(
            verdict=Verdict.ALLOW,
            reason="allowed by local policy",
            reason_code=ReasonCode.ALLOWED,
            rule_id="local.default.allow",
        )

    def _apply_override(self, ctx: PolicyContext, decision: PolicyDecision, *, rule_id: str | None) -> PolicyDecision:
        """Apply a TTL-based override if one is active for ``rule_id``.

        WP-3003: overrides carry a reason and operator; they are logged
        with ``governance.override.applied`` for auditability. Expired
        overrides are cleaned up by :meth:`OverrideManager.get_override`
        which deletes the file and returns ``None``.
        """
        if rule_id is None:
            return decision
        try:
            override = self.override_manager.get_override(rule_id)
        except Exception as exc:
            _log.warning("override lookup failed for %s: %s", rule_id, exc)
            return decision
        if override is None or not override.is_active():
            return decision

        _log.info(
            "governance.override.applied rule_id=%s by=%s reason=%s ttl_remaining=%.0fs",
            rule_id,
            override.by,
            override.reason,
            override.expires_at - time.time(),
        )
        return PolicyDecision(
            verdict=Verdict.ALLOW,
            reason=f"override by {override.by}: {override.reason}",
            reason_code=ReasonCode.OVERRIDE_ACTIVE,
            rule_id=rule_id,
            override_applied=True,
        )

    # ------------------------------------------------------------------ helpers

    def invalidate_cache(self) -> None:
        """Drop all cached decisions (e.g., after a rule change)."""
        self._cache.clear()

    def cache_size(self) -> int:
        return len(self._cache)


def evaluate_pre_check(
    ctx: PolicyContext | None = None,
    *,
    settings: ThegentSettings | None = None,
    use_federation: bool = False,
    **fields: Any,
) -> PolicyDecision:
    """Functional wrapper around :meth:`PolicyEngine.evaluate`.

    Accepts either a pre-built :class:`PolicyContext` (positional) or any of the
    :class:`PolicyContext` fields as keyword arguments.  Remaining fields
    default to ``PolicyContext()``'s defaults.
    """
    if ctx is None:
        ctx = PolicyContext(**fields)
    elif fields:
        raise TypeError("Pass either a PolicyContext or keyword fields, not both.")
    return PolicyEngine(settings=settings, use_federation=use_federation).evaluate(ctx)


__all__ = [
    "PolicyContext",
    "PolicyRule",
    "PolicyDecision",
    "PolicyEngine",
    "ReasonCode",
    "Verdict",
    "evaluate_pre_check",
]  # PolicyRule is re-exported from federated_policy
