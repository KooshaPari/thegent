"""Dependency checks extracted from doctor."""

import platform
import shutil
from pathlib import Path
from typing import Any

from thegent.infra import run_subprocess_optimized


def check_dependencies(*, check_result_cls: type[Any], deps: bool = False, project_root: Path) -> list[Any]:
    res_list = []

    r = check_result_cls("Node.js", "Dependencies")
    node_path = shutil.which("node")
    if node_path:
        try:
            result = run_subprocess_optimized(["node", "--version"], capture_output=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                ver = (
                    result.stdout.strip()
                    if isinstance(result.stdout, str)
                    else result.stdout.decode("utf-8", errors="replace").strip()
                )
                r.status = "ok"
                r.message = f"Found Node.js {ver} at {node_path}"
        except Exception as e:
            r.status = "warn"
            r.message = f"Node.js found but failed to get version: {e}"
    else:
        r.status = "fail"
        r.message = "Node.js not found in PATH"
        r.fix_hint = "Install Node.js (v18+) from https://nodejs.org/"
    res_list.append(r)

    r = check_result_cls("Claude Code CLI", "Dependencies")
    claude_path = shutil.which("claude")
    if claude_path:
        try:
            r.status = "ok"
            r.message = f"Found 'claude' at {claude_path}"
        except Exception:
            r.status = "ok"
            r.message = f"Found 'claude' at {claude_path}"
    else:
        r.status = "fail"
        r.message = "Claude Code CLI ('claude') not found in PATH"
        r.fix_hint = "Install via: npm install -g @anthropic-ai/claude-code"
    res_list.append(r)

    r = check_result_cls("Codex CLI", "Dependencies")
    codex_path = shutil.which("codex")
    if codex_path:
        r.status = "ok"
        r.message = f"Found 'codex' at {codex_path}"
    else:
        r.status = "warn"
        r.message = "Codex CLI ('codex') not found in PATH"
        r.fix_hint = "Install via: npm install -g @openai/codex"
    res_list.append(r)

    r = check_result_cls("CLIProxyAPIPlus", "Dependencies")
    proxy_path = shutil.which("cli-proxy-api-plus")
    if proxy_path:
        r.status = "ok"
        r.message = f"Found 'cli-proxy-api-plus' at {proxy_path}"
    else:
        r.status = "fail"
        r.message = "CLIProxyAPIPlus binary not found in PATH"
        r.fix_hint = "Download and install from thegent repository or releases."
    res_list.append(r)

    from thegent.errors import get_install_hint

    for tool, name, optional in [
        ("rg", "ripgrep", True),
        ("fd", "fd-find", True),
        ("git", "Git", False),
        ("jq", "jq", True),
    ]:
        r = check_result_cls(name, "Dependencies")
        path = shutil.which(tool)
        if path:
            r.status = "ok"
            r.message = f"Found '{tool}' at {path}"
        else:
            r.status = "warn"
            r.message = f"'{tool}' not found" + (" (optional — install for 10x speedup)" if optional else " in PATH")
            r.fix_hint = get_install_hint(tool)
        res_list.append(r)

    has_mise_toml = (project_root / ".mise.toml").exists()
    has_pyproject = (project_root / "pyproject.toml").exists()
    has_brewfile = (project_root / "Brewfile").exists()

    r = check_result_cls("mise", "Dependencies")
    mise_path = shutil.which("mise")
    if mise_path:
        r.status = "ok"
        r.message = f"Found 'mise' at {mise_path}"
    elif has_mise_toml:
        r.status = "fail"
        r.message = "mise is required by repo policy (.mise.toml present) but not found"
        r.fix_hint = "Install with Homebrew (`brew install mise`) or Nix (`nix profile install nixpkgs#mise`)."
    else:
        r.status = "warn"
        r.message = "mise not found"
        r.fix_hint = "Install mise for consistent runtime pinning."
    res_list.append(r)

    r = check_result_cls("uv", "Dependencies")
    uv_path = shutil.which("uv")
    if uv_path:
        r.status = "ok"
        r.message = f"Found 'uv' at {uv_path}"
    elif has_pyproject:
        r.status = "fail"
        r.message = "uv is required by repo workflow (pyproject.toml present) but not found"
        r.fix_hint = "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    else:
        r.status = "warn"
        r.message = "uv not found"
        r.fix_hint = "Install uv for faster Python dependency management."
    res_list.append(r)

    if platform.system() == "Darwin":
        r = check_result_cls("Homebrew", "Dependencies")
        brew_path = shutil.which("brew")
        if brew_path:
            r.status = "ok"
            r.message = f"Found 'brew' at {brew_path}"
        elif has_brewfile:
            r.status = "fail"
            r.message = "Homebrew is required by repo setup (Brewfile present) but not found"
            r.fix_hint = 'Install Homebrew: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        else:
            r.status = "warn"
            r.message = "Homebrew not found"
            r.fix_hint = "Install Homebrew for macOS host dependency management."
        res_list.append(r)

    if deps and mise_path:
        r = check_result_cls("mise doctor", "Dependencies")
        try:
            result = run_subprocess_optimized(["mise", "doctor"], capture_output=True, timeout=20)
            if result.returncode == 0:
                r.status = "ok"
                r.message = "mise doctor: OK"
            else:
                stderr = result.stderr if isinstance(result.stderr, str) else result.stderr.decode("utf-8", errors="replace")
                r.status = "warn"
                r.message = "mise doctor reported issues"
                r.details = (stderr or "unknown issue")[:300]
                r.fix_hint = "Run `mise doctor` directly and address reported configuration issues."
        except Exception as e:
            r.status = "warn"
            r.message = f"Failed to run mise doctor: {e}"
        res_list.append(r)

    if deps and platform.system() == "Darwin" and has_brewfile and shutil.which("brew"):
        r = check_result_cls("brew bundle check", "Dependencies")
        try:
            result = run_subprocess_optimized(
                ["brew", "bundle", "check", "--file", str(project_root / "Brewfile")],
                capture_output=True,
                timeout=30,
            )
            if result.returncode == 0:
                r.status = "ok"
                r.message = "brew bundle check: OK"
            else:
                stdout = result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
                r.status = "warn"
                r.message = "brew bundle check reported missing packages"
                r.details = (stdout or "bundle drift detected")[:300]
                r.fix_hint = "Run `brew bundle --file Brewfile` from repo root."
        except Exception as e:
            r.status = "warn"
            r.message = f"Failed to run brew bundle check: {e}"
        res_list.append(r)

    return res_list
