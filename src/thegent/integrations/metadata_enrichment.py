"""Metadata Enrichment for workstream records.

WL-227: Metadata Enrichment
Applies enrichment rules to add metadata to workstream records.

# @trace WL-227
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EnrichmentRule:
    """Rule for enriching metadata on records."""

    key: str
    value: Any


class MetadataEnricher:
    """Enriches records with metadata based on configured rules."""

    def __init__(self) -> None:
        """Initialize the enricher with no rules."""
        self._rules: list[EnrichmentRule] = []

    def add_rule(self, key: str, value: Any) -> EnrichmentRule:
        """Add an enrichment rule.

        Args:
            key: The metadata key to add.
            value: The value to set for the key.

        Returns:
            The created EnrichmentRule.
        """
        rule = EnrichmentRule(key=key, value=value)
        self._rules.append(rule)
        return rule

    def enrich(self, record: dict[str, Any]) -> dict[str, Any]:
        """Apply enrichment rules to a single record.

        Only adds keys that are not already present in the record.

        Args:
            record: The record to enrich.

        Returns:
            A new enriched record.
        """
        enriched = dict(record)

        for rule in self._rules:
            if rule.key not in enriched:
                enriched[rule.key] = rule.value

        return enriched

    def enrich_all(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply enrichment rules to multiple records.

        Args:
            records: List of records to enrich.

        Returns:
            A new list of enriched records.
        """
        return [self.enrich(record) for record in records]

    def rules(self) -> list[EnrichmentRule]:
        """Get all configured enrichment rules.

        Returns:
            List of currently configured EnrichmentRule instances.
        """
        return list(self._rules)
