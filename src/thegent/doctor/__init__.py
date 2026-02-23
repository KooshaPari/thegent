"""Doctor - Health checks and diagnostics for thegent.

This package contains:
- doctor/core.py: ProcessInfo, run_doctor
- doctor/checks.py: Health check functions
- doctor/checks_env.py: Environment checks (original)
- doctor/fixes.py: Fix application functions
- doctor/display.py: Display and reporting

Import from here or directly from submodules:
    from thegent.doctor import run_doctor
    from thegent.doctor.checks import check_dependencies
    from thegent.doctor.checks_env import check_environment
"""

# Re-export from original checks_env module
from .checks_env import check_environment, check_shim_binaries

# Re-export from core module  
from .core import ProcessInfo, run_doctor

# Re-export from checks module
from .checks import (
    check_dependencies,
    check_configuration,
    check_connectivity,
    check_headless,
    check_isolation,
    check_mcp_tools,
    check_nix,
    check_ollama,
    check_performance,
    check_process_health,
    check_process_leaks,
    check_project_hints,
    check_providers,
    check_runtime_infrastructure,
    check_sessions,
    check_shell,
)

# Re-export from fixes module
from .fixes import apply_fixes, can_fix

# Re-export from display module
from .display import display_results, display_fix_report

# Import from parent thegent module's doctor.py for backwards compatibility
# These are private implementation functions that tests depend on
from thegent.doctor_models import CheckResult

# Import private functions from the standalone doctor.py module
# We do this carefully to avoid circular imports
import sys
import importlib.util
from pathlib import Path

# Load the doctor.py module directly
doctor_py_path = Path(__file__).parent.parent / "doctor.py"
spec = importlib.util.spec_from_file_location("_doctor_impl", doctor_py_path)
_doctor_impl = importlib.util.module_from_spec(spec)
sys.modules['_doctor_impl'] = _doctor_impl
spec.loader.exec_module(_doctor_impl)

# Export private functions for test compatibility
_check_mcp_tools = _doctor_impl._check_mcp_tools
_apply_fixes = _doctor_impl._apply_fixes
_display_fix_report = _doctor_impl._display_fix_report

__all__ = [
    # Core
    "ProcessInfo",
    "run_doctor",
    # Checks
    "check_dependencies",
    "check_configuration",
    "check_connectivity",
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
    # Fixes
    "apply_fixes",
    "can_fix",
    # Display
    "display_results",
    "display_fix_report",
    # Private for test compatibility
    "_check_mcp_tools",
    "_apply_fixes",
    "_display_fix_report",
    # Models
    "CheckResult",
]
