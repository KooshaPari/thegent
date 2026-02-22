"""Integration-style tests for scripts/cliproxy_provider_smoke.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_PATH = _ROOT / "scripts" / "cliproxy_provider_smoke.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("cliproxy_provider_smoke", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_exists() -> None:
    assert _SCRIPT_PATH.exists(), "scripts/cliproxy_provider_smoke.py must exist"


def test_main_starts_proxy_when_unreachable(monkeypatch) -> None:
    mod = _load_module()

    args = SimpleNamespace(
        base_url="http://127.0.0.1:8317/v1",
        api_key="sk-test",
        proxy_binary="cli-proxy-api-plus",
        proxy_config=str(Path.home() / ".config" / "thegent" / "cliproxy-config.yaml"),
        startup_timeout=1,
        input="reply with exactly: ok",
        strict=False,
    )

    started = {"called": False, "terminated": False}
    reachable_calls = {"count": 0}

    class FakeProc:
        def poll(self):
            return None

        def terminate(self):
            started["terminated"] = True

    def fake_parse_args():
        return args

    def fake_reachable(_base, _key):
        reachable_calls["count"] += 1
        return reachable_calls["count"] >= 2

    def fake_start(_binary, _config, _timeout):
        started["called"] = True
        return FakeProc()

    monkeypatch.setattr(mod.argparse.ArgumentParser, "parse_args", lambda _self: fake_parse_args())
    monkeypatch.setattr(mod, "_reachable", fake_reachable)
    monkeypatch.setattr(mod, "_start_proxy", fake_start)
    monkeypatch.setattr(mod, "_run_matrix", lambda *_args: {"provider_count": 1, "passed": 1, "failed": 0, "rows": []})

    exit_code = mod.main()
    assert exit_code == 0
    assert started["called"] is True
    assert started["terminated"] is True


def test_main_strict_fails_when_any_provider_fails(monkeypatch) -> None:
    mod = _load_module()

    args = SimpleNamespace(
        base_url="http://127.0.0.1:8317/v1",
        api_key="sk-test",
        proxy_binary="cli-proxy-api-plus",
        proxy_config=str(Path.home() / ".config" / "thegent" / "cliproxy-config.yaml"),
        startup_timeout=1,
        input="reply with exactly: ok",
        strict=True,
    )

    monkeypatch.setattr(mod.argparse.ArgumentParser, "parse_args", lambda _self: args)
    monkeypatch.setattr(mod, "_reachable", lambda *_args: True)
    monkeypatch.setattr(mod, "_run_matrix", lambda *_args: {"provider_count": 2, "passed": 1, "failed": 1, "rows": []})

    exit_code = mod.main()
    assert exit_code == 1
