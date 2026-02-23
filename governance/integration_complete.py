#!/usr/bin/env python3
"""
Complete Governance Integration Script

Orchestrates the entire governance system:
1. Scans projects using document queue
2. Analyzes project structures
3. Sets up governance where needed
4. Creates quality matrices
5. Runs audits
6. Generates comprehensive reports
7. Creates task lists for completion
"""

import orjson as json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add thegent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from thegent.governance.audit_framework import AuditFramework
from thegent.governance.project_setup_enhanced import ProjectGovernanceSetupEnhanced
from thegent.governance.quality_matrix_enhanced import QualityMatrixBuilderEnhanced
from thegent.governance.task_manager_enhanced import Task, TaskManagerEnhanced, TaskMaturity, TaskPriority

from thegent.agents.document import DocumentAnalyzer, MarkdownScanner, ScanConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GovernanceIntegration:
    """Complete governance integration orchestrator."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        self.results: dict[str, any] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "projects_analyzed": [],
            "governance_setup": [],
            "quality_matrices": [],
            "audits": [],
            "tasks_created": [],
        }

    def run_complete_integration(
        self,
        scan_projects: bool = True,
        setup_governance: bool = True,
        assess_quality: bool = True,
        run_audits: bool = True,
        generate_tasks: bool = True,
    ):
        """Run complete governance integration."""
        logger.info("Starting complete governance integration...")

        # Step 1: Scan and identify projects
        if scan_projects:
            projects = self._scan_projects()
            self.results["projects_analyzed"] = [str(p) for p in projects]
        else:
            projects = self._load_existing_projects()

        logger.info(f"Found {len(projects)} projects")

        # Step 2: Analyze each project
        project_assessments = {}
        for project_path in projects:
            self._process_project(project_path, setup_governance, assess_quality, run_audits, project_assessments)

        # Step 6: Generate tasks for research completion
        if generate_tasks:
            research_files = self._find_research_files()
            tasks = self._generate_completion_tasks(research_files, projects)
            self.results["tasks_created"] = [t.id for t in tasks]

        # Step 7: Generate comprehensive report
        self._generate_master_report(project_assessments)

        self.results["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Governance integration complete!")

        return self.results

    def _process_project(
        self,
        project_path: Path,
        setup_governance: bool,
        assess_quality: bool,
        run_audits: bool,
        project_assessments: dict,
    ) -> None:
        """Process a single project."""
        try:
            logger.info(f"Analyzing: {project_path}")
            setup = ProjectGovernanceSetupEnhanced(project_path)
            structure = setup.analyze()
            project_assessments[project_path] = structure

            # Step 3: Set up governance if needed
            if setup_governance and structure.governance_level.value == "none":
                logger.info(f"Setting up governance for: {project_path}")
                setup.setup_basic_structure()
                self.results["governance_setup"].append(str(project_path))

            # Step 4: Create quality matrix
            if assess_quality:
                self._create_quality_matrix(project_path)

            # Step 5: Run audits
            if run_audits:
                self._run_project_audits(project_path)

        except Exception as e:
            logger.error(f"Error processing {project_path}: {e}")

    def _create_quality_matrix(self, project_path: Path) -> None:
        """Create quality matrix for a project."""
        try:
            logger.info(f"Creating quality matrix for: {project_path}")
            builder = QualityMatrixBuilderEnhanced(project_path)
            matrix = builder.build()
            matrix.save(project_path / "governance" / "quality-matrix.json")
            self.results["quality_matrices"].append(
                {
                    "project": str(project_path),
                    "score": matrix.overall_score,
                    "level": matrix.quality_level.value,
                }
            )
        except Exception as e:
            logger.warning(f"Error creating quality matrix: {e}")

    def _run_project_audits(self, project_path: Path) -> None:
        """Run audits for a project."""
        try:
            logger.info(f"Running audits for: {project_path}")
            framework = AuditFramework(project_path)
            framework.run_all_audits()
            framework.save_results()

            report = framework.generate_report()
            self.results["audits"].append(
                {
                    "project": str(project_path),
                    "total_findings": report["total_findings"],
                    "critical_findings": report["critical_findings"],
                }
            )
        except Exception as e:
            logger.warning(f"Error running audits: {e}")

    def _scan_projects(self) -> list[Path]:
        """Scan for projects using document queue."""
        config = ScanConfig(
            locations={
                "temp-PRODVERCEL": {"path": str(self.base_path.parent.parent), "recursive": True},
                "kush": {"path": str(self.base_path.parent.parent.parent / "kush"), "recursive": True},
            },
            min_date="2025-04",
        )

        scanner = MarkdownScanner(config)
        results = scanner.scan()

        # Extract unique project paths
        projects = set()
        analyzer = DocumentAnalyzer()

        for month_data in results.values():
            for files in month_data.values():
                for filepath in files:
                    path = Path(filepath)
                    parts = path.parts

                    # Extract project root
                    if "temp-PRODVERCEL" in parts:
                        idx = parts.index("temp-PRODVERCEL")
                        if idx + 2 < len(parts):
                            project_root = Path(*parts[: idx + 3])
                            if project_root.exists() and project_root.is_dir():
                                projects.add(project_root)

        return sorted(projects)

    def _load_existing_projects(self) -> list[Path]:
        """Load projects from existing audit."""
        audit_file = self.base_path / "docs" / "research" / "PROJECT_GOVERNANCE_AUDIT.json"
        if audit_file.exists():
            with open(audit_file) as f:
                data = json.load(f)
                # Convert project keys to paths
                projects = []
                for project_key in data.get("priority_projects", [])[:30]:
                    parts = project_key.split("/")
                    if len(parts) >= 2:
                        project_path = self.base_path.parent.parent / parts[0] / parts[1]
                        if project_path.exists():
                            projects.append(project_path)
                return projects
        return []

    def _find_research_files(self) -> list[Path]:
        """Find research files to complete."""
        research_files = []
        research_dirs = [
            self.base_path / "docs" / "research",
            self.base_path / "docs" / "plans",
        ]

        for research_dir in research_dirs:
            if research_dir.exists():
                for md_file in research_dir.glob("*.md"):
                    if "COMPLETE" not in md_file.name.upper():
                        research_files.append(md_file)

        return research_files

    def _generate_completion_tasks(self, research_files: list[Path], projects: list[Path]) -> list[Task]:
        """Generate tasks for completing research."""
        manager = TaskManagerEnhanced()
        tasks = []

        # Generate governance setup tasks for projects
        for project_path in projects:
            project_name = project_path.name
            gov_tasks = manager.generate_governance_tasks(project_path, project_name)
            for task in gov_tasks:
                success, _errors = manager.add_task(task)
                if success:
                    tasks.append(task)

        # Generate research completion tasks
        for research_file in research_files:
            task = Task(
                id=f"complete-{research_file.stem}",
                title=f"Complete research/implementation: {research_file.stem}",
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
                estimated_hours=16.0,
                links=[str(research_file)],
            )
            success, _errors = manager.add_task(task)
            if success:
                tasks.append(task)

        return tasks

    def _generate_master_report(self, project_assessments: dict[Path, any]):
        """Generate master governance report."""
        report_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_projects": len(project_assessments),
            "projects": {},
            "summary": {
                "governance_setup": len(self.results["governance_setup"]),
                "quality_matrices": len(self.results["quality_matrices"]),
                "audits": len(self.results["audits"]),
                "tasks_created": len(self.results["tasks_created"]),
            },
        }

        for project_path, structure in project_assessments.items():
            report_data["projects"][str(project_path)] = {
                "governance_level": structure.governance_level.value,
                "score": structure.calculate_score(),
                "project_type": structure.project_type.value,
                "missing_items_count": len(structure.missing_items),
            }

        # Save report
        report_file = self.base_path / "docs" / "research" / "GOVERNANCE_INTEGRATION_REPORT.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Master report saved to: {report_file}")


def main():
    """Main entry point."""
    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")

    integrator = GovernanceIntegration(base_path)
    results = integrator.run_complete_integration()

    return 0


if __name__ == "__main__":
    sys.exit(main())
