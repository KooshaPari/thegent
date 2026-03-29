"""Phench target lifecycle commands."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

import orjson as json
import typer
from rich.console import Console

console = Console()

TargetCreate = Callable[..., Any]
TargetBootstrap = Callable[..., Any]
TargetImportRepos = Callable[..., Any]
TargetAddRepo = Callable[..., Any]
TargetSetRepoRef = Callable[..., Any]
TargetLock = Callable[..., Any]
TargetMaterialize = Callable[[str, str | None], Any]
ListTargetSnapshots = Callable[..., Any]


def register_target_commands(
    target_app: typer.Typer,
    *,
    init_target_fn: TargetCreate,
    bootstrap_target_fn: TargetBootstrap,
    import_repos_fn: TargetImportRepos,
    add_repo_fn: TargetAddRepo,
    set_repo_ref_fn: TargetSetRepoRef,
    lock_target_fn: TargetLock,
    materialize_target_fn: TargetMaterialize,
    list_target_snapshots_fn: ListTargetSnapshots = None,
) -> None:
    @target_app.command("init", help="Create a new target in Phenotype/projects.")
    def target_init_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        mode: str = typer.Option("repo", "--mode", help="Target mode: repo|stack."),
    ) -> None:
        if mode not in {"repo", "stack"}:
            raise typer.BadParameter("mode must be one of: repo, stack")
        lock = init_target_fn(name, mode=mode, family=family)
        console.print_json(
            json.dumps({"target": lock.target_name, "mode": lock.mode, "lock_hash": lock.lock_hash}).decode()
        )

    @target_app.command("bootstrap", help="Create target and bulk add discovered repos.")
    def target_bootstrap_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        mode: str = typer.Option("repo", "--mode", help="Target mode: repo|stack."),
        source_root: Path | None = typer.Option(
            None,
            "--source-root",
            help="Workspace root containing sibling git checkouts (defaults to sibling repos root).",
        ),
        ref: str = typer.Option("HEAD", "--ref", help="Ref to select for discovered repos."),
        preferred_runner: str | None = typer.Option(
            None,
            "--preferred-runner",
            help="Preferred runner policy to use for these repos.",
        ),
        preferred_command: str | None = typer.Option(
            None,
            "--preferred-command",
            help="Preferred command policy to use for these repos.",
        ),
        preferred_ref: str | None = typer.Option(
            None,
            "--preferred-ref",
            help="Preferred runtime ref policy for these repos.",
        ),
        include: list[str] = typer.Option(
            [],
            "--include",
            help="Glob include pattern; repeat for multiple values.",
        ),
        exclude: list[str] = typer.Option(
            [],
            "--exclude",
            help="Glob exclude pattern; repeat for multiple values.",
        ),
        repo_ids: list[str] = typer.Option(
            [],
            "--repo-id",
            help="Optional explicit repo IDs to include. Repeat as needed.",
        ),
        auto_lock: bool = typer.Option(
            True,
            "--auto-lock/--no-auto-lock",
            help="Auto-lock after bootstrap.",
        ),
    ) -> None:
        if mode not in {"repo", "stack"}:
            raise typer.BadParameter("mode must be one of: repo, stack")
        lock = bootstrap_target_fn(
            target=name,
            family=family,
            mode=mode,
            source_root=source_root,
            selected_ref=ref,
            preferred_runner=preferred_runner,
            preferred_command=preferred_command,
            preferred_ref=preferred_ref,
            include=include or None,
            exclude=exclude or None,
            repo_ids=repo_ids or None,
            auto_lock=auto_lock,
        )
        console.print_json(
            json.dumps(
                {
                    "target": lock.target_name,
                    "mode": lock.mode,
                    "repos": [repo.repo_id for repo in lock.repos],
                    "lock_hash": lock.lock_hash,
                }
            ).decode()
        )

    @target_app.command("import-repos", help="Import discovered repos into an existing target.")
    def target_import_repos_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        source_root: Path | None = typer.Option(
            None,
            "--source-root",
            help="Workspace root containing sibling git checkouts (defaults to sibling repos root).",
        ),
        ref: str = typer.Option("HEAD", "--ref", help="Ref to select for discovered repos."),
        preferred_runner: str | None = typer.Option(
            None,
            "--preferred-runner",
            help="Preferred runner policy to use for these repos.",
        ),
        preferred_command: str | None = typer.Option(
            None,
            "--preferred-command",
            help="Preferred command policy to use for these repos.",
        ),
        preferred_ref: str | None = typer.Option(
            None,
            "--preferred-ref",
            help="Preferred runtime ref policy for these repos.",
        ),
        include: list[str] = typer.Option(
            [],
            "--include",
            help="Glob include pattern; repeat for multiple values.",
        ),
        exclude: list[str] = typer.Option(
            [],
            "--exclude",
            help="Glob exclude pattern; repeat for multiple values.",
        ),
        repo_ids: list[str] = typer.Option(
            [],
            "--repo-id",
            help="Optional explicit repo IDs to include. Repeat as needed.",
        ),
        auto_lock: bool = typer.Option(
            True,
            "--auto-lock/--no-auto-lock",
            help="Auto-lock after import.",
        ),
    ) -> None:
        lock = import_repos_fn(
            target=name,
            family=family,
            source_root=source_root,
            selected_ref=ref,
            preferred_runner=preferred_runner,
            preferred_command=preferred_command,
            preferred_ref=preferred_ref,
            include=include or None,
            exclude=exclude or None,
            repo_ids=repo_ids or None,
            auto_lock=auto_lock,
        )
        console.print_json(
            json.dumps(
                {
                    "target": lock.target_name,
                    "repos": [repo.repo_id for repo in lock.repos],
                    "lock_hash": lock.lock_hash,
                }
            ).decode()
        )

    @target_app.command("add-repo", help="Add repo+ref selection to a target.")
    def target_add_repo_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        repo: str = typer.Option(..., "--repo", help="Absolute path to repo checkout."),
        ref: str = typer.Option(..., "--ref", help="Selected git ref (branch/tag/sha)."),
        preferred_ref: str | None = typer.Option(
            None,
            "--preferred-ref",
            help="Preferred runtime ref for this repo in target policy.",
        ),
        preferred_runner: str | None = typer.Option(
            None,
            "--preferred-runner",
            help="Preferred runner for this repo in target policy.",
        ),
        preferred_command: str | None = typer.Option(
            None,
            "--preferred-command",
            help="Preferred command for this repo in target policy.",
        ),
        repo_id: str | None = typer.Option(
            None,
            "--repo-id",
            help="Optional stable repo identifier.",
        ),
        worktree: str | None = typer.Option(
            None,
            "--worktree",
            help="Optional source worktree path hint.",
        ),
    ) -> None:
        lock = add_repo_fn(
            name,
            repo,
            ref,
            family=family,
            repo_id=repo_id,
            worktree_path=worktree,
            preferred_runner=preferred_runner,
            preferred_command=preferred_command,
            preferred_ref=preferred_ref,
        )
        console.print_json(
            json.dumps(
                {
                    "target": lock.target_name,
                    "repos": [repo.repo_id for repo in lock.repos],
                    "lock_hash": lock.lock_hash,
                }
            ).decode()
        )

    @target_app.command("set-ref", help="Set selected ref for one repo and relock target.")
    def target_set_ref_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        repo_id: str = typer.Option(..., "--repo-id", help="Repo ID in target lock."),
        ref: str = typer.Option(..., "--ref", help="Git ref (branch/tag/sha)."),
    ) -> None:
        lock = set_repo_ref_fn(name, repo_id=repo_id, selected_ref=ref, family=family)
        console.print_json(
            json.dumps(
                {
                    "target": lock.target_name,
                    "repos": [repo.repo_id for repo in lock.repos],
                    "lock_hash": lock.lock_hash,
                }
            ).decode()
        )

    @target_app.command("add-module", help="Add module-selected repos to a target.")
    def target_add_module_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        module: str = typer.Option(..., "--module", help="Module name under Phenotype/projects/modules."),
        selected_ref: str | None = typer.Option(None, "--ref", help="Override selected ref for all module repos."),
        exclude: list[str] = typer.Option([], "--exclude", help="Exact repo IDs to exclude (no glob patterns)."),
    ) -> None:
        from thegent.phench import add_module_to_target
        lock = add_module_to_target(
            name,
            module_name=module,
            selected_ref=selected_ref,
            exclude_repos={v.strip() for v in exclude if v.strip()},
            family=family,
        )
        console.print_json(
            json.dumps({
                "target": lock.target_name,
                "module": module,
                "repos": [r.repo_id for r in lock.repos if r.module_name == module],
                "lock_hash": lock.lock_hash,
            }).decode()
        )

    @target_app.command("lock", help="Resolve selected refs to immutable SHAs.")
    def target_lock_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
    ) -> None:
        lock = lock_target_fn(name, family=family)
        console.print_json(
            json.dumps(
                {
                    "target": lock.target_name,
                    "lock_hash": lock.lock_hash,
                    "repos": [
                        {
                            "repo_id": repo.repo_id,
                            "selected_ref": repo.selected_ref,
                            "resolved_sha": repo.resolved_sha,
                        }
                        for repo in lock.repos
                    ],
                }
            ).decode()
        )

    @target_app.command(
        "materialize",
        help="Materialize deterministic checkouts under Phenotype/projects/<target>/repos.",
    )
    def target_materialize_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
    ) -> None:
        runtime = materialize_target_fn(name, family=family)
        console.print_json(
            json.dumps(
                {
                    "target": runtime.target_name,
                    "materialized_root": runtime.materialized_root,
                    "repos": [asdict(repo) for repo in runtime.repo_materializations],
                }
            ).decode()
        )
