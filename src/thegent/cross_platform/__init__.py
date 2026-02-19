"""Cross-platform implementations."""

from thegent.cross_platform.desktop_automation import DesktopAutomationProvider
from thegent.cross_platform.performance import CrossPlatformPerformance
from thegent.cross_platform.security import CrossPlatformSecurity
from thegent.cross_platform.shell_strategy import DualShellStrategy

__all__ = [
    "DesktopAutomationProvider",
    "DualShellStrategy",
    "CrossPlatformPerformance",
    "CrossPlatformSecurity",
]
