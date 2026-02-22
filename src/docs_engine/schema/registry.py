"""Schema registry mapping DocType to its Pydantic model class.

# @trace FR-DOCS-001
"""

from __future__ import annotations

from .base import DocFrontmatter, DocType

SCHEMA_REGISTRY: dict[DocType, type[DocFrontmatter]] = dict.fromkeys(DocType, DocFrontmatter)
