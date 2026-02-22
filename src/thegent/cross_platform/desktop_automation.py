"""Desktop automation providers (macOS/Windows/Linux)."""

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


class DesktopAutomationProvider:
    """Cross-platform desktop automation."""

    def __init__(self) -> None:
        """Initialize desktop automation."""
        self.system = platform.system()
        self.provider = self._get_provider()

    def _get_provider(self) -> str:
        """Get provider for current system.

        Returns:
            Provider name
        """
        if self.system == "Darwin":
            return "macOS"
        if self.system == "Windows":
            return "Windows"
        if self.system == "Linux":
            return "Linux"
        return "Unknown"

    def click(self, x: int, y: int) -> bool:
        """Click at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if successful
        """
        logger.info(f"Clicking at ({x}, {y}) on {self.provider}")

        if self.system == "Darwin":
            # macOS: Use AppleScript via osascript
            script = f'tell application "System Events" to click at {{{x}, {y}}}'
            try:
                subprocess.run(["osascript", "-e", script], check=True)
                return True
            except Exception as e:
                logger.error(f"macOS click failed: {e}")
                return False

        elif self.system == "Windows":
            # Windows: Use PowerShell to move cursor and click
            script = f"""
            $pos = [System.Windows.Forms.Cursor]::Position
            $pos.X = {x}
            $pos.Y = {y}
            [System.Windows.Forms.Cursor]::Position = $pos
            $signature = '[DllImport("user32.dll")]public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);'
            $type = Add-Type -MemberDefinition $signature -Name "Win32MouseEvent" -Namespace Win32 -PassThru
            $type::mouse_event(0x0002, 0, 0, 0, 0) # left down
            $type::mouse_event(0x0004, 0, 0, 0, 0) # left up
            """
            try:
                subprocess.run(["powershell", "-Command", script], check=True)
                return True
            except Exception as e:
                logger.error(f"Windows click failed: {e}")
                return False

        return False

    def type_text(self, text: str) -> bool:
        """Type text.

        Args:
            text: Text to type

        Returns:
            True if successful
        """
        logger.info(f"Typing text on {self.provider}")

        if self.system == "Darwin":
            # macOS: Use AppleScript
            script = f'tell application "System Events" to keystroke "{text}"'
            try:
                subprocess.run(["osascript", "-e", script], check=True)
                return True
            except Exception as e:
                logger.error(f"macOS type failed: {e}")
                return False

        elif self.system == "Windows":
            # Windows: Use PowerShell SendKeys
            script = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{text}")'
            try:
                subprocess.run(["powershell", "-Command", script], check=True)
                return True
            except Exception as e:
                logger.error(f"Windows type failed: {e}")
                return False

        return False

    def get_screen_size(self) -> tuple[int, int]:
        """Get screen size.

        Returns:
            (width, height) tuple
        """
        if self.system == "Darwin":
            # macOS: Use system_profiler or AppleScript
            script = 'tell application "Finder" to get bounds of window of desktop'
            try:
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
                # Output like: 0, 0, 1920, 1080
                parts = result.stdout.strip().split(", ")
                if len(parts) >= 4:
                    return (int(parts[2]), int(parts[3]))
            except Exception:
                pass

        elif self.system == "Windows":
            # Windows: Use PowerShell
            script = "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height"
            try:
                result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, check=True)
                lines = result.stdout.strip().splitlines()
                if len(lines) >= 2:
                    return (int(lines[0]), int(lines[1]))
            except Exception:
                pass

        return (1920, 1080)
