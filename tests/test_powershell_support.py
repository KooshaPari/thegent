"""Tests for WL-053: Windows PowerShell support for ``thegent install``.
"""


import pytest
pytestmark = pytest.mark.skip(reason="Module imports not implemented")
if False:
    from __future__ import annotations

    import sys
    from pathlib import Path
    from unittest.mock import MagicMock, patch

    import pytest

    from thegent.install import (
        POWERSHELL_MISE_HOOK,
        detect_powershell_profile,
        install_system_dependencies,
        write_powershell_mise_hook,
        _is_powershell_environment,
    )

    pytestmark = pytest.mark.unit


    # ---------------------------------------------------------------------------
    # _is_powershell_environment
    # ---------------------------------------------------------------------------


    class TestIsPowershellEnvironment:
        """Tests for PowerShell environment detection.  # @trace WL-053"""

        def test_win32_platform_detected(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """sys.platform == 'win32' is treated as a PowerShell environment."""
            monkeypatch.setattr(sys, "platform", "win32")
            monkeypatch.delenv("SHELL", raising=False)
            assert _is_powershell_environment() is True

        def test_shell_env_pwsh_detected(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """SHELL=/usr/bin/pwsh is treated as a PowerShell environment."""
            monkeypatch.setattr(sys, "platform", "linux")
            monkeypatch.setenv("SHELL", "/usr/bin/pwsh")
            assert _is_powershell_environment() is True

        def test_shell_env_powershell_detected(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """SHELL=powershell is treated as a PowerShell environment."""
            monkeypatch.setattr(sys, "platform", "linux")
            monkeypatch.setenv("SHELL", "powershell")
            assert _is_powershell_environment() is True

        def test_shell_env_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """SHELL env var is matched case-insensitively."""
            monkeypatch.setattr(sys, "platform", "darwin")
            monkeypatch.setenv("SHELL", "/bin/Pwsh")
            assert _is_powershell_environment() is True

        def test_posix_shell_not_detected(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """SHELL=/bin/zsh on darwin is not a PowerShell environment."""
            monkeypatch.setattr(sys, "platform", "darwin")
            monkeypatch.setenv("SHELL", "/bin/zsh")
            assert _is_powershell_environment() is False

        def test_no_shell_env_non_windows(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """Missing SHELL env on non-Windows is not a PowerShell environment."""
            monkeypatch.setattr(sys, "platform", "linux")
            monkeypatch.delenv("SHELL", raising=False)
            assert _is_powershell_environment() is False


    # ---------------------------------------------------------------------------
    # detect_powershell_profile
    # ---------------------------------------------------------------------------


    class TestDetectPowershellProfile:
        """Tests for PowerShell profile path detection.  # @trace WL-053"""

        def test_profile_env_var_used_when_set(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
            """When $PROFILE is set, that exact path is returned."""
            expected = tmp_path / "MyCustomProfile.ps1"
            monkeypatch.setenv("PROFILE", str(expected))
            result = detect_powershell_profile()
            assert result == expected

        def test_profile_env_var_takes_precedence_over_existing_ps7(
            self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
        ) -> None:
            """$PROFILE overrides even an existing PS7 profile."""
            custom = tmp_path / "custom.ps1"
            # Create a PS7-looking profile under a fake home — should be ignored.
            ps7 = tmp_path / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
            ps7.parent.mkdir(parents=True)
            ps7.write_text("# ps7")
            monkeypatch.setenv("PROFILE", str(custom))
            monkeypatch.setattr(Path, "home", lambda: tmp_path)
            result = detect_powershell_profile()
            assert result == custom

        def test_ps7_profile_returned_when_exists(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
            """When $PROFILE is absent and PS7 profile exists, it is returned."""
            monkeypatch.delenv("PROFILE", raising=False)
            ps7 = tmp_path / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
            ps7.parent.mkdir(parents=True)
            ps7.write_text("# ps7")
            monkeypatch.setattr(Path, "home", lambda: tmp_path)
            result = detect_powershell_profile()
            assert result == ps7

        def test_ps5_path_returned_when_neither_exists(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
            """When $PROFILE is absent and no profile exists, PS5 path is returned."""
            monkeypatch.delenv("PROFILE", raising=False)
            monkeypatch.setattr(Path, "home", lambda: tmp_path)
            expected = tmp_path / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
            result = detect_powershell_profile()
            assert result == expected

        def test_ps5_preferred_over_ps7_when_only_ps5_exists(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
            """PS5 path is returned when only PS5 profile exists (PS7 absent)."""
            monkeypatch.delenv("PROFILE", raising=False)
            ps5 = tmp_path / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
            ps5.parent.mkdir(parents=True)
            ps5.write_text("# ps5")
            monkeypatch.setattr(Path, "home", lambda: tmp_path)
            # ps7 does NOT exist — function should fall through to ps5 default
            result = detect_powershell_profile()
            assert result == ps5


    # ---------------------------------------------------------------------------
    # write_powershell_mise_hook
    # ---------------------------------------------------------------------------


    class TestWritePowershellMiseHook:
        """Tests for writing the mise activation hook to a PowerShell profile.

        # @trace WL-053
        """

        def test_creates_new_profile_with_hook(self, tmp_path: Path) -> None:
            """When profile does not exist, it is created with the hook content."""
            profile = tmp_path / "profile.ps1"
            assert not profile.exists()
            ok, _msg = write_powershell_mise_hook(profile)
            assert ok is True
            assert profile.exists()
            content = profile.read_text(encoding="utf-8")
            assert POWERSHELL_MISE_HOOK in content
            assert "mise activate pwsh" in content

        def test_appends_hook_to_existing_profile(self, tmp_path: Path) -> None:
            """Hook is appended to an existing profile without overwriting prior content."""
            profile = tmp_path / "profile.ps1"
            profile.write_text("# existing content\n", encoding="utf-8")
            ok, _msg = write_powershell_mise_hook(profile)
            assert ok is True
            content = profile.read_text(encoding="utf-8")
            assert "# existing content" in content
            assert POWERSHELL_MISE_HOOK in content

        def test_idempotent_when_hook_already_present(self, tmp_path: Path) -> None:
            """Hook is not appended a second time when already present."""
            profile = tmp_path / "profile.ps1"
            first_content = f"# existing\n{POWERSHELL_MISE_HOOK}\n"
            profile.write_text(first_content, encoding="utf-8")
            ok, msg = write_powershell_mise_hook(profile)
            assert ok is True
            # Content must be unchanged — hook appears exactly once.
            final = profile.read_text(encoding="utf-8")
            assert final.count("mise activate pwsh") == 1
            assert "already present" in msg

        def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
            """Dry-run returns success but does not create the file."""
            profile = tmp_path / "profile.ps1"
            ok, msg = write_powershell_mise_hook(profile, dry_run=True)
            assert ok is True
            assert not profile.exists()
            assert "Would append" in msg

        def test_parent_directories_created(self, tmp_path: Path) -> None:
            """Missing parent directories are created automatically."""
            profile = tmp_path / "a" / "b" / "profile.ps1"
            ok, _ = write_powershell_mise_hook(profile)
            assert ok is True
            assert profile.exists()

        def test_hook_content_is_correct(self, tmp_path: Path) -> None:
            """The written hook exactly matches the canonical POWERSHELL_MISE_HOOK string."""
            profile = tmp_path / "profile.ps1"
            write_powershell_mise_hook(profile)
            content = profile.read_text(encoding="utf-8")
            assert POWERSHELL_MISE_HOOK in content

        def test_console_output_on_write(self, tmp_path: Path) -> None:
            """Console is called when hook is written."""
            profile = tmp_path / "profile.ps1"
            console = MagicMock()
            write_powershell_mise_hook(profile, console=console)
            console.print.assert_called_once()

        def test_console_output_already_present(self, tmp_path: Path) -> None:
            """Console is called with 'already in' message when hook is already present."""
            profile = tmp_path / "profile.ps1"
            profile.write_text(f"{POWERSHELL_MISE_HOOK}\n", encoding="utf-8")
            console = MagicMock()
            write_powershell_mise_hook(profile, console=console)
            call_args = console.print.call_args[0][0]
            assert "already in" in call_args


    # ---------------------------------------------------------------------------
    # install_system_dependencies with --powershell
    # ---------------------------------------------------------------------------


    class TestInstallSystemDependenciesPowershell:
        """Tests for ``install_system_dependencies(install_powershell=True)``.

        # @trace WL-053
        """

        @patch("thegent.install.install_homebrew", return_value=(True, "already installed"))
        @patch("thegent.install.install_mise", return_value=(True, "mise already installed"))
        @patch("thegent.install.verify_mise_installation", return_value=(True, []))
        def test_powershell_flag_writes_hook(
            self,
            _verify: MagicMock,
            _mise: MagicMock,
            _brew: MagicMock,
            tmp_path: Path,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """install_powershell=True writes the hook to the detected profile."""
            profile = tmp_path / "profile.ps1"
            monkeypatch.setenv("PROFILE", str(profile))
            results = install_system_dependencies(
                install_homebrew_pkg=False,
                install_mise_pkg=False,
                install_powershell=True,
            )
            assert results["powershell"]["installed"] is True
            assert profile.exists()
            assert POWERSHELL_MISE_HOOK in profile.read_text(encoding="utf-8")

        @patch("thegent.install.install_homebrew", return_value=(True, "already installed"))
        @patch("thegent.install.install_mise", return_value=(True, "mise already installed"))
        def test_powershell_flag_false_does_not_write(
            self,
            _mise: MagicMock,
            _brew: MagicMock,
            tmp_path: Path,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """install_powershell=False does not invoke write_powershell_mise_hook."""
            profile = tmp_path / "profile.ps1"
            monkeypatch.setenv("PROFILE", str(profile))
            results = install_system_dependencies(
                install_homebrew_pkg=False,
                install_mise_pkg=False,
                install_powershell=False,
            )
            # powershell key starts as unset (False/empty message).
            assert results["powershell"]["installed"] is False
            assert not profile.exists()

        @patch("thegent.install.install_homebrew", return_value=(True, "already installed"))
        @patch("thegent.install.install_mise", return_value=(True, "mise already installed"))
        def test_powershell_flag_dry_run(
            self,
            _mise: MagicMock,
            _brew: MagicMock,
            tmp_path: Path,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """install_powershell=True with dry_run=True returns success without writing."""
            profile = tmp_path / "profile.ps1"
            monkeypatch.setenv("PROFILE", str(profile))
            results = install_system_dependencies(
                install_homebrew_pkg=False,
                install_mise_pkg=False,
                install_powershell=True,
                dry_run=True,
            )
            assert results["powershell"]["installed"] is True
            assert not profile.exists()
            assert "Would append" in results["powershell"]["message"]

        @patch("thegent.install.install_homebrew", return_value=(True, "already installed"))
        @patch("thegent.install.install_mise", return_value=(True, "mise already installed"))
        @patch("thegent.install.verify_mise_installation", return_value=(True, []))
        def test_results_dict_has_powershell_key(
            self,
            _verify: MagicMock,
            _mise: MagicMock,
            _brew: MagicMock,
        ) -> None:
            """Results dict always contains a 'powershell' key regardless of flag."""
            results = install_system_dependencies(
                install_homebrew_pkg=False,
                install_mise_pkg=False,
                install_powershell=False,
            )
            assert "powershell" in results


    # ---------------------------------------------------------------------------
    # Integration: auto-detection in install_mise triggers PS hook on Windows
    # ---------------------------------------------------------------------------


    class TestInstallMisePowershellAutoDetection:
        """Tests that install_mise writes the PS hook when the env is PowerShell.

        # @trace WL-053
        """

        @patch("thegent.install._command_exists", return_value=False)
        @patch("thegent.install.install_homebrew", return_value=(True, "installed"))
        @patch("thegent.install._run_command", return_value=(0, "", ""))
        @patch("thegent.install._is_powershell_environment", return_value=True)
        @patch("thegent.install.write_powershell_mise_hook")
        @patch("thegent.install.detect_powershell_profile")
        def test_ps_hook_written_on_powershell_environment(
            self,
            mock_detect: MagicMock,
            mock_write: MagicMock,
            mock_is_ps: MagicMock,
            mock_run: MagicMock,
            mock_brew: MagicMock,
            mock_cmd: MagicMock,
            tmp_path: Path,
        ) -> None:
            """When environment is PowerShell, install_mise calls write_powershell_mise_hook."""
            from thegent.install import install_mise

            mock_profile = tmp_path / "profile.ps1"
            mock_detect.return_value = mock_profile
            mock_write.return_value = (True, "hook written")

            # Build a minimal settings object with shell_path already set so the
            # lazy ThegentSettings import inside install_mise is never triggered.
            fake_settings = MagicMock()
            fake_settings.shell_path = "/bin/zsh"
            ok, _msg = install_mise(settings=fake_settings)

            assert ok is True
            mock_write.assert_called_once_with(mock_profile, console=None, dry_run=False)

        @patch("thegent.install._command_exists", return_value=False)
        @patch("thegent.install.install_homebrew", return_value=(True, "installed"))
        @patch("thegent.install._run_command", return_value=(0, "", ""))
        @patch("thegent.install._is_powershell_environment", return_value=False)
        @patch("thegent.install.write_powershell_mise_hook")
        def test_ps_hook_not_written_on_posix_environment(
            self,
            mock_write: MagicMock,
            mock_is_ps: MagicMock,
            mock_run: MagicMock,
            mock_brew: MagicMock,
            mock_cmd: MagicMock,
        ) -> None:
            """When environment is POSIX, install_mise does not call write_powershell_mise_hook."""
            from thegent.install import install_mise

            fake_settings = MagicMock()
            fake_settings.shell_path = "/bin/bash"
            install_mise(settings=fake_settings)

            mock_write.assert_not_called()

