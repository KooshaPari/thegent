from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from thegent.phench.service import (
    add_repo,
    audit_shared_modules,
    create_target_snapshot,
    bootstrap_target,
    load_module_manifest,
    list_modules,
    get_env_profile,
    discover_repos,
    init_target,
    import_repos,
    list_targets,
    list_target_snapshots,
    lock_target,
    materialize_target,
    show_target_snapshot,
    build_project_execution_matrix,
    set_repo_ref,
    run_env_doctor_for_target,
    run_target,
    target_timeline,
    target_status,
    set_env_profile,
    sync_target,
)
from thegent.phench.models import RunnerCatalog, RunnerCommand
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
    (path / "Taskfile.yml").write_text(
        "version: '3'\ntasks:\n  hello:\n    cmds:\n      - echo hello\n", encoding="utf-8"
    )
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


def test_list_targets_supports_family_filtering(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("one", mode="repo")
    init_target("two", mode="repo", family="acme")

    assert list_targets() == ["one", "acme/two"]
    assert list_targets(family="acme") == ["two"]


def test_list_modules_lists_directory_basenames_with_manifests(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    modules_root = phenotype_root / "projects" / "modules"
    (modules_root / "thegent-app").mkdir(parents=True, exist_ok=True)
    (modules_root / "platform-core").mkdir(parents=True, exist_ok=True)
    (modules_root / "legacy").mkdir(parents=True, exist_ok=True)
    (modules_root / "legacy" / "manifest.json").write_text("{}", encoding="utf-8")
    (modules_root / "thegent-app" / "manifest.json").write_text("{}", encoding="utf-8")
    (modules_root / "platform-core" / "manifest.json").write_text("{}", encoding="utf-8")

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))

    assert list_modules() == ["legacy", "platform-core", "thegent-app"]


def test_list_modules_missing_root_returns_empty(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    assert list_modules() == []


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
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    monkeypatch.setattr(
        "thegent.phench.service.build_runner_catalog",
        lambda target, repo_checkout: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", str(repo_checkout / "Taskfile.yml"))],
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
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    with pytest.raises(ValueError):
        run_target("stacky2", all_repos=True)


def test_run_target_with_snapshot_id_runs_from_snapshot_state(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "repo"
    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("snaprun", mode="repo")
    add_repo("snaprun", repo_path=str(source_repo), selected_ref="HEAD", repo_id="repo")
    lock_target("snaprun")
    materialize_target("snaprun")
    snapshot = create_target_snapshot("snaprun")

    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: (_ for _ in ()).throw(RuntimeError("unexpected live env doctor call")),
    )
    monkeypatch.setattr(
        "thegent.phench.service._run_env_doctor_for_materializations",
        lambda target, materializations, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )
    calls: list[str] = []
    monkeypatch.setattr(
        "thegent.phench.service.build_runner_catalog",
        lambda target, repo_checkout: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", str(repo_checkout / "Taskfile.yml"))],
            default_command="task hello",
        ),
    )

    def _fake_run_command(
        checkout: Path,
        runner: str,
        command_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> int:
        calls.append(str(checkout))
        return 0

    monkeypatch.setattr("thegent.phench.service.run_command", _fake_run_command)

    exit_code = run_target(
        "snaprun",
        snapshot_id=str(snapshot["snapshot_id"]),
        runner="task",
        command_name="hello",
    )
    assert exit_code == 0
    expected_checkout = str((phenotype_root / "projects" / "snaprun" / "repos" / "repo").resolve())
    assert calls == [expected_checkout]


def test_run_target_with_invalid_snapshot_runtime_fails(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "repo"
    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("snapbroken", mode="repo")
    add_repo("snapbroken", repo_path=str(source_repo), selected_ref="HEAD", repo_id="repo")
    lock_target("snapbroken")
    materialize_target("snapbroken")
    snapshot = create_target_snapshot("snapbroken")
    monkeypatch.setattr(
        "thegent.phench.service.show_target_snapshot",
        lambda target, snapshot_id, family=None: {"runtime": "bad-runtime", "lock": snapshot.get("lock", {})},
    )

    with pytest.raises(ValueError, match=r"snapshot '.*' has no runtime payload"):
        run_target("snapbroken", snapshot_id=str(snapshot["snapshot_id"]))


def test_run_target_with_invalid_snapshot_lock_fails(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "repo"
    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("snaplocked", mode="repo")
    add_repo("snaplocked", repo_path=str(source_repo), selected_ref="HEAD", repo_id="repo")
    lock_target("snaplocked")
    materialize_target("snaplocked")
    snapshot = create_target_snapshot("snaplocked")
    monkeypatch.setattr(
        "thegent.phench.service.show_target_snapshot",
        lambda target, snapshot_id, family=None: {
            "runtime": {"repo_materializations": [{"repo_id": "repo", "checkout_path": "repo"}]},
            "lock": "invalid-lock",
        },
    )

    with pytest.raises(ValueError, match=r"snapshot '.*' has invalid lock payload"):
        run_target("snaplocked", snapshot_id=str(snapshot["snapshot_id"]))


def test_run_target_ref_override_rematerializes_runtime_checkout(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo"
    _init_git_repo(repo)

    _run(["git", "-C", str(repo), "checkout", "-b", "feature"], cwd=repo)
    _run(["bash", "-lc", "printf '\\nfeature\\n' >> README.md"], cwd=repo)
    _run(["git", "-C", str(repo), "add", "README.md"], cwd=repo)
    _run(["git", "-C", str(repo), "commit", "-m", "feature"], cwd=repo)
    _run(["git", "-C", str(repo), "checkout", "main"], cwd=repo)

    feature_sha_proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "feature^{commit}"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert feature_sha_proc.returncode == 0
    feature_sha = feature_sha_proc.stdout.strip()

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("runref", mode="repo")
    add_repo("runref", repo_path=str(repo), selected_ref="main", repo_id="repo")
    lock_target("runref")
    materialize_target("runref")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    resolved_refs: list[str] = []
    materialize_calls: list[tuple[str, str, str]] = []

    def _recorded_resolve_ref(repo_path: Path, ref: str) -> str:
        resolved_refs.append(ref)
        proc = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", f"{ref}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        return proc.stdout.strip()

    monkeypatch.setattr("thegent.phench.service.resolve_ref_to_sha", _recorded_resolve_ref)
    monkeypatch.setattr(
        "thegent.phench.service.materialize_repo_checkout",
        lambda source_repo, checkout_path, resolved_sha: materialize_calls.append(
            (str(source_repo), str(checkout_path), resolved_sha),
        ),
    )
    monkeypatch.setattr(
        "thegent.phench.service.build_runner_catalog",
        lambda target, repo_checkout: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", str(repo_checkout / "Taskfile.yml"))],
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
        calls.append(f"{checkout.name}:{command_name}:{(checkout / '.git').exists()}")
        return 0

    monkeypatch.setattr("thegent.phench.service.run_command", _fake_run_command)

    exit_code = run_target("runref", runner="task", command_name="hello", selected_ref="feature")
    assert exit_code == 0
    assert resolved_refs == ["feature"]
    assert len(materialize_calls) == 1
    assert len(calls) == 1
    assert materialize_calls == [
        (
            str(repo),
            str((phenotype_root / "projects" / "runref" / "repos" / "repo").resolve()),
            feature_sha,
        )
    ]


def test_run_target_non_interactive_requires_explicit_runner_and_command(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo"
    _init_git_repo(repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("runnon", mode="repo")
    add_repo("runnon", repo_path=str(repo), selected_ref="HEAD", repo_id="repo")
    lock_target("runnon")
    materialize_target("runnon")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    with pytest.raises(ValueError, match="requires runner policy"):
        run_target("runnon", non_interactive=True)


def test_run_target_uses_repo_policy_runner_command_and_ref(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo-policy"
    _init_git_repo(repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("policy", mode="repo")
    add_repo(
        "policy",
        repo_path=str(repo),
        selected_ref="HEAD",
        repo_id="repo",
        preferred_runner="task",
        preferred_command="hello",
        preferred_ref="feature",
    )

    _run(["git", "-C", str(repo), "checkout", "-b", "feature"], cwd=repo)
    _run(["bash", "-lc", "printf '\\nfeature\\n' >> README.md"], cwd=repo)
    _run(["git", "-C", str(repo), "add", "README.md"], cwd=repo)
    _run(["git", "-C", str(repo), "commit", "-m", "feature"], cwd=repo)
    _run(["git", "-C", str(repo), "checkout", "main"], cwd=repo)

    lock_target("policy")
    materialize_target("policy")

    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    observed_ref: list[str] = []

    def _fake_resolve_ref(repo_path: Path, ref: str) -> str:
        observed_ref.append(ref)
        proc = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", f"{ref}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        return proc.stdout.strip()

    monkeypatch.setattr("thegent.phench.service.resolve_ref_to_sha", _fake_resolve_ref)
    monkeypatch.setattr(
        "thegent.phench.service.build_runner_catalog",
        lambda target, repo_checkout: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", str(repo_checkout / "Taskfile.yml"))],
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
        calls.append(f"{runner}:{command_name}")
        return 0

    monkeypatch.setattr("thegent.phench.service.run_command", _fake_run_command)

    exit_code = run_target("policy")
    assert exit_code == 0
    assert observed_ref == ["feature"]
    assert calls == ["task:hello"]


def test_run_target_all_repos_uses_policy_runner_when_allows_single_command_mode(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    _init_git_repo(repo_a)
    _init_git_repo(repo_b)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("policy-stack", mode="stack")
    add_repo(
        "policy-stack",
        repo_path=str(repo_a),
        selected_ref="HEAD",
        repo_id="a",
        preferred_runner="task",
        preferred_command="hello",
    )
    add_repo(
        "policy-stack",
        repo_path=str(repo_b),
        selected_ref="HEAD",
        repo_id="b",
        preferred_runner="task",
        preferred_command="hello",
    )
    lock_target("policy-stack")
    materialize_target("policy-stack")

    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )
    monkeypatch.setattr(
        "thegent.phench.service.build_runner_catalog",
        lambda target, repo_checkout: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", str(repo_checkout / "Taskfile.yml"))],
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
    exit_code = run_target("policy-stack", all_repos=True, execution_mode="serial")
    assert exit_code == 0
    assert sorted(calls) == ["a:task:hello", "b:task:hello"]


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
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    with pytest.raises(ValueError):
        run_target("delta", runner="task", command_name="--help")


def test_load_module_manifest_parses_patterns_and_overrides(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    modules_dir = phenotype_root / "projects" / "modules" / "thegent-app"
    modules_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "repo_patterns": ["thegent-*", "platform-*"],
        "repo_ref_overrides": {"thegent-api": "main"},
        "repo_runner_overrides": {"thegent-api": "task"},
        "repo_command_overrides": {"thegent-api": "hello"},
        "repo_env_profile_overrides": {"platform-core": "ci"},
    }
    (modules_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    loaded = load_module_manifest(
        "thegent-app",
        available_repo_ids=["thegent-api", "platform-core", "other"],
    )
    assert loaded["repo_ids"] == ["platform-core", "thegent-api"]
    assert loaded["repo_ref_overrides"] == {"thegent-api": "main"}
    assert loaded["repo_runner_overrides"] == {"thegent-api": "task"}
    assert loaded["repo_command_overrides"] == {"thegent-api": "hello"}
    assert loaded["repo_env_profile_overrides"] == {"platform-core": "ci"}


@pytest.mark.parametrize(
    "module_input",
    [
        "{module_dir}",
        "{module_dir}/manifest.json",
        "{legacy_module_dir}",
        "{relative_legacy_module_dir}",
    ],
)
def test_load_module_manifest_accepts_legacy_module_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module_input: str,
) -> None:
    phenotype_root = tmp_path / "Phenotype"
    legacy_modules_dir = phenotype_root / "projects" / "modules" / "thegent-app"
    modules_dir = phenotype_root / "projects" / "modules" / "legacy-layout"
    relative_modules_dir = Path("projects") / "modules" / "legacy-layout"

    modules_dir.mkdir(parents=True, exist_ok=True)
    legacy_modules_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "repo_ids": ["thegent-api"]}
    (legacy_modules_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (modules_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))

    candidate = module_input.format(
        module_dir=modules_dir,
        legacy_module_dir=legacy_modules_dir,
        relative_legacy_module_dir=relative_modules_dir,
    )
    loaded = load_module_manifest(candidate, available_repo_ids=["thegent-api"])
    assert loaded["repo_ids"] == ["thegent-api"]


def test_load_module_manifest_rejects_unknown_repo_override(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    modules_dir = phenotype_root / "projects" / "modules" / "thegent-app"
    modules_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "repo_ids": ["thegent-api"],
        "repo_ref_overrides": {"missing-repo": "main"},
    }
    (modules_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    with pytest.raises(ValueError, match="unknown repo_ref_overrides key"):
        load_module_manifest("thegent-app", available_repo_ids=["thegent-api"])


def test_load_module_manifest_rejects_unsupported_schema_version(
    tmp_path: Path,
    monkeypatch,
) -> None:
    phenotype_root = tmp_path / "Phenotype"
    modules_dir = phenotype_root / "projects" / "modules" / "thegent-app"
    modules_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 99, "repo_ids": ["thegent-api"]}
    (modules_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    with pytest.raises(ValueError, match="unsupported schema_version"):
        load_module_manifest("thegent-app", available_repo_ids=["thegent-api"])


def test_load_module_manifest_defaults_schema_version_when_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    phenotype_root = tmp_path / "Phenotype"
    modules_dir = phenotype_root / "projects" / "modules" / "thegent-app"
    modules_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"repo_ids": ["thegent-api"]}
    (modules_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    loaded = load_module_manifest("thegent-app", available_repo_ids=["thegent-api"])
    assert loaded["schema_version"] == 1


def test_run_target_respects_per_repo_env_profile_override(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    _init_git_repo(repo_a)
    _init_git_repo(repo_b)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("envprofile", mode="stack")
    add_repo(
        "envprofile",
        repo_path=str(repo_a),
        repo_id="repo-a",
        selected_ref="HEAD",
        preferred_runner="task",
        preferred_command="hello",
    )
    add_repo(
        "envprofile",
        repo_path=str(repo_b),
        repo_id="repo-b",
        selected_ref="HEAD",
        preferred_runner="task",
        preferred_command="hello",
    )
    lock_target("envprofile")
    materialize_target("envprofile")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    set_env_profile("envprofile", "ci-a", {"ENV": "A"})
    set_env_profile("envprofile", "ci-b", {"ENV": "B"})

    observed: dict[str, dict[str, str]] = {}

    def _fake_run_command(
        checkout: Path,
        runner: str,
        command_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> int:
        observed[checkout.name] = dict(env_overrides or {})
        return 0

    monkeypatch.setattr("thegent.phench.service.run_command", _fake_run_command)
    monkeypatch.setattr(
        "thegent.phench.service.build_runner_catalog",
        lambda target, repo_checkout: RunnerCatalog(
            target_name=target,
            runners_detected=["task"],
            commands=[RunnerCommand("task", "hello", "task hello", str(repo_checkout / "Taskfile.yml"))],
            default_command="task hello",
        ),
    )

    exit_code = run_target(
        "envprofile",
        repo_ids=["repo-a", "repo-b"],
        command_name="hello",
        repo_env_profile_overrides={"repo-a": "ci-a", "repo-b": "ci-b"},
    )
    assert exit_code == 0
    assert observed["repo-a"]["ENV"] == "A"
    assert observed["repo-b"]["ENV"] == "B"


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
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
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


def test_build_project_execution_matrix_returns_effective_plan(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    _init_git_repo(repo_a)
    _init_git_repo(repo_b)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("matrix", mode="stack")
    add_repo(
        "matrix",
        repo_path=str(repo_a),
        selected_ref="HEAD",
        preferred_runner="task",
        preferred_command="hello",
        repo_id="repo-a",
    )
    add_repo(
        "matrix",
        repo_path=str(repo_b),
        selected_ref="HEAD",
        preferred_runner="task",
        preferred_command="hello",
        repo_id="repo-b",
    )
    lock = lock_target("matrix")
    materialize_target("matrix")
    set_env_profile("matrix", "ci", {"ENV": "one"})
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    matrix = build_project_execution_matrix(
        "matrix",
        repo_id="repo-a",
        runner="task",
        command_name="hello",
        env_profile="ci",
    )

    assert matrix["target"] == "matrix"
    assert matrix["lock_hash"] == lock.lock_hash
    assert matrix["snapshot_hash"] is None
    assert matrix["runtime_hash"] is None
    assert matrix["repo_count"] == 1
    plan = matrix["repos"][0]
    assert plan["repo_id"] == "repo-a"
    assert plan["effective_runner"] == "task"
    assert plan["effective_command"] == "hello"
    assert plan["effective_env_profile"] == "ci"
    assert plan["env_overrides"] == {"ENV": "one"}
    assert plan["effective_ref_source"] == "selected_ref"
    assert plan["resolved_sha"] is not None


def test_build_project_execution_matrix_prefers_repo_override_then_cli_then_preferred_ref(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    _init_git_repo(repo_a)
    _run(["bash", "-lc", "printf '\nchange' >> README.md"], cwd=repo_a)
    _run(["git", "-C", str(repo_a), "add", "README.md"], cwd=repo_a)
    _run(["git", "-C", str(repo_a), "commit", "-m", "change"], cwd=repo_a)

    sha_before_proc = subprocess.run(
        ["git", "-C", str(repo_a), "rev-parse", "HEAD~1"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert sha_before_proc.returncode == 0
    sha_before = sha_before_proc.stdout.strip()
    sha_current_proc = subprocess.run(
        ["git", "-C", str(repo_a), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert sha_current_proc.returncode == 0
    sha_current = sha_current_proc.stdout.strip()
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("matrix_ref", mode="stack")
    add_repo(
        "matrix_ref",
        repo_path=str(repo_a),
        selected_ref=sha_current,
        preferred_ref=sha_before,
        repo_id="repo-a",
    )
    lock_target("matrix_ref")
    materialize_target("matrix_ref")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    override_matrix = build_project_execution_matrix(
        "matrix_ref",
        repo_id="repo-a",
        repo_ref_overrides={"repo-a": "HEAD"},
    )
    assert override_matrix["repos"][0]["effective_ref_source"] == "repo_override"
    assert override_matrix["repos"][0]["effective_ref"] == "HEAD"

    cli_matrix = build_project_execution_matrix(
        "matrix_ref",
        repo_id="repo-a",
        selected_ref=sha_before,
    )
    assert cli_matrix["repos"][0]["effective_ref_source"] == "cli_ref"
    assert cli_matrix["repos"][0]["effective_ref"] == sha_before

    preferred_matrix = build_project_execution_matrix(
        "matrix_ref",
        repo_id="repo-a",
    )
    assert preferred_matrix["repos"][0]["effective_ref_source"] == "preferred_ref"
    assert preferred_matrix["repos"][0]["effective_ref"] == sha_before


def test_build_project_execution_matrix_applies_repo_overrides_and_sorting(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    _init_git_repo(repo_a)
    _init_git_repo(repo_b)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("matrix2", mode="stack")
    add_repo("matrix2", repo_path=str(repo_a), selected_ref="HEAD", repo_id="repo-a")
    add_repo("matrix2", repo_path=str(repo_b), selected_ref="HEAD", repo_id="repo-b")
    lock_target("matrix2")
    materialize_target("matrix2")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )
    matrix = build_project_execution_matrix(
        "matrix2",
        all_repos=True,
        runner="task",
        repo_runner_overrides={"repo-b": "task"},
        repo_command_overrides={"repo-a": "hello"},
        repo_ref_overrides={"repo-a": "HEAD"},
        sort_repos=True,
    )

    assert matrix["all_repos"] is True
    assert matrix["repo_count"] == 2
    assert [item["repo_id"] for item in matrix["repos"]] == ["repo-a", "repo-b"]
    assert matrix["repos"][0]["effective_runner"] == "task"
    assert matrix["repos"][0]["effective_command"] == "hello"
    assert matrix["repos"][1]["effective_runner"] == "task"
    assert matrix["repos"][1]["effective_command"] is None
    assert matrix["repos"][0]["resolved_sha"] is not None
    assert matrix["repos"][1]["resolved_sha"] is not None


def test_build_project_execution_matrix_rejects_missing_override_repo(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo"
    _init_git_repo(repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("matrix3", mode="repo")
    add_repo("matrix3", repo_path=str(repo), selected_ref="main", repo_id="repo")
    lock_target("matrix3")
    materialize_target("matrix3")
    monkeypatch.setattr(
        "thegent.phench.service.run_env_doctor_for_target",
        lambda target, family=None: {"doctor_status": "pass", "missing_requirements": []},
    )

    with pytest.raises(ValueError, match="repo_id not materialized"):
        build_project_execution_matrix(
            "matrix3",
            repo_ids=["repo"],
            repo_ref_overrides={"missing": "main"},
        )


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


def test_discover_repos_filters_by_include_and_exclude(tmp_path: Path, monkeypatch) -> None:
    repos_root = tmp_path / "repos"
    repo_alpha = repos_root / "alpha-repo"
    repo_beta = repos_root / "beta-repo"
    hidden_repo = repos_root / ".hidden-repo"
    non_git = repos_root / "norepo"

    _init_git_repo(repo_alpha)
    _init_git_repo(repo_beta)
    non_git.mkdir(parents=True, exist_ok=True)
    hidden_repo.mkdir(parents=True, exist_ok=True)
    (hidden_repo / ".git").mkdir()

    monkeypatch.setenv("THGENT_PHENOTYPE_REPOS_ROOT", str(repos_root))

    candidates = discover_repos(include=["*-repo"], exclude=["*beta*"])
    assert [item.repo_id for item in candidates] == ["alpha-repo"]


def test_import_repos_adds_discovered_repos(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repos_root = tmp_path / "repos"
    repo_alpha = repos_root / "alpha-repo"
    repo_beta = repos_root / "beta-repo"

    _init_git_repo(repo_alpha)
    _init_git_repo(repo_beta)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("imported", mode="stack")
    lock = import_repos("imported", source_root=repos_root, include=["*-repo"], auto_lock=True)
    repo_ids = [repo.repo_id for repo in lock.repos]
    assert set(repo_ids) == {"alpha-repo", "beta-repo"}
    assert all(repo.resolved_sha is not None for repo in lock.repos)


def test_import_repos_with_filter_no_candidates_raises(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repos_root = tmp_path / "repos"

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("empty", mode="stack")

    with pytest.raises(ValueError, match="no repos discovered"):
        import_repos("empty", source_root=repos_root, include=["*.repo"])


def test_import_repos_supports_repo_filter_without_lock(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repos_root = tmp_path / "repos"
    repo_alpha = repos_root / "alpha-repo"
    repo_beta = repos_root / "beta-repo"

    _init_git_repo(repo_alpha)
    _init_git_repo(repo_beta)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("imported2", mode="stack")
    lock = import_repos(
        "imported2",
        source_root=repos_root,
        repo_ids=["alpha-repo"],
        include=["*-repo"],
        auto_lock=False,
    )
    assert [repo.repo_id for repo in lock.repos] == ["alpha-repo"]
    assert lock.repos[0].resolved_sha is None


def test_create_target_snapshot_and_list_show_work_together(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "source-repo"

    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("snapshot", mode="repo")
    add_repo("snapshot", repo_path=str(source_repo), selected_ref="HEAD")
    lock = lock_target("snapshot")
    materialize_target("snapshot")

    created = create_target_snapshot("snapshot", snapshot_id="custom-id")
    second = create_target_snapshot("snapshot", snapshot_id="custom-id-2")

    assert created["snapshot_id"] == "custom-id"
    assert created["target"] == "snapshot"
    assert isinstance(created["written_at_utc"], str)

    snapshots = list_target_snapshots("snapshot")
    assert {entry["snapshot_id"] for entry in snapshots} == {"custom-id", "custom-id-2"}

    payload = show_target_snapshot("snapshot", "custom-id")
    assert payload["snapshot_id"] == "custom-id"
    assert payload["target_name"] == "snapshot"
    assert payload["lock"]["lock_hash"] == lock.lock_hash
    assert payload["runtime_hash"] != ""
    assert payload["snapshot_hash"] != ""

    assert second["filename"] == "snapshots/custom-id-2.json"


def test_create_and_list_snapshots_are_family_scoped(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "source-repo"

    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("snapshot2", mode="repo", family="acme")
    add_repo("snapshot2", family="acme", repo_path=str(source_repo), selected_ref="HEAD")
    lock = lock_target("snapshot2", family="acme")
    materialize_target("snapshot2", family="acme")

    created = create_target_snapshot("snapshot2", family="acme", snapshot_id="family-id")
    assert created["snapshot_id"] == "family-id"
    assert created["target"] == "snapshot2"

    snapshots = list_target_snapshots("snapshot2", family="acme")
    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot["snapshot_id"] == "family-id"
    assert snapshot["filename"] == "snapshots/family-id.json"
    assert snapshot["target_name"] == "snapshot2"
    assert snapshot["lock_hash"] == lock.lock_hash
    assert snapshot["runtime_hash"] != ""
    assert snapshot["snapshot_hash"] != ""
    assert list_target_snapshots("snapshot2") == []

    payload = show_target_snapshot("snapshot2", "family-id", family="acme")
    assert payload["snapshot_id"] == "family-id"
    assert payload["lock"]["lock_hash"] == lock.lock_hash


def test_target_status_includes_snapshot_provenance_summary(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    source_repo = tmp_path / "source-repo"

    _init_git_repo(source_repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("snapshot-status", mode="repo")
    add_repo("snapshot-status", repo_path=str(source_repo), selected_ref="HEAD")
    lock = lock_target("snapshot-status")
    materialize_target("snapshot-status")
    create_target_snapshot("snapshot-status", snapshot_id="custom-id")
    snapshot_payload = show_target_snapshot("snapshot-status", "custom-id")

    status = target_status("snapshot-status")
    assert status["latest_snapshot"] is not None
    assert status["latest_snapshot"]["snapshot_id"] == "custom-id"
    assert status["latest_snapshot"]["lock_hash"] == lock.lock_hash
    assert status["latest_snapshot"]["runtime_hash"] == snapshot_payload["runtime_hash"]
    assert status["latest_snapshot"]["snapshot_hash"] == snapshot_payload["snapshot_hash"]


def test_bootstrap_target_uses_discovered_repos(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repos_root = tmp_path / "repos"
    repo_alpha = repos_root / "alpha-repo"
    repo_beta = repos_root / "beta-repo"
    _init_git_repo(repo_alpha)
    _init_git_repo(repo_beta)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    lock = bootstrap_target(
        "bootstrap",
        mode="stack",
        source_root=repos_root,
        include=["*-repo"],
        auto_lock=True,
    )
    assert [repo.repo_id for repo in lock.repos] == ["alpha-repo", "beta-repo"]


def test_set_repo_ref_updates_target_selection_and_relocks(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo"
    _init_git_repo(repo)
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    init_target("setref", mode="repo")
    lock = add_repo("setref", repo_path=str(repo), selected_ref="HEAD")
    lock = lock_target("setref")
    original = lock.repos[0].resolved_sha
    repo_id = lock.repos[0].repo_id

    _run(["bash", "-lc", f"printf '\\nchange' >> {repo / 'README.md'}"], cwd=repo)
    _run(["git", "-C", str(repo), "add", "README.md"], cwd=repo)
    _run(["git", "-C", str(repo), "commit", "-m", "change"], cwd=repo)

    previous = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD~1"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert previous.returncode == 0
    previous_sha = previous.stdout.strip()

    updated = set_repo_ref("setref", repo_id=repo_id, selected_ref="HEAD~1")
    assert updated.repos[0].selected_ref == "HEAD~1"
    assert updated.repos[0].resolved_sha == previous_sha
    assert updated.repos[0].resolved_sha == original


def test_target_timeline_supports_branch_filter(tmp_path: Path, monkeypatch) -> None:
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    repo = tmp_path / "repo"

    _init_git_repo(repo)
    _run(["git", "-C", str(repo), "checkout", "-b", "feature"], cwd=repo)
    _run(["bash", "-lc", f"printf '\\nfeature' >> {repo / 'README.md'}"], cwd=repo)
    _run(["git", "-C", str(repo), "add", "README.md"], cwd=repo)
    _run(["git", "-C", str(repo), "commit", "-m", "feature"], cwd=repo)

    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))
    init_target("timeline", mode="repo")
    add_repo("timeline", repo_path=str(repo), selected_ref="HEAD")
    lock_target("timeline")

    default_timeline = target_timeline("timeline", limit=5)
    assert default_timeline["target"] == "timeline"
    assert default_timeline["selected_ref"] == "HEAD"
    assert default_timeline["branch_exists"] is False
    assert default_timeline["branch"] is None

    feature_timeline = target_timeline("timeline", branch="feature", limit=5)
    assert feature_timeline["selected_ref"] == "feature"
    assert feature_timeline["branch"] == "feature"
    assert feature_timeline["branch_exists"] is True

    with pytest.raises(ValueError, match="unknown branch"):
        target_timeline("timeline", branch="missing")
