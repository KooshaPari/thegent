"""Playwright-based browser automation and recording for VitePress documentation.

Provides high-level utilities for:
- Browser automation (launch, navigation, interactions)
- Video recording for feature demonstrations
- Screenshot capture with annotations
- Error recovery and timeout handling
- Multi-browser support (Chromium, Firefox, WebKit)
"""

import asyncio
import orjson as json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from playwright.async_api import (  # type: ignore
    Browser,  # type: ignore
    BrowserContext,  # type: ignore
    BrowserType,  # type: ignore
    Page,  # type: ignore
    async_playwright,  # type: ignore
)
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class ScreenshotOptions(BaseModel):
    """Configuration for screenshot capture."""

    model_config = ConfigDict(extra="forbid")

    full_page: bool = Field(default=False, description="Capture full page or viewport")
    quality: int = Field(default=95, ge=1, le=100, description="JPEG quality (1-100)")
    omit_background: bool = Field(default=False, description="Omit background for PNG")
    annotations: dict[str, Any] = Field(default_factory=dict, description="Overlay annotations")
    timeout: int = Field(default=30000, ge=1000, description="Timeout in milliseconds")
    wait_for_selector: str | None = Field(default=None, description="Wait for selector before capturing")


class VideoRecordingOptions(BaseModel):
    """Configuration for video recording."""

    model_config = ConfigDict(extra="forbid")

    size: dict[str, int] = Field(
        default_factory=lambda: {"width": 1280, "height": 720},
        description="Video resolution",
    )
    bitrate: int = Field(default=5000, ge=1000, description="Video bitrate (kbps)")
    fps: int = Field(default=30, ge=15, le=60, description="Frames per second")
    timeout: int = Field(default=300000, ge=30000, description="Recording timeout")


class RecordingConfig(BaseModel):
    """Configuration for recording sessions."""

    model_config = ConfigDict(extra="forbid")

    base_url: str = Field(default="http://localhost:5173", description="Base URL")
    browser: str = Field(
        default="chromium",
        description="Browser engine (chromium, firefox, webkit)",
    )
    headless: bool = Field(default=False, description="Run browser headless")
    slow_motion: int = Field(default=0, ge=0, description="Slow down actions (ms)")
    viewport_width: int = Field(default=1280, ge=640, description="Viewport width")
    viewport_height: int = Field(default=720, ge=480, description="Viewport height")
    device_scale_factor: float = Field(default=1.0, ge=1.0, description="Device scale")
    locale: str = Field(default="en-US", description="Locale for browser")
    timezone_id: str = Field(default="America/New_York", description="Timezone")
    user_agent: str | None = Field(default=None, description="Custom user agent")
    storage_state: str | None = Field(default=None, description="Storage state file")
    http_timeout: int = Field(default=30000, ge=5000, description="HTTP timeout")
    navigation_timeout: int = Field(default=30000, ge=5000, description="Navigation timeout")
    video: VideoRecordingOptions = Field(default_factory=VideoRecordingOptions, description="Video settings")
    screenshot: ScreenshotOptions = Field(default_factory=ScreenshotOptions, description="Screenshot settings")
    output_dir: Path = Field(default_factory=lambda: Path("docs/recordings"), description="Output directory")

    @field_validator("browser")
    @classmethod
    def validate_browser(cls, v: str) -> str:
        """Validate browser is one of the supported types."""
        if v not in ("chromium", "firefox", "webkit"):
            msg = f"Unknown browser: {v}. Must be one of: chromium, firefox, webkit"
            raise ValueError(msg)
        return v

    def model_post_init(self, __context):
        """Create output directory after model init."""
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class RecordingResult:
    """Result of a recording session."""

    success: bool
    video_path: Path | None = None
    screenshot_paths: list[Path] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "video_path": str(self.video_path) if self.video_path else None,
            "screenshot_paths": [str(p) for p in self.screenshot_paths],
            "timestamp": self.timestamp,
        }

    def to_json(self, path: Path | None = None) -> str:
        """Convert to JSON string or save to file."""
        json_data = json.dumps(self.to_dict().decode(), indent=2, default=str)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json_data)
        return json_data


class PlaywrightRecorder:
    """High-level wrapper for Playwright browser automation and recording.

    Handles:
    - Browser lifecycle (launch, close, context management)
    - Navigation and page interactions
    - Video recording with configurable quality
    - Screenshot capture
    - Error recovery and timeout handling
    - Multi-browser support

    Example:
        async with PlaywrightRecorder() as recorder:
            result = await recorder.record_feature("seed-detection")
    """

    def __init__(self, config: RecordingConfig | None = None) -> None:
        """Initialize recorder with configuration."""
        self.config = config or RecordingConfig()
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self._playwright = None
        self._browser_type: BrowserType | None = None
        self._start_time: float | None = None
        self._video_path: Path | None = None

    async def __aenter__(self) -> "PlaywrightRecorder":
        """Async context manager entry."""
        await self.launch()
        return self

    async def __aexit__(self, exc_type, _exc_val, _exc_tb) -> bool:
        """Async context manager exit."""
        await self.close()
        return False

    async def launch(self) -> None:
        """Launch browser instance."""
        try:
            self._playwright = await async_playwright().start()

            # Select browser type
            browsers = {
                "chromium": self._playwright.chromium,
                "firefox": self._playwright.firefox,
                "webkit": self._playwright.webkit,
            }
            self._browser_type = browsers.get(self.config.browser)
            if not self._browser_type:
                msg = f"Unknown browser: {self.config.browser}. Must be one of: {', '.join(browsers.keys())}"
                raise ValueError(msg)

            # Launch browser
            self.browser = await self._browser_type.launch(headless=self.config.headless)
            logger.info(f"Launched {self.config.browser} browser")

            # Create context with recording
            context_kwargs = {
                "viewport": {
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height,
                },
                "device_scale_factor": self.config.device_scale_factor,
                "locale": self.config.locale,
                "timezone_id": self.config.timezone_id,
            }

            if self.config.slow_motion > 0:
                context_kwargs["slow_motion"] = self.config.slow_motion

            if self.config.user_agent:
                context_kwargs["user_agent"] = self.config.user_agent

            if self.config.storage_state and Path(self.config.storage_state).exists():
                context_kwargs["storage_state"] = self.config.storage_state

            # Set up video recording
            self._video_path = self.config.output_dir / f"video_{int(time.time())}.webm"
            context_kwargs["record_video_dir"] = str(self._video_path.parent)

            self.context = await self.browser.new_context(**context_kwargs)
            self.context.set_default_timeout(self.config.http_timeout)
            self.context.set_default_navigation_timeout(self.config.navigation_timeout)

            self.page = await self.context.new_page()
            viewport_str = f"{self.config.viewport_width}x{self.config.viewport_height}"
            logger.info(f"Created context with viewport {viewport_str}")

        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            raise

    async def close(self) -> None:
        """Close browser and cleanup."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    async def navigate(
        self,
        url: str,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
    ) -> None:
        """Navigate to URL with configurable wait condition.

        Args:
            url: URL to navigate to (can be relative)
            wait_until: Wait condition for navigation
        """
        if not self.page:
            raise RuntimeError("Browser not launched")

        full_url = url if url.startswith("http") else f"{self.config.base_url}{url}"
        logger.info(f"Navigating to {full_url}")

        await self.page.goto(full_url, wait_until=wait_until)

    async def click(self, selector: str, button: Literal["left", "middle", "right"] = "left", delay: int = 0) -> None:
        """Click element."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.click(selector, button=button, delay=delay)
        logger.debug(f"Clicked {selector}")

    async def type_text(self, selector: str, text: str, delay: int = 100) -> None:
        """Type text into input element."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.fill(selector, "")
        await self.page.type(selector, text, delay=delay)
        logger.debug(f"Typed into {selector}: {text[:50]}")

    async def fill(self, selector: str, value: str) -> None:
        """Fill input element."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.fill(selector, value)
        logger.debug(f"Filled {selector}: {value[:50]}")

    async def press(self, selector: str, key: str) -> None:
        """Press key on element."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.click(selector)
        await self.page.press(selector, key)
        logger.debug(f"Pressed {key} on {selector}")

    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """Wait for element to appear."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.wait_for_selector(selector, timeout=timeout)
        logger.debug(f"Waited for {selector}")

    async def wait_for_function(self, expression: str, timeout: int = 30000) -> None:
        """Wait for JavaScript expression to return true."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.wait_for_function(expression, timeout=timeout)
        logger.debug(f"Waited for expression: {expression}")

    async def wait(self, ms: int) -> None:
        """Wait for specified milliseconds."""
        await asyncio.sleep(ms / 1000.0)
        logger.debug(f"Waited {ms}ms")

    async def evaluate(self, expression: str) -> Any:
        """Evaluate JavaScript expression."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        return await self.page.evaluate(expression)

    async def get_text_content(self, selector: str) -> str | None:
        """Get text content of element."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        return await self.page.text_content(selector)

    async def screenshot(self, name: str | None = None, options: ScreenshotOptions | None = None) -> Path:
        """Capture screenshot."""
        if not self.page:
            raise RuntimeError("Browser not launched")

        options = options or self.config.screenshot
        timestamp = int(time.time() * 1000)
        suffix = f"_{name}_{timestamp}.png" if name else f"_{timestamp}.png"
        filename = f"screenshot{suffix}"
        filepath = self.config.output_dir / filename

        # Wait for selector if specified
        if options.wait_for_selector:
            await self.wait_for_selector(options.wait_for_selector, options.timeout)

        # Capture screenshot
        screenshot_kwargs = {
            "path": str(filepath),
            "full_page": options.full_page,
        }

        await self.page.screenshot(**screenshot_kwargs)
        logger.info(f"Screenshot saved to {filepath}")

        return filepath

    async def get_video_path(self) -> Path | None:
        """Get path to recorded video after closing context.

        Returns None until context is closed.
        """
        if not self.context or not self._video_path:
            return None

        video_files = list(self._video_path.parent.glob("**/*.webm"))
        return video_files[0] if video_files else None

    async def _execute_action(self, action: str, selector: str, value: Any | None) -> None:
        """Execute a single interaction action safely."""
        try:
            if action == "click":
                await self.click(selector)
            elif action == "type":
                await self.type_text(selector, value or "")
            elif action == "fill":
                await self.fill(selector, value or "")
            elif action == "press":
                await self.press(selector, value or "Enter")
            elif action == "wait":
                await self.wait_for_selector(selector)
            elif action == "wait_function":
                await self.wait_for_function(selector)
            elif action == "navigate":
                await self.navigate(selector)
            elif action == "evaluate":
                await self.evaluate(selector)
            elif action == "sleep":
                await self.wait(int(value or 1000))
            else:
                logger.warning(f"Unknown action: {action}")
        except Exception as e:
            logger.error(f"Failed to execute {action} on {selector}: {e}")
            raise

    async def record_interaction(
        self,
        name: str,
        instructions: list[tuple[str, str, Any | None]] | None = None,
        wait_selector: str | None = None,
        wait_function: str | None = None,
        wait_ms: int = 0,
        screenshot_after: bool = True,
    ) -> RecordingResult:
        """Record a single interaction or sequence of interactions.

        Args:
            name: Feature/interaction name
            instructions: List of (action, selector, value) tuples
            wait_selector: Wait for selector before recording
            wait_function: Wait for JS function before recording
            wait_ms: Wait time in milliseconds
            screenshot_after: Take screenshot after interactions

        Returns:
            RecordingResult with paths to video and screenshots
        """
        start_time = time.time()
        result = RecordingResult(success=False, metadata={"name": name})

        try:
            if not self.page:
                raise RuntimeError("Browser not launched")

            logger.info(f"Recording interaction: {name}")

            if wait_selector:
                await self.wait_for_selector(wait_selector)
            if wait_function:
                await self.wait_for_function(wait_function)
            if wait_ms > 0:
                await self.wait(wait_ms)

            instructions = instructions or []
            for action, selector, value in instructions:
                await self._execute_action(action, selector, value)

            if screenshot_after:
                screenshot_path = await self.screenshot(name)
                result.screenshot_paths.append(screenshot_path)

            result.success = True
            logger.info(f"Successfully recorded {name}")

        except Exception as e:
            logger.error(f"Failed to record {name}: {e}")
            result.error = str(e)

        finally:
            result.duration = time.time() - start_time
            result.metadata["duration"] = result.duration

        return result

    async def record_feature(
        self,
        feature_name: str,
        route: str = "/",
        interactions: list[tuple[str, str, Any | None]] | None = None,
        wait_selector: str | None = None,
        wait_function: str | None = None,
        initial_wait_ms: int = 1000,
        description: str | None = None,
    ) -> RecordingResult:
        """Record a complete feature demonstration.

        Args:
            feature_name: Name of feature
            route: Route to navigate to
            interactions: List of interactions
            wait_selector: Element to wait for before interactions
            wait_function: JS function to wait for
            initial_wait_ms: Initial wait after navigation
            description: Feature description

        Returns:
            RecordingResult with video and screenshot paths
        """
        start_time = time.time()
        result = RecordingResult(
            success=False,
            metadata={
                "feature": feature_name,
                "route": route,
                "description": description,
                "browser": self.config.browser,
            },
        )

        try:
            await self.navigate(route)
            await self.wait(initial_wait_ms)

            interaction_result = await self.record_interaction(
                feature_name,
                instructions=interactions,
                wait_selector=wait_selector,
                wait_function=wait_function,
                screenshot_after=True,
            )

            if not interaction_result.success:
                msg = f"Interaction failed: {interaction_result.error}"
                raise RuntimeError(msg)

            result.screenshot_paths = interaction_result.screenshot_paths
            result.metadata.update(interaction_result.metadata)
            result.success = True

        except Exception as e:
            logger.error(f"Failed to record feature {feature_name}: {e}")
            result.error = str(e)

        finally:
            result.duration = time.time() - start_time
            result.metadata["duration"] = result.duration

        return result

    async def record_page_flow(
        self,
        flow_name: str,
        steps: list[dict[str, Any]],
        description: str | None = None,
    ) -> RecordingResult:
        """Record a multi-step page flow/workflow.

        Args:
            flow_name: Name of the flow
            steps: List of step configurations
            description: Flow description

        Returns:
            RecordingResult with all screenshots and videos
        """
        start_time = time.time()
        result = RecordingResult(
            success=False,
            metadata={
                "flow": flow_name,
                "description": description,
                "steps": len(steps),
            },
        )

        try:
            for step in steps:
                if "navigate" in step:
                    await self.navigate(step["navigate"])
                    await self.wait(step.get("wait_ms", 500))

                if "actions" in step:
                    for action, selector, value in step["actions"]:
                        if action == "click":
                            await self.click(selector)
                        elif action == "type":
                            await self.type_text(selector, value or "")
                        elif action == "fill":
                            await self.fill(selector, value or "")
                        elif action == "wait":
                            await self.wait_for_selector(selector)

                if "screenshot" in step:
                    screenshot_path = await self.screenshot(step["screenshot"])
                    result.screenshot_paths.append(screenshot_path)

            result.success = True

        except Exception as e:
            logger.error(f"Failed to record flow {flow_name}: {e}")
            result.error = str(e)

        finally:
            result.duration = time.time() - start_time
            result.metadata["duration"] = result.duration

        return result


async def record_simple_demo(
    feature_name: str,
    route: str = "/",
    interactions: list[tuple[str, str, Any | None]] | None = None,
    config: RecordingConfig | None = None,
) -> RecordingResult:
    """Simple function for recording a feature demo.

    Handles browser lifecycle automatically.

    Args:
        feature_name: Name of feature to record
        route: Route to navigate to
        interactions: List of interactions
        config: Recording configuration

    Returns:
        RecordingResult with paths and metadata
    """
    config = config or RecordingConfig()

    async with PlaywrightRecorder(config) as recorder:
        result = await recorder.record_feature(feature_name, route=route, interactions=interactions)
    return result
