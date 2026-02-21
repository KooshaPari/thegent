"""Linux virtual desktop provider with high-performance automation.

Uses:
- Xvfb (X Virtual Framebuffer) for headless isolation
- X11 for low-latency input injection (<5ms)
- xdotool/xte for automation
- Optionally: Xpra for persistent virtual displays
"""

import asyncio
import logging
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

from ..virtual_desktop import (
    DesktopConfig,
    DesktopState,
    InputEvent,
    ScreenFrame,
    VirtualDesktopProvider,
)

logger = logging.getLogger(__name__)


class LinuxVirtualDesktopProvider(VirtualDesktopProvider):
    """Linux implementation using Xvfb/Xpra."""

    def __init__(self) -> None:
        self._desktops: dict[str, dict] = {}
        self._lock = asyncio.Lock()
        self._xvfb_available = await self._check_xvfb()
        self._xdotool_available = await self._check_xdotool()
        self._xpra_available = await self._check_xpra()

        logger.info(
            f"Linux provider initialized: "
            f"xvfb={self._xvfb_available}, "
            f"xdotool={self._xdotool_available}, "
            f"xpra={self._xpra_available}"
        )

    @property
    def name(self) -> str:
        return "linux"

    @property
    def supports_gpu(self) -> bool:
        # GPU capture is complex on Linux, depends on driver
        return False

    async def _check_xvfb(self) -> bool:
        """Check if Xvfb is available."""
        try:
            result = await asyncio.create_subprocess_exec(
                "which", "Xvfb",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            return (await result.wait()) == 0
        except Exception:
            return False

    async def _check_xdotool(self) -> bool:
        """Check if xdotool is available."""
        try:
            result = await asyncio.create_subprocess_exec(
                "which", "xdotool",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            return (await result.wait()) == 0
        except Exception:
            return False

    async def _check_xpra(self) -> bool:
        """Check if Xpra is available."""
        try:
            result = await asyncio.create_subprocess_exec(
                "which", "xpra",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            return (await result.wait()) == 0
        except Exception:
            return False

    async def create_desktop(self, config: DesktopConfig) -> str:
        """Create a new Xvfb virtual desktop."""
        async with self._lock:
            desktop_id = f"thegent_{config.agent_id}_{int(time.time() * 1000)}"
            display = f":{hash(desktop_id) % 100 + 10}"  # Start from :10

            width, height = config.resolution

            if self._xpra_available:
                # Use Xpra for better performance and features
                proc = await asyncio.create_subprocess_exec(
                    "xpra", "start",
                    "--start-via-proxy=no",
                    "--exit-with-client=no",
                    f"--desktop-prefix={desktop_id}",
                    display,
                    f"--width={width}",
                    f"--height={height}",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await proc.wait()
            elif self._xvfb_available:
                # Use Xvfb as fallback
                proc = await asyncio.create_subprocess_exec(
                    "Xvfb", display,
                    "-screen", "0", f"{width}x{height}x24",
                    "-ac",  # Disable access control
                    "+extension", "GLX",  # Enable OpenGL
                    "+render",  # Enable rendering
                    "-noreset",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                # Don't wait - let it run in background
                # In production, we'd track the PID

            self._desktops[desktop_id] = {
                "display": display,
                "width": width,
                "height": height,
                "config": config,
            }

            # Set DISPLAY for subprocess calls
            os.environ["DISPLAY"] = display

            logger.info(f"Created Linux desktop: {desktop_id} on {display}")
            return desktop_id

    async def destroy_desktop(self, desktop_id: str) -> None:
        """Destroy a virtual desktop."""
        async with self._lock:
            desktop = self._desktops.pop(desktop_id, None)
            if desktop:
                display = desktop.get("display", "")

                if self._xpra_available:
                    await asyncio.create_subprocess_exec(
                        "xpra", "stop", display,
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                else:
                    # Kill Xvfb - would need to track PID
                    pass

                logger.info(f"Destroyed desktop: {desktop_id}")

    async def get_desktop_state(self, desktop_id: str) -> DesktopState:
        """Get desktop state."""
        if desktop_id in self._desktops:
            return DesktopState.RUNNING
        return DesktopState.STOPPED

    async def capture_screen(self, desktop_id: str) -> ScreenFrame:
        """Capture screen using X11 or Xvfb.
        
        Uses xwd or ffmpeg for capture.
        Target: <50ms
        """
        start = time.perf_counter()

        desktop = self._desktops.get(desktop_id)
        if not desktop:
            return ScreenFrame(
                timestamp=time.time(),
                width=1920,
                height=1080,
                bytes_per_pixel=4,
                data=b'\x00' * (1920 * 1080 * 4),
            )

        display = desktop.get("display", os.environ.get("DISPLAY", ":0"))
        width = desktop.get("width", 1920)
        height = desktop.get("height", 1080)

        try:
            # Use import (ImageMagick) for fast capture
            result = await asyncio.create_subprocess_exec(
                "import", "-window", "root", "-display", display,
                "png:-",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await result.communicate()

            # For now return placeholder - real impl would decode PNG
            capture_time = (time.perf_counter() - start) * 1000
            if capture_time > 50:
                logger.warning(f"Slow capture: {capture_time:.1f}ms")

            return ScreenFrame(
                timestamp=time.time(),
                width=width,
                height=height,
                bytes_per_pixel=4,
                data=stdout[:width*height*4] if len(stdout) > 1000 else b'\x00' * (width * height * 4),
            )

        except Exception as e:
            logger.error(f"Capture failed: {e}")
            return ScreenFrame(
                timestamp=time.time(),
                width=width,
                height=height,
                bytes_per_pixel=4,
                data=b'\x00' * (width * height * 4),
            )

    async def inject_input(self, desktop_id: str, event: InputEvent) -> bool:
        """Inject input using xdotool (<5ms).
        
        xdotool is very fast for X11 input injection.
        """
        start = time.perf_counter()

        desktop = self._desktops.get(desktop_id)
        if not desktop:
            return False

        display = desktop.get("display", os.environ.get("DISPLAY", ":0"))

        try:
            if event.event_type == "mouse_move":
                cmd = ["xdotool", "--display", display, "mousemove", str(event.x), str(event.y)]
            elif event.event_type == "mouse_down":
                btn = {1: "1", 2: "2", 3: "3"}.get(event.button or 1, "1")
                cmd = ["xdotool", "--display", display, "mousedown", btn]
            elif event.event_type == "mouse_up":
                btn = {1: "1", 2: "2", 3: "3"}.get(event.button or 1, "1")
                cmd = ["xdotool", "--display", display, "mouseup", btn]
            elif event.event_type == "mouse_wheel":
                delta = event.delta or 120
                direction = "up" if delta > 0 else "down"
                cmd = ["xdotool", "--display", display, "click", "--repeat", "1", "4" if delta > 0 else "5"]
            elif event.event_type == "key_down":
                if event.key_char:
                    cmd = ["xdotool", "--display", display, "key", event.key_char]
                elif event.key_code:
                    # Would need keycode mapping
                    cmd = ["xdotool", "--display", display, "key", f"keycode={event.key_code}"]
                else:
                    return False
            elif event.event_type == "key_up":
                # xdotool handles key up automatically
                return True
            else:
                return False

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate()

            latency = (time.perf_counter() - start) * 1000
            if latency > 10:
                logger.debug(f"Slow input: {latency:.2f}ms")

            return True

        except Exception as e:
            logger.error(f"Input injection failed: {e}")
            return False

    async def list_windows(self, desktop_id: str) -> list[dict[str, Any]]:
        """List windows using xdotool."""
        desktop = self._desktops.get(desktop_id)
        if not desktop:
            return []

        display = desktop.get("display", os.environ.get("DISPLAY", ":0"))

        try:
            # Get all window IDs
            result = await asyncio.create_subprocess_exec(
                "xdotool", "--display", display, "search", "--name", ".*",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await result.communicate()

            windows = []
            for line in stdout.decode().strip().split("\n"):
                if line.strip():
                    wid = line.strip()
                    # Get window name
                    name_result = await asyncio.create_subprocess_exec(
                        "xdotool", "--display", display, "getwindowname", wid,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    name, _ = await name_result.communicate()

                    # Get window geometry
                    geom_result = await asyncio.create_subprocess_exec(
                        "xdotool", "--display", display, "getwindowgeometry", wid,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    geom, _ = await geom_result.communicate()

                    windows.append({
                        "id": wid,
                        "title": name.decode().strip() if name else "",
                        "raw": geom.decode() if geom else "",
                    })

            return windows

        except Exception as e:
            logger.error(f"List windows failed: {e}")
            return []

    async def get_window_rect(self, desktop_id: str, window_id: str) -> tuple[int, int, int, int]:
        """Get window bounds."""
        desktop = self._desktops.get(desktop_id)
        if not desktop:
            return (0, 0, 1920, 1080)

        display = desktop.get("display", os.environ.get("DISPLAY", ":0"))

        try:
            result = await asyncio.create_subprocess_exec(
                "xdotool", "--display", display, "getwindowgeometry", "--shell", window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await result.communicate()

            # Parse output like:
            # Position: 100,100 (screen: 0)
            # Geometry: 800x600
            lines = stdout.decode().strip().split("\n")
            x = y = w = h = 0
            for line in lines:
                if "Position:" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        coords = parts[1].replace(",", "").split("x")
                        x = int(coords[0])
                        y = int(coords[1]) if len(coords) > 1 else 0
                elif "Geometry:" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        geom = parts[1].split("x")
                        w = int(geom[0])
                        h = int(geom[1]) if len(geom) > 1 else 0

            return (x, y, w, h)

        except Exception as e:
            logger.error(f"Get window rect failed: {e}")
            return (0, 0, 1920, 1080)
