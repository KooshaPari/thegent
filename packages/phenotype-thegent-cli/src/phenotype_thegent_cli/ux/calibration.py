"""WP-4008: Feedback loops and confidence calibration."""

import orjson as json
import logging

from phenotype_thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """Calibrates agent confidence scores based on operator feedback."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings
        self.calibration_file = settings.session_dir / "confidence_calibration.json"
        self.bias_map = self._load_calibration()

    def calibrate(self, agent_name: str, raw_confidence: float) -> float:
        """Apply calibration bias to a raw confidence score."""
        bias = self.bias_map.get(agent_name, 0.0)
        calibrated = max(0.0, min(1.0, raw_confidence + bias))
        return calibrated

    def record_feedback(self, agent_name: str, provided_confidence: float, actual_success: bool):
        """Record feedback to update bias map."""
        # Simple moving average bias adjustment
        learning_rate = 0.1
        error = (1.0 if actual_success else 0.0) - provided_confidence

        current_bias = self.bias_map.get(agent_name, 0.0)
        new_bias = current_bias + (error * learning_rate)

        self.bias_map[agent_name] = new_bias
        self._save_calibration()

    def _load_calibration(self) -> dict[str, float]:
        if not self.calibration_file.exists():
            return {}
        try:
            payload = json.loads(self.calibration_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            _log.warning("Failed to parse calibration JSON at %s: %s", self.calibration_file, exc)
            return {}
        except OSError as exc:
            _log.warning("Failed reading calibration file at %s: %s", self.calibration_file, exc)
            return {}

        if not isinstance(payload, dict):
            _log.warning(
                "Invalid calibration schema at %s: expected object, got %s", self.calibration_file, type(payload)
            )
            return {}

        for agent_name, bias in payload.items():
            if not isinstance(agent_name, str) or not isinstance(bias, int | float):
                _log.warning(
                    "Invalid calibration schema at %s: entries must be str->number mappings",
                    self.calibration_file,
                )
                return {}

        return {agent_name: float(bias) for agent_name, bias in payload.items()}

    def _save_calibration(self):
        self.settings.session_dir.mkdir(parents=True, exist_ok=True)
        self.calibration_file.write_text(json.dumps(self.bias_map, indent=2), encoding="utf-8")
