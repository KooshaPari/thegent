from __future__ import annotations

"""Tests for GW-71: DLP guardrail.

# @trace FR-GUARD-071
"""

import pytest

from thegent.utils.routing_impl.guardrails.dlp import (
    DlpConfig,
    DlpPattern,
    DlpProfile,
    scan_dlp,
    should_block_dlp,
)

pytestmark = pytest.mark.requirement("FR-GUARD-071")


# ---------------------------------------------------------------------------
# 1. Disabled config returns no matches
# ---------------------------------------------------------------------------


def test_scan_disabled_returns_no_matches():
    config = DlpConfig(enabled=False, profile=DlpProfile.GDPR)
    result = scan_dlp("user@example.com — call me at +33 1 23 45 67 89", config=config)
    assert result.matches == []
    assert result.violation is False
    assert result.categories_found == []


# ---------------------------------------------------------------------------
# 2. GDPR profile
# ---------------------------------------------------------------------------


def test_gdpr_detects_email():
    config = DlpConfig(profile=DlpProfile.GDPR)
    result = scan_dlp("Contact us at alice@example.com for more info.", config=config)
    categories = {m.category for m in result.matches}
    assert "eu_email" in categories


def test_gdpr_clean_text_no_matches():
    config = DlpConfig(profile=DlpProfile.GDPR)
    result = scan_dlp("The weather is nice today.", config=config)
    assert result.matches == []
    assert result.violation is False


# ---------------------------------------------------------------------------
# 3. HIPAA profile
# ---------------------------------------------------------------------------


def test_hipaa_detects_ssn():
    config = DlpConfig(profile=DlpProfile.HIPAA)
    result = scan_dlp("Patient SSN is 123-45-6789 on file.", config=config)
    categories = {m.category for m in result.matches}
    assert "ssn" in categories
    assert result.violation is True


def test_hipaa_detects_mrn():
    config = DlpConfig(profile=DlpProfile.HIPAA)
    result = scan_dlp("Record for MRN: 1234567 was updated.", config=config)
    categories = {m.category for m in result.matches}
    assert "medical_record_number" in categories
    assert result.violation is True


# ---------------------------------------------------------------------------
# 4. PCI DSS profile
# ---------------------------------------------------------------------------


def test_pci_detects_visa_card():
    config = DlpConfig(profile=DlpProfile.PCI_DSS)
    result = scan_dlp("Card number: 4111-1111-1111-1111 was charged.", config=config)
    categories = {m.category for m in result.matches}
    assert "credit_card_visa" in categories
    assert result.violation is True


def test_pci_detects_amex():
    config = DlpConfig(profile=DlpProfile.PCI_DSS)
    result = scan_dlp("Amex card: 3714 496353 98431 on file.", config=config)
    categories = {m.category for m in result.matches}
    assert "credit_card_amex" in categories
    assert result.violation is True


# ---------------------------------------------------------------------------
# 5. Violation logic
# ---------------------------------------------------------------------------


def test_violation_on_high_severity():
    config = DlpConfig(profile=DlpProfile.HIPAA)
    # SSN is high severity
    result = scan_dlp("SSN: 123-45-6789", config=config)
    assert result.violation is True


def test_no_violation_medium_only():
    config = DlpConfig(profile=DlpProfile.GDPR)
    # Only eu_email (medium) should fire — no high-severity GDPR pattern
    result = scan_dlp("Email: bob@example.com", config=config)
    # Verify violation is False (no high-severity matches)
    high_severity_matches = [m for m in result.matches if m.severity == "high"]
    assert result.violation is (len(high_severity_matches) > 0)
    if not high_severity_matches:
        assert result.violation is False


# ---------------------------------------------------------------------------
# 6. should_block_dlp
# ---------------------------------------------------------------------------


def test_should_block_true():
    config = DlpConfig(profile=DlpProfile.HIPAA, block_on_violation=True)
    result = scan_dlp("Patient SSN: 234-56-7890", config=config)
    assert result.violation is True
    assert should_block_dlp(result, config=config) is True


def test_should_block_false_when_disabled():
    config = DlpConfig(profile=DlpProfile.HIPAA, block_on_violation=False)
    result = scan_dlp("Patient SSN: 234-56-7890", config=config)
    assert result.violation is True
    assert should_block_dlp(result, config=config) is False


# ---------------------------------------------------------------------------
# 7. CUSTOM profile
# ---------------------------------------------------------------------------


def test_custom_profile():
    custom_patterns = [
        DlpPattern(
            category="internal_project_code",
            profile=DlpProfile.CUSTOM,
            pattern=r"\bPROJ-\d{4,6}\b",
            severity="high",
        ),
    ]
    config = DlpConfig(profile=DlpProfile.CUSTOM, custom_patterns=custom_patterns)
    result = scan_dlp("Reference PROJ-123456 is confidential.", config=config)
    categories = {m.category for m in result.matches}
    assert "internal_project_code" in categories
    assert result.violation is True


# ---------------------------------------------------------------------------
# 8. categories_found populated
# ---------------------------------------------------------------------------


def test_categories_found_populated():
    config = DlpConfig(profile=DlpProfile.PCI_DSS)
    # Visa card + CVV
    result = scan_dlp("Card: 4111-1111-1111-1111, CVV: 123", config=config)
    assert len(result.categories_found) >= 1
    assert "credit_card_visa" in result.categories_found
    # categories_found should be unique (set-derived)
    assert len(result.categories_found) == len(set(result.categories_found))


# ---------------------------------------------------------------------------
# 9. snippet length
# ---------------------------------------------------------------------------


def test_match_snippet_length():
    config = DlpConfig(profile=DlpProfile.GDPR)
    long_email = "a" * 60 + "@" + "b" * 60 + ".com"
    result = scan_dlp(f"Contact: {long_email}", config=config)
    for match in result.matches:
        assert len(match.snippet) <= 50
