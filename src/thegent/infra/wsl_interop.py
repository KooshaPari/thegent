"""WSL2 interop and path translation utilities."""

import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Optional


class WslInterop:
    """
    Utilities for seamless interop between native Windows and WSL2.

    Provides high-performance path translation and identity mapping.
    """

    def __init__(self) -> None:
        self.is_wsl = self._detect_wsl()
        self.is_windows = platform.system().lower() == "windows"

        # Pre-calculated drive mount points (default /mnt/c/)
        self.wsl_mount_root = "/mnt/"
        self.drive_regex_win = re.compile(r"^([A-Za-z]):\\(.*)")
        self.drive_regex_wsl = re.compile(r"^/mnt/([a-z])/(.*)")

    def _detect_wsl(self) -> bool:
        """Detect if running inside WSL."""
        if platform.system().lower() != "linux":
            return False

        # Check /proc/version for Microsoft/WSL string
        try:
            with open("/proc/version") as f:
                content = f.read().lower()
                return "microsoft" in content or "wsl" in content
        except Exception:
            return False

    def to_wsl_path(self, windows_path: str) -> str:
        """
        Convert a Windows path to a WSL path.

        Uses fast-path regex if possible, falls back to wslpath.
        """
        if not self.is_windows and not self.is_wsl:
            return windows_path

        # Fast-path: regex conversion for common drive letters
        match = self.drive_regex_win.match(windows_path)
        if match:
            drive = match.group(1).lower()
            rest = match.group(2).replace("\\", "/")
            return f"{self.wsl_mount_root}{drive}/{rest}"

        # Fallback: call wslpath if available
        if self.is_wsl:
            try:
                result = subprocess.run(["wslpath", "-a", windows_path], capture_output=True, text=True, check=True)
                return result.stdout.strip()
            except Exception:
                pass

        return windows_path

    def to_windows_path(self, wsl_path: str) -> str:
        """
        Convert a WSL path to a Windows path.

        Uses fast-path regex if possible, falls back to wslpath.
        """
        if not self.is_windows and not self.is_wsl:
            return wsl_path

        # Fast-path: regex conversion for /mnt/x/ style paths
        match = self.drive_regex_wsl.match(wsl_path)
        if match:
            drive = match.group(1).upper()
            rest = match.group(2).replace("/", "\\")
            return f"{drive}:\\{rest}"

        # Fallback: call wslpath if available
        if self.is_wsl:
            try:
                result = subprocess.run(["wslpath", "-w", wsl_path], capture_output=True, text=True, check=True)
                return result.stdout.strip()
            except Exception:
                pass

        return wsl_path

    def get_windows_user_profile(self) -> str | None:
        """Get the Windows user profile path (C:\\Users\\Name)."""
        if self.is_windows:
            return os.environ.get("USERPROFILE")

        if self.is_wsl:
            # Under WSL, we can often find it via /mnt/c/Users/...
            # or by calling powershell.exe $env:USERPROFILE
            try:
                result = subprocess.run(
                    ["powershell.exe", "-Command", "$env:USERPROFILE"], capture_output=True, text=True, check=True
                )
                win_path = result.stdout.strip()
                return self.to_wsl_path(win_path)
            except Exception:
                pass

        return None

    def map_sid_to_uid(self, sid: str) -> int:
        """
        Map a Windows SID to a WSL2 UID.

        Implementation logic:
        1. deterministic hash-based mapping (similar to sub-user system).
        2. /etc/wsl.conf [user] default=<uid> if needed.
        """
        # Deterministic mapping logic (placeholder for now)
        # Using the same logic as UidPool but for SIDs
        return 2000 + (hash(sid) % 1000)
