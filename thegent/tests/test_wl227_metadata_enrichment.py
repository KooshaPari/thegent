"""Tests for WL-227: Metadata Enrichment.

Verifies metadata enrichment rule application and record enhancement.

# @trace WL-227
"""

from __future__ import annotations

import pytest


@pytest.mark.requirement("WL-227")
class TestMetadataEnricher:
    """WL-227: Metadata enrichment for workstream records."""

    def test_enrichment_rule_dataclass_structure(self):
        """# @trace WL-227 — EnrichmentRule has required fields."""
        from thegent.integrations.metadata_enrichment import EnrichmentRule

        rule = EnrichmentRule(key="status", value="PENDING")
        assert rule.key == "status"
        assert rule.value == "PENDING"

    def test_add_rule_creates_and_returns_rule(self):
        """# @trace WL-227 — add_rule() creates and returns an EnrichmentRule."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        rule = enricher.add_rule("priority", "HIGH")

        assert rule.key == "priority"
        assert rule.value == "HIGH"

    def test_add_rule_stores_rule(self):
        """# @trace WL-227 — add_rule() stores the rule internally."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")

        rules = enricher.rules()
        assert len(rules) == 1
        assert rules[0].key == "priority"
        assert rules[0].value == "HIGH"

    def test_add_multiple_rules(self):
        """# @trace WL-227 — add_rule() can be called multiple times."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")
        enricher.add_rule("owner", "alice")
        enricher.add_rule("status", "ACTIVE")

        rules = enricher.rules()
        assert len(rules) == 3

    def test_enrich_adds_new_keys(self):
        """# @trace WL-227 — enrich() adds keys not present in record."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")
        enricher.add_rule("owner", "alice")

        record = {"id": "WL-001", "title": "Test"}
        enriched = enricher.enrich(record)

        assert enriched["id"] == "WL-001"
        assert enriched["title"] == "Test"
        assert enriched["priority"] == "HIGH"
        assert enriched["owner"] == "alice"

    def test_enrich_does_not_override_existing_keys(self):
        """# @trace WL-227 — enrich() only adds keys not already present."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")
        enricher.add_rule("owner", "alice")

        record = {"id": "WL-001", "priority": "LOW"}
        enriched = enricher.enrich(record)

        assert enriched["priority"] == "LOW"  # Original value preserved
        assert enriched["owner"] == "alice"  # New key added

    def test_enrich_returns_new_dict(self):
        """# @trace WL-227 — enrich() returns a new dict without modifying original."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")

        original = {"id": "WL-001"}
        enriched = enricher.enrich(original)

        assert "priority" not in original
        assert enriched["priority"] == "HIGH"
        assert original is not enriched

    def test_enrich_empty_record(self):
        """# @trace WL-227 — enrich() adds all rules to empty record."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("key1", "value1")
        enricher.add_rule("key2", "value2")

        enriched = enricher.enrich({})

        assert enriched["key1"] == "value1"
        assert enriched["key2"] == "value2"

    def test_enrich_with_no_rules(self):
        """# @trace WL-227 — enrich() with no rules returns copy of record."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        record = {"id": "WL-001", "title": "Test"}
        enriched = enricher.enrich(record)

        assert enriched == record
        assert enriched is not record

    def test_enrich_all_with_multiple_records(self):
        """# @trace WL-227 — enrich_all() enriches all records in list."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")

        records = [
            {"id": "WL-001"},
            {"id": "WL-002"},
            {"id": "WL-003"},
        ]
        enriched_records = enricher.enrich_all(records)

        assert len(enriched_records) == 3
        assert all("priority" in r for r in enriched_records)
        assert all(r["priority"] == "HIGH" for r in enriched_records)

    def test_enrich_all_preserves_original_list(self):
        """# @trace WL-227 — enrich_all() does not modify original list."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")

        records = [{"id": "WL-001"}]
        enriched_records = enricher.enrich_all(records)

        assert "priority" not in records[0]
        assert enriched_records[0]["priority"] == "HIGH"

    def test_enrich_all_empty_list(self):
        """# @trace WL-227 — enrich_all() handles empty list."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")

        enriched = enricher.enrich_all([])
        assert enriched == []

    def test_enrich_all_no_rules(self):
        """# @trace WL-227 — enrich_all() with no rules returns copies."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        records = [{"id": "WL-001"}, {"id": "WL-002"}]

        enriched = enricher.enrich_all(records)

        assert len(enriched) == 2
        assert enriched[0] == records[0]
        assert enriched[1] == records[1]
        assert enriched[0] is not records[0]
        assert enriched[1] is not records[1]

    def test_rules_returns_list_of_enrichment_rules(self):
        """# @trace WL-227 — rules() returns list of EnrichmentRule instances."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("key1", "value1")
        enricher.add_rule("key2", "value2")

        rules = enricher.rules()

        assert len(rules) == 2
        assert rules[0].key == "key1"
        assert rules[0].value == "value1"
        assert rules[1].key == "key2"
        assert rules[1].value == "value2"

    def test_rules_returns_copy_not_reference(self):
        """# @trace WL-227 — rules() returns a copy, not reference to internal list."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("key1", "value1")

        rules1 = enricher.rules()
        rules2 = enricher.rules()

        assert rules1 is not rules2
        assert rules1[0].key == rules2[0].key

    def test_enrich_with_various_value_types(self):
        """# @trace WL-227 — enrich() handles various value types."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("string_val", "text")
        enricher.add_rule("int_val", 42)
        enricher.add_rule("float_val", 3.14)
        enricher.add_rule("bool_val", True)
        enricher.add_rule("list_val", [1, 2, 3])
        enricher.add_rule("dict_val", {"nested": "value"})
        enricher.add_rule("none_val", None)

        record = {"id": "WL-001"}
        enriched = enricher.enrich(record)

        assert enriched["string_val"] == "text"
        assert enriched["int_val"] == 42
        assert enriched["float_val"] == 3.14
        assert enriched["bool_val"] is True
        assert enriched["list_val"] == [1, 2, 3]
        assert enriched["dict_val"] == {"nested": "value"}
        assert enriched["none_val"] is None

    def test_enrich_with_overlapping_rules(self):
        """# @trace WL-227 — later rules don't override earlier ones if key exists."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")
        enricher.add_rule("priority", "LOW")  # Second rule with same key

        record = {}
        enriched = enricher.enrich(record)

        # First rule should be applied since it's not already in record
        assert enriched["priority"] == "HIGH"

    def test_enrich_multiple_records_with_different_existing_keys(self):
        """# @trace WL-227 — enrich_all() respects existing keys per record."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("priority", "HIGH")
        enricher.add_rule("owner", "alice")

        records = [
            {"id": "WL-001", "priority": "LOW"},  # priority exists
            {"id": "WL-002", "owner": "bob"},  # owner exists
            {"id": "WL-003"},  # neither exists
        ]

        enriched = enricher.enrich_all(records)

        assert enriched[0]["priority"] == "LOW"  # Original preserved
        assert enriched[0]["owner"] == "alice"  # New key added
        assert enriched[1]["owner"] == "bob"  # Original preserved
        assert enriched[1]["priority"] == "HIGH"  # New key added
        assert enriched[2]["priority"] == "HIGH"  # New key added
        assert enriched[2]["owner"] == "alice"  # New key added

    def test_rules_empty_initially(self):
        """# @trace WL-227 — rules() returns empty list initially."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        rules = enricher.rules()

        assert rules == []

    def test_enrich_preserves_all_original_fields(self):
        """# @trace WL-227 — enrich() preserves all fields from original record."""
        from thegent.integrations.metadata_enrichment import MetadataEnricher

        enricher = MetadataEnricher()
        enricher.add_rule("new_key", "new_value")

        record = {
            "id": "WL-001",
            "title": "Test",
            "status": "PENDING",
            "tags": ["a", "b"],
            "metadata": {"version": "1.0"},
        }
        enriched = enricher.enrich(record)

        for key in record:
            assert enriched[key] == record[key]
        assert enriched["new_key"] == "new_value"
