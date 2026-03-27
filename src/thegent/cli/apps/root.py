"""Root CLI registration helpers for thegent."""

from __future__ import annotations

import typer

from thegent.cli.apps import (
    audit,
    bench,
    crew,
    domain,
    enterprise,
    govern,
    isolation,
    memory,
    orchestrate,
    plan,
    queue,
    registry,
    routing,
    rules,
    run,
    session,
    skills,
    mcp,
    sync,
    sys,
    team,
)
from thegent.cli.apps.project import install_app, scaffold_app, setup_project_app, update_app
from thegent.cli.governance.cli_git_worktree_governance import worktree_governance_app
from thegent.cli.atlas import app as atlas_app
from thegent.dotfiles.cli import app as dotfiles_app
from thegent.mesh.main import app as mesh_app


def register_root_apps(app: typer.Typer, git_app: typer.Typer) -> None:
    """Register the root command hierarchy."""
    app.add_typer(run.app, name="run", help="Execution: Agent tasks, background runs, and history.")
    app.add_typer(crew.app, name="crew", help="Crew: create, execute, inspect, and monitor crews.")
    app.add_typer(bench.app, name="bench", help="Benchmark: run benchmark suites and persist result rows.")
    app.add_typer(sync.app, name="sync", help="Synchronization: Rules, DAG, work-stream, and catalog.")
    app.add_typer(skills.app, name="skill", help="Skills: Auto-discovery and management of agent skills.")
    app.add_typer(audit.app, name="audit", help="Integrity: System health, security, and planning risk.")
    app.add_typer(plan.app, name="plan", help="Roadmap: DAG tasks, work streams, and initiatives.")
    app.add_typer(queue.app, name="queue", help="Queue: Unified prompt queue for deferred tasks (FR-HAX-001).")
    app.add_typer(rules.app, name="rules", help="Rules: Cross-platform rules synchronization (FR-HAX-002).")
    app.add_typer(team.app, name="team", help="Swarm: Coordination, teammates, and hierarchy.")
    app.add_typer(domain.app, name="domain", help="Domain: mapping and tunnel advisor workflows (WL-124).")
    app.add_typer(govern.app, name="govern", help="Governance: approval/rejection and escalation decisions.")
    app.add_typer(sys.app, name="sys", help="System: Setup, MCP, LSP, and configuration.")
    app.add_typer(
        setup_project_app,
        name="project",
        help="Project tenancy commands (alias for `thegent sys setup project`).",
    )
    app.add_typer(mcp.app, name="mcp", help="MCP: install, service, migration, and cleanup helpers.")
    app.add_typer(isolation.app, name="isolation", help="Isolation: Multi-tenancy, L1/L2 nesting, and SHM.")
    app.add_typer(mesh_app, name="mesh", help="Mesh: Local agent coordination, status, and discovery.")
    app.add_typer(install_app, name="install", help="Install user/system assets and project runtime installation.")
    app.add_typer(update_app, name="update", help="Update user/system assets and project runtime installation.")
    app.add_typer(git_app, name="git", help="Coordinated git workflows for multi-agent development.")
    app.add_typer(worktree_governance_app, name="worktree", help="Structured worktree governance lifecycle.")
    app.add_typer(
        registry.app, name="registry", help="Registry: Agent capability index, recommendations, and health (WL-034)."
    )
    app.add_typer(
        routing.app, name="routing", help="Routing: LiteLLM, Pareto router, and model-first routing control (WL-012)."
    )
    app.add_typer(scaffold_app, name="scaffold", help="Project scaffolding and brownfield migration entrypoints.")
    app.add_typer(
        enterprise.app, name="enterprise", help="Enterprise: compliance, GDPR, org hierarchy, key rotation (WL-051)."
    )
    app.add_typer(memory.app, name="memory", help="Memory: agent memory logs, synthesis, and gardening (WL-060).")
    app.add_typer(session.app, name="session", help="Session: resume and inspect background sessions (WL-110).")
    app.add_typer(
        orchestrate.app,
        name="orchestrate",
        help="Orchestrate: sub-agent goal decomposition and execution (WL-088).",
    )
    app.add_typer(atlas_app, name="atlas", help="Atlas: Codebase visualization, LOC stats, and tree generation.")
    app.add_typer(dotfiles_app, name="dotfiles", help="Dotfiles: deploy tool configs from thegent templates to ~/.")
