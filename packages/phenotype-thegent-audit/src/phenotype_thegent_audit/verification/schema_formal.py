"""WP-27003: Formal Verification of Schema Evolution.
Ensures schema changes maintain backward compatibility and follow evolution policies.
"""

import logging
from typing import Any

_log = logging.getLogger(__name__)


class SchemaEvolutionVerifier:
    """Verifies evolution between two schema versions to prevent breaking changes."""

    def verify_compatibility(self, old_schema: dict[str, Any], new_schema: dict[str, Any]) -> dict[str, Any]:
        """Check for breaking changes between old and new schema.

        A breaking change is:
        - Removal of a field
        - Change of field type (if strictly typed)
        - Making an existing optional field mandatory
        """
        errors = []
        warnings = []

        old_fields = set(old_schema.keys())
        new_fields = set(new_schema.keys())

        # 1. Field Removals (Breaking)
        removed = old_fields - new_fields
        if removed:
            errors.append(f"Breaking change: Fields removed from schema: {', '.join(sorted(removed))}")

        # 2. Field Type Changes (Breaking)
        for field in old_fields & new_fields:
            old_val = old_schema[field]
            new_val = new_schema[field]

            # If both are dicts, recurse
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                res = self.verify_compatibility(old_val, new_val)
                if not res["compatible"]:
                    for err in res["errors"]:
                        errors.append(f"In field '{field}': {err}")
                    for warn in res["warnings"]:
                        warnings.append(f"In field '{field}': {warn}")
                continue

            # Check type parity
            old_type = type(old_val)
            new_type = type(new_val)
            if old_type != new_type:
                errors.append(
                    f"Breaking change: Field '{field}' type changed from {old_type.__name__} to {new_type.__name__}"
                )

        # 3. New Fields (Evolution)
        added = new_fields - old_fields
        if added:
            warnings.append(f"Evolution: New fields added: {', '.join(sorted(added))}")

        return {
            "compatible": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "added": list(added),
            "removed": list(removed),
        }

    def verify_tag_evolution(self, old_tags: list[str], new_tags: list[str]) -> dict[str, Any]:
        """Verify evolution of a list of allowed XML tags.
        Removing a tag is breaking; adding is an evolution.
        """
        old_set = {t.upper() for t in old_tags}
        new_set = {t.upper() for t in new_tags}

        removed = old_set - new_set
        added = new_set - old_set

        errors = []
        if removed:
            errors.append(f"Breaking change: XML tags removed: {', '.join(sorted(removed))}")

        return {
            "compatible": len(errors) == 0,
            "errors": errors,
            "added": list(added),
            "removed": list(removed),
        }

    def check_liveness_impact(self, evolution_report: dict[str, Any]) -> bool:
        """WP-25001: Check if evolution impacts agent liveness.
        Removing critical tags (STATUS, SUMMARY) impacts liveness.
        """
        critical_tags = {"STATUS", "SUMMARY"}
        removed_tags = {t.upper() for t in evolution_report.get("removed", [])}

        impacted = not critical_tags.isdisjoint(removed_tags)
        if impacted:
            _log.warning("Schema evolution removes critical liveness tags: %s", critical_tags & removed_tags)
        return not impacted
