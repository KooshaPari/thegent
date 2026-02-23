"""Doctor package - diagnostics and health checks.

Modular package for thegent diagnostics.
"""

from thegent.doctor_v2.checks import run_doctor
from thegent.doctor_v2.process import ProcessInfo, find_stuck_processes

__all__ = ["run_doctor", "ProcessInfo", "find_stuck_processes"]
