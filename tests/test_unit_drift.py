"""Tests for WP-3005: Policy drift detection."""

import json
import time
from unittest.mock import MagicMock

import pytest

from thegent.config import ThegentSettings
from thegent.governance.drift import DriftDetector


@pytest.fixture
def mock_settings(tmp_path):
    settings = MagicMock(spec=ThegentSettings)
    settings.session_dir = tmp_path / "session"
    settings.session_dir.mkdir(parents=True)
    return settings


def test_drift_detector_detects_expired_overrides(mock_settings):
    # Setup: create an expired override manually
    overrides_dir = mock_settings.session_dir / "overrides"
    overrides_dir.mkdir()

    expired_time = time.time() - 3600
    override = {
        "policy_id": "ov_expired",
        "by": "user",
        "expires_at": expired_time,
        "reason": "Old override",
        "created_at": time.time() - 7200,
        "metadata": {},
    }
    with (overrides_dir / "ov_expired.json").open("w") as f:
        json.dump(override, f)

    detector = DriftDetector(mock_settings)
    report = detector.detect_drift()

    assert report["drift_detected"] is True
    assert len(report["expired_overrides"]) == 1
    assert report["expired_overrides"][0]["id"] == "ov_expired"

    # Check log was created
    assert (mock_settings.session_dir / "policy_drift.jsonl").exists()


def test_drift_detector_sweep_cleans_overrides(mock_settings):
    overrides_dir = mock_settings.session_dir / "overrides"
    overrides_dir.mkdir()

    # Create one expired and one valid override
    expired_time = time.time() - 3600
    valid_time = time.time() + 3600

    with (overrides_dir / "expired.json").open("w") as f:
        json.dump(
            {
                "policy_id": "expired",
                "by": "u",
                "expires_at": expired_time,
                "reason": "r",
                "created_at": time.time(),
                "metadata": {},
            },
            f,
        )
    with (overrides_dir / "valid.json").open("w") as f:
        json.dump(
            {
                "policy_id": "valid",
                "by": "u",
                "expires_at": valid_time,
                "reason": "r",
                "created_at": time.time(),
                "metadata": {},
            },
            f,
        )

    detector = DriftDetector(mock_settings)
    results = detector.sweep()

    assert results["overrides_cleaned"] == 1
    assert not (overrides_dir / "expired.json").exists()
    assert (overrides_dir / "valid.json").exists()
