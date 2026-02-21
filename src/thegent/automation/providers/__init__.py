"""Virtual desktop automation providers."""

from .windows_virtual_desktop import WindowsVirtualDesktopProvider
from .linux_virtual_desktop import LinuxVirtualDesktopProvider
from .macos_virtual_desktop import MacOSVirtualDesktopProvider

__all__ = [
    "LinuxVirtualDesktopProvider",
    "MacOSVirtualDesktopProvider",
    "WindowsVirtualDesktopProvider",
]
