"""Task management module for thegent."""

from thegent.task.migrate import migrate_legacy_task_to_yaml_frontmatter, migrate_work_stream_to_tasks
from thegent.task.parser import parse_legacy_task, parse_task_file, parse_yaml_frontmatter
from thegent.task.sync import WorkStreamSync
from thegent.task.types import Task, TaskMetadata, TaskOutput, TaskStep
from thegent.task.validator import TaskValidator, ValidationResult, validate_task, validate_task_file

__all__ = [
    "Task",
    "TaskMetadata",
    "TaskOutput",
    "TaskStep",
    "TaskValidator",
    "ValidationResult",
    "WorkStreamSync",
    "migrate_legacy_task_to_yaml_frontmatter",
    "migrate_work_stream_to_tasks",
    "parse_legacy_task",
    "parse_task_file",
    "parse_yaml_frontmatter",
    "validate_task",
    "validate_task_file",
]
