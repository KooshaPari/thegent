from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from thegent.phench.service import (
    add_repo,
    audit_shared_modules,
    add_module_to_target,
    scan_shared_modules_across_repos,
    get_env_profile,
    init_target,
    list_targets,
    lock_target,
    materialize_target,
    run_env_doctor_for_target,
    run_target,
    set_env_profile,
    sync_target,
)
from thegent.phench.models import RepoSelection, RunnerCatalog, RunnerCommand, TargetLock
from thegent.phench.store import read_dual


def _run(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{proc.stderr}")


def _init_git_repo(path: Path) -> str:
    path.mkdir(parents=True, exist_ok=True)
    _run(["git", "init"], cwd=path)
    _run(["git", "config", "user.email", "test@example.com"], cwd=path)
    _run(["git", "config", "user.name", "Test User"], cwd=path)
    (path / "Taskfile.yml").write_text("version: '3'\ntasks:\n  hello:\n    cmds:\n      - echo hello\n", encoding="utf-8")
    (path / "README.md").write_text("hello\n", encoding="utf-8")
    _run(["git", "add", "."], cwd=path)
    _run(["git", "commit", "-m", "init"], cwd=path)
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(path), capture_output=True, text=True, check=False)
    assert proc.returncode == 0
    return proc.stdout.strip()


def _init_git_repo_with_pkg(path: Path, pkg_name: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _run(["git", "init"], cwd=path)
    _run(["git", "config", "user.email", "test@example.com"], cwd=path)
    _run(["git", "config", "user.name", "Test User"], cwd=path)
    pkg_dir = path / "src" / pkg_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (path / "README.md").write_text("hello\n", encoding="utf-8")
    _run(["git", "add", "."], cwd=path)
    _run(["git", "commit", "-m", "init"], cwd=path)


def test_lock_and_materialize_with_dual_write(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    projects_root = phenotype_root / "projects"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "source-repo"

    sha = _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    lock = init_target("alpha", mode="repo")
    assert lock.target_name == "alpha"

    lock = add_repo("alpha", repo_path=str(source_repo), selected_ref="HEAD")
    assert len(lock.repos) == 1

    lock = lock_target("alpha")
    assert lock.repos[0].resolved_sha == sha

    runtime = materialize_target("alpha")
    assert runtime.repo_materializations
    checkout = Path(runtime.repo_materializations[0].checkout_path)
    assert (checkout / "README.md").exists()

    project_lock = projects_root / "alpha" / ".phench" / "target.lock.json"
    mirror_lock = mirror_root / "alpha" / ".phench" / "target.lock.json"
    assert project_lock.exists()
    assert mirror_lock.exists()


def test_env_doctor_reports_missing_runner_binary(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "source-repo"

    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("beta", mode="repo")
    add_repo("beta", repo_path=str(source_repo), selected_ref="HEAD")
    lock_target("beta")
    materialize_target("beta")

    monkeypatch.setattr("shutil.which", lambda name: None)
    report = run_env_doctor_for_target("beta")
    assert report["doctor_status"] == "fail"
    assert "task" in report["missing_requirements"]


def test_sync_repairs_dual_state(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    projects_root = phenotype_root / "projects"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "source-repo"

    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("gamma", mode="repo")
    add_repo("gamma", repo_path=str(source_repo), selected_ref="HEAD")
    lock_target("gamma")

    project_lock = projects_root / "gamma" / ".phench" / "target.lock.json"
    payload = json.loads(project_lock.read_text(encoding="utf-8"))
    payload["payload"]["lock_hash"] = "corrupt"
    project_lock.write_text(json.dumps(payload), encoding="utf-8")

    result = sync_target("gamma", prefer="home")
    assert "target.lock.json" in result
    repaired = json.loads(project_lock.read_text(encoding="utf-8"))
    assert repaired["payload"]["lock_hash"] != "corrupt"


def test_list_targets_discovers_initialized_targets(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("one", mode="repo")
    init_target("two", mode="stack")
    assert list_targets() == ["one", "two"]


def test_invalid_target_name_rejected(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(tmp_path / "Phenotype"))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(tmp_path / "home-phench"))
    with pytest.raises(ValueError):
        init_target("../bad", mode="repo")


def test_run_target_all_repos_serial_and_parallel(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    _init_git_repo(repo_a)
    _init_git_repo(repo_b)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("stacky", mode="stack")
    add_repo("stacky", repo_path=str(repo_a), selected_ref="HEAD", repo_id="a")
    add_repo("stacky", repo_path=str(repo_b), selected_ref="HEAD", repo_id="b")
    lock_target("stacky")
    materialize_target("stacky")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target: {"doctor_status": "pass", "missing_requirements": []},
    )

    monkeypatch.setattr(
        "thegent.phench.service.build_catalog",
        lambda target, repo_id=None: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", "Taskfile.yml")],
            default_command="task hello",
        ),
    )

    calls: list[str] = []

    def _fake_run_command(
        checkout: Path,
        runner: str,
        command_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> int:
        calls.append(f"{checkout.name}:{runner}:{command_name}")
        return 0

    monkeypatch.setattr("thegent.phench.service.run_command", _fake_run_command)

    serial_code = run_target("stacky", runner="task", command_name="hello", all_repos=True, execution_mode="serial")
    assert serial_code == 0
    assert len(calls) == 2

    calls.clear()
    parallel_code = run_target(
        "stacky",
        runner="task",
        command_name="hello",
        all_repos=True,
        execution_mode="parallel",
    )
    assert parallel_code == 0
    assert len(calls) == 2


def test_run_target_all_repos_requires_explicit_runner_and_command(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    _init_git_repo(repo_a)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("stacky2", mode="stack")
    add_repo("stacky2", repo_path=str(repo_a), selected_ref="HEAD", repo_id="a")
    lock_target("stacky2")
    materialize_target("stacky2")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target: {"doctor_status": "pass", "missing_requirements": []},
    )

    with pytest.raises(ValueError):
        run_target("stacky2", all_repos=True)


def test_run_target_rejects_runner_flag_like_command_name(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo"
    _init_git_repo(repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("delta", mode="repo")
    add_repo("delta", repo_path=str(repo), selected_ref="HEAD", repo_id="repo")
    lock_target("delta")
    materialize_target("delta")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target: {"doctor_status": "pass", "missing_requirements": []},
    )

    with pytest.raises(ValueError):
        run_target("delta", runner="task", command_name="--help")


def test_read_dual_rejects_hash_mismatch(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    projects_root = phenotype_root / "projects"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "source-repo"
    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("epsilon", mode="repo")
    add_repo("epsilon", repo_path=str(source_repo), selected_ref="HEAD")
    lock_target("epsilon")

    project_lock = projects_root / "epsilon" / ".phench" / "target.lock.json"
    mirror_lock = mirror_root / "epsilon" / ".phench" / "target.lock.json"
    payload = json.loads(project_lock.read_text(encoding="utf-8"))
    payload["payload"]["lock_hash"] = "corrupt"
    project_lock.write_text(json.dumps(payload), encoding="utf-8")
    mirror_lock.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        read_dual("epsilon", "target.lock.json")


def test_env_profile_applies_to_run(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo-env"
    _init_git_repo(repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("zeta", mode="repo")
    add_repo("zeta", repo_path=str(repo), selected_ref="HEAD", repo_id="repo")
    lock_target("zeta")
    materialize_target("zeta")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target: {"doctor_status": "pass", "missing_requirements": []},
    )

    set_env_profile("zeta", "ci", {"FOO": "BAR"})
    assert get_env_profile("zeta", "ci") == {"FOO": "BAR"}

    observed: dict[str, str] = {}

    def _fake_run_command(
        checkout: Path,
        runner: str,
        command_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> int:
        if env_overrides:
            observed.update(env_overrides)
        return 0

    monkeypatch.setattr("thegent.phench.service.run_command", _fake_run_command)
    run_target("zeta", runner="task", command_name="hello", env_profile="ci")
    assert observed == {"FOO": "BAR"}


def test_add_module_to_target_appends_matching_repos(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = phenotype_root / "repos" / "repo-a"
    repo_b = phenotype_root / "repos" / "repo-b"
    repo_x = phenotype_root / "repos" / "other-repo"
    _init_git_repo(repo_a)
    _init_git_repo(repo_b)
    _init_git_repo(repo_x)

    module_root = phenotype_root / "projects" / "modules" / "thegent-test-module"
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repo_patterns": ["repo-*"],
                "default_ref": "HEAD",
                "repo_ref_overrides": {"repo-a": "HEAD"},
                "repo_runner_overrides": {"repo-a": "task"},
                "repo_command_overrides": {"repo-a": "hello"},
                "repo_env_profile_overrides": {"repo-b": "ci"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("module-target", mode="stack")
    lock = add_module_to_target("module-target", "thegent-test-module")
    repos = {repo.repo_id: repo for repo in lock.repos}
    assert set(repos.keys()) == {"repo-a", "repo-b"}
    assert repos["repo-a"].selected_ref == "HEAD"
    assert repos["repo-a"].selected_runner == "task"
    assert repos["repo-a"].selected_command == "hello"
    assert repos["repo-b"].selected_env_profile == "ci"


def test_add_module_to_target_fails_when_manifest_missing(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("module-missing", mode="stack")
    with pytest.raises(ValueError, match="manifest not found"):
        add_module_to_target("module-missing", "no-such-module")


def test_add_module_to_target_fails_when_no_repos_match_patterns(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = phenotype_root / "repos" / "repo-a"
    _init_git_repo(repo_a)

    module_root = phenotype_root / "projects" / "modules" / "thegent-empty-module"
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repo_patterns": ["does-not-match-*"],
                "default_ref": "HEAD",
                "repo_ref_overrides": {},
                "repo_runner_overrides": {},
                "repo_command_overrides": {},
                "repo_env_profile_overrides": {},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("module-empty", mode="stack")
    with pytest.raises(ValueError, match="selected no matching repos"):
        add_module_to_target("module-empty", "thegent-empty-module")


def test_add_module_to_target_uses_default_excludes(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = phenotype_root / "repos" / "repo-a"
    excluded = [
        phenotype_root / "repos" / "4sgm",
        phenotype_root / "repos" / "parpour",
        phenotype_root / "repos" / "civ",
        phenotype_root / "repos" / "trace",
    ]
    _init_git_repo(repo_a)
    for repo in excluded:
        _init_git_repo(repo)

    module_root = phenotype_root / "projects" / "modules" / "thegent-default-excludes"
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repo_patterns": ["*"],
                "default_ref": "HEAD",
                "repo_ref_overrides": {},
                "repo_runner_overrides": {},
                "repo_command_overrides": {},
                "repo_env_profile_overrides": {},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("module-excludes", mode="stack")
    lock = add_module_to_target("module-excludes", "thegent-default-excludes")
    assert [entry.repo_id for entry in lock.repos] == ["repo-a"]


def test_add_module_respects_repo_and_global_excludes(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = phenotype_root / "repos" / "repo-a"
    repo_b = phenotype_root / "repos" / "repo-b"
    excluded = phenotype_root / "repos" / "repo-ex"
    _init_git_repo(repo_a)
    _init_git_repo(repo_b)
    _init_git_repo(excluded)

    module_root = phenotype_root / "projects" / "modules" / "thegent-test-module-ex"
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repo_patterns": ["repo-*"],
                "default_ref": "HEAD",
                "repo_ref_overrides": {},
                "repo_runner_overrides": {},
                "repo_command_overrides": {},
                "repo_env_profile_overrides": {},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("module-target-2", mode="stack")
    lock = add_module_to_target("module-target-2", "thegent-test-module-ex", exclude_repos={"repo-b"})
    assert {entry.repo_id for entry in lock.repos} == {"repo-a", "repo-ex"}


def test_run_target_uses_module_overrides(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = phenotype_root / "repos" / "repo-run"
    _init_git_repo(repo)

    module_root = phenotype_root / "projects" / "modules" / "thegent-run-module"
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repo_patterns": ["repo-*"],
                "default_ref": "HEAD",
                "repo_ref_overrides": {},
                "repo_runner_overrides": {"repo-run": "task"},
                "repo_command_overrides": {"repo-run": "hello"},
                "repo_env_profile_overrides": {"repo-run": "ci"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("module-run", mode="repo")
    add_module_to_target("module-run", "thegent-run-module")
    lock_target("module-run")
    materialize_target("module-run")
    set_env_profile("module-run", "ci", {"FROM_PROFILE": "1"})
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target: {"doctor_status": "pass", "missing_requirements": []},
    )
    monkeypatch.setattr(
        "thegent.phench.service.build_catalog",
        lambda target, repo_id=None: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", "Taskfile.yml")],
            default_command="task hello",
        ),
    )

    observed: dict[str, str] = {}

    def _fake_run_command(
        checkout: Path,
        runner: str,
        command_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> int:
        observed["runner"] = runner
        observed["command_name"] = command_name
        if env_overrides:
            observed.update(env_overrides)
        return 0

    monkeypatch.setattr("thegent.phench.service.run_command", _fake_run_command)
    exit_code = run_target("module-run")
    assert exit_code == 0
    assert observed["runner"] == "task"
    assert observed["command_name"] == "hello"
    assert observed["FROM_PROFILE"] == "1"


def test_audit_shared_modules(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    _init_git_repo_with_pkg(repo_a, "sharedpkg")
    _init_git_repo_with_pkg(repo_b, "sharedpkg")

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))
    init_target("audity", mode="stack")
    add_repo("audity", repo_path=str(repo_a), selected_ref="HEAD", repo_id="a")
    add_repo("audity", repo_path=str(repo_b), selected_ref="HEAD", repo_id="b")

    result = audit_shared_modules("audity")
    assert result["shared_modules"]["sharedpkg"] == ["a", "b"]


def test_scan_shared_modules_across_repos_respects_excludes_and_minimum_repo_count(tmp_path: Path) -> None:
    phenotype_root = tmp_path / "Phenotype"
    repos_root = phenotype_root / "repos"
    repo_a = repos_root / "repo-a"
    repo_b = repos_root / "repo-b"
    repo_c = repos_root / "repo-c"
    repo_d = phenotype_root / "repos" / "4sgm"

    _init_git_repo_with_pkg(repo_a, "sharedpkg")
    _init_git_repo_with_pkg(repo_a, "exclusive-a")
    _init_git_repo_with_pkg(repo_b, "sharedpkg")
    _init_git_repo_with_pkg(repo_b, "bothrepos")
    _init_git_repo_with_pkg(repo_c, "sharedpkg")
    _init_git_repo_with_pkg(repo_c, "bothrepos")
    _init_git_repo_with_pkg(repo_d, "sharedpkg")

    result = scan_shared_modules_across_repos(
        repos_root=repos_root,
        exclude_repos={"repo-a"},
        min_repo_count=2,
    )
    assert result["shared_modules"] == {"bothrepos": ["repo-b", "repo-c"], "sharedpkg": ["repo-b", "repo-c"]}

    min3 = scan_shared_modules_across_repos(repos_root=repos_root, min_repo_count=3)
    assert min3["shared_modules"] == {"sharedpkg": ["repo-a", "repo-b", "repo-c"]}

    result_with_default = scan_shared_modules_across_repos(repos_root=repos_root, exclude_repos=set())
    assert "sharedpkg" in result_with_default["shared_modules"]
    assert "4sgm" not in result_with_default["examined_repos"]
    assert result_with_default["scan_schema_version"] == 1


def test_scan_shared_modules_across_repos_validates_exclude_ids(tmp_path: Path) -> None:
    phenotype_root = tmp_path / "Phenotype"
    repos_root = phenotype_root / "repos"
    repo_a = repos_root / "repo-a"

    _init_git_repo_with_pkg(repo_a, "sharedpkg")

    with pytest.raises(ValueError, match="exclude repo id cannot be blank"):
        scan_shared_modules_across_repos(
            repos_root=repos_root,
            exclude_repos={"   "},
        )

    with pytest.raises(ValueError, match="invalid repo id: repo/a"):
        scan_shared_modules_across_repos(
            repos_root=repos_root,
            exclude_repos={"repo/a"},
        )


def test_scan_shared_modules_across_repos_supports_worktree_root_mode(tmp_path: Path) -> None:
    phenotype_root = tmp_path / "Phenotype"
    worktrees_root = phenotype_root / "thegent-wtrees"
    repo_a = worktrees_root / "worktree-a"
    repo_b = worktrees_root / "worktree-b"
    _init_git_repo_with_pkg(repo_a, "sharedpkg")
    _init_git_repo_with_pkg(repo_b, "sharedpkg")

    result = scan_shared_modules_across_repos(
        repos_root=worktrees_root,
        min_repo_count=2,
        repos_root_mode="worktrees",
    )
    assert result["repos_root_mode"] == "worktrees"
    assert result["shared_modules"] == {"sharedpkg": ["worktree-a", "worktree-b"]}


def test_scan_shared_modules_cli_command(tmp_path: Path, monkeypatch) -> None:
    import importlib.util

    from typer.testing import CliRunner

    cli_module_path = Path(__file__).resolve().parents[1] / "packages/thegent-cli/src/thegent_cli/cli/apps/phench.py"
    spec = importlib.util.spec_from_file_location("phench_cli_scan_module", cli_module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load phench cli module")
    phench_cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phench_cli)

    monkeypatch.setattr(
        phench_cli,
        "scan_shared_modules_across_repos",
        lambda **kwargs: {
            "repos_root": str(kwargs.get("repos_root", "/tmp/repos")),
            "shared_modules": {"sharedpkg": ["repo-a", "repo-b"]},
            "shared_count": 1,
            "module_count": 2,
            "repo_count": 2,
            "excluded_repos": ["4sgm", "parpour"],
            "examined_repos": ["repo-a", "repo-b"],
            "min_repo_count": 2,
        },
    )

    result = CliRunner().invoke(
        phench_cli.app,
        [
            "scan-shared-repos",
            "--repos-root",
            str(tmp_path / "Phenotype" / "repos"),
            "--repos-root-mode",
            "repos",
            "--exclude",
            "repo-b",
            "--min-repos",
            "2",
            "--candidates",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["repos_root"] == str(tmp_path / "Phenotype" / "repos")
    assert payload["shared_modules"] == {"sharedpkg": ["repo-a", "repo-b"]}
    assert payload["module_candidates"][0]["module"] == "sharedpkg"


def test_cli_target_add_module_cmd_invokes_service(monkeypatch) -> None:
    import importlib.util

    from typer.testing import CliRunner

    cli_module_path = Path(__file__).resolve().parents[1] / "packages/thegent-cli/src/thegent_cli/cli/apps/phench.py"
    spec = importlib.util.spec_from_file_location("phench_cli_target_module", cli_module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load phench cli module")
    phench_cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phench_cli)

    observed: dict[str, str | set[str] | None] = {"name": None, "module": None, "ref": None, "exclude": set()}

    def _fake_add_module_to_target(
        name: str,
        module_name: str,
        selected_ref: str | None = None,
        exclude_repos: set[str] | None = None,
    ) -> TargetLock:
        observed["name"] = name
        observed["module"] = module_name
        observed["ref"] = selected_ref
        observed["exclude"] = exclude_repos or set()
        return TargetLock(
            schema_version=1,
            target_name=name,
            mode="stack",
            repos=[
                RepoSelection(
                    repo_id="repo-a",
                    repo_path="/tmp/repo-a",
                    selected_ref="HEAD",
                    module_name=module_name,
                )
            ],
            lock_hash="abc",
        )

    monkeypatch.setattr(phench_cli, "add_module_to_target", _fake_add_module_to_target)
    result = CliRunner().invoke(phench_cli.app, ["target", "add-module", "smoke", "--module", "thegent-app", "--ref", "dev", "--exclude", "skip-me"])
    assert result.exit_code == 0
    assert observed["name"] == "smoke"
    assert observed["module"] == "thegent-app"
    assert observed["ref"] == "dev"
    assert observed["exclude"] == {"skip-me"}
    payload = json.loads(result.output)
    assert payload["target"] == "smoke"
    assert payload["module"] == "thegent-app"
    assert payload["repos"] == ["repo-a"]
