"""WL header normalization for consistent record formatting.

# @trace WL-184
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NormalizationResult:
    """Result of normalizing a WL record.

    Attributes:
        wl_id: The work stream item identifier.
        original: Original record state.
        normalized: Normalized record state.
        changed: Whether any field was changed.
    """

    wl_id: str
    original: str
    normalized: str
    changed: bool


class WLHeaderNormalizer:
    """Normalizer for WL record headers."""

    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalize a title field.

        - Strips extra whitespace
        - Ensures title-case for WL IDs (e.g., "wl-123: foo bar" → "WL-123: Foo Bar")
        - Strips leading/trailing punctuation

        Args:
            title: The title to normalize.

        Returns:
            The normalized title.
        """
        # Strip whitespace
        normalized = title.strip()

        # Check if title starts with WL ID pattern (e.g., "wl-123" or "WL-123")
        wl_prefix = ""
        rest = normalized

        if normalized.lower().startswith("wl-"):
            # Find where the WL ID ends
            parts = normalized.split(":", 1)
            if len(parts) == 2:
                wl_prefix = parts[0].upper()  # Uppercase WL ID
                rest = parts[1].strip()
            else:
                wl_prefix = parts[0].upper()
                rest = ""

        # Title-case the rest of the title (capitalize first letter of each word)
        if rest:
            rest = " ".join(word.capitalize() for word in rest.split())

        # Combine and strip punctuation
        if wl_prefix and rest:
            result = f"{wl_prefix}: {rest}"
        elif wl_prefix:
            result = wl_prefix
        else:
            result = rest

        return result.rstrip(".,;:")

    @staticmethod
    def normalize_status(status: str) -> str:
        """Normalize a status field.

        - Uppercases known statuses (backlog/in_progress/completed/blocked)
        - Returns uppercased for unknown statuses

        Args:
            status: The status to normalize.

        Returns:
            The normalized status.
        """
        status = status.strip()
        lower_status = status.lower()

        known_statuses = {
            "backlog": "BACKLOG",
            "in_progress": "IN_PROGRESS",
            "completed": "COMPLETED",
            "blocked": "BLOCKED",
        }

        if lower_status in known_statuses:
            return known_statuses[lower_status]

        return status.upper()

    @staticmethod
    def normalize_priority(priority: str) -> str:
        """Normalize a priority field.

        - Uppercases P0-P9 patterns
        - Returns stripped and uppercased for other patterns

        Args:
            priority: The priority to normalize.

        Returns:
            The normalized priority.
        """
        priority = priority.strip()

        # Check for P0-P9 pattern
        if len(priority) == 2 and priority[0].lower() == "p" and priority[1].isdigit():
            return priority.upper()

        # For other patterns, return stripped and uppercase
        return priority.upper()

    @staticmethod
    def normalize_record(record: dict) -> NormalizationResult:
        """Normalize all fields in a WL record.

        Args:
            record: Dictionary with keys: wl_id, title, status, priority

        Returns:
            NormalizationResult with original, normalized states and change indicator.

        Raises:
            KeyError: If required fields are missing from record.
        """
        required_fields = {"wl_id", "title", "status", "priority"}
        if not required_fields.issubset(record.keys()):
            raise KeyError(f"Record missing required fields: {required_fields}")

        wl_id = record["wl_id"]

        # Store original as string representation
        original_str = str(record)

        # Normalize each field
        normalized_record = record.copy()
        normalized_record["title"] = WLHeaderNormalizer.normalize_title(record["title"])
        normalized_record["status"] = WLHeaderNormalizer.normalize_status(record["status"])
        normalized_record["priority"] = WLHeaderNormalizer.normalize_priority(record["priority"])

        # Determine if anything changed
        changed = normalized_record != record

        # Store normalized as string representation
        normalized_str = str(normalized_record)

        return NormalizationResult(
            wl_id=wl_id,
            original=original_str,
            normalized=normalized_str,
            changed=changed,
        )
