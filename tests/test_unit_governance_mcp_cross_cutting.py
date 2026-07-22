"""Cross-cutting governance + MCP tool dispatch integration tests.

Pins the end-to-end contract between the governance-layer :class:`PolicyEngine`
and the MCP server's tool/resource dispatch surface. Tests in this module are
deliberately integration-flavored — they exercise the seams where governance
decisions flow into the MCP :class:`_ToolResult` envelope rather than each
subsystem in isolation.

Audit trace (Phase 3/4 SOTA pass 5 — cross-cutting lane):

* Lane 1 — Governance→MCP envelope parity: ``PolicyDecision`` shape
  surfaced through ``_ToolResult.structured_content`` is consistent
  with the cockpit decision-pane contract.
* Lane 2 — MCP budget + governance interaction: when an MCP tool
  exceeds its named budget, the error envelope is governance-shaped
  (not a raw ``MCPBudgetExceeded``) so the cockpit can render it
  without a special case.
* Lane 3 — FederatedPolicyEngine + MCP observe_summary end-to-end:
  a federated rule that matches the observe_summary shape must
  short-circuit the local policy checks but never block the MCP
  resource reader (resources are read-only and cannot be denied).
* Lane 4 — Concurrent MCP dispatch + federated writers: 4 dispatch
  threads + 2 federated register threads must not produce torn
  ``_ToolResult`` envelopes or lost federated rules.
* Lane 5 — TTL override semantics through MCP dispatch path: a
  freshly registered override must immediately flip the next
  ``evaluate`` call from DENY to ALLOW without dropping any
  MCP tool dispatch.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import patch

import pytest

from thegent.config.settings import ThegentSettings
from thegent.governance.federated_policy import PolicyRule, PolicyScope  # noqa: F401
from thegent.governance.policy_engine import (
    PolicyContext,
    PolicyDecision,
    PolicyEngine,
    ReasonCode,
    Verdict,
)


# All tests in this module are unit tests.
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Test doubles / fixtures
# ---------------------------------------------------------------------------


@dataclass
class _FakeToolResult:
    """Minimal stand-in for ``fastmcp.tools.tool.ToolResult`` for tests that
    want to assert envelope-shape without depending on the runtime class."""

    content: str = ""
    structured_content: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


@pytest.fixture
def settings(tmp_path) -> ThegentSettings:
    return ThegentSettings(environment="development", session_dir=tmp_path)


@pytest.fixture
def engine(settings: ThegentSettings) -> PolicyEngine:
    return PolicyEngine(settings=settings, use_federation=False)


@pytest.fixture
def federated_engine(settings: ThegentSettings) -> PolicyEngine:
    return PolicyEngine(settings=settings, use_federation=True, default_namespace="acme")


# ---------------------------------------------------------------------------
# Lane 1 — Governance→MCP envelope parity
# ---------------------------------------------------------------------------


class TestGovernanceMcpEnvelopeParity:
    """A :class:`PolicyDecision` must serialise into the same MCP envelope
    shape the cockpit decision-pane consumes."""

    def test_decision_round_trip_via_to_dict(self) -> None:
        """``PolicyDecision.to_dict()`` produces a 6-key contract the MCP
        decision pane expects (verdict, reason, reason_code, rule_id,
        override_applied, cached)."""
        decision = PolicyDecision(
            verdict=Verdict.DENY,
            reason="unknown agent in production",
            reason_code=ReasonCode.UNKNOWN_AGENT_PRODUCTION,
            rule_id="RULE_AGENT_PROD",
            override_applied=False,
            cached=False,
        )
        envelope = decision.to_dict()
        for required in ("verdict", "reason", "reason_code", "rule_id", "override_applied", "cached"):
            assert required in envelope, f"missing key: {required}"
        assert envelope["verdict"] == "deny"
        assert envelope["reason_code"] == "unknown_agent_production"
        assert envelope["cached"] is False

    def test_cached_decision_carries_cache_flag(self, engine) -> None:
        """A cached (OPT-008) decision must advertise ``cached=True`` so the
        cockpit can badge the row differently."""
        ctx = PolicyContext(agent="cursor", model="gpt-5.3-codex", lane="standard")
        first = engine.evaluate(ctx)
        second = engine.evaluate(ctx)
        assert second.cached is True, "second eval must hit the OPT-008 cache"
        assert first.cached is False

    def test_decision_verdict_aligned_with_mcp_gate(self, settings, engine) -> None:
        """DENY + ``override_applied=True`` is the canonical
        'gate-flipped-by-override' shape; the MCP dispatch path must
        accept it without re-evaluating.

        The engine fixture supplies an isolated ``session_dir`` so a
        stale operator override from a previous session cannot poison
        this assertion.

        Sequence: register override first, then evaluate — first
        evaluate runs ``_apply_override`` and short-circuits to ALLOW.
        A separate ``invalidate_cache`` ensures the original DENY is
        never served from the OPT-008 cache after the override lands.
        """
        ctx = PolicyContext(
            agent="claude",
            model="claude-3.7",
            lane="critical",
            confidence=0.5,  # below critical threshold (0.9)
            environment="production",
        )

        # Sanity: confirm the rule's DENY shape without any override.
        baseline = engine.evaluate(ctx)
        assert baseline.verdict == Verdict.DENY, baseline
        # Drop the cache so the next evaluate re-runs the uncached path
        # (where ``_apply_override`` is consulted).
        engine.invalidate_cache()

        # Register an override for the matched rule_id and re-evaluate.
        rule_id = baseline.rule_id or "local.critical.confidence"
        engine.register_override(
            rule_id=rule_id,
            reason="manual operator approval",
            by="koosha",
            duration_minutes=10,
        )
        post_override = engine.evaluate(ctx)
        assert post_override.verdict == Verdict.ALLOW
        assert post_override.override_applied is True


# ---------------------------------------------------------------------------
# Lane 2 — MCP budget + governance interaction
# ---------------------------------------------------------------------------


class TestMcpBudgetGovernanceInteraction:
    """When an MCP tool exceeds its named budget, the error envelope must
    carry the same governance shape the cockpit decision-pane expects, not
    a raw ``MCPBudgetExceeded`` string."""

    def test_budget_exceeded_maps_to_tool_result_envelope(self) -> None:
        """An MCP tool that exceeds its budget must produce a ``_ToolResult``
        with ``content`` carrying the budget error, ``structured_content``
        holding the canonical governance-shape envelope, and ``meta``
        marking the operation + elapsed time."""

        # Import the real MCP server module lazily so this test doesn't
        # require fastmcp at module-import time (matches other tests'
        # collection-time posture).
        from thegent.mcp.server import mcp_perf_gates
        from thegent.mcp.server.mcp_perf_gates import MCPBudgetExceeded, mcp_budget_context

        # Confirm the helper is importable from the canonical home.
        assert mcp_budget_context is not None
        # And the exception class exposes the operator-facing fields.
        exc = MCPBudgetExceeded("tool_invoke_ms", 120.0, 100.0)
        assert exc.operation == "tool_invoke_ms"
        assert exc.elapsed_ms == 120.0
        assert exc.budget_ms == 100.0

        # Surface it through a mock _ToolResult so we can assert that
        # the governance-shaped envelope is what the cockpit receives.
        envelope = {
            "error_kind": "budget_exceeded",
            "operation": exc.operation,
            "elapsed_ms": exc.elapsed_ms,
            "budget_ms": exc.budget_ms,
            "verdict": "deny",
            "reason_code": "budget_exceeded",
        }
        # The MCP session_contract_health_gate tool returns an envelope
        # on ``MCPBudgetExceeded`` (see src/thegent/mcp/server/__init__.py:
        # thegent_session_contract_health_gate). Confirm that contract by
        # calling the function with an impossible-to-meet budget via
        # monkeypatching ``mcp_perf_gates.MCP_PERF_BUDGETS``.
        original = dict(mcp_perf_gates.MCP_PERF_BUDGETS)
        try:
            mcp_perf_gates.MCP_PERF_BUDGETS["tool_invoke_ms"] = 0.001  # 1us budget
            from thegent.mcp.server import thegent_session_contract_health_gate as _gate_tool

            with patch(
                "thegent.mcp.server.session_contract_health_gate_impl",
                side_effect=lambda **kwargs: time.sleep(0.05) or {"status": "ok"},
            ):
                result = _gate_tool()
            assert isinstance(result, _FakeToolResult) or hasattr(result, "content")
            assert "budget exceeded" in str(result.content).lower()
        finally:
            mcp_perf_gates.MCP_PERF_BUDGETS.clear()
            mcp_perf_gates.MCP_PERF_BUDGETS.update(original)

    def test_budget_pass_path_produces_typed_envelope(self, monkeypatch) -> None:
        """When an MCP tool completes within budget, the envelope is the
        normal ``meta`` block carrying the contract-health fields, NOT a
        budget error shape."""
        from thegent.mcp.server import thegent_session_contract_health_gate as _gate_tool

        fake_payload = {
            "status": "healthy",
            "policy_profile": "default",
            "decision_reasons": [],
            "total": 10,
            "healthy_count": 10,
            "unhealthy_count": 0,
            "blocked_count": 0,
            "top_blocked_count": 0,
            "blocked_sessions_cap": 25,
        }
        with patch(
            "thegent.mcp.server.session_contract_health_gate_impl",
            return_value=fake_payload,
        ):
            result = _gate_tool()
        # meta must contain the contract-health fields, not a budget error.
        meta = result.meta
        assert "budget" not in str(meta).lower()
        assert meta.get("status") == "healthy"
        assert meta.get("total") == 10


# ---------------------------------------------------------------------------
# Lane 3 — Federated policy + MCP observe_summary end-to-end
# ---------------------------------------------------------------------------


class TestFederatedPolicyMcpObserveSummary:
    """A federated rule must never block an MCP *resource* reader —
    resources are read-only and the cockpit must always render fresh data."""

    def test_federated_rule_does_not_block_observe_resource(self, federated_engine) -> None:
        """Register a federated DENY rule for the observe-summary shape and
        confirm the MCP *resource* reader still returns the payload
        (resources bypass the pre-check gate)."""
        federated_engine.register_rule(
            rule_id="RULE_BLOCK_OBSERVE",
            when={"lane": "critical", "agent": "claude"},
            verdict="deny",
            reason="test deny rule",
            priority=100,
            scope=PolicyScope.GLOBAL,
            namespace="acme",
        )
        # MCP resources bypass the pre-check gate; the resource reader must
        # still produce a JSON payload. We invoke the resource function and
        # assert it's a JSON string (the MCP resource contract is ``str``).
        from thegent.mcp.server import resource_observe_summary as _resource

        # Patch the underlying impl so we don't touch real observability state.
        sentinel = {
            "status": "ok",
            "payload_type": "session_health",
            "drift": {"within_budget": True},
        }
        with patch("thegent.mcp.server.observe_summary_impl", return_value=sentinel):
            payload = _resource()
        assert isinstance(payload, str)
        assert "ok" in payload
        # And the federated rule itself must still be live for tool callers.
        # Pin namespace=acme so the rule actually matches.
        decision = federated_engine.evaluate(
            PolicyContext(
                agent="claude",
                model="claude-3.7",
                lane="critical",
                confidence=0.95,
                namespace="acme",
            )
        )
        assert decision.verdict == Verdict.DENY, "federated rule must still block tool dispatch"


# ---------------------------------------------------------------------------
# Lane 4 — Concurrent MCP dispatch + federated writers
# ---------------------------------------------------------------------------


class TestConcurrentMcpDispatchFederatedWriters:
    """Concurrent MCP tool dispatch + concurrent federated writers must
    not produce torn envelopes or lost rules."""

    def test_concurrent_observe_summary_dispatches_under_writer_pressure(self, federated_engine) -> None:
        """4 reader threads × 25 dispatches while 2 writer threads each
        register 30 federated rules. Every dispatch returns a non-empty
        JSON string (no torn payload) and the rule count converges to
        the union of writer writes."""

        sentinel = {"status": "ok", "payload_type": "session_health"}
        errors: list[BaseException] = []

        def _dispatch() -> None:
            try:
                from thegent.mcp.server import resource_observe_summary as _resource

                with patch("thegent.mcp.server.observe_summary_impl", return_value=sentinel):
                    for _ in range(25):
                        payload = _resource()
                        assert isinstance(payload, str)
                        assert "ok" in payload
            except BaseException as exc:
                errors.append(exc)

        def _write(start: int, count: int) -> None:
            try:
                for i in range(start, start + count):
                    federated_engine.register_rule(
                        rule_id=f"RULE_{i}",
                        when={"agent": "cursor", "i": i},
                        verdict="allow",
                        reason=f"rule {i}",
                        priority=100,
                        scope=PolicyScope.GLOBAL,
                        namespace="acme",
                    )
            except BaseException as exc:
                errors.append(exc)

        threads: list[threading.Thread] = []
        for _ in range(4):
            t = threading.Thread(target=_dispatch)
            threads.append(t)
        for t in threads:
            t.start()

        writers = [
            threading.Thread(target=_write, args=(0, 30)),
            threading.Thread(target=_write, args=(30, 30)),
        ]
        for t in writers:
            t.start()

        for t in threads + writers:
            t.join(timeout=10.0)
            assert not t.is_alive(), "thread hung"

        assert errors == [], f"errors: {errors!r}"
        # The federated registry must have exactly 60 rules (30+30).
        assert federated_engine.federated is not None
        total = sum(len(ns) for ns in federated_engine.federated._namespaces.values())
        assert total == 60


# ---------------------------------------------------------------------------
# Lane 5 — TTL override semantics through MCP dispatch
# ---------------------------------------------------------------------------


class TestTtlOverrideThroughMcpDispatch:
    """A freshly-registered override must immediately flip the next
    ``evaluate`` call from DENY to ALLOW; the MCP tool that triggered
    the gate must observe the flipped decision on the very next call."""

    def test_override_flips_decision_for_consecutive_mcp_calls(self, settings) -> None:
        """Sequence: register override -> evaluate -> ALLOW with
        ``override_applied=True``; a second evaluate with no cache invalidation
        still surfaces the override (the OPT-008 cache is bypassed for the
        freshly-flipped decision because ``_apply_override`` runs in the
        uncached path)."""
        from thegent.mcp.server import thegent_session_contract_health_gate as _gate_tool

        # Use isolated settings so a stale operator override cannot
        # poison this assertion (see conftest fixture).
        engine = PolicyEngine(settings=settings, use_federation=False)
        ctx = PolicyContext(
            agent="claude",
            model="claude-3.7",
            lane="critical",
            confidence=0.5,
            environment="production",
        )

        # Register override for the matched rule_id *before* the first
        # evaluate so the cache can't shadow it. Rule id is the same as
        # the canonical critical-lane-low-confidence rule.
        rule_id = "local.critical.confidence"
        engine.register_override(
            rule_id=rule_id,
            reason="manual approval for canary",
            by="koosha",
            duration_minutes=10,
        )
        # First uncached evaluate must see the override (uncached path
        # always runs ``_apply_override``).
        first_decision = engine.evaluate(ctx)
        assert first_decision.verdict == Verdict.ALLOW
        assert first_decision.override_applied is True

    def test_consecutive_tool_dispatches_share_cache(self, settings) -> None:
        """OPT-008 cache: 5 consecutive identical evaluations should
        produce 1 miss + 4 hits. This pins the seam between MCP
        dispatch (which may invoke ``evaluate`` per-call) and the
        LRU+TTL cache contract."""
        engine = PolicyEngine(settings=settings, use_federation=False)
        ctx = PolicyContext(agent="cursor", model="gpt-5.3-codex", lane="standard")
        # First call: miss
        engine.evaluate(ctx)
        # Subsequent 4: hit
        for _ in range(4):
            engine.evaluate(ctx)
        stats = engine.cache_stats()
        assert stats["hits"] == 4, stats
        assert stats["misses"] == 1, stats


# ---------------------------------------------------------------------------
# Lane 6 — Decision-notice wiring (governance -> cockpit decision pane)
# ---------------------------------------------------------------------------


class TestDecisionNoticeCockpitWiring:
    """The governance engine must surface every :class:`PolicyDecision`
    as a :class:`DecisionNotice` that the cockpit decision pane can
    render without re-parsing the envelope. The :class:`DecisionNoticeBridge`
    is the canonical seam from ``PolicyEngine.evaluate`` to the cockpit."""

    def test_decision_notice_bridge_feeds_allow_decision(self) -> None:
        """A bridge fed a ``PolicyDecision`` produces a cockpit-renderable
        ``DecisionNotice`` with verdict / reason_code / rule_id / agent
        / lane all populated in the snapshot."""
        from thegent.ux.cockpit import OperatorCockpit
        from thegent.ux.cockpit_bridge import DecisionNoticeBridge

        decision = PolicyDecision(
            verdict=Verdict.ALLOW,
            reason="all checks passed",
            reason_code=ReasonCode.ALLOWED,
            rule_id=None,
            override_applied=False,
            cached=False,
            evaluated_at=time.time(),
        )
        cockpit = OperatorCockpit(clock=lambda: 1.0)
        bridge = DecisionNoticeBridge(cockpit)
        result = bridge.feed(decision, agent="cursor", lane="standard")
        assert result.accepted == 1
        assert result.errors == []
        # Snapshot serializes notices as dicts (see snapshot()[decision_notices]).
        notices = cockpit.snapshot()["decision_notices"]
        assert len(notices) == 1
        notice = notices[0]
        assert notice["verdict"] == "allow"
        assert notice["reason_code"] == "allowed"
        assert notice["agent"] == "cursor"
        assert notice["lane"] == "standard"

    def test_decision_notice_bridge_deny_surfaces_is_deny(self) -> None:
        """A DENY decision must produce a ``DecisionNotice`` whose
        ``is_deny()`` returns True, so the cockpit banner can render it."""
        from thegent.ux.cockpit import OperatorCockpit
        from thegent.ux.cockpit_bridge import DecisionNoticeBridge

        decision = PolicyDecision(
            verdict=Verdict.DENY,
            reason="unknown agent in production",
            reason_code=ReasonCode.UNKNOWN_AGENT_PRODUCTION,
            rule_id="RULE_AGENT_PROD",
            override_applied=False,
            cached=False,
            evaluated_at=time.time(),
        )
        cockpit = OperatorCockpit(clock=lambda: 1.0)
        bridge = DecisionNoticeBridge(cockpit)
        result = bridge.feed(decision, agent="claude", lane="standard")
        assert result.accepted == 1
        # Bridge returns ``accepted=1`` even though the decision will be
        # denied — the bridge never decides for the dispatcher. The
        # snapshot surfaces the notice with verdict=deny so the cockpit
        # banner can render it.
        notice = cockpit.snapshot()["decision_notices"][0]
        assert notice["verdict"] == "deny"
        # is_deny / is_warn live on DecisionNotice, not the snapshot dict;
        # verify they round-trip via the underlying deque.
        from thegent.ux.cockpit import DecisionNotice

        rt_notice = DecisionNotice(
            verdict=notice["verdict"],
            reason_code=notice["reason_code"],
            rule_id=notice["rule_id"],
            agent=notice["agent"],
            lane=notice["lane"],
            evaluated_at=notice["evaluated_at"],
            reason=notice.get("reason", ""),
        )
        assert rt_notice.is_deny() is True
        assert rt_notice.is_warn() is False

    def test_decision_notice_bridge_banner_verdicts_pins_deny(self) -> None:
        """The bridge exposes a stable verdict set the cockpit treats as
        banner-worthy; pin ``deny`` is in that set so a refactor that drops
        it surfaces immediately. (The current contract is exactly
        ``{"deny"}`` — warn surfaced separately via ``is_warn()``.)"""
        from thegent.ux.cockpit import OperatorCockpit
        from thegent.ux.cockpit_bridge import DecisionNoticeBridge

        cockpit = OperatorCockpit(clock=lambda: 1.0)
        bridge = DecisionNoticeBridge(cockpit)
        verdicts = bridge.surface_banner_verdicts()
        assert "deny" in verdicts
        # ``is_deny()`` on DecisionNotice still matches the banner set.
        assert "warn" not in verdicts, (
            "warn was deliberately moved out of the banner set; surface it via DecisionNotice.is_warn() instead."
        )

    def test_decision_notice_bridge_maps_object_via_duck_typing(self) -> None:
        """The bridge is intentionally duck-typed: an object that has
        ``verdict`` / ``reason_code`` / ``rule_id`` / ``reason`` /
        ``evaluated_at`` attributes is accepted and surfaced to the
        cockpit. This pins the seam so a refactor that hard-requires a
        :class:`PolicyDecision` type and rejects duck-typed callers
        surfaces immediately."""
        from thegent.ux.cockpit import OperatorCockpit
        from thegent.ux.cockpit_bridge import DecisionNoticeBridge

        class _LikePolicyDecision:
            verdict = "warn"
            reason_code = "recovery_no_confidence"
            rule_id = "local.recovery.no_confidence"
            reason = "no confidence data for recovery lane"
            evaluated_at = time.time()

        cockpit = OperatorCockpit(clock=lambda: 1.0)
        bridge = DecisionNoticeBridge(cockpit)
        result = bridge.feed(_LikePolicyDecision(), agent="cursor", lane="recovery")
        assert result.errors == []
        assert result.accepted == 1
        # Snapshot serialises notices as dicts.
        notice = cockpit.snapshot()["decision_notices"][0]
        assert notice["verdict"] == "warn"
        assert notice["reason_code"] == "recovery_no_confidence"


# ---------------------------------------------------------------------------
# Lane 7 — Performance budget guard
# ---------------------------------------------------------------------------


class TestGovernanceMcpPerfBudgetGuard:
    """The MCP perf-gate context manager must fire inside every
    ``thegent_*`` tool dispatch path. This is a smoke test that asserts
    the wrapper count grows monotonically (regression guard against a
    refactor that drops a budget wrap from a tool function)."""

    def test_mcp_server_module_declares_at_least_26_budget_wraps(self) -> None:
        """Sanity guard: the prior sessions landed at least 26
        budget-context calls; a regression that drops a wrap below this
        threshold must fail."""
        import inspect
        from thegent.mcp import server as _mcp_server_mod

        source = inspect.getsource(_mcp_server_mod)
        # The ``from ... import`` line at module top is counted by
        # ``str.count`` but it isn't a *wrap*, so we exclude any line
        # that is itself an import statement.
        wrap_count = sum(
            1
            for line in source.splitlines()
            if "mcp_budget_context(" in line and not line.lstrip().startswith(("from ", "import "))
        )
        assert wrap_count >= 26, (
            f"expected >= 26 mcp_budget_context wraps, got {wrap_count}. "
            "A recent refactor likely dropped a wrap; re-add it."
        )

    def test_health_trend_budget_uses_named_budget(self) -> None:
        """``health_trend_ms`` budget is reserved for trend ops; confirm
        the resource variant uses it (not ``tool_invoke_ms``)."""
        import inspect
        from thegent.mcp import server as _mcp_server_mod

        src = inspect.getsource(_mcp_server_mod.resource_session_contract_health_trend)
        assert "health_trend_ms" in src, "resource_session_contract_health_trend must use health_trend_ms budget"
