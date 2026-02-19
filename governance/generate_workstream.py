#!/usr/bin/env python3
"""
Generate Comprehensive Work Stream Plan

Creates a complete work stream plan for:
1. Setting up governance for all projects
2. Creating quality matrices
3. Setting up audits
4. Completing all research/ideas at mature level
"""

import json
import sys
from pathlib import Path

# Add thegent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from thegent.governance.workstream_integration import WorkStreamIntegrator


def main():
    """Generate work stream plan."""

    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")

    # Load integration data
    integration_file = base_path / "docs" / "research" / "WORKSTREAM_INTEGRATION_DATA.json"
    if not integration_file.exists():
        return 1

    with open(integration_file) as f:
        integration_data = json.load(f)

    # Convert to Path objects
    research_files = [Path(f) for f in integration_data["research_files"]]
    project_paths = [Path(p) for p in integration_data["projects"]]


    # Create integrator
    integrator = WorkStreamIntegrator(base_path)

    # Generate work stream plan
    plan = integrator.create_work_stream_plan(project_paths, research_files)

    # Save plan
    plan_file = base_path / "docs" / "research" / "COMPREHENSIVE_WORKSTREAM_PLAN.json"
    integrator.save_work_stream_plan(plan, plan_file)

    for _phase_data in plan["phases"].values():
        pass

    # Get ready tasks
    ready_tasks = integrator.get_next_actions()
    if ready_tasks:
        for _task in ready_tasks[:10]:
            pass

    # Save task manager state
    integrator.task_manager.save()

    return 0


if __name__ == "__main__":
    sys.exit(main())
