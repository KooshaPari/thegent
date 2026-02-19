"""Unit tests for ConfigProvider abstraction (control plane Phase 1)."""

import pytest

from thegent.config_provider import EnvConfigProvider, get_config_provider


@pytest.mark.unit
class TestEnvConfigProvider:
    """Tests for EnvConfigProvider."""

    def test_resolve_returns_dict(self) -> None:
        """resolve() returns a dict with config keys."""
        p = EnvConfigProvider()
        cfg = p.resolve()
        assert isinstance(cfg, dict)
        assert "default_timeout" in cfg
        assert "default_timeout_claude" in cfg
        assert "session_dir" in cfg

    def test_resolve_merges_request_overrides(self) -> None:
        """request_overrides override base config."""
        p = EnvConfigProvider()
        cfg = p.resolve(request_overrides={"default_timeout": 1800})
        assert cfg["default_timeout"] == 1800

    def test_resolve_keys_subset(self) -> None:
        """keys param limits returned keys."""
        p = EnvConfigProvider()
        cfg = p.resolve(keys=["default_timeout"])
        assert list(cfg.keys()) == ["default_timeout"]

    def test_get_tenant_config_returns_none(self) -> None:
        """EnvConfigProvider has no tenant catalog; returns None."""
        p = EnvConfigProvider()
        assert p.get_tenant_config("acme") is None


@pytest.mark.unit
class TestGetConfigProvider:
    """Tests for get_config_provider() factory."""

    def test_returns_env_provider_by_default(self, monkeypatch) -> None:
        """Without THGENT_CONTROL_PLANE_URL, returns EnvConfigProvider."""
        # Remove THGENT_CONTROL_PLANE_URL if set
        monkeypatch.delenv("THGENT_CONTROL_PLANE_URL", raising=False)
        p = get_config_provider()
        assert isinstance(p, EnvConfigProvider)

    def test_returns_env_provider_when_cp_import_fails(self, monkeypatch) -> None:
        """When CP URL set but ControlPlaneConfigProvider not available, falls back to Env."""
        monkeypatch.setenv("THGENT_CONTROL_PLANE_URL", "http://127.0.0.1:3848")
        p = get_config_provider()
        # ControlPlaneConfigProvider doesn't exist yet; ImportError → EnvConfigProvider
        assert isinstance(p, EnvConfigProvider)
