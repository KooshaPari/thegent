"""Project-oriented phench orchestration commands."""

from __future__ import annotations

import orjson as json
from typing import Any, Callable

import typer
from rich.console import Console
from rich.prompt import IntPrompt

from thegent.phench import load_module_manifest, load_target_lock

console = Console()

TargetResolver = Callable[..., list[str]]
TargetLockLoader = Callable[..., Any]
TargetTimelineLoader = Callable[..., dict[str, Any]]
TargetAction = Callable[..., Any]
ModuleLister = Callable[[], list[str]]
ProjectMatrixAction = Callable[..., dict[str, Any]]
RunAction = Callable[..., int]


def _ensure_target_name(
    target: str | None,
    *,
    family: str | None,
    non_interactive: bool,
    list_targets_fn: TargetResolver,
) -> str:
    targets = list_targets_fn(family=family)
    if not targets:
        raise typer.BadParameter("No targets found under Phenotype/projects. Initialize one with `phench target init`.")

    if target is not None:
        if target not in targets:
            raise typer.BadParameter(f"Unknown target: {target}")
        return target

    if non_interactive:
        raise typer.BadParameter("--target is required when --no-interactive is set")

    if len(targets) == 1:
        return targets[0]

    console.print("Select target:")
    for idx, value in enumerate(targets, start=1):
        console.print(f"{idx}. {value}")
    target_index = IntPrompt.ask("Target number", default=1)
    if target_index < 1 or target_index > len(targets):
        raise typer.BadParameter("Target selection out of range.")
    return targets[target_index - 1]


def _ensure_repo_id(
    selected_target: str,
    lock_repos: list,
    *,
    repo_id: str | None,
    all_repos: bool,
    non_interactive: bool,
) -> str | None:
    if all_repos:
        return None

    repo_ids = [repo.repo_id for repo in lock_repos]
    if not repo_ids:
        raise typer.BadParameter(f"target {selected_target} has no repos")

    if repo_id is not None:
        if repo_id not in repo_ids:
            raise typer.BadParameter(f"repo-id not found in target lock: {repo_id}")
        return repo_id

    if len(repo_ids) == 1:
        return repo_ids[0]

    if non_interactive:
        raise typer.BadParameter("--repo-id is required when --all-repos is false in non-interactive mode")

    console.print("Select repo:")
    for idx, value in enumerate(repo_ids, start=1):
        console.print(f"{idx}. {value}")
    repo_index = IntPrompt.ask("Repository number", default=1)
    if repo_index < 1 or repo_index > len(repo_ids):
        raise typer.BadParameter("Repository selection out of range.")
    return repo_ids[repo_index - 1]


def _ensure_selected_ref(
    selected_target: str,
    selected_repo_id: str,
    *,
    ref: str | None,
    branch: str | None,
    no_interactive: bool,
    timeline_limit: int,
    target_timeline_fn: TargetTimelineLoader,
    family: str | None,
) -> str | None:
    if ref is not None:
        return ref
    if branch is not None:
        return branch

    if no_interactive:
        raise typer.BadParameter(
            "--ref/--branch is required when --no-interactive is set for single repo selection"
        )

    timeline = target_timeline_fn(selected_target, repo_id=selected_repo_id, family=family, limit=timeline_limit)
    options: list[tuple[str, str]] = [("HEAD", "HEAD")]
    for branch_name in timeline.get("branches", []):
        if branch_name:
            options.append((branch_name, f"branch: {branch_name}"))
    for tag_name in timeline.get("tags", []):
        if tag_name:
            options.append((tag_name, f"tag: {tag_name}"))
    for line in timeline.get("recent", []):
        if len(options) >= 18:
            break
        head = line.split(maxsplit=1)[0] if isinstance(line, str) else ""
        if not head or head.startswith("("):
            continue
        options.append((head, f"recent commit: {line}"))

    console.print("Select ref:")
    for idx, (_, label) in enumerate(options, start=1):
        console.print(f"{idx}. {label}")
    selected_ref_index = IntPrompt.ask("Ref number", default=1)
    if selected_ref_index < 1 or selected_ref_index > len(options):
        raise typer.BadParameter("Ref selection out of range.")
    return options[selected_ref_index - 1][0]


def _parse_repo_ref_specs(
    repo_ref_specs: list[str] | None,
    lock_repo_ids: set[str],
) -> list[tuple[str, str]]:
    if not repo_ref_specs:
        return []

    parsed: list[tuple[str, str]] = []
    seen: set[str] = set()

    for spec in repo_ref_specs:
        if "@" not in spec:
            raise typer.BadParameter(
                "repo-ref entries must use the format <repo-id>@<ref> (for example "
                "repo-a@feature-branch)"
            )
        repo_id, ref = spec.split("@", 1)
        repo_id = repo_id.strip()
        ref = ref.strip()
        if not repo_id:
            raise typer.BadParameter("repo-ref entry is missing a repo-id before '@'")
        if not ref:
            raise typer.BadParameter(f"repo-ref entry is missing a ref after '@': {spec}")
        if repo_id not in lock_repo_ids:
            raise typer.BadParameter(f"repo-ref repo-id not in target lock: {repo_id}")
        if repo_id in seen:
            raise typer.BadParameter(f"repo-ref specified multiple times for repo: {repo_id}")
        seen.add(repo_id)
        parsed.append((repo_id, ref))
    return parsed


def _merge_override_maps(
    base: dict[str, str] | None,
    extra: list[tuple[str, str]],
) -> dict[str, str]:
    base_map = dict(base or {})
    return {**base_map, **dict(extra)}


def _build_projects_plan_kwargs(
    *,
    target: str | None,
    family: str | None,
    snapshot_id: str | None,
    repo_id: str | None,
    runner: str | None,
    command: str | None,
    ref: str | None,
    branch: str | None,
    module: str | None,
    repo_refs: list[str] | None,
    all_repos: bool,
    execution_mode: str,
    env_profile: str | None,
    no_interactive: bool,
    timeline_limit: int,
    list_targets_fn: TargetResolver,
    load_target_lock_fn: TargetLockLoader,
    target_timeline_fn: TargetTimelineLoader,
    ) -> tuple[str, dict[str, Any]]:
    if ref is not None and branch is not None:
        raise typer.BadParameter("--ref and --branch are mutually exclusive")

    selected_target = _ensure_target_name(
        target,
        family=family,
        non_interactive=no_interactive,
        list_targets_fn=list_targets_fn,
    )
    lock = load_target_lock_fn(selected_target, family=family)
    lock_repo_ids = {repo.repo_id for repo in lock.repos}
    module_repo_ids: list[str] = []
    module_repo_ref_overrides: dict[str, str] = {}
    module_runner_overrides: dict[str, str] = {}
    module_command_overrides: dict[str, str] = {}
    module_env_profile_overrides: dict[str, str] = {}

    if module is not None:
        if all_repos:
            raise typer.BadParameter("--module is not compatible with --all-repos")
        if repo_id is not None:
            raise typer.BadParameter("--module already defines repos; do not pass --repo-id")
        module_manifest = load_module_manifest(module, available_repo_ids=sorted(lock_repo_ids))
        module_repo_ids = module_manifest["repo_ids"]
        module_repo_ref_overrides = module_manifest["repo_ref_overrides"]
        module_runner_overrides = module_manifest["repo_runner_overrides"]
        module_command_overrides = module_manifest["repo_command_overrides"]
        module_env_profile_overrides = module_manifest["repo_env_profile_overrides"]
        lock_repo_ids = set(module_repo_ids)
        if not module_repo_ids:
            raise typer.BadParameter(f"module has no repos: {module}")

    repo_ref_pairs = _parse_repo_ref_specs(repo_refs, lock_repo_ids)
    if repo_ref_pairs and all_repos:
        raise typer.BadParameter("--repo-ref is not compatible with --all-repos")
    if repo_ref_pairs and repo_id:
        raise typer.BadParameter("--repo-ref already defines repo-id; do not pass --repo-id")

    snapshot_mode = snapshot_id is not None
    selected_repo_id = None
    if not repo_ref_pairs:
        if module:
            selected_repo_ids = list(module_repo_ids)
        else:
            selected_repo_id = _ensure_repo_id(
                selected_target,
                lock.repos,
                repo_id=repo_id,
                all_repos=all_repos,
                non_interactive=no_interactive,
            )

    selected_ref: str | None = ref or branch
    if snapshot_mode and (ref is not None or branch is not None):
        raise typer.BadParameter("--ref/--branch are not compatible with --snapshot-id")
    if selected_repo_id is not None and selected_ref is None and not snapshot_mode:
        selected_ref = _ensure_selected_ref(
            selected_target,
            selected_repo_id,
            ref=ref,
            branch=branch,
            no_interactive=no_interactive,
            timeline_limit=timeline_limit,
            target_timeline_fn=target_timeline_fn,
            family=family,
        )

    if selected_ref is not None and repo_ref_pairs:
        raise typer.BadParameter("--repo-ref conflicts with --ref/--branch")

    # Caller may prepare target state separately before execution.
    base_run_kwargs = {
        "snapshot_id": snapshot_id,
        "runner": runner,
        "command_name": command,
        "selected_ref": selected_ref,
        "all_repos": all_repos,
        "execution_mode": execution_mode,
        "env_profile": env_profile,
        "non_interactive": no_interactive,
        "family": family,
    }

    if module:
        base_run_kwargs["repo_ids"] = list(module_repo_ids)
        if module_repo_ref_overrides:
            base_run_kwargs["repo_ref_overrides"] = module_repo_ref_overrides
        if module_runner_overrides:
            base_run_kwargs["repo_runner_overrides"] = module_runner_overrides
        if module_command_overrides:
            base_run_kwargs["repo_command_overrides"] = module_command_overrides
        if module_env_profile_overrides:
            base_run_kwargs["repo_env_profile_overrides"] = module_env_profile_overrides

    if repo_ref_pairs:
        base_run_kwargs["repo_id"] = None
        base_run_kwargs["repo_ids"] = list(module_repo_ids) if module else [repo_id for repo_id, _ in repo_ref_pairs]
        if module:
            base_run_kwargs["repo_ref_overrides"] = _merge_override_maps(
                module_repo_ref_overrides,
                repo_ref_pairs,
            )
        else:
            base_run_kwargs["repo_ref_overrides"] = dict(repo_ref_pairs)
        base_run_kwargs["selected_ref"] = None
        base_run_kwargs["all_repos"] = False
        base_run_kwargs["execution_mode"] = "serial"
    else:
        base_run_kwargs["repo_id"] = selected_repo_id
    return selected_target, base_run_kwargs


def _projects_run_impl(
    *,
    target: str | None,
    family: str | None,
    snapshot_id: str | None,
    repo_id: str | None,
    runner: str | None,
    command: str | None,
    ref: str | None,
    branch: str | None,
    module: str | None,
    repo_refs: list[str] | None,
    all_repos: bool,
    execution_mode: str,
    env_profile: str | None,
    no_interactive: bool,
    no_prepare: bool,
    timeline_limit: int,
    list_targets_fn: TargetResolver,
    load_target_lock_fn: TargetLockLoader,
    target_timeline_fn: TargetTimelineLoader,
    lock_target_fn: TargetAction,
    materialize_target_fn: TargetAction,
    run_target_fn: RunAction,
) -> None:
    selected_target, base_run_kwargs = _build_projects_plan_kwargs(
        target=target,
        family=family,
        snapshot_id=snapshot_id,
        repo_id=repo_id,
        runner=runner,
        command=command,
        ref=ref,
        branch=branch,
        module=module,
        repo_refs=repo_refs,
        all_repos=all_repos,
        execution_mode=execution_mode,
        env_profile=env_profile,
        no_interactive=no_interactive,
        timeline_limit=timeline_limit,
        list_targets_fn=list_targets_fn,
        load_target_lock_fn=load_target_lock_fn,
        target_timeline_fn=target_timeline_fn,
    )

    if not no_prepare and snapshot_id is None:
        lock_target_fn(selected_target, family=family)
        materialize_target_fn(selected_target, family=family)

    if snapshot_id is not None:
        base_run_kwargs["snapshot_id"] = snapshot_id

    exit_code = run_target_fn(selected_target, **base_run_kwargs)
    raise typer.Exit(exit_code)


def register_projects_run(
    projects_app: typer.Typer,
    *,
    list_targets_fn: TargetResolver,
    list_modules_fn: ModuleLister,
    load_target_lock_fn: TargetLockLoader | None = None,
    target_timeline_fn: TargetTimelineLoader,
    target_status_fn: Callable[[str, str | None], Any],
    lock_target_fn: TargetAction,
    materialize_target_fn: TargetAction,
    run_target_fn: RunAction,
    build_matrix_fn: ProjectMatrixAction,
) -> None:
    if load_target_lock_fn is None:
        load_target_lock_fn = load_target_lock

    @projects_app.command("run", help="Run through guided target/repo/ref selection.")
    def projects_run_cmd(
        target: str | None = typer.Option(None, "--target", help="Target name to run."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target lock."),
        module: str | None = typer.Option(
            None,
            "--module",
            help="Execute the module-defined repo subset (thegent/projects/modules/<module>).",
        ),
        repo_refs: list[str] | None = typer.Option(
            None,
            "--repo-ref",
            help="Repo/ref override in <repo-id>@<ref> format (repeatable).",
        ),
        runner: str | None = typer.Option(None, "--runner", help="Explicit runner override (task|just|make|pnpm|npm|bun)."),
        command: str | None = typer.Option(None, "--command", help="Explicit command/target name for runner."),
        ref: str | None = typer.Option(None, "--ref", help="Ref to resolve for this execution (branch/tag/sha)."),
        branch: str | None = typer.Option(None, "--branch", help="Alias for --ref."),
        all_repos: bool = typer.Option(False, "--all-repos", help="Run command selection on all repos in target."),
        execution_mode: str = typer.Option("serial", "--mode", help="Execution mode for --all-repos: serial|parallel."),
        env_profile: str | None = typer.Option(None, "--env-profile", help="Optional env profile name."),
        no_interactive: bool = typer.Option(False, "--no-interactive", help="Fail if command selection would be interactive."),
        no_prepare: bool = typer.Option(False, "--no-prepare", help="Skip lock+materialize before run."),
        snapshot_id: str | None = typer.Option(
            None,
            "--snapshot-id",
            help="Run from a target snapshot instead of current materialized state.",
        ),
        timeline_limit: int = typer.Option(20, "--timeline-limit", help="Number of refs to show for interactive timeline selection."),
        ) -> None:
        _projects_run_impl(
            target=target,
            family=family,
            snapshot_id=snapshot_id,
            repo_id=repo_id,
            module=module,
            runner=runner,
            command=command,
            ref=ref,
            branch=branch,
            repo_refs=repo_refs,
            all_repos=all_repos,
            execution_mode=execution_mode,
            env_profile=env_profile,
            no_interactive=no_interactive,
            no_prepare=no_prepare,
            timeline_limit=timeline_limit,
            list_targets_fn=list_targets_fn,
            load_target_lock_fn=load_target_lock_fn,
            target_timeline_fn=target_timeline_fn,
            lock_target_fn=lock_target_fn,
            materialize_target_fn=materialize_target_fn,
            run_target_fn=run_target_fn,
        )

    @projects_app.command("matrix", help="Show resolved execution matrix for target/repo execution.")
    def projects_matrix_cmd(
        target: str | None = typer.Option(None, "--target", help="Target name to inspect."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target lock."),
        module: str | None = typer.Option(
            None,
            "--module",
            help="Show module-defined repo subset (thegent/projects/modules/<module>).",
        ),
        repo_refs: list[str] | None = typer.Option(
            None,
            "--repo-ref",
            help="Repo/ref override in <repo-id>@<ref> format (repeatable).",
        ),
        runner: str | None = typer.Option(None, "--runner", help="Explicit runner override (task|just|make|pnpm|npm|bun)."),
        command: str | None = typer.Option(None, "--command", help="Explicit command/target name for runner."),
        ref: str | None = typer.Option(None, "--ref", help="Ref to resolve for this execution (branch/tag/sha)."),
        branch: str | None = typer.Option(None, "--branch", help="Alias for --ref."),
        all_repos: bool = typer.Option(False, "--all-repos", help="Include all repos in target lock."),
        env_profile: str | None = typer.Option(None, "--env-profile", help="Optional env profile name."),
        no_interactive: bool = typer.Option(False, "--no-interactive", help="Fail if selection would be interactive."),
        snapshot_id: str | None = typer.Option(
            None,
            "--snapshot-id",
            help="Build matrix from a target snapshot instead of current materialized state.",
        ),
        sort_repos: bool = typer.Option(
            True,
            "--sort-repos/--no-sort-repos",
            help="Sort repos in matrix output for deterministic order.",
        ),
        timeline_limit: int = typer.Option(20, "--timeline-limit", help="Number of refs to show for interactive timeline selection."),
    ) -> None:
        selected_target, base_run_kwargs = _build_projects_plan_kwargs(
            target=target,
            family=family,
            snapshot_id=snapshot_id,
            repo_id=repo_id,
            runner=runner,
            command=command,
            ref=ref,
            branch=branch,
            module=module,
            repo_refs=repo_refs,
            all_repos=all_repos,
            execution_mode="serial",
            env_profile=env_profile,
            no_interactive=no_interactive,
            timeline_limit=timeline_limit,
            list_targets_fn=list_targets_fn,
            load_target_lock_fn=load_target_lock_fn,
            target_timeline_fn=target_timeline_fn,
        )

        matrix_kwargs = dict(base_run_kwargs)
        matrix_kwargs.pop("execution_mode", None)
        matrix_kwargs["non_interactive"] = no_interactive
        matrix_kwargs["sort_repos"] = sort_repos
        matrix = build_matrix_fn(selected_target, **matrix_kwargs)
        console.print_json(data=matrix)

    @projects_app.command("status", help="Show lock/runtime state for a target under Phenotype/projects.")
    def projects_status_cmd(
        target: str | None = typer.Option(None, "--target", help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
    ) -> None:
        selected_target = _ensure_target_name(
            target,
            family=family,
            non_interactive=False,
            list_targets_fn=list_targets_fn,
        )
        state = target_status_fn(selected_target, family=family)
        state["projects_root"] = f"projects/{selected_target}"
        console.print_json(json.dumps(state).decode())


    @projects_app.command("modules", help="List or inspect module manifests under Phenotype/projects/modules.")
    def projects_modules_cmd(
        module: str | None = typer.Option(None, "--module", help="Inspect a specific module manifest."),
        target: str | None = typer.Option(None, "--target", help="Optional target to validate module repos against lock."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
    ) -> None:
        if module is None:
            modules = list_modules_fn()
            console.print_json(data=modules)
            return

        available_repo_ids: list[str] | None = None
        if target is not None:
            selected_target = _ensure_target_name(
                target,
                family=family,
                non_interactive=False,
                list_targets_fn=list_targets_fn,
            )
            lock = load_target_lock_fn(selected_target, family=family)
            available_repo_ids = [repo.repo_id for repo in lock.repos]
            available_repo_ids.sort()

        manifest = load_module_manifest(module, available_repo_ids=available_repo_ids)
        manifest = dict(manifest)
        manifest["module"] = module
        if target is not None:
            manifest["target"] = target
        console.print_json(data=manifest)
