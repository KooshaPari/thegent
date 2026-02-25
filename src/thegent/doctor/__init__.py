"""Doctor module - health checks and diagnostics for thegent.

This package contains:
- doctor/core.py: ProcessInfo, run_doctor
- doctor/checks.py: All health check functions (_check_*)
- doctor/helpers.py: Utility functions
- doctor/fixes.py: Fix application functions
- doctor/checks_env.py: Environment and binary checks
- doctor/display.py: Display and formatting

Import from here or directly from submodules:
    from thegent.doctor import ProcessInfo, run_doctor
    from thegent.doctor.checks import _check_dependencies
"""

from ..doctor_models import CheckResult
from .core import ProcessInfo, run_doctor
from .checks import (
    _check_configuration,
    _check_connectivity,
    _check_dependencies,
    _check_environment,
    _check_headless,
    _check_isolation,
    _check_mcp_tools,
    _check_ollama,
    _check_performance,
    _check_process_health_v2,
    _check_process_leaks,
    _check_project_hints,
    _check_providers,
    _check_runtime_infrastructure,
    _check_sessions,
    _check_shim_binaries,
)
from .helpers import (
    _display_results,
    _extract_process_info,
    _find_stuck_processes,
    _is_process_actively_working,
)
from .fixes import _apply_fixes, _display_fix_report
from .checks_env import check_environment
from .display import display_results, display_fix_report

# Wrapper functions for public API
def check_dependencies(deps: bool = False):
    """Check dependencies."""
    return _check_dependencies(deps=deps)

def check_configuration():
    """Check configuration."""
    return _check_configuration()

def check_connectivity(auto_start: bool = True):
    """Check connectivity."""
    return _check_connectivity(auto_start=auto_start)

def check_headless():
    """Check headless operation."""
    return _check_headless()

def check_isolation():
    """Check isolation."""
    return _check_isolation()

def check_mcp_tools():
    """Check MCP tools."""
    return _check_mcp_tools()

def check_nix():
    """Check nix."""
    # Delegate to doctor_shell_nix module
    from thegent.doctor_shell_nix import check_nix as _check_nix_impl
    return _check_nix_impl(check_result_cls=__import__('thegent.doctor_models', fromlist=['CheckResult']).CheckResult)

def check_ollama():
    """Check Ollama."""
    return _check_ollama()

def check_performance():
    """Check performance."""
    return _check_performance()

def check_process_health():
    """Check process health."""
    return _check_process_health_v2()

def check_process_leaks():
    """Check for process leaks."""
    return _check_process_leaks()

def check_project_hints():
    """Check project hints."""
    return _check_project_hints()

def check_providers():
    """Check providers."""
    return _check_providers()

def check_runtime_infrastructure():
    """Check runtime infrastructure."""
    return _check_runtime_infrastructure()

def check_sessions():
    """Check sessions."""
    return _check_sessions()

def check_shell():
    """Check shell."""
    # Delegate to doctor_shell_nix module
    from thegent.doctor_shell_nix import check_shell as _check_shell_impl
    return _check_shell_impl(check_result_cls=__import__('thegent.doctor_models', fromlist=['CheckResult']).CheckResult)

def apply_fixes(results, dry_run=False):
    """Apply fixes."""
    return _apply_fixes(results, dry_run=dry_run)

def can_fix(result):
    """Check if a result can be fixed."""
    return getattr(result, 'fix', None) is not None

__all__ = [
    # Core
    "CheckResult",
    "ProcessInfo",
    # Private
    "_apply_fixes",
    "_check_configuration",
    "_check_connectivity",
    "_check_dependencies",
    "_check_environment",
    "_check_headless",
    "_check_isolation",
    "_check_mcp_tools",
    "_check_ollama",
    "_check_performance",
    "_check_process_health_v2",
    "_check_process_leaks",
    "_check_project_hints",
    "_check_providers",
    "_check_runtime_infrastructure",
    "_check_sessions",
    "_check_shim_binaries",
    "_display_fix_report",
    "_display_results",
    # Fixes
    "apply_fixes",
    "can_fix",
    # Checks
    "check_configuration",
    "check_connectivity",
    "check_dependencies",
    "check_environment",
    "check_headless",
    "check_isolation",
    "check_mcp_tools",
    "check_nix",
    "check_ollama",
    "check_performance",
    "check_process_health",
    "check_process_leaks",
    "check_project_hints",
    "check_providers",
    "check_runtime_infrastructure",
    "check_sessions",
    "check_shell",
    "check_shim_binaries",
    "display_fix_report",
    # Display
    "display_results",
    "run_doctor",
]
