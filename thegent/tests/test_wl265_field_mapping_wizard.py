"""Tests for WL-265: Field Mapping Bootstrap Wizard.

Verifies that field mappings can be added, retrieved, and applied with
optional transformations.

# @trace WL-265
"""

from __future__ import annotations

import pytest

from thegent.integrations.field_mapping_wizard import (
    FieldMappingEntry,
    FieldMappingWizard,
)


@pytest.mark.requirement("WL-265")
class TestFieldMappingWizard:
    """WL-265: Field mapping bootstrap wizard for connector setup."""

    def test_add_and_get_mapping(self):
        """# @trace WL-265 — add a mapping and retrieve it by source field."""
        wizard = FieldMappingWizard()

        entry = wizard.add("email", "user_email", transform="identity")

        assert entry.source_field == "email"
        assert entry.target_field == "user_email"
        assert entry.transform == "identity"

        retrieved = wizard.get("email")
        assert retrieved.source_field == "email"
        assert retrieved.target_field == "user_email"

    def test_add_mapping_with_default_transform(self):
        """# @trace WL-265 — add a mapping without specifying transform defaults to identity."""
        wizard = FieldMappingWizard()

        entry = wizard.add("name", "full_name")

        assert entry.transform == "identity"

    def test_get_missing_field_raises_key_error(self):
        """# @trace WL-265 — retrieving a non-existent field raises KeyError."""
        wizard = FieldMappingWizard()

        with pytest.raises(KeyError, match="Field mapping for 'missing' not found"):
            wizard.get("missing")

    def test_apply_identity_transform(self):
        """# @trace WL-265 — apply identity transform returns value unchanged."""
        wizard = FieldMappingWizard()
        wizard.add("email", "user_email", transform="identity")

        result = wizard.apply("email", "test@example.com")

        assert result == "test@example.com"

    def test_apply_with_missing_field_raises_key_error(self):
        """# @trace WL-265 — applying a transform to a non-existent field raises KeyError."""
        wizard = FieldMappingWizard()

        with pytest.raises(KeyError, match="Field mapping for 'missing' not found"):
            wizard.apply("missing", "value")

    def test_all_mappings_returns_list(self):
        """# @trace WL-265 — all_mappings() returns all configured mappings."""
        wizard = FieldMappingWizard()
        wizard.add("email", "user_email")
        wizard.add("name", "full_name")
        wizard.add("phone", "phone_number")

        mappings = wizard.all_mappings()

        assert len(mappings) == 3
        assert all(isinstance(m, FieldMappingEntry) for m in mappings)

        source_fields = {m.source_field for m in mappings}
        assert source_fields == {"email", "name", "phone"}

    def test_all_mappings_returns_empty_list_initially(self):
        """# @trace WL-265 — all_mappings() returns empty list on new wizard."""
        wizard = FieldMappingWizard()

        mappings = wizard.all_mappings()

        assert mappings == []

    def test_multiple_mappings_are_independent(self):
        """# @trace WL-265 — multiple mappings are stored independently."""
        wizard = FieldMappingWizard()
        wizard.add("email", "user_email", transform="identity")
        wizard.add("name", "full_name", transform="identity")

        email_entry = wizard.get("email")
        name_entry = wizard.get("name")

        assert email_entry.source_field == "email"
        assert email_entry.target_field == "user_email"

        assert name_entry.source_field == "name"
        assert name_entry.target_field == "full_name"

    def test_overwriting_existing_mapping(self):
        """# @trace WL-265 — adding a mapping with same source field overwrites previous."""
        wizard = FieldMappingWizard()
        wizard.add("email", "user_email")
        wizard.add("email", "contact_email")  # Overwrite

        entry = wizard.get("email")

        assert entry.target_field == "contact_email"

    def test_apply_with_empty_value(self):
        """# @trace WL-265 — apply handles empty string values correctly."""
        wizard = FieldMappingWizard()
        wizard.add("optional_field", "nullable_field")

        result = wizard.apply("optional_field", "")

        assert result == ""

    def test_apply_with_special_characters(self):
        """# @trace WL-265 — apply handles special characters in values."""
        wizard = FieldMappingWizard()
        wizard.add("data", "transformed_data")

        special_value = "hello\nworld\t\r@#$%^&*()"
        result = wizard.apply("data", special_value)

        assert result == special_value
