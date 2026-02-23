"""Doctor core models and entry point.

Domain: Core
- ProcessInfo: Process information model
- run_doctor: Main entry point
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ProcessInfo:
    """Process information for health checks."""
    pid: int
    name: str
    status: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    cmdline: str = ""
    create_time: float = 0.0


def run_doctor(
    checks: list[str] | None = None,
    fix: bool = False,
    verbose: bool = False,
) -> int:
    """Run doctor health checks.
    
    Args:
        checks: List of check names to run (default: all)
        fix: Whether to apply fixes
        verbose: Verbose output
        
    Returns:
        Exit code (0 = all passed, 1 = issues found)
    """
    from doctor.checks import (
        check_dependencies,
        check_configuration,
        check_connectivity,
        check_environment,
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
        check_shim_binaries,
    )
    from doctor.display import display_results
    from doctor.fixes import apply_fixes
    
    # Run checks
    all_results = []
    
    check_funcs = {
        "dependencies": check_dependencies,
        "configuration": check_configuration,
        "connectivity": check_connectivity,
        "environment": check_environment,
        "headless": check_headless,
        "isolation": check_isolation,
        "mcp_tools": check_mcp_tools,
        "nix": check_nix,
        "ollama": check_ollama,
        "performance": check_performance,
        "process_health": check_process_health,
        "process_leaks": check_process_leaks,
        "project_hints": check_project_hints,
        "providers": check_providers,
        "runtime_infrastructure": check_runtime_infrastructure,
        "sessions": check_sessions,
        "shell": check_shell,
        "shim_binaries": check_shim_binaries,
    }
    
    targets = checks if checks else list(check_funcs.keys())
    
    for check_name in targets:
        if check_name in check_funcs:
            results = check_funcs[check_name]()
            all_results.extend(results)
    
    # Display results
    passed = display_results(all_results, verbose=verbose)
    
    # Apply fixes if requested
    if fix and not passed:
        apply_fixes(all_results, dry_run=False)
    
    return 0 if passed else 1
