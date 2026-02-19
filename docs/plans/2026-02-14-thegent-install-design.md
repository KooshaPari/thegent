# Design: thegent install CLI Command

**Date:** 2026-02-14
**Status:** Approved
**Merged into:** [UNIFIED_SYSTEM_APPLICATION_PLAN.md](./UNIFIED_SYSTEM_APPLICATION_PLAN.md) — install is Phase 1 of unified setup

## Purpose

1-click persistent installation and synchronization of all Claude Code configuration from thegent codebase to `~/.claude` and `~/.factory`.

## Command Interface

```
thegent install [OPTIONS]

Options:
  -t, --target TARGET     Target: claude|factory|both (default: both)
  -e, --editable          Symlink install instead of copy (bi-directional sync)
  -f, --force             Overwrite all files (no merge)
  -n, --dry-run           Show what would happen without making changes
  -v, --verbose           Show detailed progress
  -h, --help              Show this message and exit
```

## Source → Destination Mapping

### Primary: thegent → ~/.claude / ~/.factory

| Source (thegent) | Destination |
|------------------|-------------|
| `skills/*` | `~/.claude/skills/` |
| `hooks/*` | `~/.claude/hooks/` |
| `templates/*` | `~/.claude/templates/` |
| `CLAUDE.md` (root) | `~/.claude/CLAUDE.md` |
| `mcp_servers.json` | `~/.claude/mcp_servers.json` |
| `qa-config.json` | `~/.claude/qa-config.json` |
| `agents/*` | `~/.claude/agents/` |
| `commands/*` | `~/.claude/commands/` |
| `contracts/*` | `~/.claude/contracts/` |
| `.claude/plugins/*` | `~/.claude/plugins/` |
| `.factory/hooks/*` | `~/.factory/hooks/` |
| `.factory/skills/*` | `~/.factory/skills/` |
| `.factory/commands/*` | `~/.factory/commands/` |
| `.factory/droids/*` | `~/.factory/droids/` |
| `.factory/plugins/*` | `~/.factory/plugins/` |
| `.factory/mcp.json` | `~/.factory/mcp.json` |
| `.factory/config.json` | `~/.factory/config.json` |
| `.factory/settings.json` | `~/.factory/settings.json` |

### Skills to Sync

Only `skills/agent-orchestra` is synced (unified orchestration - no need for separate codex/cursor/copilot/gemini/droid skills as agent-orchestra covers all via thegent).

## Behavior Modes

### Default (Smart Copy)
1. **First run**: Copy all files
2. **Subsequent runs**:
   - For each file, compare modification times
   - If `target_mtime > source_mtime`: skip (user modified)
   - If `target_mtime <= source_mtime`: update from source
   - If target doesn't exist: copy from source

### Editable Mode (--editable/-e)
- Create symlinks from target → source
- Live bi-directional sync (edits in either location reflect in both)
- Useful for development

### Force Mode (--force/-f)
- Overwrite all files regardless of modification time
- User changes are lost

### Dry Run Mode (--dry-run)
- Show what would happen without making any changes
- Print list of: files to copy, files to skip, conflicts

## Conflict Resolution

When a file exists in both source and target but differs:

| Mode | Behavior |
|------|----------|
| default (smart) | Keep user version, backup source to `~/.claude/.thegent-backup/{timestamp}/` |
| `--editable` | Symlink (overwrites existing) |
| `--force` | Overwrite with source |
| `--interactive` | Show diff, ask per-file (future enhancement) |

## Implementation Details

### File: `src/thegent/cli_impl.py` or new `src/thegent/install.py`

Core function: `run_install(targets, mode, dry_run, verbose)`

### Key Functions

1. `get_source_dest_mapping(thegent_root, target)` → dict
   - Returns {source_path: dest_path} for requested target(s)

2. `smart_copy_file(src, dst, verbose)` → status
   - Status: "copied" | "skipped" | "conflict"
   - Handles backup creation for conflicts

3. `create_symlink(src, dst, verbose)` → status
   - Creates symlink, handles existing files

4. `backup_source(src, backup_dir)` 
   - Copies source to timestamped backup dir

5. `run_dry_run(mapping, verbose)` → list
   - Returns list of actions without executing

### Exclusions

Skip these runtime/generated directories (never sync):
- `__pycache__/`
- `.pytest_cache/`
- `.ruff_cache/`
- `.mypy_cache/`
- `history.jsonl`
- `session-env/`
- `debug/`
- `todos/`
- `tasks/`
- `teams/`
- `shell-snapshots/`
- `file-history/`
- `paste-cache/`

### Output Summary

```
=== thegent install ===
Target: both
Mode: smart copy

~/.claude:
  Copied:   15 files
  Skipped:  42 files (up-to-date)
  Conflicts: 3 files (kept user version)

~/.factory:
  Copied:   8 files
  Skipped:  12 files

Run with --verbose for details
```

## Error Handling

- Exit with error if thegent source directory missing
- Create destination dirs if they don't exist
- Continue on individual file errors, report at end
- Exit code: 0 = success, 1 = errors occurred

## Testing

- Unit tests for `smart_copy_file` logic
- Integration tests for full install flow
- Test dry-run output matches actual behavior


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

