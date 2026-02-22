"""Local Tag Taxonomy Validator for workstream tags.

Enforces a controlled vocabulary of allowed tags and validates
against the taxonomy.

# @trace WL-288
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TaxonomyViolation:
    """Represents a single taxonomy violation.

    Attributes:
        tag: The tag that violated the taxonomy.
        wl_id: The workstream item identifier where violation occurred.
        reason: Human-readable reason for the violation.
    """

    tag: str
    wl_id: str
    reason: str


class TagTaxonomyValidator:
    """Validates tags against a controlled vocabulary (taxonomy).

    Maintains an allowed set of tags and validates items against it.
    """

    def __init__(self, allowed_tags: list[str]) -> None:
        """Initialize the validator with allowed tags.

        Args:
            allowed_tags: List of tags that are allowed.

        Raises:
            ValueError: If allowed_tags is not a list or is empty.
        """
        if not isinstance(allowed_tags, list):
            raise ValueError("allowed_tags must be a list")

        if not allowed_tags:
            raise ValueError("allowed_tags cannot be empty")

        self._allowed_tags = set(allowed_tags)

    def validate(self, wl_id: str, tags: list[str]) -> list[TaxonomyViolation]:
        """Validate tags against the taxonomy.

        Args:
            wl_id: The workstream item identifier.
            tags: List of tags to validate.

        Returns:
            List of TaxonomyViolation objects (empty if valid).

        Raises:
            ValueError: If wl_id is empty or tags is not a list.
        """
        if not wl_id:
            raise ValueError("wl_id cannot be empty")

        if not isinstance(tags, list):
            raise ValueError("tags must be a list")

        violations = []

        for tag in tags:
            if tag not in self._allowed_tags:
                violations.append(
                    TaxonomyViolation(
                        tag=tag,
                        wl_id=wl_id,
                        reason=f"Tag '{tag}' is not in the allowed taxonomy",
                    )
                )

        return violations

    def is_valid(self, wl_id: str, tags: list[str]) -> bool:
        """Check if tags are all valid according to taxonomy.

        Args:
            wl_id: The workstream item identifier.
            tags: List of tags to validate.

        Returns:
            True if all tags are in the taxonomy, False otherwise.

        Raises:
            ValueError: If wl_id is empty or tags is not a list.
        """
        violations = self.validate(wl_id, tags)
        return len(violations) == 0

    def add_allowed(self, tag: str) -> None:
        """Add a tag to the allowed set.

        Args:
            tag: The tag to add.

        Raises:
            ValueError: If tag is empty.
        """
        if not tag:
            raise ValueError("tag cannot be empty")

        self._allowed_tags.add(tag)

    def list_allowed(self) -> list[str]:
        """Return the list of all allowed tags.

        Returns:
            Sorted list of allowed tags.
        """
        return sorted(self._allowed_tags)
