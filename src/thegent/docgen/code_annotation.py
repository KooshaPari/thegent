"""Implement code annotation component for documentation."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class CodeAnnotationGenerator:
    """Generate code annotations for documentation."""

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
