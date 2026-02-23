"""Doctor diagnostics for thegent.

This module has been migrated to doctor_v2 package.
"""

import warnings
warnings.warn(
    "doctor module migrated to doctor_v2. Import from there.",
    DeprecationWarning,
    stacklevel=2
)

from thegent.doctor_v2 import run_doctor, ProcessInfo, find_stuck_processes
from thegent.doctor_v2.checks import CheckResult

__all__ = ["run_doctor", "ProcessInfo", "find_stuck_processes", "CheckResult"]
