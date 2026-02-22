"""Tests for artifact redaction pipeline.

# @trace WL-276
"""

from __future__ import annotations

import pytest

from thegent.integrations.artifact_redaction import (
    ArtifactRedactionPipeline,
    RedactionRule,
)


@pytest.mark.requirement("WL-276")
class TestRedactionRule:
    """Test RedactionRule dataclass."""

    def test_redaction_rule_default_replacement(self) -> None:
        """Test RedactionRule with default replacement."""
        rule = RedactionRule(field_path="password")
        assert rule.field_path == "password"
        assert rule.replacement == "[REDACTED]"

    def test_redaction_rule_custom_replacement(self) -> None:
        """Test RedactionRule with custom replacement."""
        rule = RedactionRule(field_path="api_key", replacement="***")
        assert rule.field_path == "api_key"
        assert rule.replacement == "***"


@pytest.mark.requirement("WL-276")
class TestArtifactRedactionPipeline:
    """Test ArtifactRedactionPipeline."""

    def test_add_rule_default_replacement(self) -> None:
        """Test adding a rule with default replacement."""
        pipeline = ArtifactRedactionPipeline()
        rule = pipeline.add_rule("password")
        assert rule.field_path == "password"
        assert rule.replacement == "[REDACTED]"

    def test_add_rule_custom_replacement(self) -> None:
        """Test adding a rule with custom replacement."""
        pipeline = ArtifactRedactionPipeline()
        rule = pipeline.add_rule("token", replacement="***HIDDEN***")
        assert rule.field_path == "token"
        assert rule.replacement == "***HIDDEN***"

    def test_add_multiple_rules(self) -> None:
        """Test adding multiple rules."""
        pipeline = ArtifactRedactionPipeline()
        rule1 = pipeline.add_rule("password")
        rule2 = pipeline.add_rule("api_key", replacement="***")
        rules = pipeline.rules()
        assert len(rules) == 2
        assert rules[0] == rule1
        assert rules[1] == rule2

    def test_redact_single_field(self) -> None:
        """Test redacting a single field."""
        pipeline = ArtifactRedactionPipeline()
        pipeline.add_rule("password")
        data = {"username": "admin", "password": "secret123"}
        redacted = pipeline.redact(data)
        assert redacted["username"] == "admin"
        assert redacted["password"] == "[REDACTED]"

    def test_redact_multiple_fields(self) -> None:
        """Test redacting multiple fields."""
        pipeline = ArtifactRedactionPipeline()
        pipeline.add_rule("password")
        pipeline.add_rule("api_key", replacement="***")
        data = {
            "username": "admin",
            "password": "secret123",
            "api_key": "sk-12345",
        }
        redacted = pipeline.redact(data)
        assert redacted["username"] == "admin"
        assert redacted["password"] == "[REDACTED]"
        assert redacted["api_key"] == "***"

    def test_redact_missing_field(self) -> None:
        """Test redacting when field doesn't exist."""
        pipeline = ArtifactRedactionPipeline()
        pipeline.add_rule("password")
        data = {"username": "admin"}
        redacted = pipeline.redact(data)
        assert redacted == {"username": "admin"}
        assert "password" not in redacted

    def test_redact_returns_copy(self) -> None:
        """Test that redact returns a copy, not modifying original."""
        pipeline = ArtifactRedactionPipeline()
        pipeline.add_rule("password")
        original = {"username": "admin", "password": "secret123"}
        redacted = pipeline.redact(original)
        assert original["password"] == "secret123"
        assert redacted["password"] == "[REDACTED]"

    def test_rules_returns_list(self) -> None:
        """Test that rules() returns a list."""
        pipeline = ArtifactRedactionPipeline()
        pipeline.add_rule("password")
        pipeline.add_rule("token")
        rules = pipeline.rules()
        assert isinstance(rules, list)
        assert len(rules) == 2

    def test_empty_pipeline_redact(self) -> None:
        """Test redacting with no rules."""
        pipeline = ArtifactRedactionPipeline()
        data = {"username": "admin", "password": "secret123"}
        redacted = pipeline.redact(data)
        assert redacted == data
