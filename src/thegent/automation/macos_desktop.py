"""macOS Desktop Automation provider wrapping AppleScript and JXA."""

import shutil
import subprocess
import sys
from dataclasses import dataclass, field


class AutomationError(Exception):
    """Raised when a desktop automation operation fails unexpectedly."""


@dataclass
class AutomationResult:
    """Result from a desktop automation operation."""

    success: bool
    output: str
    error: str | None = field(default=None)


class MacOSDesktopAutomation:
    """macOS desktop automation via AppleScript (osascript) and JXA.

    Falls back gracefully on non-macOS platforms: every method returns an
    ``AutomationResult(success=False, ...)`` rather than raising.
    """

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True when running on macOS and *osascript* is on PATH."""
        return sys.platform == "darwin" and shutil.which("osascript") is not None

    # ------------------------------------------------------------------
    # Core script runners
    # ------------------------------------------------------------------

    def run_applescript(self, script: str, timeout_s: float = 10.0) -> AutomationResult:
        """Execute an AppleScript snippet via *osascript*.

        Args:
            script: AppleScript source code to execute.
            timeout_s: Maximum wall-clock seconds to allow (default 10).

        Returns:
            AutomationResult with success flag, stdout, and optional error.
        """
        if not self.is_available():
            return AutomationResult(success=False, output="", error="Not macOS")

        try:
            proc = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            if proc.returncode == 0:
                return AutomationResult(success=True, output=proc.stdout.strip())
            return AutomationResult(
                success=False,
                output=proc.stdout.strip(),
                error=proc.stderr.strip() or f"osascript exited {proc.returncode}",
            )
        except subprocess.TimeoutExpired:
            return AutomationResult(
                success=False,
                output="",
                error=f"osascript timed out after {timeout_s}s",
            )

    def run_jxa(self, script: str, timeout_s: float = 10.0) -> AutomationResult:
        """Execute a JavaScript for Automation (JXA) snippet via *osascript*.

        Args:
            script: JXA source code to execute.
            timeout_s: Maximum wall-clock seconds to allow (default 10).

        Returns:
            AutomationResult with success flag, stdout, and optional error.
        """
        if not self.is_available():
            return AutomationResult(success=False, output="", error="Not macOS")

        try:
            proc = subprocess.run(
                ["osascript", "-l", "JavaScript", "-e", script],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            if proc.returncode == 0:
                return AutomationResult(success=True, output=proc.stdout.strip())
            return AutomationResult(
                success=False,
                output=proc.stdout.strip(),
                error=proc.stderr.strip() or f"osascript (JXA) exited {proc.returncode}",
            )
        except subprocess.TimeoutExpired:
            return AutomationResult(
                success=False,
                output="",
                error=f"osascript (JXA) timed out after {timeout_s}s",
            )

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------

    def open_application(self, name: str) -> AutomationResult:
        """Activate (open/bring to front) an application by name.

        Args:
            name: Application name as it appears in /Applications, e.g. "Safari".

        Returns:
            AutomationResult indicating success or failure.
        """
        script = f'tell application "{name}" to activate'
        return self.run_applescript(script)

    def get_frontmost_app(self) -> str | None:
        """Return the name of the currently frontmost application.

        Returns:
            Application name string, or None if the query fails.
        """
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = self.run_applescript(script)
        if result.success and result.output:
            return result.output
        return None

    def click_menu_item(self, app: str, menu: str, item: str) -> AutomationResult:
        """Click a menu item inside an application's menu bar.

        Args:
            app: Application name, e.g. "Safari".
            menu: Top-level menu name, e.g. "File".
            item: Menu item name, e.g. "New Window".

        Returns:
            AutomationResult indicating success or failure.
        """
        script = (
            f'tell application "{app}"\n'
            f"    activate\n"
            f"end tell\n"
            f'tell application "System Events"\n'
            f'    tell process "{app}"\n'
            f'        click menu item "{item}" of menu "{menu}" of menu bar 1\n'
            f"    end tell\n"
            f"end tell"
        )
        return self.run_applescript(script)
