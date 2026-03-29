import importlib
import sys
import types
from pathlib import Path


def _noop(*args: object, **kwargs: object) -> object:
    return None


def _stub_module(name: str, symbols: list[str]) -> types.ModuleType:
    module = types.ModuleType(name)
    for symbol in symbols:
        setattr(module, symbol, _noop)
    return module


def _load_impl_module(monkeypatch) -> types.ModuleType:
    session_symbols = [
        "_build_continuation_prompt",
        "_extract_blocked_ratio",
        "_find_session_meta",
        "_is_non_empty_contract_string",
        "_load_prior_session_output",
        "_normalize_contract_string",
        "_normalize_output_format",
        "_parse_contract_timestamp",
        "_read_session_meta",
        "_resolve_latest_session_id",
        "_resolve_session_status",
        "_run_background_session_observer",
        "_save_session_meta",
        "_session_state_path",
        "_write_session_state",
        "events_impl",
        "explain_run_impl",
        "history_impl",
        "inspect_impl",
        "list_session_contracts_impl",
        "logs_impl",
        "metrics_impl",
        "prune_sessions_impl",
        "ps_impl",
        "purge_impl",
        "session_contract_audit_impl",
        "session_contract_health_gate_impl",
        "session_contract_health_report_impl",
        "session_contract_health_trend_impl",
        "session_contract_negotiate_impl",
        "session_list_impl",
        "session_meta_impl",
        "session_send_impl",
        "status_impl",
        "stop_impl",
        "wait_impl",
    ]
    infra_symbols = [
        "_scan_ide_agents",
        "concurrency_set_impl",
        "concurrency_show_impl",
        "isolation_check_impl",
        "lock_resource_impl",
        "monitor_impl",
        "orchestrate_plan_impl",
        "orchestrate_run_impl",
        "unlock_resource_impl",
        "verify_context_impl",
    ]
    monkeypatch.setitem(sys.modules, "thegent.cli.commands.session_impl", _stub_module("session_impl", session_symbols))
    monkeypatch.setitem(sys.modules, "thegent.cli.commands.infra_impl", _stub_module("infra_impl", infra_symbols))
    sys.modules.pop("thegent.cli.commands.impl", None)
    return importlib.import_module("thegent.cli.commands.impl")


def test_run_impl_wrapper_delegates_with_argument_passthrough(monkeypatch, tmp_path: Path) -> None:
    impl = _load_impl_module(monkeypatch)
    run_execution_core_helpers = importlib.import_module("thegent.cli.services.run_execution_core_helpers")

    captured: dict[str, object] = {}

    def fake_run_impl_core(**kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        return {"ok": "run"}

    monkeypatch.setattr(run_execution_core_helpers, "run_impl_core", fake_run_impl_core)

    result = impl.run_impl(
        agent="antigravity",
        prompt="execute",
        cd=tmp_path,
        timeout=42,
        model="gemini-3-flash",
        provider="gemini",
        run_id="run_test_1",
        lane="critical",
        routing="pareto",
        include_contract=True,
        image_paths=["/tmp/fake.png"],
        audio_files=["/tmp/fake.wav"],
        google_grounding=True,
    )

    assert result == {"ok": "run"}
    assert captured["agent"] == "antigravity"
    assert captured["prompt"] == "execute"
    assert captured["cd"] == tmp_path
    assert captured["timeout"] == 42
    assert captured["routing"] == "pareto"
    assert captured["include_contract"] is True
    assert captured["image_paths"] == ["/tmp/fake.png"]
    assert captured["audio_files"] == ["/tmp/fake.wav"]
    assert captured["google_grounding"] is True
    assert captured["impl_ns"] is impl


def test_bg_impl_wrapper_delegates_with_argument_passthrough(monkeypatch, tmp_path: Path) -> None:
    impl = _load_impl_module(monkeypatch)
    run_execution_core_helpers = importlib.import_module("thegent.cli.services.run_execution_core_helpers")

    captured: dict[str, object] = {}

    def fake_bg_impl_core(**kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        return {"ok": "bg"}

    monkeypatch.setattr(run_execution_core_helpers, "bg_impl_core", fake_bg_impl_core)

    result = impl.bg_impl(
        agent="codex",
        prompt="background",
        cd=tmp_path,
        timeout=75,
        model="gpt-5",
        provider="openai",
        continue_from="session-123",
        continuation_include_stderr=True,
        routing="pareto",
        failover=True,
        run_id="run_test_2",
        lane="critical",
        image_paths=["/tmp/bg.png"],
    )

    assert result == {"ok": "bg"}
    assert captured["agent"] == "codex"
    assert captured["prompt"] == "background"
    assert captured["cd"] == tmp_path
    assert captured["timeout"] == 75
    assert captured["routing"] == "pareto"
    assert captured["failover"] is True
    assert captured["continue_from"] == "session-123"
    assert captured["continuation_include_stderr"] is True
    assert captured["image_paths"] == ["/tmp/bg.png"]
    assert captured["impl_ns"] is impl
