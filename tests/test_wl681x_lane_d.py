from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from thegent.commands.sync import SyncCommand, SyncOperationStatus
from thegent.design.design_language import DesignLanguage
from thegent.discovery.sync import SyncLoop
from thegent.integration.unified_config import UnifiedConfigManager
from thegent.learning.promotion import ModelPromoter
from thegent.mcp.gateway import McpGateway, McpServerConfig, McpToolCall
from thegent.orchestration.dispatcher import DispatchConfig, SubAgentDispatcher
from thegent.security.sandboxing import SandboxProvider
from thegent.verification.zkp import ZKGovernor


def test_wl6810_sync_configs_merges_conflicts_and_persists(tmp_path: Path) -> None:
    manager = UnifiedConfigManager()
    tg = tmp_path / "thegent.yaml"
    mg = tmp_path / "manage.yaml"
    ws = tmp_path / "WORK_STREAM.md"
    pl = tmp_path / "PLAN.md"

    tg.write_text("providers:\n  anthropic: sonnet\n", encoding="utf-8")
    mg.write_text("providers:\n  anthropic: haiku\n", encoding="utf-8")
    ws.write_text("---\nproviders:\n  anthropic: opus\n---\n# ws\n", encoding="utf-8")
    pl.write_text("---\nproviders:\n  anthropic: mini\n---\n# plan\n", encoding="utf-8")

    manager.config_sources = [("thegent", tg), ("manage", mg), ("workstream", ws), ("plan", pl)]
    manager.unified_config = {
        "thegent": {"providers": {"anthropic": "sonnet"}},
        "manage": {"providers": {"anthropic": "haiku"}},
        "workstream": {"providers": {"anthropic": "opus"}},
        "plan": {"providers": {"anthropic": "mini"}},
    }

    manager.sync_configs()

    assert manager.last_sync_conflicts["providers.anthropic"]["manage"] == "haiku"
    assert manager.unified_config["thegent"]["providers"]["anthropic"] == "sonnet"
    assert "sonnet" in mg.read_text(encoding="utf-8")
    assert "sonnet" in ws.read_text(encoding="utf-8")

    first = mg.read_text(encoding="utf-8")
    manager.sync_configs()
    assert mg.read_text(encoding="utf-8") == first


def test_wl6811_sync_loop_collects_real_state_and_validates_payload(tmp_path: Path) -> None:
    class _Registry:
        def list_projects(self):
            return [{"id": "local", "path": str(tmp_path)}, {"id": "peer", "path": str(tmp_path / "peer")}]

    loop = SyncLoop(registry=_Registry(), sync_dir=tmp_path / "sync")
    (tmp_path / ".thegent").mkdir()
    (tmp_path / ".thegent" / "team_registry.json").write_text(
        json.dumps({"teams": [{"id": "a", "active": True}, {"id": "b", "active": False}]}), encoding="utf-8"
    )
    (tmp_path / ".thegent" / "handoff_registry.jsonl").write_text(
        json.dumps({"snapshot_id": "s1"}) + "\n", encoding="utf-8"
    )

    state = loop._collect_local_state(tmp_path)
    assert len(state["active_teams"]) == 1
    assert state["active_teams"][0]["id"] == "a"

    peer = tmp_path / "peer"
    loop._push_state_to_peer(peer, "local", state)
    pushed = peer / ".thegent" / "sync_inbox" / "local_state.json"
    assert pushed.exists()


def test_wl6811_sync_loop_malformed_files_fail_loud(tmp_path: Path) -> None:
    class _Registry:
        def list_projects(self):
            return []

    loop = SyncLoop(registry=_Registry(), sync_dir=tmp_path / "sync")
    (tmp_path / ".thegent").mkdir()
    (tmp_path / ".thegent" / "team_registry.json").write_text("{oops", encoding="utf-8")

    with pytest.raises(ValueError):
        loop._collect_local_state(tmp_path)


def test_wl6812_zk_verify_valid_stale_mismatch_and_tamper() -> None:
    gov = ZKGovernor("a1", freshness_window_s=5)
    proof = gov.generate_proof("secret", "challenge-1")
    assert gov.verify_proof(proof, proof.commitment) is True

    # replay should fail
    assert gov.verify_proof(proof, proof.commitment) is False

    stale = gov.generate_proof("secret", "challenge-2")
    stale.timestamp = "2000-01-01T00:00:00+00:00"
    assert gov.verify_proof(stale, stale.commitment) is False

    bad_commit = gov.generate_proof("secret", "challenge-3")
    assert gov.verify_proof(bad_commit, "0" * 64) is False

    tampered = gov.generate_proof("secret", "challenge-4")
    tampered.response = "f" * 64
    assert gov.verify_proof(tampered, tampered.commitment) is False


def test_wl6813_push_success_partial_failure_and_unreachable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "agents").mkdir()
    (tmp_path / "hooks").mkdir()
    (tmp_path / "agents" / "a.md").write_text("# a\n", encoding="utf-8")
    (tmp_path / "hooks" / "h.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    cmd = SyncCommand(project_root=tmp_path)

    ok_target = tmp_path / "remote"
    ok = cmd.push(target=str(ok_target))
    assert ok.status == SyncOperationStatus.SUCCESS
    assert ok.details["files_uploaded"] == 2

    monkeypatch.setattr(cmd, "_discover_hook_scripts", lambda: {"h", "missing"})
    partial = cmd.push(target=str(ok_target))
    assert partial.status == SyncOperationStatus.FAILED
    assert partial.details["files_failed"] == 1

    bad = cmd.push(target="<local-stub>")
    assert bad.status == SyncOperationStatus.FAILED


def test_wl6814_gateway_exec_success_unknown_server_tool_and_transport_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    gw = McpGateway()
    gw.register_server(McpServerConfig(server_id="fs", command="fake-cmd", env={}))

    class _Proc:
        def __init__(self, stdout: str, returncode: int = 0, stderr: str = ""):
            self.stdout = stdout
            self.returncode = returncode
            self.stderr = stderr

    def _ok_run(*args, **kwargs):
        return _Proc('{"jsonrpc":"2.0","id":"thegent-gateway","result":{"ok":true}}\n')

    monkeypatch.setattr("thegent.mcp.gateway.subprocess.run", _ok_run)
    ok = gw.execute(McpToolCall(server_id="fs", tool="read_file", arguments={"path": "/tmp/a"}))
    assert ok.error == ""
    assert ok.result == {"ok": True}

    unknown_server = gw.execute(McpToolCall(server_id="nope", tool="x", arguments={}))
    assert "Unknown server_id" in unknown_server.error

    def _unknown_tool(*args, **kwargs):
        return _Proc('{"jsonrpc":"2.0","id":"thegent-gateway","error":{"code":-32601,"message":"method not found"}}\n')

    monkeypatch.setattr("thegent.mcp.gateway.subprocess.run", _unknown_tool)
    unknown_tool = gw.execute(McpToolCall(server_id="fs", tool="bad_tool", arguments={}))
    assert "Unknown tool 'bad_tool'" in unknown_tool.error

    def _transport_fail(*args, **kwargs):
        return _Proc("", returncode=1, stderr="connection reset")

    monkeypatch.setattr("thegent.mcp.gateway.subprocess.run", _transport_fail)
    fail = gw.execute(McpToolCall(server_id="fs", tool="x", arguments={}))
    assert fail.error.startswith("transport_error")


def test_wl6897_gateway_exec_accepts_transport_and_invalid_response(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def _transport(
        *,
        command: list[str],
        request_payload: str,
        env: dict[str, str],
        timeout_sec: float,
    ) -> tuple[int, str, str]:
        captured["command"] = command
        captured["request_payload"] = request_payload
        captured["timeout_sec"] = timeout_sec
        return (0, '{"jsonrpc":"2.0","result":{"ok":true}}\n', "")

    gw = McpGateway()
    gw.register_server(
        McpServerConfig(
            server_id="fs",
            command="fake-cmd",
            env={},
            transport=_transport,
        )
    )

    ok = gw.execute(McpToolCall(server_id="fs", tool="read_file", arguments={"path": "/tmp/a"}))
    assert ok.error == ""
    assert ok.result == {"ok": True}
    assert captured["command"] == ["fake-cmd"]
    assert json.loads(captured["request_payload"])["params"]["name"] == "read_file"

    def _invalid_transport(
        *,
        command: list[str],
        request_payload: str,
        env: dict[str, str],
        timeout_sec: float,
    ) -> tuple[int, str, str]:
        return (0, "not-json", "")

    gw.register_server(
        McpServerConfig(
            server_id="invalid",
            command="fake-cmd",
            env={},
            transport=_invalid_transport,
        )
    )
    bad = gw.execute(McpToolCall(server_id="invalid", tool="read_file", arguments={"path": "/tmp/a"}))
    assert "transport_error: invalid or empty MCP response" in bad.error

    def _transport_exception(
        *,
        command: list[str],
        request_payload: str,
        env: dict[str, str],
        timeout_sec: float,
    ) -> tuple[int, str, str]:
        raise RuntimeError("transport down")

    gw.register_server(
        McpServerConfig(
            server_id="raise",
            command="fake-cmd",
            env={},
            transport=_transport_exception,
        )
    )
    raised = gw.execute(McpToolCall(server_id="raise", tool="read_file", arguments={}))
    assert "transport_error: RuntimeError: transport down" in raised.error


def test_wl6815_dispatcher_execute_task_success_failure_and_approval_block(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Index:
        def recommend(self, *_args, **_kwargs):
            return []

    class _Policy:
        def await_approval(self, **_kwargs):
            return None

    class _RunnerOK:
        def run(self, **_kwargs):
            return SimpleNamespace(exit_code=0, stdout="ok", stderr="")

    class _RunnerBad:
        def run(self, **_kwargs):
            return SimpleNamespace(exit_code=1, stdout="", stderr="boom")

    dispatcher = SubAgentDispatcher(_Index(), policy_engine=_Policy(), config=DispatchConfig(hitl_enabled=True))
    node = SimpleNamespace(id="n1", task="do x", metadata={})

    monkeypatch.setattr("thegent.agents.registry.get_runner", lambda _n: _RunnerOK())
    out, success, err = asyncio.run(dispatcher._execute_task(node, "claude"))
    assert success is True
    assert out == "ok"
    assert err is None

    monkeypatch.setattr("thegent.agents.registry.get_runner", lambda _n: _RunnerBad())
    out2, success2, err2 = asyncio.run(dispatcher._execute_task(node, "claude"))
    assert success2 is False
    assert "boom" in (err2 or "")

    blocked = SimpleNamespace(id="n2", task="secure", metadata={"require_approval": True, "approval_granted": False})
    with pytest.raises(RuntimeError):
        asyncio.run(dispatcher._check_hitl_gate(blocked, None))


def test_wl6898_dispatcher_execute_task_respects_hitl_policy_on_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Index:
        def recommend(self, *_args, **_kwargs):
            return []

    class _Policy:
        def await_approval(self, **_kwargs):
            return None

    node = SimpleNamespace(id="n1", task="secure", metadata={"require_approval": True, "approval_granted": False})
    dispatcher = SubAgentDispatcher(_Index(), policy_engine=_Policy(), config=DispatchConfig(hitl_enabled=True))

    with pytest.raises(RuntimeError):
        asyncio.run(dispatcher._execute_task(node, None))


def test_wl6898_dispatcher_execute_task_blocks_without_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Index:
        def recommend(self, *_args, **_kwargs):
            return []

    node = SimpleNamespace(id="n1", task="do something", metadata={})
    dispatcher = SubAgentDispatcher(_Index(), config=DispatchConfig(hitl_enabled=False))
    monkeypatch.setattr("thegent.agents.registry.get_runner", lambda _n: None)

    output, success, error = asyncio.run(dispatcher._execute_task(node, None))
    assert output == ""
    assert success is False
    assert "No runner resolved for node n1" in (error or "")


def test_wl6898_dispatcher_execute_task_propagates_runner_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Index:
        def recommend(self, *_args, **_kwargs):
            return []

    class _Runner:
        def run(self, **_kwargs) -> None:
            raise RuntimeError("runner crash")

    node = SimpleNamespace(id="n2", task="fail", metadata={})
    dispatcher = SubAgentDispatcher(_Index(), config=DispatchConfig(hitl_enabled=False))
    monkeypatch.setattr("thegent.agents.registry.get_runner", lambda _n: _Runner())

    output, success, error = asyncio.run(dispatcher._execute_task(node, "bad-runner"))
    assert output == ""
    assert success is False
    assert "RuntimeError: runner crash" in (error or "")


def test_wl6816_design_language_apply_to_cli_requires_tokens() -> None:
    design = DesignLanguage()
    # force missing required token path
    design.tokens.pop("color.info", None)
    with pytest.raises(KeyError):
        design.apply_to_cli()


def test_wl6816_design_language_apply_to_cli_success() -> None:
    design = DesignLanguage()
    design.apply_to_cli()
    assert hasattr(design, "cli_theme")
    assert "primary" in design.cli_theme.styles
    assert "info" in design.cli_theme.styles


def test_wl6817_kpis_from_telemetry_and_sparse_behavior(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from thegent.execution import KPIManager

    class _Registry:
        def __init__(self, _session_dir: Path):
            return None

        def list_runs(self, limit: int = 1000):
            return [
                {
                    "status": "completed",
                    "started_at_utc": "2026-02-22T00:00:00+00:00",
                    "confidence": 0.8,
                    "cost_usd": 0.2,
                    "agent": "claude",
                    "model": "claude-sonnet-4.6",
                },
                {
                    "status": "failed",
                    "started_at_utc": "2026-02-20T00:00:00+00:00",
                    "confidence": 0.6,
                    "cost_usd": 0.1,
                    "agent": "codex",
                    "model": "gpt-5.3-codex",
                },
            ]

    class _Telemetry:
        def __init__(self, _session_dir: Path):
            return None

        def get_stats(self, limit: int = 100):
            return {"total": 2, "fallback_rate": 0.25, "avg_confidence": 0.7}

    class _Fatigue:
        def __init__(self, _session_dir: Path):
            return None

        def get_fatigue_score(self, window_s: int = 3600):
            return 0.1

    monkeypatch.setattr("thegent.execution.RunRegistry", _Registry)
    monkeypatch.setattr("thegent.contracts.telemetry.ContractTelemetry", _Telemetry)
    monkeypatch.setattr("thegent.execution.InterruptionTracker", _Fatigue)

    kpis = KPIManager(tmp_path).get_kpis()
    assert kpis["throughput"] == 2
    assert kpis["fallback_rate"] == 0.25
    assert kpis["data_availability"] == "sparse"
    assert 0.0 <= kpis["kpi_confidence"] <= 1.0


def test_wl6818_model_promotion_persists_with_audit_and_idempotency(tmp_path: Path) -> None:
    from thegent.config import ThegentSettings

    settings = ThegentSettings(
        session_dir=tmp_path / "session",
        custom_models_path=tmp_path / "custom_models.yaml",
    )
    promoter = ModelPromoter(settings)

    promoter._update_model_tier("claude-sonnet-4.6", "production")
    data = (tmp_path / "custom_models.yaml").read_text(encoding="utf-8")
    assert "tier: production" in data

    audit_path = tmp_path / "session" / "model_promotion_audit.jsonl"
    first_count = len(audit_path.read_text(encoding="utf-8").splitlines())
    promoter._update_model_tier("claude-sonnet-4.6", "production")
    second_count = len(audit_path.read_text(encoding="utf-8").splitlines())
    assert first_count == second_count

    with pytest.raises(KeyError):
        promoter._update_model_tier("unknown-model", "production")


def test_wl6819_tier2_bwrap_has_worktree_bind_and_no_root_bind(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    worktree = tmp_path / "wt"
    worktree.mkdir()
    monkeypatch.setenv("THGENT_SANDBOX_WORKTREE", str(worktree))
    monkeypatch.setenv("THGENT_SANDBOX_ALLOWED_READS", str(tmp_path))

    provider = SandboxProvider()
    provider.system = "Linux"

    args = provider.wrap_command(["echo", "hi"], tier=2)
    assert "--bind" in args
    assert str(worktree) in args
    assert args[0:3] != ["--ro-bind", "/", "/"]

    tier1 = provider.wrap_command(["echo", "hi"], tier=1)
    assert "--ro-bind" in tier1
    assert "/" in tier1
