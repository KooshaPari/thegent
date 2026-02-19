"""
Comprehensive Task Management System

Manages all tasks for completing research, ideas, and projects at mature level.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class TaskStatus(Enum):
    """Task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


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


@dataclass
class Task:
    """Individual task."""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    maturity: TaskMaturity = TaskMaturity.MATURE

    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)

    # Project context
    project_path: Path | None = None
    category: str = "general"
    tags: set[str] = field(default_factory=set)

    # Governance requirements
    requires_governance: bool = False
    requires_quality_matrix: bool = False
    requires_audit: bool = False

    # Completion criteria
    acceptance_criteria: list[str] = field(default_factory=list)
    definition_of_done: list[str] = field(default_factory=list)

    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None

    # Metadata
    assignee: str | None = None
    notes: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)

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
            "project_path": str(self.project_path) if self.project_path else None,
            "category": self.category,
            "tags": list(self.tags),
            "requires_governance": self.requires_governance,
            "requires_quality_matrix": self.requires_quality_matrix,
            "requires_audit": self.requires_audit,
            "acceptance_criteria": self.acceptance_criteria,
            "definition_of_done": self.definition_of_done,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "assignee": self.assignee,
            "notes": self.notes,
            "links": self.links,
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
            project_path=Path(data["project_path"]) if data.get("project_path") else None,
            category=data.get("category", "general"),
            tags=set(data.get("tags", [])),
            requires_governance=data.get("requires_governance", False),
            requires_quality_matrix=data.get("requires_quality_matrix", False),
            requires_audit=data.get("requires_audit", False),
            acceptance_criteria=data.get("acceptance_criteria", []),
            definition_of_done=data.get("definition_of_done", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            estimated_hours=data.get("estimated_hours"),
            actual_hours=data.get("actual_hours"),
            assignee=data.get("assignee"),
            notes=data.get("notes", []),
            links=data.get("links", []),
        )
        return task


class TaskManager:
    """Manages tasks across all projects."""

    def __init__(self, tasks_file: Path | None = None) -> None:
        if tasks_file is None:
            tasks_file = Path.home() / ".thegent" / "tasks.json"
        self.tasks_file = Path(tasks_file)
        self.tasks: dict[str, Task] = {}
        self._load()

    def _load(self):
        """Load tasks from file."""
        if self.tasks_file.exists():
            with open(self.tasks_file) as f:
                data = json.load(f)
                self.tasks = {
                    task_id: Task.from_dict(task_data) for task_id, task_data in data.get("tasks", {}).items()
                }

    def save(self):
        """Save tasks to file."""
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_file, "w") as f:
            json.dump(
                {
                    "version": "1.0",
                    "updated_at": datetime.now().isoformat(),
                    "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                },
                f,
                indent=2,
            )

    def add_task(self, task: Task):
        """Add a task."""
        self.tasks[task.id] = task
        self.save()

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Get tasks by status."""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_project(self, project_path: Path) -> list[Task]:
        """Get tasks for a project."""
        return [task for task in self.tasks.values() if task.project_path and task.project_path == project_path]

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

            if deps_met:
                ready.append(task)

        return sorted(
            ready,
            key=lambda t: (
                t.priority.value == TaskPriority.CRITICAL.value,
                t.priority.value == TaskPriority.HIGH.value,
            ),
            reverse=True,
        )

    def update_task_status(self, task_id: str, status: TaskStatus):
        """Update task status."""
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.now()
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
            self.save()

    def generate_governance_tasks(self, project_path: Path, project_name: str) -> list[Task]:
        """Generate governance setup tasks for a project."""
        tasks = []

        # Task 1: Basic structure
        tasks.append(
            Task(
                id=f"gov-{project_name}-structure",
                title=f"Set up basic project structure for {project_name}",
                description="Create basic directory structure, README, LICENSE, and docs/",
                priority=TaskPriority.HIGH,
                project_path=project_path,
                category="governance",
                tags={"governance", "structure", "setup"},
                requires_governance=False,  # This task creates it
                acceptance_criteria=[
                    "README.md exists and is comprehensive",
                    "LICENSE file exists",
                    "docs/ directory created",
                    "tests/ directory created",
                    "governance/ directory created",
                ],
                definition_of_done=[
                    "All directories created",
                    "All basic files created",
                    "Structure verified",
                ],
                estimated_hours=2.0,
            )
        )

        # Task 2: Governance framework
        tasks.append(
            Task(
                id=f"gov-{project_name}-framework",
                title=f"Set up governance framework for {project_name}",
                description="Create quality gates, audit config, and policy files",
                priority=TaskPriority.HIGH,
                project_path=project_path,
                category="governance",
                tags={"governance", "framework", "quality"},
                depends_on=[f"gov-{project_name}-structure"],
                requires_governance=True,
                acceptance_criteria=[
                    "quality-gates.yaml created",
                    "audit-config.yaml created",
                    "Governance structure verified",
                ],
                definition_of_done=[
                    "All governance files created",
                    "Configuration validated",
                ],
                estimated_hours=3.0,
            )
        )

        # Task 3: Quality matrix
        tasks.append(
            Task(
                id=f"gov-{project_name}-quality",
                title=f"Create quality matrix for {project_name}",
                description="Assess and create quality matrix with all categories",
                priority=TaskPriority.MEDIUM,
                project_path=project_path,
                category="governance",
                tags={"governance", "quality", "matrix"},
                depends_on=[f"gov-{project_name}-framework"],
                requires_quality_matrix=True,
                acceptance_criteria=[
                    "Quality matrix created",
                    "All categories assessed",
                    "Score calculated",
                    "Improvement plan created",
                ],
                definition_of_done=[
                    "Matrix saved",
                    "Report generated",
                ],
                estimated_hours=4.0,
            )
        )

        # Task 4: Audit setup
        tasks.append(
            Task(
                id=f"gov-{project_name}-audit",
                title=f"Set up audit framework for {project_name}",
                description="Configure and run initial audits",
                priority=TaskPriority.MEDIUM,
                project_path=project_path,
                category="governance",
                tags={"governance", "audit"},
                depends_on=[f"gov-{project_name}-quality"],
                requires_audit=True,
                acceptance_criteria=[
                    "Audit framework configured",
                    "Initial audit completed",
                    "Issues documented",
                ],
                definition_of_done=[
                    "Audit report generated",
                    "Issues tracked",
                ],
                estimated_hours=3.0,
            )
        )

        return tasks

    def generate_completion_tasks(self, research_files: list[Path]) -> list[Task]:
        """Generate tasks for completing all research/ideas."""
        tasks = []

        for research_file in research_files:
            if not research_file.exists():
                continue

            # Analyze file to determine tasks needed
            content = research_file.read_text()
            file_name = research_file.stem

            # Create task for completing this research
            task = Task(
                id=f"complete-{file_name}",
                title=f"Complete research/implementation: {file_name}",
                description=f"Complete all items in {research_file.name} at mature level",
                priority=TaskPriority.HIGH,
                maturity=TaskMaturity.MATURE,
                project_path=research_file.parent,
                category="research",
                tags={"research", "completion", "mature"},
                requires_governance=True,
                requires_quality_matrix=True,
                requires_audit=True,
                acceptance_criteria=[
                    "All research items completed",
                    "Implementation at mature level (not MVP)",
                    "Documentation complete",
                    "Tests written",
                    "Quality gates passing",
                ],
                definition_of_done=[
                    "All acceptance criteria met",
                    "Code reviewed",
                    "Documentation reviewed",
                    "Quality matrix passing",
                    "Audit passed",
                ],
                estimated_hours=16.0,  # Default estimate
                links=[str(research_file)],
            )
            tasks.append(task)

        return tasks
