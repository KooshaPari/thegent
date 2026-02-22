"""Implement code annotation component for documentation."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CodeAnnotationGenerator:
    """Generate code annotations for documentation."""

    REQUIRED_REFLECTION_KEYS = (
        "schema",
        "wl_id",
        "connector",
        "direction",
        "decision",
        "mutation_id",
        "timestamp",
    )

    def __init__(self, annotation_format: str = "yaml") -> None:
        self.annotation_format = annotation_format

    def parse_annotations(self, code: str) -> list[dict[str, Any]]:
        """Parse annotations from code (comments like # @annotation).

        Args:
            code: Source code

        Returns:
            List of annotations
        """
        import re

        # Simple regex for # @annotation: key=value
        pattern = re.compile(r"#\s*@annotation:\s*(?P<key>[^=]+)=(?P<value>.+)")
        annotations = []
        for match in pattern.finditer(code):
            annotations.append(
                {
                    "key": match.group("key").strip(),
                    "value": match.group("value").strip(),
                }
            )
        return annotations

    def generate_annotation_component(self, annotations: list[dict[str, Any]]) -> str:
        """Generate documentation component from annotations.

        Args:
            annotations: List of parsed annotations

        Returns:
            Formatted documentation component
        """
        if not annotations:
            return ""

        lines = ["## Annotations"]
        for ann in annotations:
            lines.append(f"- **{ann['key']}**: {ann['value']}")
        return "\n".join(lines)

    def format_reflection_annotation(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Normalize a remote->local annotation payload to canonical schema/order."""
        normalized: dict[str, Any] = {}
        for key in self.REQUIRED_REFLECTION_KEYS:
            if key not in payload:
                raise ValueError(f"missing required annotation key: {key}")
            normalized[key] = payload[key]
        for key, value in payload.items():
            if key in normalized:
                continue
            normalized[key] = value
        return normalized
