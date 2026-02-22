"""High-performance virtual desktop automation for agents.

This module provides low-latency (<50ms) desktop automation using virtual desktop
isolation, similar to UFO2's Picture-in-Picture approach. Each agent gets its own
isolated desktop session where it can automate without colliding with the user.

Architecture:
- VirtualDesktop: Creates isolated desktop sessions per agent
- ScreenCapture: GPU-accelerated screen capture (DXGI/X11/Quartz)
- InputInjector: Low-latency input injection (direct API, not subprocess)
- DesktopSession: Manages the isolated session lifecycle
"""

import asyncio
import logging
import platform
import uuid
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


class DesktopState(Enum):
    """Desktop session state."""

    CREATING = auto()
    RUNNING = auto()
    IDLE = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()


@dataclass
class DesktopConfig:
    """Configuration for a virtual desktop session."""

    agent_id: str
    resolution: tuple[int, int] = (1920, 1080)
    color_depth: int = 32
    dpi: int = 96
    memory_mb: int = 2048
    gpu_enabled: bool = True
    audio_enabled: bool = False
    network_bridge: bool = True
    startup_app: str | None = None
    working_directory: Path | None = None


@dataclass
class ScreenFrame:
    """A single screen frame capture."""

    timestamp: float
    width: int
    height: int
    bytes_per_pixel: int
    data: bytes
    format: str = "BGRA"

    @property
    def size_bytes(self) -> int:
        return len(self.data)

    @property
    def latency_ms(self) -> float:
        """Capture latency in milliseconds."""
        return (time.time() - self.timestamp) * 1000


@dataclass
class InputEvent:
    """Input event for injection."""

    event_type: str  # key_down, key_up, mouse_move, mouse_down, mouse_up, mouse_wheel
    x: int | None = None
    y: int | None = None
    key_code: int | None = None
    key_char: str | None = None
    delta: int | None = None  # For mouse wheel
    button: int | None = None  # 1=left, 2=right, 3=middle


class VirtualDesktopProvider(ABC):
    """Abstract base for platform-specific virtual desktop implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""

    @property
    @abstractmethod
    def supports_gpu(self) -> bool:
        """Whether this provider supports GPU acceleration."""

    @abstractmethod
    async def create_desktop(self, config: DesktopConfig) -> str:
        """Create a new virtual desktop session.

        Returns:
            Desktop ID that can be used to reference this session
        """

    @abstractmethod
    async def destroy_desktop(self, desktop_id: str) -> None:
        """Destroy a virtual desktop session."""

    @abstractmethod
    async def get_desktop_state(self, desktop_id: str) -> DesktopState:
        """Get the current state of a desktop."""

    @abstractmethod
    async def capture_screen(self, desktop_id: str) -> ScreenFrame:
        """Capture a frame from the virtual desktop.

        Must complete in <50ms for FPS-like performance.
        """

    @abstractmethod
    async def inject_input(self, desktop_id: str, event: InputEvent) -> bool:
        """Inject an input event into the desktop.

        Must complete in <10ms for responsive control.
        """

    @abstractmethod
    async def list_windows(self, desktop_id: str) -> list[dict[str, Any]]:
        """List windows in the desktop."""

    @abstractmethod
    async def get_window_rect(self, desktop_id: str, window_id: str) -> tuple[int, int, int, int]:
        """Get window bounds (x, y, width, height)."""


class DesktopSession:
    """Represents a single virtual desktop session."""

    def __init__(
        self,
        agent_id: str,
        desktop_id: str,
        provider: VirtualDesktopProvider,
        config: DesktopConfig,
    ) -> None:
        self.agent_id = agent_id
        self.desktop_id = desktop_id
        self.provider = provider
        self.config = config
        self._state = DesktopState.CREATING
        self._capture_loop: asyncio.Task | None = None
        self._last_frame: ScreenFrame | None = None
        self._frame_callbacks: list[Callable[[ScreenFrame], None]] = []
        self._input_latency_sum: float = 0
        self._input_count: int = 0

    @property
    def state(self) -> DesktopState:
        return self._state

    @state.setter
    def state(self, value: DesktopState) -> None:
        self._state = value
        logger.debug(f"Session {self.agent_id} state: {value}")

    async def start(self) -> None:
        """Start the session."""
        self.state = DesktopState.RUNNING
        logger.info(f"Started session {self.agent_id}")

    async def stop(self) -> None:
        """Stop the session."""
        self.state = DesktopState.STOPPING
        if self._capture_loop:
            self._capture_loop.cancel()
            self._capture_loop = None
        self.state = DesktopState.STOPPED
        logger.info(f"Stopped session {self.agent_id}")

    async def destroy(self) -> None:
        """Destroy the session and clean up resources."""
        await self.stop()

    async def capture(self) -> ScreenFrame:
        """Capture a screen frame.

        Target: <50ms latency
        """
        frame = await self.provider.capture_screen(self.desktop_id)
        self._last_frame = frame
        for callback in self._frame_callbacks:
            callback(frame)
        return frame

    async def inject(self, event: InputEvent) -> bool:
        """Inject an input event.

        Target: <10ms latency
        """
        start = time.perf_counter()
        result = await self.provider.inject_input(self.desktop_id, event)
        latency = (time.perf_counter() - start) * 1000
        self._input_latency_sum += latency
        self._input_count += 1

        if self._input_count % 100 == 0:
            avg_latency = self._input_latency_sum / self._input_count
            logger.debug(f"Avg input latency: {avg_latency:.2f}ms")

        return result

    async def click(self, x: int, y: int, button: int = 1) -> bool:
        """Click at coordinates."""
        # Mouse move
        await self.inject(InputEvent(event_type="mouse_move", x=x, y=y))
        # Mouse down
        await self.inject(InputEvent(event_type="mouse_down", x=x, y=y, button=button))
        # Mouse up
        await self.inject(InputEvent(event_type="mouse_up", x=x, y=y, button=button))
        return True

    async def type_text(self, text: str) -> bool:
        """Type text."""
        for char in text:
            await self.inject(InputEvent(event_type="key_down", key_char=char))
            await self.inject(InputEvent(event_type="key_up", key_char=char))
        return True

    async def press_key(self, key_code: int) -> bool:
        """Press a key by code."""
        await self.inject(InputEvent(event_type="key_down", key_code=key_code))
        await self.inject(InputEvent(event_type="key_up", key_code=key_code))
        return True

    def on_frame(self, callback: Callable[[ScreenFrame], None]) -> None:
        """Register a callback for new frames."""
        self._frame_callbacks.append(callback)

    @property
    def last_frame(self) -> ScreenFrame | None:
        return self._last_frame


class VirtualDesktopManager:
    """Manages virtual desktop sessions for agents."""

    def __init__(self) -> None:
        self._desktops: dict[str, VirtualDesktopProvider] = {}
        self._sessions: dict[str, DesktopSession] = {}
        self._provider = self._get_provider()
        self._lock = asyncio.Lock()
        logger.info(f"Initialized VirtualDesktopManager with provider: {self._provider.name}")

    def _get_provider(self) -> VirtualDesktopProvider:
        """Get the appropriate provider for this platform."""
        system = platform.system()

        if system == "Windows":
            from thegent.automation.providers.windows_virtual_desktop import WindowsVirtualDesktopProvider

            return WindowsVirtualDesktopProvider()

        if system == "Linux":
            from thegent.automation.providers.linux_virtual_desktop import LinuxVirtualDesktopProvider

            return LinuxVirtualDesktopProvider()

        if system == "Darwin":
            from thegent.automation.providers.macos_virtual_desktop import MacOSVirtualDesktopProvider

            return MacOSVirtualDesktopProvider()

        logger.warning("No native virtual desktop provider for '%s'; using fallback provider.", system)
        return _UnsupportedPlatformVirtualDesktopProvider(system=system)

    async def create_session(self, agent_id: str, config: DesktopConfig | None = None) -> DesktopSession:
        """Create a new virtual desktop session for an agent."""
        if config is None:
            config = DesktopConfig(agent_id=agent_id)

        async with self._lock:
            if agent_id in self._sessions:
                raise ValueError(f"Session already exists for agent {agent_id}")

            desktop_id = await self._provider.create_desktop(config)
            session = DesktopSession(
                agent_id=agent_id,
                desktop_id=desktop_id,
                provider=self._provider,
                config=config,
            )
            self._sessions[agent_id] = session
            self._desktops[desktop_id] = self._provider

            logger.info(f"Created virtual desktop {desktop_id} for agent {agent_id}")
            return session

    async def get_session(self, agent_id: str) -> DesktopSession | None:
        """Get an existing session."""
        return self._sessions.get(agent_id)

    async def destroy_session(self, agent_id: str) -> None:
        """Destroy a session."""
        async with self._lock:
            session = self._sessions.pop(agent_id, None)
            if session:
                await session.destroy()
                await self._provider.destroy_desktop(session.desktop_id)
                logger.info(f"Destroyed session for agent {agent_id}")

    async def list_sessions(self) -> list[DesktopSession]:
        """List all active sessions."""
        return list(self._sessions.values())


# Global manager instance
_manager: VirtualDesktopManager | None = None


def get_desktop_manager() -> VirtualDesktopManager:
    """Get the global desktop manager."""
    global _manager
    if _manager is None:
        _manager = VirtualDesktopManager()
    return _manager


class _UnsupportedPlatformVirtualDesktopProvider(VirtualDesktopProvider):
    """Fallback provider when running on unsupported platforms."""

    def __init__(self, system: str) -> None:
        self._system = system
        self._desktops: dict[str, DesktopConfig] = {}

    @property
    def name(self) -> str:
        return f"unsupported:{self._system.lower()}"

    @property
    def supports_gpu(self) -> bool:
        return False

    async def create_desktop(self, config: DesktopConfig) -> str:
        """Create a fallback in-memory session entry."""
        desktop_id = f"fallback-{self._system.lower()}-{uuid.uuid4().hex}"
        self._desktops[desktop_id] = config
        return desktop_id

    async def destroy_desktop(self, desktop_id: str) -> None:
        """Remove a fallback session entry."""
        self._desktops.pop(desktop_id, None)

    async def get_desktop_state(self, desktop_id: str) -> DesktopState:
        """Return tracked state for fallback sessions."""
        return DesktopState.RUNNING if desktop_id in self._desktops else DesktopState.STOPPED

    async def capture_screen(self, desktop_id: str) -> ScreenFrame:
        """Return a deterministic black frame."""
        config = self._desktops.get(desktop_id)
        width, height = config.resolution if config else (1920, 1080)
        return ScreenFrame(
            timestamp=time.time(),
            width=width,
            height=height,
            bytes_per_pixel=4,
            data=b"\x00" * (width * height * 4),
        )

    async def inject_input(self, desktop_id: str, event: InputEvent) -> bool:
        """Acknowledge supported event types for deterministic fallback behavior."""
        if desktop_id not in self._desktops:
            return False
        supported = {"mouse_move", "mouse_down", "mouse_up", "mouse_wheel", "key_down", "key_up"}
        return event.event_type in supported

    async def list_windows(self, desktop_id: str) -> list[dict[str, Any]]:
        """No windows are enumerated for fallback provider."""
        if desktop_id not in self._desktops:
            return []
        return []

    async def get_window_rect(self, desktop_id: str, window_id: str) -> tuple[int, int, int, int]:
        """Return default rect for fallback sessions."""
        if desktop_id not in self._desktops:
            return (0, 0, 0, 0)
        config = self._desktops[desktop_id]
        return (0, 0, config.resolution[0], config.resolution[1])
