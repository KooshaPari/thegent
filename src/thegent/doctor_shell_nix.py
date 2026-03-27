"""Shell and Nix checks extracted from doctor."""

import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from thegent.infra import run_subprocess_optimized


def check_shell(*, check_result_cls: type[Any]) -> list[Any]:
    res_list: list[Any] = []
    home = Path.home()

    for name, path in [
        (".zshenv", home / ".zshenv"),
        (".zshrc", home / ".zshrc"),
        (".zsh_bundle.zsh", home / ".zsh_bundle.zsh"),
    ]:
        r = check_result_cls(name, "Shell")
        if path.exists():
            try:
                content = path.read_text()
                if "thegent" in content or "THEGENT" in content:
                    r.status = "ok"
                    r.message = f"{name} present (thegent-managed)"
                else:
                    r.status = "warn"
                    r.message = f"{name} exists but may not be thegent-managed"
            except OSError:
                r.status = "warn"
                r.message = f"{name} exists (unreadable)"
        else:
            r.status = "fail"
            r.message = f"{name} missing"
            r.fix_hint = "Run: thegent install -t shell"
        res_list.append(r)

    r = check_result_cls(".zshrc.local", "Shell")
    zshrc_local = home / ".zshrc.local"
    if zshrc_local.exists():
        r.status = "ok"
        r.message = "~/.zshrc.local present (plugins, prompt, runtime)"
    else:
        r.status = "warn"
        r.message = "~/.zshrc.local missing (no fnm/mise, fzf-tab, prompt)"
        r.fix_hint = "Run: thegent install -t shell  (creates from template)"
    res_list.append(r)

    plugins_dir = home / ".zsh" / "plugins"
    for plugin in ["fzf-tab", "zsh-autosuggestions", "fast-syntax-highlighting"]:
        r = check_result_cls(f"Plugin: {plugin}", "Shell")
        if (plugins_dir / plugin).exists():
            r.status = "ok"
            r.message = f"{plugin} installed"
        else:
            r.status = "warn"
            r.message = f"{plugin} not installed"
            r.fix_hint = "Run: thegent install -t shell  (or: ./scripts/install_zsh_plugins.sh)"
        res_list.append(r)

    r = check_result_cls("Prompt", "Shell")
    has_starship = shutil.which("starship") is not None
    has_p10k = (home / ".zsh" / "themes" / "powerlevel10k").exists()
    if has_starship or has_p10k:
        r.status = "ok"
        r.message = "starship" if has_starship else "powerlevel10k"
    else:
        r.status = "warn"
        r.message = "No prompt (starship/p10k)"
        r.fix_hint = "brew install starship  or  git clone powerlevel10k to ~/.zsh/themes/"
    res_list.append(r)

    r = check_result_cls("Runtime (Node)", "Shell")
    has_mise = shutil.which("mise") is not None
    has_fnm = shutil.which("fnm") is not None
    if has_mise or has_fnm:
        r.status = "ok"
        r.message = "mise" if has_mise else "fnm"
    else:
        r.status = "warn"
        r.message = "No Node version manager (mise/fnm)"
        r.fix_hint = "brew install mise  or  brew install fnm"
    res_list.append(r)

    return res_list


def check_nix_daemon_status() -> tuple[bool, str]:
    """Check if Nix daemon is running. Returns (is_running, status_message)."""
    if platform.system() == "Darwin":
        try:
            result = run_subprocess_optimized(
                ["launchctl", "list"],
                check=False,
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout:
                output = (
                    result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
                )
                if "com.determinate.nix-daemon" in output or "nix-daemon" in output.lower():
                    return True, "Running (launchd)"
                if "determinate-nixd" in output.lower():
                    return True, "Running (determinate-nixd)"
            return False, "Not running (launchd)"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Cannot check (launchctl not available)"
    if platform.system() == "Linux":
        try:
            result = run_subprocess_optimized(
                ["systemctl", "--user", "status", "nix-daemon"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True, "Running (systemd)"
            return False, "Not running (systemd)"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Cannot check (systemctl not available)"
    return False, "Unknown platform"


def check_nix(*, check_result_cls: type[Any], project_root: Path) -> list[Any]:
    res_list = []
    nix_path = shutil.which("nix")

    r = check_result_cls("Nix Installed", "Nix Support")
    if nix_path:
        try:
            result = run_subprocess_optimized(["nix", "--version"], capture_output=True, timeout=5)
            stdout = (
                result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
            )
            stderr = (
                result.stderr if isinstance(result.stderr, str) else result.stderr.decode("utf-8", errors="replace")
            )
            if result.returncode == 0 and stdout.strip():
                r.status = "ok"
                r.message = f"Found Nix: {stdout.strip()}"
            elif result.returncode == 0:
                r.status = "warn"
                r.message = "Nix command returned empty version output"
                r.details = "nix --version exited 0 but emitted no stdout"
                r.fix_hint = "Reinstall or repair Nix; then re-run doctor."
            else:
                r.status = "fail"
                r.message = f"Nix binary found, but '--version' failed (exit {result.returncode})"
                bounded_stderr = stderr.strip()[:200] if stderr else "<no stderr>"
                r.details = f"stderr: {bounded_stderr}"
                r.fix_hint = "Run 'nix --version' manually and repair the Nix installation."
        except subprocess.TimeoutExpired:
            r.status = "warn"
            r.message = "Nix command timed out"
            r.fix_hint = "Nix may be initializing. Try again in a moment."
        except PermissionError as exc:
            r.status = "fail"
            r.message = "Nix binary found but not executable"
            r.details = f"{type(exc).__name__}: {str(exc)[:200]}"
            r.fix_hint = f"Check execute permissions for {nix_path}."
        except (subprocess.SubprocessError, OSError) as exc:
            r.status = "fail"
            r.message = "Nix binary found but invocation failed"
            r.details = f"{type(exc).__name__}: {str(exc)[:200]}"
            r.fix_hint = "Run 'nix --version' manually and repair shell/path/runtime issues."
    elif Path("/nix/var/nix/profiles/default/bin/nix").exists():
        r.status = "warn"
        r.message = "Nix installed but not in PATH"
        r.fix_hint = "Reload shell or run: . ~/.zshenv"
    else:
        r.status = "warn"
        r.message = "Nix not found (optional)"
        r.fix_hint = "Install Nix from https://nixos.org/ or use Determinate Systems installer."
    res_list.append(r)

    if nix_path:
        r = check_result_cls("Nix Daemon", "Nix Support")
        daemon_running, daemon_msg = check_nix_daemon_status()
        if daemon_running:
            r.status = "ok"
            r.message = daemon_msg
        else:
            r.status = "warn"
            r.message = daemon_msg
            r.fix_hint = "Nix daemon may start automatically when needed"
        res_list.append(r)

    r = check_result_cls("Flake config", "Nix Support")
    flake_path = project_root / "flake.nix"
    try:
        if flake_path.exists():
            r.status = "ok"
            r.message = "flake.nix exists"
        elif nix_path:
            r.status = "fail"
            r.message = "flake.nix missing (required for Nix development environment)"
            r.fix_hint = "Create flake.nix or remove Nix if not using it"
        else:
            r.status = "ok"
            r.message = "flake.nix not needed (Nix not installed)"
    except Exception:
        r.status = "fail"
        r.message = "Could not check flake.nix (permission error)"
    res_list.append(r)

    r = check_result_cls("direnv integration", "Nix Support")
    if Path(".envrc").exists():
        r.status = "ok"
        r.message = ".envrc exists"
        if not shutil.which("direnv"):
            r.status = "warn"
            r.message += " but 'direnv' command not found"
            r.fix_hint = "Install direnv: brew install direnv"
    else:
        r.status = "warn"
        r.message = ".envrc missing"
        r.fix_hint = "Run: thegent install (to regenerate environment files)"
    res_list.append(r)

    return res_list
