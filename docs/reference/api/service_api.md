# service API Reference

> **Source**: `src/thegent/phench/service.py`

## add_module_to_target

```python
add_module_to_target(target: str, module_name: str, selected_ref: Any, exclude_repos: Any, family: Any) -> TargetLock
```

---

## add_repo

```python
add_repo(target: str, repo_path: str, selected_ref: str, repo_id: Any, worktree_path: Any, module_name: Any, selected_runner: Any, selected_command: Any, selected_env_profile: Any, preferred_runner: Any, preferred_command: Any, preferred_ref: Any, family: Any) -> TargetLock
```

---

## audit_shared_modules

```python
audit_shared_modules(target: str, family: Any) -> dict[(str, Any)]
```

---

## audit_shared_modules_across_repos

---

## bootstrap_target

```python
bootstrap_target(target: str, mode: TargetMode, family: Any, source_root: Any, selected_ref: str, preferred_runner: Any, preferred_command: Any, preferred_ref: Any, include: Any, exclude: Any, repo_ids: Any, auto_lock: bool)
```

Create a target and add discovered repositories from a workspace.

---

## build_catalog

```python
build_catalog(target: str, repo_id: Any, family: Any) -> RunnerCatalog
```

---

## build_module_manifest_payload

```python
build_module_manifest_payload(module_name: str, repo_ids: list[str]) -> dict[(str, Any)]
```

---

## build_project_execution_matrix

```python
build_project_execution_matrix(target: str, family: Any, snapshot_id: Any, repo_id: Any, repo_ids: Any, repo_ref_overrides: Any, repo_runner_overrides: Any, repo_command_overrides: Any, repo_env_profile_overrides: Any, runner: Any, command_name: Any, selected_ref: Any, all_repos: bool, env_profile: Any, non_interactive: bool, validate_commands: bool, sort_repos: bool) -> dict[(str, Any)]
```

---

## build_scan_candidates

```python
build_scan_candidates(shared_modules: dict[(str, list[str])]) -> list[dict[(str, Any)]]
```

---

## create_target_snapshot

```python
create_target_snapshot(target: str, family: Any, snapshot_id: Any) -> dict[(str, Any)]
```

---

## discover_repos

```python
discover_repos(root: Any, include: Any, exclude: Any)
```

Discover available local repositories for bootstrap workflows.

---

## get_env_profile

```python
get_env_profile(target: str, profile: Any, family: Any) -> dict[(str, str)]
```

---

## import_repos

```python
import_repos(target: str, family: Any, source_root: Any, selected_ref: str, preferred_runner: Any, preferred_command: Any, preferred_ref: Any, include: Any, exclude: Any, repo_ids: Any, auto_lock: bool)
```

Import discovered repositories into an existing target.

---

## init_target

```python
init_target(target: str, mode: TargetMode, family: Any) -> TargetLock
```

---

## list_modules

---

## list_target_snapshots

```python
list_target_snapshots(target: str, family: Any) -> list[dict[(str, Any)]]
```

---

## list_targets

```python
list_targets(family: Any) -> list[str]
```

---

## load_module_manifest

```python
load_module_manifest(module: str) -> dict[(str, Any)]
```

---

## load_module_repos

```python
load_module_repos(module: str) -> list[str]
```

---

## load_target_lock

```python
load_target_lock(target: str, family: Any) -> TargetLock
```

---

## lock_target

```python
lock_target(target: str, family: Any) -> TargetLock
```

---

## materialize_module_candidate_manifest

```python
materialize_module_candidate_manifest(module: str) -> dict[(str, Any)]
```

---

## materialize_scan_candidate_manifest

```python
materialize_scan_candidate_manifest(candidate: dict[(str, Any)]) -> dict[(str, Any)]
```

---

## materialize_target

```python
materialize_target(target: str, family: Any) -> RuntimeState
```

---

## run_env_doctor_for_target

```python
run_env_doctor_for_target(target: str, family: Any) -> dict[(str, Any)]
```

---

## run_target

```python
run_target(target: str, family: Any, snapshot_id: Any, repo_id: Any, repo_ids: Any, repo_ref_overrides: Any, repo_runner_overrides: Any, repo_command_overrides: Any, repo_env_profile_overrides: Any, runner: Any, command_name: Any, selected_ref: Any, all_repos: bool, execution_mode: str, env_profile: Any, non_interactive: bool) -> int
```

---

## scan_shared_modules_across_repos

```python
scan_shared_modules_across_repos(repos_root: Any) -> dict[(str, Any)]
```

---

## set_env_profile

```python
set_env_profile(target: str, profile: str, values: dict[(str, str)], family: Any) -> dict[(str, Any)]
```

---

## set_repo_ref

```python
set_repo_ref(target: str, repo_id: str, selected_ref: str, family: Any)
```

Update a single repo selection ref in a target and relock the target.

---

## show_target_snapshot

```python
show_target_snapshot(target: str, snapshot_id: str, family: Any) -> dict[(str, Any)]
```

---

## sync_project_modules_from_repos

---

## sync_target

```python
sync_target(target: str, prefer: Any, family: Any) -> dict[(str, Any)]
```

---

## target_status

```python
target_status(target: str, family: Any) -> dict[(str, Any)]
```

---

## target_timeline

```python
target_timeline(target: str, family: Any, repo_id: Any, limit: int, branch: Any) -> dict[(str, Any)]
```

---

