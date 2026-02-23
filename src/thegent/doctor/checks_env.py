"""Doctor - Environment checks module.

Contains: _check_environment, _check_shim_binaries
"""

import os
import re
import shutil
from pathlib import Path

from thegent.doctor_models import CheckResult
from thegent.infra import run_subprocess_optimized


def check_environment(project_root: Path | None = None) -> list[CheckResult]:
    """Check environment variables and PATH configuration."""
    res_list = []
    project_root = project_root or Path.cwd()

    # PATH check for ~/.local/bin
    r = CheckResult("Shim PATH", "Environment")
    local_bin = str(Path.home() / ".local" / "bin")
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    if local_bin in path_dirs:
        if path_dirs.index(local_bin) < 5:
            r.status = "ok"
            r.message = "~/.local/bin is correctly placed early in PATH"
        else:
            r.status = "warn"
            r.message = "~/.local/bin is in PATH but late; shims might be overridden"
            r.fix_hint = "Move ~/.local/bin to the front of your PATH in your shell profile."
    else:
        r.status = "fail"
        r.message = "~/.local/bin not found in PATH"
        r.fix_hint = f"Add {local_bin} to your PATH."
    res_list.append(r)

    # Shims installation
    r = CheckResult("Tool Shims", "Environment")
    bin_dir = Path.home() / ".local" / "bin"
    installed_shims = []
    shim_details = {}

    for shim in ["git", "grep", "find", "jq", "uv", "clode", "codex", "copilot", "droid", "roid"]:
        shim_path = bin_dir / shim
        if shim_path.exists():
            installed_shims.append(shim)
            try:
                content = shim_path.read_text()
                if shim_path.is_symlink():
                    target = shim_path.resolve()
                    shim_details[shim] = {"type": "symlink", "target": str(target), "exists": target.exists()}
                elif "thegent" in content.lower() or "shim" in content.lower():
                    lines = content.split("\n")
                    target_binary = None
                    for line in lines[:20]:
                        line_lower = line.lower()
                        if "real_" in line_lower:
                            if "resolve_real_binary" in line_lower:
                                match = re.search(r"resolve_real_binary\s+([a-z-]+)", line_lower)
                                if match:
                                    target_binary = shutil.which(match.group(1))
                                    if target_binary:
                                        break
                            elif "command -v" in line_lower:
                                match = re.search(r"command -v\s+([a-z-]+)", line_lower)
                                if match:
                                    target_binary = shutil.which(match.group(1))
                                    if target_binary:
                                        break
                        if "exec" in line_lower or "which" in line_lower:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part in ["exec", "which"] and i + 1 < len(parts):
                                    potential_binary = parts[i + 1].strip("'\"")
                                    if "/" in potential_binary or potential_binary in [
                                        "git", "grep", "find", "jq", "uv", "clode", "codex", "copilot", "droid", "roid"
                                    ]:
                                        target_binary = shutil.which(potential_binary)
                                        break
                            if target_binary:
                                break
                    shim_details[shim] = {
                        "type": "script",
                        "target": target_binary,
                        "exists": target_binary is not None and Path(target_binary).exists() if target_binary else False,
                    }
                else:
                    shim_details[shim] = {"type": "unknown", "target": None, "exists": False}
            except (OSError, UnicodeDecodeError):
                shim_details[shim] = {"type": "unknown", "target": None, "exists": False}

    # Codex/Copilot path checks
    for agent in ["codex", "copilot"]:
        agent_path = shutil.which(agent)
        if agent_path:
            r_agent = CheckResult(f"{agent} path", "Environment")
            if ".local/bin" in agent_path:
                r_agent.status = "ok"
                r_agent.message = f"{agent} -> {agent_path} (thegent shim)"
            else:
                r_agent.status = "warn"
                r_agent.message = f"{agent} -> {agent_path} (not thegent shim; may cause git errors)"
                r_agent.fix_hint = "Run: thegent install-shims --force"
            res_list.append(r_agent)

    # Harmful ps shim check
    ps_shim = bin_dir / "ps"
    if ps_shim.exists():
        try:
            content = ps_shim.read_text()
            if "thegent" in content and "ps" in content:
                r_ps = CheckResult("ps Shim (harmful)", "Environment")
                r_ps.status = "fail"
                r_ps.message = "~/.local/bin/ps shadows system ps; causes 130s+ hangs"
                r_ps.fix_hint = "Run: rm ~/.local/bin/ps"
                res_list.append(r_ps)
        except OSError:
            pass

    if len(installed_shims) >= 6:
        r.status = "ok"
        r.message = f"Installed shims: {', '.join(installed_shims)}"
    elif installed_shims:
        r.status = "warn"
        r.message = f"Only some shims installed: {', '.join(installed_shims)}"
        r.fix_hint = "Run: thegent install-shims --all"
    else:
        r.status = "fail"
        r.message = "No thegent tool shims found in ~/.local/bin"
        r.fix_hint = "Run: thegent install-shims --all"
    res_list.append(r)

    # Enhanced shim version checks
    for shim_name, details in shim_details.items():
        if details.get("type") == "unknown":
            continue

        r_shim = CheckResult(f"{shim_name} Shim Details", "Environment")
        target = details.get("target")
        exists = details.get("exists", False)

        if target and exists:
            version_info = None
            try:
                if shim_name in ["git", "grep", "find", "jq", "uv"]:
                    if shim_name == "git":
                        result = run_subprocess_optimized(["git", "--version"], capture_output=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            stdout = result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
                            version_info = stdout.strip()
                    elif shim_name == "grep":
                        result = run_subprocess_optimized(["grep", "--version"], capture_output=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            stdout = result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
                            version_info = stdout.split("\n")[0] if stdout else None
                    elif shim_name == "uv":
                        result = run_subprocess_optimized(["uv", "--version"], capture_output=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            stdout = result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
                            version_info = stdout.strip()
            except Exception:
                pass

            if version_info:
                r_shim.status = "ok"
                r_shim.message = f"{shim_name} -> {target} ({version_info})"
            else:
                r_shim.status = "ok"
                r_shim.message = f"{shim_name} -> {target} (binary available)"
        elif target:
            r_shim.status = "warn"
            r_shim.message = f"{shim_name} -> {target} (target binary not found)"
            r_shim.fix_hint = f"Install {shim_name} or fix shim target"
        else:
            r_shim.status = "warn"
            r_shim.message = f"{shim_name} shim exists but target unclear"

        res_list.append(r_shim)

    return res_list


def check_shim_binaries(project_root: Path | None = None) -> list[CheckResult]:
    """Check thegent-hooks and thegent-shims (Rust) binary version and availability."""
    res_list: list[CheckResult] = []
    project_root = project_root or Path.cwd()

    for name, candidates in [
        ("thegent-hooks", ["thegent-hooks", "crates/target/release/thegent-hooks"]),
        ("thegent-shims", ["thegent-shims", "crates/target/release/thegent-shims"]),
    ]:
        r = CheckResult(name, "Shim Binaries")
        bin_path = shutil.which(name)
        if not bin_path:
            for rel in candidates[1:]:
                p = project_root / rel
                if p.exists() and p.is_file():
                    bin_path = str(p)
                    break

        if bin_path:
            r.status = "ok"
            r.message = f"Found: {bin_path}"
            # Try to get version
            try:
                result = run_subprocess_optimized([bin_path, "--version"], capture_output=True, timeout=5)
                if result.returncode == 0 and result.stdout:
                    version = result.stdout.decode("utf-8", errors="replace").strip().split("\n")[0]
                    r.message += f" ({version})"
            except Exception:
                pass
        else:
            r.status = "warn"
            r.message = f"{name} not found in PATH or project"
            r.fix_hint = f"Build: cd {project_root}/crates && cargo build --release"
        res_list.append(r)

    return res_list
