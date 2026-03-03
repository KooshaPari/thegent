# `scan-shared-repos` Output Contract (v1)

## Command

`scan-shared-repos` returns one JSON object and supports:

- `--repos-root`: path to scan source
- `--repos-root-mode`: `repos` (default) or `worktrees`
- `--exclude`: repeated exclusions
- `--min-repos`: minimum repo overlap threshold
- `--candidates`: include candidate manifest templates in output
- `--recommended`: always returns sorted overlap recommendations in `recommended_modules`

## Safety and Dry-Run Guidance

- `scan-shared-repos` uses default excludes (`4sgm`, `parpour`, `civ`, `trace`) unless explicitly overridden.
- Use `materialize-module-manifest --dry-run` to validate generated manifest paths and payloads before writing files.
- Keep `--min-repos`/`--min-count` explicitly at or above `2`.
- Use `--print-snippets` to print reproducible commands for creating a stack target.

## JSON Payload

Top-level keys are stable for API consumers:

- `scan_schema_version`: integer contract version (currently `1`)
- `repos_root`: resolved root path used for scanning
- `repos_root_mode`: one of `repos` or `worktrees`
- `shared_modules`: map of module name to sorted repo-id array
- `shared_count`: number of shared modules
- `module_count`: number of unique modules discovered in the scan path
- `repo_count`: number of repos included after exclusion and mode filtering
- `excluded_repos`: sorted list of repos excluded by default or explicit flags
- `examined_repos`: sorted list of repos that contributed module discoveries
- `min_repo_count`: minimum overlap value used to classify a module as shared
- `recommended_modules`: up to 10 module recommendations sorted by descending overlap count

`recommended_modules` contains:

- `module`: module name
- `repo_count`: number of matching repos
- `repo_ids`: repo identifiers sorted alphabetically

### Example workflow

```bash
# 1) Discover shared modules and render candidate manifests.
thegent phench scan-shared-repos --repos-root /path/to/Phenotype/repos --candidates

# 2) Materialize a manifest candidate in preview mode before writing disk.
thegent phench materialize-module-manifest --module sharedpkg --repos-root /path/to/Phenotype/repos --repo shared-repo-1 --repo shared-repo-2 --min-count 2 --dry-run

# 3) Generate commands to bootstrap a stack target for this module.
thegent phench materialize-module-manifest --module sharedpkg --repos-root /path/to/Phenotype/repos --repo shared-repo-1 --repo shared-repo-2 --min-count 2 --print-snippets
```

### `--candidates` payload

When `--candidates` is enabled, each entry in `module_candidates` has:

- `module`: module name
- `module_name`: generated manifest folder name
- `repo_ids`: sorted repo ids that contain the module
- `repo_count`: size of `repo_ids`
- `manifest_template`: minimal module manifest scaffold for this candidate

`manifest_template` currently contains:

- `schema_version` (currently `1`)
- `repo_patterns` (sorted selected repos)
- `default_ref` (currently `"HEAD"`)
- `repo_ref_overrides`
- `repo_runner_overrides`
- `repo_command_overrides`
- `repo_env_profile_overrides`
- `matched_repos`: same value as `repo_ids`

### Candidate naming

- Generated candidate manifest names follow: `shared-module-<module>-<repo-count>`.
- Names are lowercased, punctuation is replaced with `-`, duplicates append a stable
  8-char suffix, and names are truncated to 60 chars.

## `--repos-root-mode`

- `repos`: scan directories under `<THGENT_PHENOTYPE_ROOT>/repos` or explicit `--repos-root`
  as sibling repo roots.
- `worktrees`: scan worktree-style layouts where each child directory is a repo candidate
  (or the explicit `--repos-root` itself if it already points to a checkout with `src`).

## Error Semantics

- `exclude` entries are validated:
  - blank values are rejected
  - whitespace-only values are rejected
  - malformed repo IDs are rejected
