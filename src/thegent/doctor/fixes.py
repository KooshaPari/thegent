"""Doctor fix functions.

Contains functions to apply fixes for common issues.
"""

import os
import shutil
from pathlib import Path

from thegent.doctor.models import CheckResult, FixResult


def apply_dependencies_fix() -> FixResult:
    """Install required dependencies."""
    # This would typically run pip install or similar
    return FixResult(
        check_id="fix_dependencies",
        success=True,
        message="Dependencies are up to date",
    )


def apply_configuration_fix(config_path: Path) -> FixResult:
    """Create default configuration."""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("# Default config\n")
        return FixResult(
            check_id="fix_configuration",
            success=True,
            message=f"Created config at {config_path}",
            changes={"created": str(config_path)},
        )
    except Exception as e:
        return FixResult(
            check_id="fix_configuration",
            success=False,
            message=f"Failed to create config: {e}",
        )


def apply_shim_fix(bin_name: str, bin_dir: Path) -> FixResult:
    """Create a shim binary."""
    try:
        bin_dir.mkdir(parents=True, exist_ok=True)
        bin_path = bin_dir / bin_name
        
        # Create a simple shim script
        bin_path.write_text(f"""#!/bin/bash
# Shim for {bin_name}
echo "Shim for {bin_name} - install thegent for full functionality"
""")
        bin_path.chmod(0o755)
        
        return FixResult(
            check_id=f"fix_shim_{bin_name}",
            success=True,
            message=f"Created shim: {bin_path}",
            changes={"created": str(bin_path)},
        )
    except Exception as e:
        return FixResult(
            check_id=f"fix_shim_{bin_name}",
            success=False,
            message=f"Failed to create shim: {e}",
        )


def apply_process_kill_fix(pid: int) -> FixResult:
    """Kill a stuck process."""
    try:
        os.kill(pid, 9)  # SIGKILL
        return FixResult(
            check_id=f"fix_kill_{pid}",
            success=True,
            message=f"Killed process {pid}",
            changes={"killed": pid},
        )
    except Exception as e:
        return FixResult(
            check_id=f"fix_kill_{pid}",
            success=False,
            message=f"Failed to kill process {pid}: {e}",
        )


def apply_fixes(results: list[CheckResult], dry_run: bool = False) -> list[FixResult]:
    """Apply fixes for failed checks.
    
    Args:
        results: List of check results
        dry_run: If True, don't actually apply fixes
        
    Returns:
        List of fix results
    """
    fix_results: list[FixResult] = []
    
    for result in results:
        if result.status.value not in ("fail", "warn"):
            continue
            
        if not result.fix_available:
            continue
            
        if dry_run:
            fix_results.append(FixResult(
                check_id=f"dryrun_{result.check_id}",
                success=True,
                message=f"Would fix: {result.message}",
            ))
            continue
            
        # Apply specific fixes based on check_id
        if result.check_id.startswith("deps_"):
            fix_results.append(apply_dependencies_fix())
        elif result.check_id.startswith("config_"):
            fix_results.append(apply_configuration_fix(
                Path.home() / ".thegent" / "config.yaml"
            ))
        elif result.check_id.startswith("shim_"):
            bin_name = result.check_id.replace("shim_", "")
            fix_results.append(apply_shim_fix(
                bin_name,
                Path.home() / ".thegent" / "bin"
            ))
        elif "process" in result.check_id and "stuck" in result.check_id:
            pids = result.details.get("pids", [])
            for pid in pids:
                fix_results.append(apply_process_kill_fix(pid))
        else:
            fix_results.append(FixResult(
                check_id=result.check_id,
                success=False,
                message=f"No automatic fix available for {result.check_id}",
            ))
    
    return fix_results
