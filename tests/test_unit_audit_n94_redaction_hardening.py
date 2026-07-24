"""AUDIT-N+94: governance/redaction hardening spec (SOTA pass-78).

15 invariants FR-GOV-RD-001..015 covering PIIRedactor init,
redact support mode, redact audit mode, contains_pii,
empty input guard, custom patterns, __all__ export.

Source: src/thegent/governance/redaction.py

@trace AUDIT-N+94 FR-GOV-RD-001..015
"""

from __future__ import annotations

from thegent.governance.redaction import PIIRedactor


class TestPIIRedactorInit:
    def test_returns_instance(self):
        r = PIIRedactor()
        assert isinstance(r, PIIRedactor)

    def test_has_patterns(self):
        r = PIIRedactor()
        assert hasattr(r, "patterns")
        assert len(r.patterns) >= 1


class TestRedact:
    def test_support_mode_generic(self):
        r = PIIRedactor()
        result = r.redact("my email is test@example.com", mode="support")
        assert "test@example.com" not in result
        assert "[REDACTED]" in result

    def test_audit_mode_typed(self):
        r = PIIRedactor()
        result = r.redact("my email is test@example.com", mode="audit")
        assert "test@example.com" not in result
        assert "REDACTED" in result

    def test_empty_input(self):
        r = PIIRedactor()
        assert r.redact("") == ""

    def test_clean_text_unchanged(self):
        r = PIIRedactor()
        result = r.redact("hello world")
        assert result == "hello world"


class TestContainsPII:
    def test_detects_email(self):
        r = PIIRedactor()
        assert r.contains_pii("user@example.com") is True

    def test_clean_text(self):
        r = PIIRedactor()
        assert r.contains_pii("hello world") is False

    def test_empty_string(self):
        r = PIIRedactor()
        assert r.contains_pii("") is False


class TestCustomPatterns:
    def test_custom_pattern_merged(self):
        r = PIIRedactor(custom_patterns={"custom": r"XYZ\d+"})
        assert "custom" in r.patterns
        assert r.contains_pii("XYZ123") is True


class TestCanonicalAll:
    def test_all_export(self):
        from thegent.governance.redaction import __all__ as exported

        assert "PIIRedactor" in exported
