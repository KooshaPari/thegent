"""
Work Stream Integration

Integrates governance, quality matrices, and audits into the work stream.
"""

import orjson as json
from datetime import datetime
from pathlib import Path

from .project_setup import ProjectGovernanceSetup, ProjectStructure
from .quality_matrix import QualityMatrix, QualityMatrixBuilder
from .task_manager import Task, TaskManager, TaskPriority


class WorkStreamIntegrator:
    """Integrates governance into work stream."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        self.task_manager = TaskManager()
        self.governance_setups: dict[Path, ProjectGovernanceSetup] = {}
        self.quality_matrices: dict[Path, QualityMatrix] = {}

    def audit_all_projects(self, project_paths: list[Path]) -> dict[Path, ProjectStructure]:
        """Audit all projects and return structure assessments."""
        assessments = {}

        for project_path in project_paths:
            setup = ProjectGovernanceSetup(project_path)
            structure = setup.analyze()
            assessments[project_path] = structure
            self.governance_setups[project_path] = setup

        return assessments

    def setup_governance_for_projects(self, project_paths: list[Path]):
        """Set up governance for projects that need it."""
        for project_path in project_paths:
            setup = ProjectGovernanceSetup(project_path)
            structure = setup.analyze()

            if structure.governance_level.value == "none":
                # Generate and add governance setup tasks
                project_name = project_path.name
                tasks = self.task_manager.generate_governance_tasks(project_path, project_name)
                for task in tasks:
                    self.task_manager.add_task(task)

                # Optionally auto-setup basic structure
                setup.setup_basic_structure()

    def create_quality_matrices(self, project_paths: list[Path]):
        """Create quality matrices for all projects."""
        for project_path in project_paths:
            builder = QualityMatrixBuilder(project_path)
            matrix = builder.build()
            self.quality_matrices[project_path] = matrix

            # Save matrix
            output_path = project_path / "governance" / "quality-matrix.json"
            matrix.save(output_path)

    def generate_completion_plan(self, research_files: list[Path]) -> list[Task]:
        """Generate comprehensive completion plan for all research/ideas."""
        tasks = []

        # Generate tasks for each research file
        completion_tasks = self.task_manager.generate_completion_tasks(research_files)
        for task in completion_tasks:
            self.task_manager.add_task(task)
            tasks.append(task)

        return tasks

    def create_work_stream_plan(self, projects: list[Path], research_files: list[Path]) -> dict:
        """Create comprehensive work stream plan."""

        # Phase 1: Governance Setup
        governance_tasks = []
        for project_path in projects:
            project_name = project_path.name
            tasks = self.task_manager.generate_governance_tasks(project_path, project_name)
            governance_tasks.extend(tasks)

        # Phase 2: Quality Assessment
        quality_tasks = []
        for project_path in projects:
            task = Task(
                id=f"quality-{project_path.name}",
                title=f"Create quality matrix for {project_path.name}",
                description="Assess project quality and create improvement plan",
                priority=TaskPriority.HIGH,
                project_path=project_path,
                category="quality",
                tags={"quality", "matrix", "assessment"},
                depends_on=[f"gov-{project_path.name}-framework"],
                requires_quality_matrix=True,
                estimated_hours=4.0,
            )
            quality_tasks.append(task)
            self.task_manager.add_task(task)

        # Phase 3: Audit Setup
        audit_tasks = []
        for project_path in projects:
            task = Task(
                id=f"audit-{project_path.name}",
                title=f"Set up audit framework for {project_path.name}",
                description="Configure and run initial audits",
                priority=TaskPriority.MEDIUM,
                project_path=project_path,
                category="audit",
                tags={"audit", "compliance"},
                depends_on=[f"quality-{project_path.name}"],
                requires_audit=True,
                estimated_hours=3.0,
            )
            audit_tasks.append(task)
            self.task_manager.add_task(task)

        # Phase 4: Research Completion
        research_tasks = self.generate_completion_plan(research_files)

        # Create plan document
        plan = {
            "created_at": datetime.now().isoformat(),
            "phases": {
                "phase_1_governance_setup": {
                    "name": "Governance Setup",
                    "description": "Set up governance for all projects",
                    "tasks": [t.id for t in governance_tasks],
                    "estimated_hours": sum(t.estimated_hours or 0 for t in governance_tasks),
                },
                "phase_2_quality_assessment": {
                    "name": "Quality Assessment",
                    "description": "Create quality matrices for all projects",
                    "tasks": [t.id for t in quality_tasks],
                    "estimated_hours": sum(t.estimated_hours or 0 for t in quality_tasks),
                },
                "phase_3_audit_setup": {
                    "name": "Audit Setup",
                    "description": "Set up audit frameworks",
                    "tasks": [t.id for t in audit_tasks],
                    "estimated_hours": sum(t.estimated_hours or 0 for t in audit_tasks),
                },
                "phase_4_research_completion": {
                    "name": "Research Completion",
                    "description": "Complete all research/ideas at mature level",
                    "tasks": [t.id for t in research_tasks],
                    "estimated_hours": sum(t.estimated_hours or 0 for t in research_tasks),
                },
            },
            "total_tasks": len(governance_tasks) + len(quality_tasks) + len(audit_tasks) + len(research_tasks),
            "total_estimated_hours": sum(
                sum(t.estimated_hours or 0 for t in task_list)
                for task_list in [governance_tasks, quality_tasks, audit_tasks, research_tasks]
            ),
        }

        return plan

    def save_work_stream_plan(self, plan: dict, output_path: Path):
        """Save work stream plan to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(plan, f, indent=2)

    def get_next_actions(self) -> list[Task]:
        """Get next actions from work stream."""
        return self.task_manager.get_ready_tasks()
