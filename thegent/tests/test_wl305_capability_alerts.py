"""Tests for WL-305 Capability Mismatch Alerts.

# @trace WL-305
"""

from __future__ import annotations

import pytest

from thegent.integrations.capability_alerts import CapabilityMismatchDetector


class TestCapabilityMismatchDetectorInit:
    """Tests for detector initialization."""

    def test_init_with_single_capability(self) -> None:
        """Initialize with single required capability."""
        detector = CapabilityMismatchDetector(["read"])
        assert detector.required_capabilities == ["read"]

    def test_init_with_multiple_capabilities(self) -> None:
        """Initialize with multiple required capabilities."""
        caps = ["read", "write", "delete"]
        detector = CapabilityMismatchDetector(caps)
        assert detector.required_capabilities == caps

    def test_init_with_empty_list_raises(self) -> None:
        """Empty required_capabilities raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            CapabilityMismatchDetector([])

    def test_init_with_non_list_raises(self) -> None:
        """Non-list required_capabilities raises ValueError."""
        with pytest.raises(ValueError, match="must be a list"):
            CapabilityMismatchDetector("read")

    def test_init_with_non_list_dict_raises(self) -> None:
        """Dict instead of list raises ValueError."""
        with pytest.raises(ValueError, match="must be a list"):
            CapabilityMismatchDetector({"read": True})

    @pytest.mark.requirement("WL-305")
    def test_init_preserves_order(self) -> None:
        """Initialization preserves capability order."""
        caps = ["z", "a", "m"]
        detector = CapabilityMismatchDetector(caps)
        assert detector.required_capabilities == caps


class TestCheckConnector:
    """Tests for check_connector method."""

    def test_check_all_present(self) -> None:
        """All capabilities present returns empty list."""
        detector = CapabilityMismatchDetector(["read", "write"])
        missing = detector.check_connector("github", ["read", "write"])
        assert missing == []

    def test_check_all_missing(self) -> None:
        """All capabilities missing."""
        detector = CapabilityMismatchDetector(["read", "write"])
        missing = detector.check_connector("github", [])
        assert set(missing) == {"read", "write"}

    def test_check_partial_missing(self) -> None:
        """Partial capabilities missing."""
        detector = CapabilityMismatchDetector(["read", "write", "delete"])
        missing = detector.check_connector("github", ["read"])
        assert set(missing) == {"write", "delete"}

    def test_check_extra_capabilities_ignored(self) -> None:
        """Extra connector capabilities don't affect result."""
        detector = CapabilityMismatchDetector(["read"])
        missing = detector.check_connector(
            "github",
            ["read", "write", "delete", "execute"],
        )
        assert missing == []

    def test_check_empty_available_capabilities(self) -> None:
        """Empty available capabilities returns all required."""
        detector = CapabilityMismatchDetector(["read", "write"])
        missing = detector.check_connector("github", [])
        assert set(missing) == {"read", "write"}

    def test_check_empty_connector_name_raises(self) -> None:
        """Empty connector name raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="non-empty string"):
            detector.check_connector("", ["read"])

    def test_check_non_string_connector_name_raises(self) -> None:
        """Non-string connector name raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="non-empty string"):
            detector.check_connector(123, ["read"])

    def test_check_non_list_available_raises(self) -> None:
        """Non-list available_capabilities raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="must be a list"):
            detector.check_connector("github", "read")

    @pytest.mark.requirement("WL-305")
    def test_check_case_sensitive(self) -> None:
        """Capability matching is case-sensitive."""
        detector = CapabilityMismatchDetector(["Read"])
        missing = detector.check_connector("github", ["read"])
        assert missing == ["Read"]


class TestIsCompatible:
    """Tests for is_compatible method."""

    def test_is_compatible_all_present(self) -> None:
        """All capabilities present returns True."""
        detector = CapabilityMismatchDetector(["read", "write"])
        assert detector.is_compatible("github", ["read", "write"]) is True

    def test_is_compatible_with_extra(self) -> None:
        """Compatible with extra capabilities."""
        detector = CapabilityMismatchDetector(["read"])
        assert detector.is_compatible("github", ["read", "write", "delete"]) is True

    def test_is_compatible_missing_one(self) -> None:
        """Missing one capability returns False."""
        detector = CapabilityMismatchDetector(["read", "write"])
        assert detector.is_compatible("github", ["read"]) is False

    def test_is_compatible_all_missing(self) -> None:
        """All missing returns False."""
        detector = CapabilityMismatchDetector(["read", "write"])
        assert detector.is_compatible("github", []) is False

    def test_is_compatible_empty_connector_name_raises(self) -> None:
        """Empty connector name raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="non-empty string"):
            detector.is_compatible("", ["read"])

    def test_is_compatible_non_list_available_raises(self) -> None:
        """Non-list available_capabilities raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="must be a list"):
            detector.is_compatible("github", "read")

    @pytest.mark.requirement("WL-305")
    def test_is_compatible_delegates_to_check(self) -> None:
        """is_compatible is consistent with check_connector."""
        detector = CapabilityMismatchDetector(["a", "b", "c"])

        # When check returns empty, is_compatible is True
        assert detector.is_compatible("x", ["a", "b", "c"]) is True

        # When check returns non-empty, is_compatible is False
        assert detector.is_compatible("x", ["a"]) is False


class TestGenerateAlert:
    """Tests for generate_alert method."""

    def test_generate_alert_no_missing(self) -> None:
        """No missing capabilities generates 'ok' alert."""
        detector = CapabilityMismatchDetector(["read"])
        alert = detector.generate_alert("github", [])

        assert alert["connector"] == "github"
        assert alert["missing"] == []
        assert alert["severity"] == "ok"
        assert "timestamp" in alert

    def test_generate_alert_with_missing(self) -> None:
        """Missing capabilities generates 'critical' alert."""
        detector = CapabilityMismatchDetector(["read"])
        alert = detector.generate_alert("github", ["read", "write"])

        assert alert["connector"] == "github"
        assert alert["missing"] == ["read", "write"]
        assert alert["severity"] == "critical"
        assert "timestamp" in alert

    def test_generate_alert_single_missing(self) -> None:
        """Single missing capability."""
        detector = CapabilityMismatchDetector(["read"])
        alert = detector.generate_alert("github", ["write"])

        assert alert["missing"] == ["write"]
        assert alert["severity"] == "critical"

    def test_generate_alert_empty_connector_raises(self) -> None:
        """Empty connector name raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="non-empty string"):
            detector.generate_alert("", ["read"])

    def test_generate_alert_non_string_connector_raises(self) -> None:
        """Non-string connector name raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="non-empty string"):
            detector.generate_alert(None, ["read"])

    def test_generate_alert_non_list_missing_raises(self) -> None:
        """Non-list missing raises ValueError."""
        detector = CapabilityMismatchDetector(["read"])
        with pytest.raises(ValueError, match="must be a list"):
            detector.generate_alert("github", "read")

    def test_generate_alert_timestamp_is_iso(self) -> None:
        """Timestamp is ISO format."""
        detector = CapabilityMismatchDetector(["read"])
        alert = detector.generate_alert("github", [])

        ts = alert["timestamp"]
        # Should parse as valid ISO datetime
        from datetime import datetime

        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert dt is not None

    @pytest.mark.requirement("WL-305")
    def test_generate_alert_all_fields(self) -> None:
        """Alert has all required fields."""
        detector = CapabilityMismatchDetector(["read"])
        alert = detector.generate_alert("github", ["missing"])

        required_keys = {"connector", "missing", "severity", "timestamp"}
        assert required_keys.issubset(alert.keys())


class TestIntegrationFlow:
    """Integration tests for typical detector usage."""

    def test_detector_workflow_compatible(self) -> None:
        """Workflow for compatible connector."""
        detector = CapabilityMismatchDetector(["read", "write"])

        # Check returns no missing
        missing = detector.check_connector("github", ["read", "write", "delete"])
        assert missing == []

        # is_compatible returns True
        assert detector.is_compatible("github", ["read", "write", "delete"]) is True

        # Alert severity is ok
        alert = detector.generate_alert("github", missing)
        assert alert["severity"] == "ok"

    def test_detector_workflow_incompatible(self) -> None:
        """Workflow for incompatible connector."""
        detector = CapabilityMismatchDetector(["read", "write"])

        # Check returns missing items
        missing = detector.check_connector("basic", ["read"])
        assert set(missing) == {"write"}

        # is_compatible returns False
        assert detector.is_compatible("basic", ["read"]) is False

        # Alert severity is critical
        alert = detector.generate_alert("basic", missing)
        assert alert["severity"] == "critical"
        assert set(alert["missing"]) == {"write"}

    @pytest.mark.requirement("WL-305")
    def test_detector_multiple_connectors(self) -> None:
        """Can check multiple connectors."""
        detector = CapabilityMismatchDetector(["read", "write"])

        # Check each
        github_ok = detector.is_compatible("github", ["read", "write"])
        linear_missing = detector.is_compatible("linear", ["read"])

        assert github_ok is True
        assert linear_missing is False
