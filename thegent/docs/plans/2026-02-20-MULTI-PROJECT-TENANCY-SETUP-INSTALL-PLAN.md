# Plan: Multi-Project Tenancy + AG-DD Template Spawning (2026-02-20)

## 1. Objective

Add first-class project tenancy to Thegent with two human-facing commands:

1. `thegent sys setup project` for project registration + tenancy bootstrapping.
2. `thegent install project` for installing project-local runtime assets and optional template scaffolding.

Scope also includes template spawning for `ag-dd` (Project AG-DD).

## 2. Current State (Codebase Inventory)

Existing primitives we should reuse:

1. `src/thegent/infra/project_registry.py`
   - Hierarchy DB (`products`, `milestones`, `sprints`, `tasks`, `episodes`) in `~/.thegent/registry.db`.
2. `src/thegent/security/tenancy.py`
   - `KeyIsolator` supports isolated key directories by owner under `~/.thegent/.../tenants/<owner>`.
3. `src/thegent/cross_platform/coordination.py`
   - Basic tenant isolation path helper for `~/.thegent/tenants/<tenant_id>`.
4. `src/thegent/cli/commands/cli.py`
   - `project_register_cmd` + `project_list_cmd` (jsonl-based, not yet integrated into apps stream).
5. `templates/initialize-project/`
   - Existing project bootstrap template area.
6. `src/thegent/install.py`
   - Install pipeline + target handling already in place.
7. `src/thegent/cli/apps/sys.py`
   - Existing `sys setup` command entrypoint.
8. `src/thegent/cli/apps/main.py`
   - Existing top-level `install` compatibility entrypoint.

## 3. Command Design (Human-Facing)

### 3.1 `thegent sys setup project`

Purpose: Register current/new project as a tenant and initialize project metadata.

Proposed subcommands:

1. `thegent sys setup project init`
   - Inputs:
     - `--name <name>` required logical project name.
     - `--path <path>` default `cwd`.
     - `--tenant <tenant_id>` optional (default slug(name)).
     - `--product <product_name>` optional registry product seed.
     - `--template ag-dd|none` default `none`.
     - `--json` optional structured output.
   - Effects:
     - Ensure tenant root: `~/.thegent/tenants/<tenant_id>/`.
     - Register project mapping in a canonical JSON registry file.
     - Create or link product in `ProjectRegistry`.
     - Optionally scaffold AG-DD template.

2. `thegent sys setup project list`
   - Show registered projects with tenant, path, product_id, created_at.

3. `thegent sys setup project show <project|tenant>`
   - Detailed view: tenancy paths, registry linkage, template version.

4. `thegent sys setup project doctor [--fix]`
   - Validate required files and links; optional repair.

### 3.2 `thegent install project`

Purpose: Install project-local Thegent runtime assets into an existing registered project.

Flags:

1. `--project <name|tenant|path>` selector (default current path).
2. `--template ag-dd|none` optional overlay.
3. `--mode smart|overwrite|skip` mirrors install semantics.
4. `--dry-run` preview changes.
5. `--json` machine-readable summary.

Install payload:

1. `.thegent/config.yaml` (project tenancy metadata + defaults).
2. `.thegent/ownership.json` (owner/tenant policy stub).
3. `.thegent/templates.lock` (template/version lock).
4. Project-local hooks/quality scripts symlink/copy policy (explicit, no fallback).

## 4. Data Model

Add canonical project tenancy registry:

1. File: `~/.thegent/projects/registry.json`
2. Schema:
   - `project_id`
   - `name`
   - `tenant_id`
   - `path`
   - `product_id`
   - `template` (`ag-dd|none`)
   - `template_version`
   - `created_at`
   - `updated_at`

Rationale:

1. Replaces ad-hoc `projects.jsonl` flows.
2. Enables deterministic lookup by name, tenant, or path.
3. Supports strict validation and future migrations.

## 5. AG-DD Template Spec

Template identifier: `ag-dd`

Target output (minimum):

1. `AGENTS.md` (project-local agent contract).
2. `PLAN.md`, `PRD.md`, `FUNCTIONAL_REQUIREMENTS.md`, `USER_JOURNEYS.md` from specs templates.
3. `docs/reference/WORK_STREAM.md` seed aligned to Thegent format.
4. `Taskfile.yml` and quality includes aligned with `templates/shared`.
5. `.thegent/config.yaml` with tenancy/project identifiers.

Template source layout:

1. New: `templates/projects/ag-dd/` (explicit, versioned).
2. Manifest: `template.manifest.json`
   - file list
   - render variables
   - post-install checks

No fallback behavior:

1. If required template file missing, command fails with explicit error.
2. If destination conflict in `smart` mode, report conflict and exit non-zero unless `--mode overwrite`.

## 6. Integration Points (Implementation Targets)

1. `src/thegent/cli/apps/sys.py`
   - Add `setup project` sub-typer.
2. `src/thegent/cli/apps/main.py`
   - Extend top-level `install` with project pathway or add dedicated `project` install route.
3. `src/thegent/install.py`
   - Add `run_install_project(...)`.
4. `src/thegent/infra/`
   - Add `project_tenancy_registry.py`.
5. `src/thegent/templates/` or `src/thegent/project_init/`
   - Add template renderer + manifest validation.
6. Tests:
   - `tests/cli/apps/test_sys_setup_project.py`
   - `tests/install/test_install_project.py`
   - `tests/infra/test_project_tenancy_registry.py`

## 7. Phased WBS (DAG)

| Phase | Task ID | Description | Depends On | Agent Effort |
|---|---|---|---|---|
| P1 Discovery | MP-01 | Validate existing setup/install/project code paths and remove dead duplicates from execution path | - | 5-8 tool calls, 2-4 min |
| P1 Discovery | MP-02 | Finalize command contract and JSON schema | MP-01 | 4-6 tool calls, 2-3 min |
| P2 Core | MP-03 | Implement `project_tenancy_registry.py` read/write/lookup API | MP-02 | 8-12 tool calls, 4-7 min |
| P2 Core | MP-04 | Implement AG-DD template manifest loader + renderer | MP-02 | 8-12 tool calls, 4-7 min |
| P2 Core | MP-05 | Add `thegent sys setup project init/list/show/doctor` CLI wiring | MP-03 | 8-12 tool calls, 4-7 min |
| P2 Core | MP-06 | Add `thegent install project` CLI + `run_install_project` | MP-03, MP-04 | 10-15 tool calls, 5-9 min |
| P3 Validation | MP-07 | Add unit tests for registry + template + CLI parsing | MP-05, MP-06 | 10-16 tool calls, 6-10 min |
| P3 Validation | MP-08 | Add integration tests for `init -> install project` happy path + conflict path | MP-07 | 8-12 tool calls, 4-8 min |
| P4 Rollout | MP-09 | Update docs and CLI examples for tenancy and AG-DD flows | MP-08 | 4-8 tool calls, 2-4 min |

Total expected wall clock (agent): 30-55 min in 2-3 focused batches.

## 8. Acceptance Criteria

1. `thegent sys setup project init --name X` creates canonical project record and tenancy root.
2. `thegent sys setup project list` and `show` resolve by name, tenant, and path.
3. `thegent install project --project X --template ag-dd` materializes AG-DD template and writes template lock.
4. Conflict behavior is explicit and deterministic across `smart|overwrite|skip`.
5. Tests cover happy path + conflict + missing-template hard-fail.
6. No legacy fallback import paths are introduced.

## 9. Example UX

```bash
# Register and initialize project tenancy
thegent sys setup project init --name ag-dd-core --tenant agdd --template ag-dd

# Verify
thegent sys setup project show ag-dd-core

# Install local runtime assets into this project
thegent install project --project ag-dd-core --mode smart

# Health check
thegent sys setup project doctor --fix
```

## 10. Risks and Mitigations

1. Risk: Duplicate project registries (`projects.jsonl` vs new registry).
   - Mitigation: Single canonical registry and one-time migration command.
2. Risk: Template drift across repos.
   - Mitigation: manifest lock + template version pin.
3. Risk: Path collisions in multi-tenant local setup.
   - Mitigation: strict `tenant_id` sanitization and explicit duplicate detection.
