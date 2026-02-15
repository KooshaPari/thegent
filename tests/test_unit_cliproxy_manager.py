"""Unit tests for cliproxy_manager (CLIProxyAPIPlus lifecycle, login flows)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.agents.cliproxy_manager import (
    _LOGIN_FLAGS,
    _binary_available,
    ensure_proxy_running,
    run_login,
    start_proxy_managed,
)
from thegent.config import ThegentSettings


class TestLoginFlags:
    """Tests for login flag coverage."""

    def test_cliproxy_providers_have_flags(self) -> None:
        """All providers (including roo, kilo) use CLIProxy -login flags."""
        assert "claude" in _LOGIN_FLAGS
        assert _LOGIN_FLAGS["claude"] == "-claude-login"
        assert "gemini" in _LOGIN_FLAGS
        assert _LOGIN_FLAGS["gemini"] == "-login"
        assert "roo" in _LOGIN_FLAGS
        assert _LOGIN_FLAGS["roo"] == "-roo-login"
        assert "kilo" in _LOGIN_FLAGS
        assert _LOGIN_FLAGS["kilo"] == "-kilo-login"

    def test_all_providers_covered(self) -> None:
        """Full provider set includes roo, kilo, claude, glm, minimax, kiro variants."""
        assert "roo" in _LOGIN_FLAGS
        assert "kilo" in _LOGIN_FLAGS
        assert "claude" in _LOGIN_FLAGS
        assert "glm" in _LOGIN_FLAGS
        assert _LOGIN_FLAGS["glm"] == "-iflow-login"
        assert "minimax" in _LOGIN_FLAGS
        assert _LOGIN_FLAGS["minimax"] == "-minimax-login"
        assert "kiro-aws" in _LOGIN_FLAGS


class TestBinaryAvailable:
    """Tests for _binary_available."""

    def test_returns_true_when_path_exists(self, tmp_path: Path) -> None:
        """Returns True when binary path exists."""
        (tmp_path / "bin").touch()
        assert _binary_available(str(tmp_path / "bin")) is True

    @patch("thegent.agents.cliproxy_manager.shutil.which")
    def test_returns_true_when_on_path(self, mock_which: MagicMock) -> None:
        """Returns True when binary on PATH."""
        mock_which.return_value = "/usr/bin/foo"
        assert _binary_available("foo") is True

    def test_returns_false_when_missing(self) -> None:
        """Returns False when path does not exist and not on PATH."""
        with patch("thegent.agents.cliproxy_manager.shutil.which", return_value=None):
            assert _binary_available("/nonexistent/path/xyz") is False


class TestRunLogin:
    """Tests for run_login."""

    def test_unknown_provider_raises(self) -> None:
        """Unknown provider raises ValueError."""
        settings = ThegentSettings()
        with pytest.raises(ValueError, match="Unknown provider"):
            run_login(settings, "unknown-xyz")

    @patch("thegent.agents.cliproxy_manager._resolve_binary")
    @patch("thegent.agents.cliproxy_manager._ensure_config")
    @patch("thegent.agents.cliproxy_manager.subprocess.run")
    def test_roo_login_invokes_cliproxy(
        self,
        mock_run: MagicMock,
        mock_ensure: MagicMock,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        """run_login roo passes -roo-login to CLIProxy binary."""
        fake_binary = tmp_path / "cli-proxy-api-plus"
        fake_binary.touch()
        mock_resolve.return_value = str(fake_binary)
        mock_ensure.return_value = tmp_path / "config.yaml"
        mock_run.return_value = MagicMock(returncode=0)

        settings = ThegentSettings()
        rc = run_login(settings, "roo")

        assert rc == 0
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert str(fake_binary) in cmd or "cli-proxy-api-plus" in str(cmd)
        assert "-config" in cmd
        assert "-roo-login" in cmd

    @patch("thegent.agents.cliproxy_manager._resolve_binary")
    @patch("thegent.agents.cliproxy_manager._ensure_config")
    @patch("thegent.agents.cliproxy_manager.subprocess.run")
    def test_kilo_login_invokes_cliproxy(
        self,
        mock_run: MagicMock,
        mock_ensure: MagicMock,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        """run_login kilo passes -kilo-login to CLIProxy binary."""
        fake_binary = tmp_path / "cli-proxy-api-plus"
        fake_binary.touch()
        mock_resolve.return_value = str(fake_binary)
        mock_ensure.return_value = tmp_path / "config.yaml"
        mock_run.return_value = MagicMock(returncode=0)

        settings = ThegentSettings()
        rc = run_login(settings, "kilo")

        assert rc == 0
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "-kilo-login" in cmd

    @patch("thegent.agents.cliproxy_manager._resolve_binary")
    @patch("thegent.agents.cliproxy_manager._ensure_config")
    @patch("thegent.agents.cliproxy_manager.subprocess.run")
    def test_claude_login_invokes_cliproxy(
        self,
        mock_run: MagicMock,
        mock_ensure: MagicMock,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        """run_login claude passes -claude-login to CLIProxy binary."""
        fake_binary = tmp_path / "cli-proxy-api-plus"
        fake_binary.touch()
        mock_resolve.return_value = str(fake_binary)
        mock_ensure.return_value = tmp_path / "config.yaml"
        mock_run.return_value = MagicMock(returncode=0)

        settings = ThegentSettings()
        rc = run_login(settings, "claude")

        assert rc == 0
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert str(fake_binary) in cmd or "cli-proxy-api-plus" in str(cmd)
        assert "-config" in cmd
        assert "-claude-login" in cmd


class TestEnsureProxyRunning:
    """Tests for ensure_proxy_running."""

    @patch("thegent.agents.cliproxy_manager._is_proxy_reachable")
    def test_returns_base_url_when_already_reachable(
        self, mock_reachable: MagicMock
    ) -> None:
        """Skips start when proxy already running."""
        mock_reachable.return_value = True
        settings = ThegentSettings()
        base_url = ensure_proxy_running(settings)
        assert base_url == f"http://127.0.0.1:{settings.cliproxy_port}/v1"
        mock_reachable.assert_called()

    @patch("thegent.agents.cliproxy_manager._is_proxy_reachable")
    @patch("thegent.agents.cliproxy_manager._resolve_binary")
    @patch("thegent.agents.cliproxy_manager._ensure_config")
    @patch("thegent.agents.cliproxy_manager.subprocess.Popen")
    def test_starts_proxy_when_not_reachable(
        self,
        mock_popen: MagicMock,
        mock_ensure: MagicMock,
        mock_resolve: MagicMock,
        mock_reachable: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Starts proxy when not reachable."""
        fake_binary = tmp_path / "cli-proxy-api-plus"
        fake_binary.touch()
        mock_reachable.side_effect = [False, True]  # first check fails, second succeeds
        mock_resolve.return_value = str(fake_binary)
        mock_ensure.return_value = tmp_path / "config.yaml"
        mock_popen.return_value = MagicMock(poll=MagicMock(return_value=None))

        settings = ThegentSettings()
        base_url = ensure_proxy_running(settings)

        assert base_url == f"http://127.0.0.1:{settings.cliproxy_port}/v1"
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "-config" in call_args
        assert str(tmp_path / "config.yaml") in call_args


class TestStartProxyManaged:
    """Tests for start_proxy_managed."""

    @patch("thegent.agents.cliproxy_manager._is_proxy_reachable")
    def test_returns_none_proc_when_already_reachable(
        self, mock_reachable: MagicMock
    ) -> None:
        """Returns (None, base_url) when proxy already running."""
        mock_reachable.return_value = True
        settings = ThegentSettings()
        proc, base_url = start_proxy_managed(settings)
        assert proc is None
        assert base_url == f"http://127.0.0.1:{settings.cliproxy_port}/v1"

    @patch("thegent.agents.cliproxy_manager._is_proxy_reachable")
    @patch("thegent.agents.cliproxy_manager._resolve_binary")
    @patch("thegent.agents.cliproxy_manager._ensure_config")
    @patch("thegent.agents.cliproxy_manager.subprocess.Popen")
    def test_returns_proc_when_started(
        self,
        mock_popen: MagicMock,
        mock_ensure: MagicMock,
        mock_resolve: MagicMock,
        mock_reachable: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Returns (proc, base_url) when proxy is started."""
        fake_binary = tmp_path / "cli-proxy-api-plus"
        fake_binary.touch()
        mock_reachable.side_effect = [False, True]
        mock_resolve.return_value = str(fake_binary)
        mock_ensure.return_value = tmp_path / "config.yaml"
        mock_proc = MagicMock(poll=MagicMock(return_value=None))
        mock_popen.return_value = mock_proc

        settings = ThegentSettings()
        proc, base_url = start_proxy_managed(settings)

        assert proc is mock_proc
        assert base_url == f"http://127.0.0.1:{settings.cliproxy_port}/v1"
