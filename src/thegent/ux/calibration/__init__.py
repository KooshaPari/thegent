"""Confidence calibration loading."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """Calibrator for confidence scores."""

    def __init__(self, settings: Any | None = None, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self.bias_map: dict[str, float] = {}
        self.settings = settings
        if settings is not None:
            self.bias_map = self._load_calibration(Path(settings.session_dir))

    def _load_calibration(self, session_dir: Path) -> dict[str, float]:
        path = session_dir / "confidence_calibration.json"
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse calibration JSON: %s", exc)
            return {}
        if not isinstance(data, dict) or not all(
            isinstance(key, str) and isinstance(value, (int, float)) for key, value in data.items()
        ):
            logger.warning("Invalid calibration schema in %s", path)
            return {}
        return {key: float(value) for key, value in data.items()}

    def calibrate(self, score: float) -> float:
        """Calibrate a confidence score."""
        return min(1.0, max(0.0, score))

    def is_confident(self, score: float) -> bool:
        """Check if score meets confidence threshold."""
        return score >= self.threshold


__all__ = ["ConfidenceCalibrator"]
