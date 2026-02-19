"""Documentation tools for VitePress browser recordings and automation."""

from .playwright_recorder import (  # type: ignore
    PlaywrightRecorder,
    RecordingConfig,
    RecordingResult,
    ScreenshotOptions,
    VideoRecordingOptions,
)

__all__ = [
    "PlaywrightRecorder",
    "RecordingConfig",
    "RecordingResult",
    "ScreenshotOptions",
    "VideoRecordingOptions",
]
