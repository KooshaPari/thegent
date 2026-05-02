"""Schema base - STUB."""
"""Schema base - STUB."""
from enum import Enum
from typing import Any
from dataclasses import dataclass


class DocType(str, Enum):
    """Document types."""
    MARKDOWN = "markdown"
    RST = "rst"
    HTML = "html"
    IDEA = "idea"


class DocStatus(str, Enum):
    """Document status values."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"


@dataclass
class DocFrontmatter:
    """Frontmatter for documentation."""
    type: DocType = DocType.MARKDOWN
    status: str = ""
    date: str = ""
    title: str = ""
    layer: int = 0
    metadata: dict[str, Any] | None = None


@dataclass
class Schema:
    version: str
    fields: dict[str, Any]

    def validate(self, data, *args, **kwargs) -> bool:
        return True


__all__ = ["DocFrontmatter", "DocStatus", "DocType", "Schema"]
