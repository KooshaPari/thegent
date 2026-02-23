"""Doctor module for comprehensive health and preflight checks of thegent environment."""

# Backward compatibility - import from new submodule
from thegent.doctor.checks_env import check_environment as _check_environment_impl
from thegent.doctor.checks_env import check_shim_binaries as _check_shim_binaries_impl

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from thegent.config import ThegentSettings
from thegent.doctor_dependencies import check_dependencies as _check_dependencies_impl
from thegent.doctor_models import CheckResult
from thegent.doctor_project_root import detect_project_root
from thegent.doctor_setup_checks import (
    check_configuration as _check_configuration_impl,
    check_connectivity as _check_connectivity_impl,
    check_isolation as _check_isolation_impl,
)
from thegent.doctor_shell_nix import (
    check_nix as _check_nix_impl,
    check_shell as _check_shell_impl,
)
from thegent.infra import run_subprocess_optimized

import psutil


def _check_dependencies(deps: bool = False) -> list[CheckResult]:
    return _check_dependencies_impl(
        check_result_cls=CheckResult,
        deps=deps,
        project_root=_project_root_cache or Path.cwd(),
    )


def _check_configuration() -> list[CheckResult]:
    return _check_configuration_impl(check_result_cls=CheckResult)


def _check_isolation() -> list[CheckResult]:
    return _check_isolation_impl(check_result_cls=CheckResult)


def _check_connectivity(auto_start: bool = True) -> list[CheckResult]:
    return _check_connectivity_impl(check_result_cls=CheckResult, console=console, auto_start=auto_start)

def _check_environment() -> list[CheckResult]:
    """Check environment variables and PATH configuration.
    
    Delegates to thegent.doctor.checks_env module.
    """
    return _check_environment_impl(project_root=_project_root_cache)


def _check_shim_binaries() -> list[CheckResult]:
    """Check thegent-hooks and thegent-shims (Rust) binary version and availability.
    
    Delegates to thegent.doctor.checks_env module.
    """
    return _check_shim_binaries_impl(project_root=_project_root_cache)


def _check_providers() -> list[CheckResult]:
    """Validate all configured OAuth providers via proxy (ROB-016).

    REQUIRES OAuth credentials - API keys are NOT used for OAuth-capable providers.
    Checks providers from /v1/models AND cliproxy config so nothing is missed.
    """
    res_list: list[CheckResult] = []
    proxy_url = "http://127.0.0.1:8317/v1/models"
    providers_from_models: dict[str, list[str]] = {}
    configured_providers = _get_configured_providers_from_cliproxy()

    try:
        resp = httpx.get(proxy_url, timeout=5.0)
        if resp.status_code != 200:
            r = CheckResult("Models API", "Providers")
            r.status = "warn"  # Changed from fail to warn
            r.message = f"Could not fetch models from proxy (HTTP {resp.status_code})"
            r.details = "Suspicion Level: LOW\nCLIProxy returned non-200 status. This is OK if you're not using provider validation."
            r.fix_hint = "Ensure CLIProxy is running: thegent mcp up"
            res_list.append(r)
            return res_list
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        # Connection refused or timeout - CLIProxy not running
        r = CheckResult("Providers", "Providers")
        r.status = "warn"  # Changed from fail to warn - CLIProxy may not be needed for all workflows
        r.message = f"CLIProxy not reachable: {e}"
        r.details = "Suspicion Level: LOW\nCLIProxy is not running. This is OK if you're not using provider validation."
        r.fix_hint = "Start CLIProxy if needed: thegent mcp up"
        res_list.append(r)
        return res_list

    try:
        data = resp.json()
        models = data.get("models", []) or data.get("data", [])

        for m in models:
            provider = m.get("owned_by", "unknown")
            mid = m.get("id")
            if provider not in providers_from_models:
                providers_from_models[provider] = []
            providers_from_models[provider].append(mid)

        all_providers = set(providers_from_models) | configured_providers
        for provider in sorted(all_providers):
            r = CheckResult(f"Provider: {provider}", "Providers")
            p_models = providers_from_models.get(provider, [])
            test_model = p_models[0] if p_models else None
            if not test_model:
                try:
                    from thegent.agents.cliproxy_manager import (
                        PROVIDER_LOGIN_CONFIG,
                        _get_provider_definitions,
                    )

                    # Try PROVIDER_LOGIN_CONFIG first (has model field for OAuth providers)
                    login_cfg = PROVIDER_LOGIN_CONFIG.get(provider.lower(), {})
                    if login_cfg.get("model"):
                        test_model = login_cfg["model"]
                    else:
                        # Fallback to provider_definitions.json
                        defs_ = _get_provider_definitions()
                        cfg = defs_.get(provider, {}) if isinstance(defs_.get(provider), dict) else {}
                        test_model = cfg.get("model")

                    # If still no model and provider has no models in /v1/models, skip validation
                    if not test_model and not p_models:
                        r.status = "warn"
                        r.message = "No models available (provider may need configuration)"
                        r.fix_hint = f"Run: thegent cliproxy login {provider}"
                        res_list.append(r)
                        continue

                    # Last resort: use provider name (may fail, but better than skipping)
                    if not test_model:
                        test_model = provider
                except Exception:
                    # If we can't get model info and no models from /v1/models, skip
                    if not p_models:
                        r.status = "warn"
                        r.message = "No models available (provider may need configuration)"
                        r.fix_hint = f"Run: thegent cliproxy login {provider}"
                        res_list.append(r)
                        continue
                    test_model = provider
            try:
                payload = {"model": test_model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}
                test_resp = httpx.post(
                    "http://127.0.0.1:8317/v1/chat/completions",
                    json=payload,
                    timeout=20.0,
                )
                if test_resp.status_code == 200:
                    r.status = "ok"
                    r.message = f"Validated ({len(p_models)} models)" if p_models else "Validated"
                else:
                    r.status = "fail"  # Required feature - providers must work
                    r.message = f"HTTP {test_resp.status_code}"
                    try:
                        err = test_resp.json()
                        msg = err.get("error", {}).get("message", test_resp.text[:100])
                        r.details = msg
                    except Exception:
                        r.details = test_resp.text[:100]
                    # Check if it's an auth error - suggest OAuth login
                    if test_resp.status_code in (401, 403):
                        r.fix_hint = f"OAuth authentication failed. Run: thegent cliproxy login {provider}"
                    else:
                        r.fix_hint = f"Check provider configuration: thegent cliproxy login {provider}"
            except Exception as e:
                r.status = "fail"  # Required feature
                r.message = f"Inaccessible: {e!s}"
                r.fix_hint = f"Check OAuth credentials: thegent cliproxy login {provider}"
            res_list.append(r)

        if not all_providers:
            r = CheckResult("Providers", "Providers")
            r.status = "fail"  # Required - at least one provider must be configured
            r.message = "No active providers found in proxy"
            r.fix_hint = "Run: thegent cliproxy login <provider> (e.g., claude, codex, gemini)"
            res_list.append(r)

    except Exception as e:
        r = CheckResult("Providers", "Providers")
        # Distinguish between connection errors (CLIProxy not running) and other errors
        if "Connection refused" in str(e) or "ConnectError" in str(type(e).__name__):
            r.status = "warn"  # Changed from fail to warn - CLIProxy may not be needed
            r.message = f"CLIProxy not reachable: {e}"
            r.details = (
                "Suspicion Level: LOW\nCLIProxy is not running. This is OK if you're not using provider validation."
            )
            r.fix_hint = "Start CLIProxy if needed: thegent mcp up"
        else:
            r.status = "fail"
            r.message = f"Failed to fetch providers: {e}"
            r.details = f"Error details: {str(e)[:200]}"
            r.fix_hint = "Ensure CLIProxy is running: thegent mcp up"
        res_list.append(r)

    return res_list


def _check_ollama() -> list[CheckResult]:
    """Check Ollama daemon availability and local models.

    WL-118: Ollama local model provider check.
    """
    res_list: list[CheckResult] = []

    # First check if Ollama binary exists
    r = CheckResult("Ollama CLI", "Providers")
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        r.status = "warn"
        r.message = "Ollama CLI ('ollama') not found in PATH"
        r.fix_hint = "Install Ollama: https://ollama.com/download"
        res_list.append(r)
        return res_list

    r.status = "ok"
    r.message = f"Found 'ollama' at {ollama_path}"
    res_list.append(r)

    # Now check if the daemon is running
    r = CheckResult("Ollama Daemon", "Providers")
    try:
        from thegent.utils.routing_impl.ollama_provider import is_ollama_available, get_available_models

        if is_ollama_available():
            r.status = "ok"
            r.message = "Ollama daemon is running at localhost:11434"
            res_list.append(r)

            # Also get available models
            r_models = CheckResult("Ollama Models", "Providers")
            try:
                models = get_available_models()
                if models:
                    r_models.status = "ok"
                    r_models.message = f"Available models: {', '.join(models[:5])}"
                    if len(models) > 5:
                        r_models.message += f" (+{len(models) - 5} more)"
                else:
                    r_models.status = "warn"
                    r_models.message = "Daemon running but no models installed"
                    r_models.fix_hint = "Pull models with: ollama pull llama3.3"
            except Exception as e:
                r_models.status = "warn"
                r_models.message = f"Could not fetch models: {e}"
            res_list.append(r_models)
        else:
            r.status = "warn"
            r.message = "Ollama daemon not running at localhost:11434"
            r.fix_hint = "Start with: ollama serve"
            res_list.append(r)
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check Ollama status: {e}"
        res_list.append(r)

    return res_list


def _check_headless() -> list[CheckResult]:
    """Perform headless test runs for Claude and Codex (ROB-016).

    REQUIRES OAuth credentials (not API keys) for providers that support OAuth.
    Checks for stuck processes before running tests to avoid false failures.
    """
    res_list = []
    from thegent.agents.cliproxy_manager import _has_oauth_credentials

    # Check for stuck processes before running headless tests
    # Only flag processes that are > 5 minutes old AND show no activity
    # Long-running sessions (>1 hour) are assumed active (user's chats run for hours)
    stuck_claude = _find_stuck_processes(["claude", "clode"], max_age_seconds=300)
    stuck_codex = _find_stuck_processes(["codex", "dex", "codex flash"], max_age_seconds=300)
    stuck_droid = _find_stuck_processes(["droid", "roid"], max_age_seconds=300)

    # Claude Headless (requires OAuth, not API key)
    r = CheckResult("Claude Headless", "Headless Runs")
    if not shutil.which("clode"):
        r.status = "fail"  # Required feature
        r.message = "clode shim not found in PATH"
        r.fix_hint = "Run: thegent install-shims --all"
        res_list.append(r)
    # Check if OAuth credentials exist (required for headless runs)
    elif not _has_oauth_credentials(ThegentSettings(), "claude"):
        r.status = "fail"
        r.message = "Skipped (Claude OAuth credentials not found)"
        r.fix_hint = "Run: thegent cliproxy login claude"
        res_list.append(r)
    elif stuck_claude:
        # Warn about stuck processes but don't fail - long-running sessions are OK
        stuck_info = ", ".join([f"PID {pid}" for pid, _, _ in stuck_claude[:3]])
        r.status = "warn"
        r.message = f"Potential stuck processes detected: {stuck_info}"
        r.details = "Long-running sessions are OK if actively working. Doctor will skip headless test."
        r.fix_hint = "Check processes manually: ps aux | grep claude"
        res_list.append(r)
    else:
        try:
            # Try a very simple print run
            process = run_subprocess_optimized(
                ["clode", "haiku", "--print", "respond with 'pong'"],
                capture_output=True,
                timeout=90,  # Increased timeout
                env={**os.environ, "THGENT_DEBUG": "0", "THGENT_LOG_LEVEL": "ERROR"},
            )
            stdout_text = (
                process.stdout
                if isinstance(process.stdout, str)
                else (process.stdout.decode("utf-8", errors="replace") if process.stdout else "")
            )
            stderr_text = (
                process.stderr
                if isinstance(process.stderr, str)
                else (process.stderr.decode("utf-8", errors="replace") if process.stderr else "")
            )
            if process.returncode == 0 and stdout_text and "pong" in stdout_text.lower():
                r.status = "ok"
                r.message = "Claude Code headless run successful"
            else:
                r.status = "fail"  # Required feature
                r.message = f"Claude Code headless run failed (code {process.returncode})"
                # Capture last line or interesting part
                output = (stderr_text or stdout_text or "").strip()
                if output:
                    r.details = output.splitlines()[-1] if "\n" in output else output[:200]
                r.fix_hint = "Check OAuth credentials: thegent cliproxy login claude"
        except subprocess.TimeoutExpired:
            r.status = "warn"  # Changed from fail to warn - timeout might be due to active sessions
            r.message = "Claude Code headless run timed out (90s)"
            r.details = "This may be normal if other Claude sessions are actively running"
            r.fix_hint = "Check for active sessions: ps aux | grep claude"
        except Exception as e:
            r.status = "fail"  # Required feature
            r.message = f"Claude Code headless run error: {str(e)[:100]}"
            r.fix_hint = "Check OAuth credentials: thegent cliproxy login claude"
        res_list.append(r)

    # Codex Headless (requires OAuth, not API key)
    r = CheckResult("Codex Headless", "Headless Runs")
    if not shutil.which("dex"):
        r.status = "fail"  # Required feature
        r.message = "dex shim not found in PATH"
        r.fix_hint = "Run: thegent install-shims --all"
        res_list.append(r)
    # Check if OAuth credentials exist (required for headless runs)
    elif not _has_oauth_credentials(ThegentSettings(), "codex"):
        r.status = "fail"
        r.message = "Skipped (Codex OAuth credentials not found)"
        r.fix_hint = "Run: thegent cliproxy login codex"
        res_list.append(r)
    elif stuck_codex:
        # Warn about stuck processes but don't fail - long-running sessions are OK
        stuck_info = ", ".join([f"PID {pid}" for pid, _, _ in stuck_codex[:3]])
        r.status = "warn"
        r.message = f"Potential stuck processes detected: {stuck_info}"
        r.details = "Long-running sessions are OK if actively working. Doctor will skip headless test."
        r.fix_hint = "Check processes manually: ps aux | grep codex"
        res_list.append(r)
    else:
        try:
            process = run_subprocess_optimized(
                ["dex", "flash", "--print", "respond with 'pong'"],
                capture_output=True,
                timeout=90,  # Increased timeout
                env={**os.environ, "THGENT_DEBUG": "0", "THGENT_LOG_LEVEL": "ERROR"},
            )
            stdout_text = (
                process.stdout
                if isinstance(process.stdout, str)
                else (process.stdout.decode("utf-8", errors="replace") if process.stdout else "")
            )
            stderr_text = (
                process.stderr
                if isinstance(process.stderr, str)
                else (process.stderr.decode("utf-8", errors="replace") if process.stderr else "")
            )
            if process.returncode == 0 and stdout_text and "pong" in stdout_text.lower():
                r.status = "ok"
                r.message = "Codex headless run successful"
            else:
                r.status = "fail"  # Required feature
                r.message = f"Codex headless run failed (code {process.returncode})"
                output = (stderr_text or stdout_text or "").strip()
                if output:
                    r.details = output.splitlines()[-1] if "\n" in output else output[:200]
                r.fix_hint = "Check OAuth credentials: thegent cliproxy login codex"
        except subprocess.TimeoutExpired:
            r.status = "warn"  # Changed from fail to warn - timeout might be due to active sessions
            r.message = "Codex headless run timed out (90s)"
            r.details = "This may be normal if other Codex sessions are actively running"
            r.fix_hint = "Check for active sessions: ps aux | grep codex"
        except Exception as e:
            r.status = "fail"  # Required feature
            r.message = f"Codex headless run error: {str(e)[:100]}"
            r.fix_hint = "Check OAuth credentials: thegent cliproxy login codex"
        res_list.append(r)

    # Droid Headless (requires droid/roid shims)
    r = CheckResult("Droid Headless", "Headless Runs")
    droid_shim = shutil.which("droid")
    roid_shim = shutil.which("roid")

    if not droid_shim and not roid_shim:
        r.status = "warn"  # Warning, not failure - droids are optional
        r.message = "droid/roid shims not found in PATH"
        r.fix_hint = "Run: thegent install-shims --all"
        res_list.append(r)
    elif stuck_droid:
        # Warn about stuck processes but don't fail - long-running sessions are OK
        stuck_info = ", ".join([f"PID {pid}" for pid, _, _ in stuck_droid[:3]])
        r.status = "warn"
        r.message = f"Potential stuck processes detected: {stuck_info}"
        r.details = "Long-running sessions are OK if actively working. Doctor will skip headless test."
        r.fix_hint = "Check processes manually: ps aux | grep droid"
        res_list.append(r)
    else:
        try:
            # Try a simple droid exec test
            droid_cmd = droid_shim or roid_shim
            if droid_cmd is None:
                raise RuntimeError("Neither droid nor roid shim is configured")
            process = run_subprocess_optimized(
                [droid_cmd, "exec", "--help"],
                capture_output=True,
                timeout=10,
                env={**os.environ, "THGENT_DEBUG": "0", "THGENT_LOG_LEVEL": "ERROR"},
            )
            stdout_text = (
                process.stdout
                if isinstance(process.stdout, str)
                else (process.stdout.decode("utf-8", errors="replace") if process.stdout else "")
            )
            if process.returncode == 0 or (
                stdout_text and ("usage" in stdout_text.lower() or "help" in stdout_text.lower())
            ):
                r.status = "ok"
                r.message = f"Droid headless run successful ({droid_cmd})"
            else:
                r.status = "warn"
                r.message = f"Droid command available but test failed (code {process.returncode})"
                r.details = "Droid may need configuration or droids directory setup"
                r.fix_hint = "Check droid setup: thegent list-droids"
        except subprocess.TimeoutExpired:
            r.status = "warn"
            r.message = "Droid headless run timed out (10s)"
            r.details = "This may be normal if droid is initializing"
            r.fix_hint = "Check droid setup: thegent list-droids"
        except FileNotFoundError:
            r.status = "warn"
            r.message = "Droid command not found"
            r.fix_hint = "Run: thegent install-shims --all"
        except Exception as e:
            r.status = "warn"
            r.message = f"Droid headless run error: {str(e)[:100]}"
            r.fix_hint = "Check droid setup: thegent list-droids"
        res_list.append(r)

    return res_list


def _check_process_health_v2(
    info: "ProcessInfo",
    current_time: float,
    high_memory_processes: list,
    high_fd_processes: list,
    orphaned_processes: list,
) -> int:
    """Check health of a single process. Returns 1 if zombie, else 0. WP-P2: Fix PERF203."""
    try:
        # Get detailed info using psutil
        proc = psutil.Process(info.pid)

        # Check for zombies
        if proc.status() == psutil.STATUS_ZOMBIE:
            return 1

        # Check memory usage
        memory_mb = proc.memory_info().rss / 1024 / 1024
        if memory_mb > 500:  # > 500MB
            high_memory_processes.append((info.pid, info.name, memory_mb, info.cmdline[:80]))

        # Check file descriptors
        try:
            num_fds = (
                proc.num_fds() if hasattr(proc, "num_fds") else len(proc.open_files()) + len(proc.net_connections())
            )
            if num_fds > 100:  # > 100 FDs
                high_fd_processes.append((info.pid, info.name, num_fds, info.cmdline[:80]))
        except (psutil.AccessDenied, AttributeError):
            pass

        # Check for orphaned processes (parent is init/systemd)
        try:
            parent = proc.parent()
            if parent and parent.pid == 1:
                runtime = current_time - info.create_time
                if runtime > 3600:  # > 1 hour
                    # Check if it's a thegent-related process
                    cmdline_lower = info.cmdline.lower()
                    if any(keyword in cmdline_lower for keyword in ["thegent", "claude", "codex", "droid", "cliproxy"]):
                        orphaned_processes.append((info.pid, info.name, runtime / 3600, info.cmdline[:80]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return 0


def _check_process_leaks() -> list[CheckResult]:
    """Check for potential process leaks and optimization opportunities."""
    res_list = []

    # Process Leak Analysis
    r = CheckResult("Process Leak Analysis", "Process Analysis & Leak Detection")
    try:
        issues = []
        zombie_count = 0
        high_memory_processes = []
        high_fd_processes = []
        orphaned_processes = []

        # Analyze processes
        process_infos = []
        for proc in psutil.process_iter(["pid", "name", "cmdline", "status", "memory_info", "num_fds", "create_time"]):
            info = _extract_process_info(proc)
            if info:
                process_infos.append(info)

        current_time = time.time()

        for info in process_infos:
            zombie_count += _check_process_health_v2(
                info, current_time, high_memory_processes, high_fd_processes, orphaned_processes
            )

        # Build suspicion report
        suspicion_level = "low"
        suggestions = []

        if zombie_count > 0:
            issues.append(f"{zombie_count} zombie process(es)")
            suspicion_level = "medium" if suspicion_level == "low" else suspicion_level
            suggestions.append("Clean up zombies: ps aux | grep '<defunct>' | awk '{print $2}' | xargs kill -9")

        if len(high_memory_processes) > 5:
            top_memory = sorted(high_memory_processes, key=lambda x: x[2], reverse=True)[:5]
            issues.append(f"{len(high_memory_processes)} high-memory processes (>500MB)")
            suspicion_level = "high" if suspicion_level in ["low", "medium"] else suspicion_level
            suggestions.append(f"Top memory hogs: {', '.join([f'PID {p[0]} ({p[2]:.0f}MB)' for p in top_memory])}")
            suggestions.append("Investigate: ps aux --sort=-%mem | head -10")

        if len(high_fd_processes) > 3:
            top_fds = sorted(high_fd_processes, key=lambda x: x[2], reverse=True)[:3]
            issues.append(f"{len(high_fd_processes)} high-FD processes (>100 FDs)")
            suspicion_level = "high" if suspicion_level in ["low", "medium"] else suspicion_level
            suggestions.append(f"Top FD users: {', '.join([f'PID {p[0]} ({p[2]} FDs)' for p in top_fds])}")
            suggestions.append("Check FD leaks: lsof -p <PID> | wc -l")

        if len(orphaned_processes) > 0:
            issues.append(f"{len(orphaned_processes)} potentially orphaned thegent processes")
            suspicion_level = "medium" if suspicion_level == "low" else suspicion_level
            top_orphaned = sorted(orphaned_processes, key=lambda x: x[2], reverse=True)[:3]
            suggestions.append(f"Orphaned processes: {', '.join([f'PID {p[0]} ({p[2]:.1f}h)' for p in top_orphaned])}")
            suggestions.append("Review: ps aux | grep -E '(thegent|claude|codex|droid)' | grep -v grep")

        # Determine status and message
        if not issues:
            r.status = "ok"
            r.message = "No process leaks detected"
            r.details = "Suspicion Level: LOW\nAll processes appear healthy"
        else:
            if suspicion_level == "critical":
                r.status = "fail"
                status_icon = "🔴"
            elif suspicion_level == "high":
                r.status = "warn"
                status_icon = "🟡"
            elif suspicion_level == "medium":
                r.status = "warn"
                status_icon = "🟠"
            else:
                r.status = "ok"
                status_icon = "✓"

            r.message = f"{status_icon} {len(issues)} potential issue(s) detected"
            r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
            r.details += f"Issues: {', '.join(issues)}\n\n"
            r.details += "Optimization Suggestions:\n"
            r.details += "\n".join(f"  • {s}" for s in suggestions[:8])  # Limit to 8 suggestions
            r.fix_hint = "; ".join(suggestions[:3])  # Top 3 suggestions

    except ImportError:
        r.status = "warn"
        r.message = "psutil not available for process analysis"
        r.fix_hint = "Install psutil: pip install psutil"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not analyze processes: {e}"
        r.details = f"Error details: {str(e)[:200]}"

    res_list.append(r)

    return res_list


def _check_runtime_infrastructure() -> list[CheckResult]:
    """Check runtime infrastructure (resource limits and monitoring)."""
    res_list = []

    # Runtime Infrastructure Initialization
    r = CheckResult("Runtime Infrastructure", "Runtime Infrastructure")
    try:
        from thegent.infra.runtime_init import is_initialized

        if is_initialized():
            r.status = "ok"
            r.message = "Runtime infrastructure initialized (resource limits and monitoring active)"
        else:
            r.status = "warn"
            r.message = "Runtime infrastructure not initialized"
            r.fix_hint = "Runtime infrastructure should initialize automatically on startup"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check runtime infrastructure: {e}"
    res_list.append(r)

    # Resource Monitoring
    r = CheckResult("Resource Monitoring", "Runtime Infrastructure")
    try:
        from thegent.infra.runtime_init import get_resource_stats

        stats = get_resource_stats()
        if stats:
            suspicion_level, suggestions = stats.get_suspicion_level()

            # Determine status based on suspicion level
            if suspicion_level == "critical":
                r.status = "fail"
                status_icon = "🔴"
            elif suspicion_level == "high":
                r.status = "warn"
                status_icon = "🟡"
            elif suspicion_level == "medium":
                r.status = "warn"
                status_icon = "🟠"
            else:
                r.status = "ok"
                status_icon = "✓"

            r.message = (
                f"{status_icon} FDs: {stats.fd_count}/{stats.fd_limit} ({stats.fd_usage_percent:.1f}%), "
                f"Memory: {stats.memory_mb:.1f}MB, "
                f"CPU: {stats.cpu_percent:.1f}%, "
                f"Processes: {stats.process_count}"
            )

            # Add detailed report with suspicion level and suggestions
            if suspicion_level != "low":
                r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
                r.details += f"Optimization Suggestions: {suggestions}"
                r.fix_hint = suggestions
        else:
            r.status = "warn"
            r.message = "Resource monitoring not active"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not get resource stats: {e}"
    res_list.append(r)

    # WL-118: Ollama local provider reachability
    r = CheckResult("Ollama Local Provider", "Runtime Infrastructure")

    def _set_ollama_result(*, status: str, severity: str, message: str, fix_hint: str | None = None) -> None:
        r.status = status
        r.severity = severity
        r.message = message
        r.fix_hint = fix_hint

    ollama_bin = shutil.which("ollama")
    if ollama_bin is None:
        _set_ollama_result(
            status="warn",
            severity="warning",
            message="Ollama CLI not found in PATH; local ollama provider runs are unavailable.",
            fix_hint=(
                "Install Ollama from https://ollama.com/download, then run `ollama serve` and `ollama pull llama3.3`."
            ),
        )
        res_list.append(r)
    else:
        try:
            resp = httpx.get("http://127.0.0.1:11434/api/tags", timeout=2.0)
            if resp.status_code == 200:
                body = resp.json() if resp.content else {}
                models = body.get("models") if isinstance(body, dict) else None
                model_count = len(models) if isinstance(models, list) else 0
                if model_count == 0:
                    _set_ollama_result(
                        status="warn",
                        severity="warning",
                        message=f"Ollama daemon reachable via {ollama_bin}, but no local models are installed.",
                        fix_hint=(
                            "Pull at least one model (for example: `ollama pull llama3.3`) "
                            "before `thegent run --provider ollama`."
                        ),
                    )
                else:
                    _set_ollama_result(
                        status="ok",
                        severity="info",
                        message=f"Ollama daemon reachable via {ollama_bin} with {model_count} model(s) installed.",
                    )
            else:
                _set_ollama_result(
                    status="warn",
                    severity="warning",
                    message=f"Ollama daemon check failed: endpoint returned HTTP {resp.status_code}.",
                    fix_hint="Restart Ollama (`ollama serve`) and verify http://127.0.0.1:11434/api/tags responds.",
                )
        except httpx.TimeoutException:
            _set_ollama_result(
                status="warn",
                severity="error",
                message=f"Ollama CLI found at {ollama_bin}, but daemon probe timed out on 127.0.0.1:11434.",
                fix_hint="Start/restart local daemon with `ollama serve`.",
            )
        except httpx.ConnectError:
            _set_ollama_result(
                status="warn",
                severity="warning",
                message=f"Ollama CLI found at {ollama_bin}, but daemon is not reachable on 127.0.0.1:11434.",
                fix_hint="Start local daemon with `ollama serve` and retry `thegent doctor`.",
            )
        except Exception as e:
            _set_ollama_result(
                status="warn",
                severity="error",
                message=f"Ollama validation failed ({type(e).__name__}).",
                fix_hint=(
                    "Ensure `ollama serve` is running and a model is installed (for example: `ollama pull llama3.3`)."
                ),
            )
    res_list.append(r)

    # Process Registry
    r = CheckResult("Process Registry", "Runtime Infrastructure")
    try:
        from thegent.infra.process_registry import get_registry

        registry = get_registry()
        active_processes = registry.list_alive()  # Fixed: use list_alive() instead of list_all()
        count = len(active_processes)

        # Analyze tracked processes for potential issues
        dead_pids = []
        long_running = []
        high_resource = []

        for handle in active_processes:
            try:
                proc = psutil.Process(handle.pid)
                status = proc.status()

                # Check if process is actually dead
                if status == psutil.STATUS_ZOMBIE:
                    dead_pids.append(handle.pid)
                    continue

                # Check runtime
                try:
                    create_time = proc.create_time()
                    runtime = time.time() - create_time
                    if runtime > 86400:  # > 24 hours
                        memory_mb = proc.memory_info().rss / 1024 / 1024
                        long_running.append((handle.pid, runtime / 3600, memory_mb))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                # Check resource usage
                try:
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    if memory_mb > 1000 or cpu_percent > 50:
                        high_resource.append((handle.pid, memory_mb, cpu_percent))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                dead_pids.append(handle.pid)

        # Build report
        issues = []
        suspicion_level = "low"
        suggestions = []

        if dead_pids:
            issues.append(f"{len(dead_pids)} dead/zombie process(es) in registry")
            suspicion_level = "medium"
            suggestions.append(f"Clean up dead processes: {', '.join([str(p) for p in dead_pids[:5]])}")

        if len(long_running) > 10:
            top_long = sorted(long_running, key=lambda x: x[1], reverse=True)[:5]
            issues.append(f"{len(long_running)} very long-running processes (>24h)")
            suspicion_level = "medium" if suspicion_level == "low" else suspicion_level
            suggestions.append(
                f"Long-running: {', '.join([f'PID {p[0]} ({p[1]:.1f}h, {p[2]:.0f}MB)' for p in top_long])}"
            )

        if len(high_resource) > 5:
            top_resource = sorted(high_resource, key=lambda x: x[1], reverse=True)[:5]
            issues.append(f"{len(high_resource)} high-resource processes")
            suspicion_level = "high" if suspicion_level in ["low", "medium"] else suspicion_level
            suggestions.append(
                f"High resource: {', '.join([f'PID {p[0]} ({p[1]:.0f}MB, {p[2]:.1f}% CPU)' for p in top_resource])}"
            )

        if count == 0:
            r.status = "ok"
            r.message = "No active tracked processes"
        elif count < 10:
            r.status = "ok"
            r.message = f"{count} active tracked process(es)"
            if issues:
                r.details = f"Suspicion Level: {suspicion_level.upper()}\n" + "\n".join(issues)
                r.fix_hint = "; ".join(suggestions[:2])
        elif count < 50:
            r.status = "ok"
            r.message = f"{count} active tracked processes (normal for active sessions)"
            if issues:
                r.details = f"Suspicion Level: {suspicion_level.upper()}\n" + "\n".join(issues)
                r.fix_hint = "; ".join(suggestions[:2])
        elif count < 100:
            r.status = "warn"
            r.message = f"{count} active tracked processes"
            if issues:
                suspicion_level = "high" if suspicion_level == "medium" else suspicion_level
            r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
            if issues:
                r.details += "Issues: " + ", ".join(issues) + "\n"
            r.details += "Consider checking for processes that should have been cleaned up"
            r.fix_hint = (
                "; ".join(suggestions[:3])
                if suggestions
                else "Review tracked processes: Check if long-running sessions are expected"
            )
        else:
            r.status = "warn"
            r.message = f"{count} active tracked processes"
            suspicion_level = "high" if not issues else suspicion_level
            r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
            if issues:
                r.details += "Issues: " + ", ".join(issues) + "\n"
            r.details += "May indicate process leak or many concurrent sessions"
            r.fix_hint = (
                "; ".join(suggestions[:3])
                if suggestions
                else "Investigate: Check for stuck processes or cleanup issues"
            )
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check process registry: {e}"
        r.details = f"Error details: {str(e)[:200]}"
    res_list.append(r)

    # psutil Availability
    r = CheckResult("psutil Library", "Runtime Infrastructure")
    r.status = "ok"
    r.message = f"psutil {psutil.__version__} available"
    res_list.append(r)

    return res_list


def _check_mcp_tools() -> list[CheckResult]:
    """Check MCP tools availability and functionality."""
    res_list = []
    settings = ThegentSettings()

    # MCP Tools Availability
    r = CheckResult("MCP Tools", "MCP Tools & Sessions")
    health_url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    try:
        # Check if MCP server is reachable (already checked in connectivity, but verify tools work)
        try:
            resp = httpx.get(health_url, timeout=2.0)
            if resp.status_code == 200:
                try:
                    payload = resp.json()
                except ValueError as exc:
                    r.status = "warn"
                    r.message = "MCP health endpoint returned malformed JSON"
                    r.details = f"{type(exc).__name__}: {str(exc)[:200]}"
                    r.fix_hint = "Run: thegent mcp up"
                else:
                    if isinstance(payload, dict):
                        r.status = "ok"
                        r.message = "MCP tools available"
                    else:
                        r.status = "warn"
                        r.message = "MCP health endpoint returned unexpected payload"
                        r.details = f"payload_type={type(payload).__name__}"
                        r.fix_hint = "Run: thegent mcp up"
            else:
                r.status = "warn"
                r.message = f"MCP health probe failed: HTTP {resp.status_code}"
                r.details = f"status_code={resp.status_code}; url={health_url}; body={resp.text[:120]}"
                r.fix_hint = "Run: thegent mcp up"
        except httpx.TimeoutException as exc:
            r.status = "warn"
            r.message = "MCP server health probe timed out"
            r.details = f"{type(exc).__name__}: {str(exc)[:200]}"
            r.fix_hint = "Run: thegent mcp up"
        except httpx.ConnectError as exc:
            r.status = "warn"
            r.message = "MCP server connection refused (tools unavailable)"
            r.details = f"{type(exc).__name__}: {str(exc)[:200]}"
            r.fix_hint = "Run: thegent mcp up"
        except httpx.HTTPError as exc:
            r.status = "warn"
            r.message = "MCP server health probe failed with protocol/network error"
            r.details = f"{type(exc).__name__}: {str(exc)[:200]}"
            r.fix_hint = "Run: thegent mcp up"
        except OSError as exc:
            r.status = "warn"
            r.message = "MCP server not reachable (tools unavailable)"
            r.details = f"{type(exc).__name__}: {str(exc)[:200]}"
            r.fix_hint = "Run: thegent mcp up"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check MCP tools: {e}"
        r.details = f"{type(e).__name__}: {str(e)[:200]}"
        r.fix_hint = "Run: thegent mcp up"
    res_list.append(r)

    return res_list


def _check_sessions() -> list[CheckResult]:
    """Check session directory and session management."""
    res_list = []
    settings = ThegentSettings()

    # Session Directory
    r = CheckResult("Session Directory", "MCP Tools & Sessions")
    session_dir = settings.session_dir.expanduser().resolve()
    try:
        if session_dir.exists():
            if os.access(session_dir, os.W_OK):
                r.status = "ok"
                r.message = f"Session directory writable: {session_dir}"

                # Check session count
                try:
                    session_count = len([d for d in session_dir.iterdir() if d.is_dir()])
                    if session_count > 0:
                        r.message += f" ({session_count} session(s))"
                except Exception:
                    pass
            else:
                r.status = "fail"
                r.message = f"Session directory not writable: {session_dir}"
                r.fix_hint = f"Fix permissions: chmod 755 {session_dir}"
        else:
            try:
                session_dir.mkdir(parents=True, exist_ok=True)
                r.status = "ok"
                r.message = f"Session directory created: {session_dir}"
            except Exception as e:
                r.status = "fail"
                r.message = f"Cannot create session directory: {e}"
                r.fix_hint = f"Create manually: mkdir -p {session_dir}"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check session directory: {e}"
    res_list.append(r)

    return res_list


def _check_project_hints() -> list[CheckResult]:
    """Project-specific hints (git repo, hooks)."""
    res_list = []
    project_root = _project_root_cache or Path.cwd()

    # Git repo: suggest hooks if .git/hooks not configured
    git_dir = project_root / ".git"
    if git_dir.exists() and git_dir.is_dir():
        hooks_dir = git_dir / "hooks"
        pre_commit = hooks_dir / "pre-commit"
        if not pre_commit.exists() or not pre_commit.is_file():
            r = CheckResult("Git Hooks", "Project")
            r.status = "warn"
            r.message = "Git repo detected but no pre-commit hook"
            r.fix_hint = "Run: thegent setup --hooks"
            res_list.append(r)

    # Stale shadow worktrees from prior agent runs can saturate disk and slow quality scans.
    shadow_max_age_hours = int(os.environ.get("THGENT_SHADOW_STALE_HOURS", "24"))
    cutoff = time.time() - (shadow_max_age_hours * 3600)
    stale_shadow_count = 0
    for p in project_root.parent.glob(".shadow-*"):
        if not p.is_dir():
            continue
        try:
            if p.stat().st_mtime < cutoff:
                stale_shadow_count += 1
        except OSError:
            continue
    if stale_shadow_count > 0:
        r = CheckResult("Stale Shadow Dirs", "Project")
        r.status = "warn"
        r.message = (
            f"Detected {stale_shadow_count} stale .shadow-* dirs older than {shadow_max_age_hours}h near project root"
        )
        r.fix_hint = "Run: thegent mcp prune --dry-run"
        res_list.append(r)

    return res_list


def _check_performance() -> list[CheckResult]:
    """Check for performance optimizations."""
    res_list = []
    # 1. Shell Strategy
    r = CheckResult("Shell Strategy", "Performance")
    settings = ThegentSettings()
    agent_shell = settings.agent_shell

    if agent_shell == "dash":
        r.status = "ok"
        r.message = "Using high-performance 'dash' for Unix execution"
    elif shutil.which("dash"):
        r.status = "warn"
        r.message = f"Currently using '{agent_shell or 'default'}' shell; 'dash' is faster for Unix"
        r.fix_hint = "Run: thegent config set agent_shell dash"
    else:
        r.status = "info"
        r.message = "Dash not found; bash is used as fallback"
        r.fix_hint = "Install dash for 2x faster hook startup"

    res_list.append(r)
    return res_list


