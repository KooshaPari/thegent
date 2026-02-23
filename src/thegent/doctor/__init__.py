"""Doctor module - health checks and diagnostics for thegent.

This module organizes doctor.py functions into logical domains:
- Core: run_doctor, ProcessInfo
- Checks: _check_* functions organized by category
- Fixes: _apply_fixes, _display_*

For a full modular refactor, consider splitting into:
- doctor/checks.py - All _check_* functions
- doctor/display.py - _display_* functions
- doctor/fixes.py - _apply_fixes
"""

# Re-export the main entry point
from thegent.doctor import ProcessInfo, run_doctor

__all__ = [
    "ProcessInfo",
    "run_doctor",
]
