"""Package: thegent.task"""

from thegent.task.parser import (
    parse_yaml_frontmatter,
    parse_task_file,
    detect_task_format,
    extract_markdown_sections,
    parse_legacy_task,
)
from thegent.task.validator import (
    ValidationError,
    ValidationResult,
    validate_task,
    validate_task_file,
)

__all__ = [
    "parse_yaml_frontmatter",
    "parse_task_file",
    "detect_task_format",
    "extract_markdown_sections",
    "parse_legacy_task",
    "ValidationError",
    "ValidationResult",
    "validate_task",
    "validate_task_file",
]
