"""
Enhanced Task Management System

Expanded with validation, conflict detection, progress tracking, and reporting.
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DEFERRED = "deferred"


class TaskPriority(Enum):
    """Task priority."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskMaturity(Enum):
    """Task maturity level."""

    MVP = "mvp"
    STANDARD = "standard"
    MATURE = "mature"


class TaskConflict(Enum):
    """Task conflict types."""

    DEPENDENCY_CYCLE = "dependency_cycle"
    RESOURCE_CONFLICT = "resource_conflict"
    TIMELINE_CONFLICT = "timeline_conflict"
    DUPLICATE = "duplicate"
    NONE = "none"


@dataclass
class Task:
    """Enhanced task with validation and tracking."""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    maturity: TaskMaturity = TaskMaturity.MATURE

    # Dependencies (enhanced)
    depends_on: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    related_tasks: list[str] = field(default_factory=list)

    # Project context (enhanced)
    project_path: Path | None = None
    category: str = "general"
    tags: set[str] = field(default_factory=set)
    epic: str | None = None
    sprint: str | None = None

    # Governance requirements (enhanced)
    requires_governance: bool = False
    requires_quality_matrix: bool = False
    requires_audit: bool = False
    requires_review: bool = False
    requires_approval: bool = False

    # Completion criteria (enhanced)
    acceptance_criteria: list[str] = field(default_factory=list)
    definition_of_done: list[str] = field(default_factory=list)
    test_requirements: list[str] = field(default_factory=list)
    documentation_requirements: list[str] = field(default_factory=list)

    # Tracking (enhanced)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    due_date: datetime | None = None

    # Estimates (enhanced)
    estimated_hours: float | None = None
    estimated_points: int | None = None
    actual_hours: float | None = None
    remaining_hours: float | None = None

    # Progress (enhanced)
    progress_percentage: float = 0.0
    checkpoints: list[dict] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)

    # Metadata (enhanced)
    assignee: str | None = None
    reviewer: str | None = None
    approver: str | None = None
    notes: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)

    # Quality metrics
    quality_score: float | None = None
    review_feedback: list[str] = field(default_factory=list)

    # Validation
    is_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)
    conflict_type: TaskConflict = TaskConflict.NONE

    def validate(self, all_tasks: dict[str, "Task"]) -> tuple[bool, list[str]]:
        """Validate task and return (is_valid, errors)."""
        errors = []

        # Check ID uniqueness (would be checked at manager level)
        if not self.id:
            errors.append("Task ID is required")

        # Check title
        if not self.title or len(self.title) < 3:
            errors.append("Task title must be at least 3 characters")

        # Check dependencies exist
        for dep_id in self.depends_on:
            if dep_id not in all_tasks:
                errors.append(f"Dependency '{dep_id}' does not exist")

        # Check for circular dependencies
        if self._has_circular_dependency(self.id, self.depends_on, all_tasks, set()):
            errors.append("Circular dependency detected")
            self.conflict_type = TaskConflict.DEPENDENCY_CYCLE

        # Check dates
        if self.due_date and self.created_at and self.due_date < self.created_at:
            errors.append("Due date cannot be before creation date")

        if self.completed_at and self.started_at and self.completed_at < self.started_at:
            errors.append("Completion date cannot be before start date")

        # Check estimates
        if self.estimated_hours and self.estimated_hours < 0:
            errors.append("Estimated hours cannot be negative")

        if self.actual_hours and self.actual_hours < 0:
            errors.append("Actual hours cannot be negative")

        # Check progress
        if self.progress_percentage < 0 or self.progress_percentage > 100:
            errors.append("Progress percentage must be between 0 and 100")

        self.is_valid = len(errors) == 0
        self.validation_errors = errors
        return self.is_valid, errors

    def _has_circular_dependency(
        self, task_id: str, deps: list[str], all_tasks: dict[str, "Task"], visited: set[str]
    ) -> bool:
        """Check for circular dependencies."""
        if task_id in visited:
            return True

        visited.add(task_id)
        for dep_id in deps:
            if dep_id in all_tasks:
                dep_task = all_tasks[dep_id]
                if self._has_circular_dependency(dep_id, dep_task.depends_on, all_tasks, visited.copy()):
                    return True

        return False

    def calculate_progress(self):
        """Calculate progress percentage."""
        if self.status == TaskStatus.COMPLETED:
            self.progress_percentage = 100.0
        elif self.status in (TaskStatus.CANCELLED, TaskStatus.PENDING):
            self.progress_percentage = 0.0
        elif self.checkpoints:
            # Calculate based on checkpoints
            completed = sum(1 for cp in self.checkpoints if cp.get("completed", False))
            total = len(self.checkpoints)
            self.progress_percentage = (completed / total) * 100 if total > 0 else 0.0
        elif self.estimated_hours and self.actual_hours:
            # Estimate based on time
            if self.remaining_hours is not None:
                total = self.estimated_hours
                remaining = self.remaining_hours
                self.progress_percentage = max(0.0, min(100.0, ((total - remaining) / total) * 100))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "maturity": self.maturity.value,
            "depends_on": self.depends_on,
            "blocks": self.blocks,
            "related_tasks": self.related_tasks,
            "project_path": str(self.project_path) if self.project_path else None,
            "category": self.category,
            "tags": list(self.tags),
            "epic": self.epic,
            "sprint": self.sprint,
            "requires_governance": self.requires_governance,
            "requires_quality_matrix": self.requires_quality_matrix,
            "requires_audit": self.requires_audit,
            "requires_review": self.requires_review,
            "requires_approval": self.requires_approval,
            "acceptance_criteria": self.acceptance_criteria,
            "definition_of_done": self.definition_of_done,
            "test_requirements": self.test_requirements,
            "documentation_requirements": self.documentation_requirements,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "estimated_hours": self.estimated_hours,
            "estimated_points": self.estimated_points,
            "actual_hours": self.actual_hours,
            "remaining_hours": self.remaining_hours,
            "progress_percentage": self.progress_percentage,
            "checkpoints": self.checkpoints,
            "blockers": self.blockers,
            "assignee": self.assignee,
            "reviewer": self.reviewer,
            "approver": self.approver,
            "notes": self.notes,
            "links": self.links,
            "attachments": self.attachments,
            "quality_score": self.quality_score,
            "review_feedback": self.review_feedback,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "conflict_type": self.conflict_type.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create from dictionary."""
        task = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            status=TaskStatus(data["status"]),
            priority=TaskPriority(data["priority"]),
            maturity=TaskMaturity(data["maturity"]),
            depends_on=data.get("depends_on", []),
            blocks=data.get("blocks", []),
            related_tasks=data.get("related_tasks", []),
            project_path=Path(data["project_path"]) if data.get("project_path") else None,
            category=data.get("category", "general"),
            tags=set(data.get("tags", [])),
            epic=data.get("epic"),
            sprint=data.get("sprint"),
            requires_governance=data.get("requires_governance", False),
            requires_quality_matrix=data.get("requires_quality_matrix", False),
            requires_audit=data.get("requires_audit", False),
            requires_review=data.get("requires_review", False),
            requires_approval=data.get("requires_approval", False),
            acceptance_criteria=data.get("acceptance_criteria", []),
            definition_of_done=data.get("definition_of_done", []),
            test_requirements=data.get("test_requirements", []),
            documentation_requirements=data.get("documentation_requirements", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            estimated_hours=data.get("estimated_hours"),
            estimated_points=data.get("estimated_points"),
            actual_hours=data.get("actual_hours"),
            remaining_hours=data.get("remaining_hours"),
            progress_percentage=data.get("progress_percentage", 0.0),
            checkpoints=data.get("checkpoints", []),
            blockers=data.get("blockers", []),
            assignee=data.get("assignee"),
            reviewer=data.get("reviewer"),
            approver=data.get("approver"),
            notes=data.get("notes", []),
            links=data.get("links", []),
            attachments=data.get("attachments", []),
            quality_score=data.get("quality_score"),
            review_feedback=data.get("review_feedback", []),
            is_valid=data.get("is_valid", True),
            validation_errors=data.get("validation_errors", []),
            conflict_type=TaskConflict(data.get("conflict_type", "none")),
        )
        return task


class TaskManagerEnhanced:
    """Enhanced task manager with validation, conflict detection, and reporting."""

    def __init__(self, tasks_file: Path | None = None) -> None:
        if tasks_file is None:
            tasks_file = Path.home() / ".thegent" / "tasks.json"
        self.tasks_file = Path(tasks_file)
        self.tasks: dict[str, Task] = {}
        self._validation_cache: dict[str, bool] = {}
        self._load()
        self._validate_all()

    def _load(self):
        """Load tasks from file."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file) as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: Task.from_dict(task_data) for task_id, task_data in data.get("tasks", {}).items()
                    }
            except Exception as e:
                logger.error(f"Error loading tasks: {e}")
                self.tasks = {}

    def save(self):
        """Save tasks to file."""
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_file, "w") as f:
            json.dump(
                {
                    "version": "2.0",
                    "updated_at": datetime.now(tz=UTC).isoformat(),
                    "total_tasks": len(self.tasks),
                    "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                },
                f,
                indent=2,
            )

    def _validate_all(self):
        """Validate all tasks."""
        for task in self.tasks.values():
            task.validate(self.tasks)
            task.calculate_progress()

    def add_task(self, task: Task) -> tuple[bool, list[str]]:
        """Add a task with validation."""
        is_valid, errors = task.validate(self.tasks)

        if not is_valid:
            return False, errors

        # Check for duplicates
        duplicate = self._find_duplicate(task)
        if duplicate:
            task.conflict_type = TaskConflict.DUPLICATE
            return False, [f"Duplicate task found: {duplicate.id}"]

        self.tasks[task.id] = task
        self.save()
        return True, []

    def _find_duplicate(self, task: Task) -> Task | None:
        """Find duplicate tasks."""
        for existing_task in self.tasks.values():
            if existing_task.id == task.id:
                continue

            # Check title similarity
            if self._similarity_score(task.title, existing_task.title) > 0.8:
                return existing_task

            # Check description similarity
            if task.description and existing_task.description:
                if self._similarity_score(task.description, existing_task.description) > 0.7:
                    return existing_task

        return None

    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate simple similarity score."""
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Get tasks by status."""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_project(self, project_path: Path) -> list[Task]:
        """Get tasks for a project."""
        return [task for task in self.tasks.values() if task.project_path and task.project_path == project_path]

    def get_tasks_by_priority(self, priority: TaskPriority) -> list[Task]:
        """Get tasks by priority."""
        return [task for task in self.tasks.values() if task.priority == priority]

    def get_overdue_tasks(self) -> list[Task]:
        """Get overdue tasks."""
        now = datetime.now(tz=UTC)
        return [
            task
            for task in self.tasks.values()
            if task.due_date and task.due_date < now and task.status != TaskStatus.COMPLETED
        ]

    def get_ready_tasks(self) -> list[Task]:
        """Get tasks that are ready to start (dependencies met)."""
        ready = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            # Check dependencies
            deps_met = True
            for dep_id in task.depends_on:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    deps_met = False
                    break

            # Check blockers
            if task.blockers:
                deps_met = False

            if deps_met and task.is_valid:
                ready.append(task)

        return sorted(
            ready,
            key=lambda t: (
                t.priority.value == TaskPriority.CRITICAL.value,
                t.priority.value == TaskPriority.HIGH.value,
                t.due_date or datetime.max.replace(tzinfo=UTC),
            ),
            reverse=True,
        )

    def detect_conflicts(self) -> dict[str, list[Task]]:
        """Detect conflicts between tasks."""
        conflicts = defaultdict(list)

        for task in self.tasks.values():
            # Check dependency cycles
            if task.conflict_type == TaskConflict.DEPENDENCY_CYCLE:
                conflicts["dependency_cycles"].append(task)

            # Check resource conflicts (same assignee, overlapping dates)
            if task.assignee and task.started_at and task.due_date:
                for other_task in self.tasks.values():
                    if other_task.id == task.id:
                        continue
                    if other_task.assignee == task.assignee:
                        if (
                            other_task.started_at
                            and other_task.due_date
                            and not (other_task.due_date < task.started_at or other_task.started_at > task.due_date)
                        ):
                            conflicts["resource_conflicts"].append(task)
                            task.conflict_type = TaskConflict.RESOURCE_CONFLICT

        return dict(conflicts)

    def update_task_status(self, task_id: str, status: TaskStatus):
        """Update task status with validation."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        old_status = task.status
        task.status = status
        task.updated_at = datetime.now(tz=UTC)

        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.now(tz=UTC)
        elif status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now(tz=UTC)
            task.progress_percentage = 100.0

        task.calculate_progress()
        self.save()

    def get_statistics(self) -> dict:
        """Get comprehensive statistics."""
        total = len(self.tasks)
        by_status = defaultdict(int)
        by_priority = defaultdict(int)
        by_category = defaultdict(int)

        total_estimated_hours = 0.0
        total_actual_hours = 0.0
        completed_hours = 0.0

        for task in self.tasks.values():
            by_status[task.status.value] += 1
            by_priority[task.priority.value] += 1
            by_category[task.category] += 1

            if task.estimated_hours:
                total_estimated_hours += task.estimated_hours
            if task.actual_hours:
                total_actual_hours += task.actual_hours
                if task.status == TaskStatus.COMPLETED:
                    completed_hours += task.actual_hours

        overdue = len(self.get_overdue_tasks())
        ready = len(self.get_ready_tasks())
        conflicts = self.detect_conflicts()
        total_conflicts = sum(len(tasks) for tasks in conflicts.values())

        return {
            "total_tasks": total,
            "by_status": dict(by_status),
            "by_priority": dict(by_priority),
            "by_category": dict(by_category),
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours,
            "completed_hours": completed_hours,
            "overdue_tasks": overdue,
            "ready_tasks": ready,
            "conflicts": total_conflicts,
            "conflict_details": {k: len(v) for k, v in conflicts.items()},
            "average_progress": sum(t.progress_percentage for t in self.tasks.values()) / total if total > 0 else 0.0,
        }

    def generate_report(self) -> dict:
        """Generate comprehensive report."""
        stats = self.get_statistics()
        conflicts = self.detect_conflicts()
        ready_tasks = self.get_ready_tasks()
        overdue_tasks = self.get_overdue_tasks()

        return {
            "generated_at": datetime.now(tz=UTC).isoformat(),
            "statistics": stats,
            "conflicts": {k: [t.id for t in v] for k, v in conflicts.items()},
            "ready_tasks": [t.id for t in ready_tasks[:10]],
            "overdue_tasks": [t.id for t in overdue_tasks],
            "recommendations": self._generate_recommendations(stats, conflicts, overdue_tasks),
        }

    def _generate_recommendations(self, stats: dict, conflicts: dict, overdue_tasks: list[Task]) -> list[str]:
        """Generate recommendations."""
        recommendations = []

        if stats["overdue_tasks"] > 0:
            recommendations.append(f"Address {stats['overdue_tasks']} overdue tasks")

        if stats["conflicts"] > 0:
            recommendations.append(f"Resolve {stats['conflicts']} task conflicts")

        if stats["ready_tasks"] > 0:
            recommendations.append(f"Start {stats['ready_tasks']} ready tasks")

        completion_rate = (
            stats["completed_hours"] / stats["total_estimated_hours"] * 100 if stats["total_estimated_hours"] > 0 else 0
        )
        if completion_rate < 50:
            recommendations.append("Improve task completion rate")

        return recommendations
