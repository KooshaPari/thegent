# thegent Third-Party Bundle Manifest

This document defines an extensible manifest format for installing external MCP tooling,
hooks, skills, and other assets through `thegent install`.

## Design intent

- Keep core targets (`claude-code`, `cursor`, `codex`, `droid`) stable.
- Move optional, third-party, community, and experimental items out of code into manifests.
- Standardize install semantics with existing modes:
  - `smart` (default): copy only when source is newer.
  - `force`: overwrite existing.
  - `editable`: symlink mode.
  - `symlink` alias for `editable`.
  - `copy` alias for target mode default (`smart` by default or command mode).
- Support both file-sync and MCP-config bundle items in one schema.

## CLI entry points

- `thegent install --bundle <name> --bundle-manifest /path/to/manifest.json`
- repeatable:
  - `thegent install --bundle web-stack --bundle zit-lint-hooks`
- command-mode still applies when a bundle omits mode.
- default install mode is `smart`; to switch, use `--force` or `--editable`.
- default manifest path:
  - `~/.config/thegent/third_party_bundles.json`
- additional maintenance flags:
  - `thegent install --list-bundles` to list known bundle names from the manifest and exit.
  - `thegent install --validate-bundles` to validate manifest schema and exit.
  - `thegent install --bundle-manifest /path/to/manifest.json --validate-bundles` to validate a custom file.
- conflict policy override:
  - `thegent install --bundle-conflict-policy force` to force all third-party bundle file writes.
  - `thegent install --bundle-conflict-policy editable` (or `symlink`) to symlink third-party bundle files.
  - `thegent install --bundle-conflict-policy smart` for timestamp-based skip-by-default behavior.
- validation output:
  - emits actionable failures (missing file, invalid JSON, missing `bundles`, wrong item shape).

## Manifest schema

```json
{
  "bundles": {
    "web-stack": [
      {
        "type": "file",
        "source": "thegent:skills/agent-orchestra",
        "target": "{home}/.thegent-extras/skills/agent-orchestra",
        "mode": "editable"
      },
      {
        "type": "file",
        "source": "/absolute/path/or/env/expanded/${HOME}/.../hook.py",
        "target": "{home}/.hooks/third-party/inspect.py",
        "mode": "smart"
      },
      {
        "type": "mcp",
        "client": "cursor",
        "path": "{home}/.cursor/mcp.json",
        "key_path": "mcpServers.thegent",
        "value": {
          "url": "http://127.0.0.1:3847/mcp",
          "transport": "http",
          "description": "Thegent agent orchestration (run, bg, ps, logs, dag, etc.)"
        }
      }
    ]
  }
}
```

Field semantics:

- `type` (optional, default `file`):
  - `file`: filesystem source-target operations
  - `mcp`: MCP config writes
  - aliases: `files`, `filesystem`, `fs`, `skill`, `hook`, `mcp_config`, `mcp-config`
  - omitted `type` is inferred from shape:
    - file-like `source`/`target` fields => `file`
    - otherwise client/key-style fields => `mcp`
- `mode` (file only):
  - supports `smart`, `force`, `editable`, `symlink`, `copy`, `interactive`.
  - optional; defaults to the CLI install mode.
- `source` (file):
  - supports absolute and relative filesystem paths.
  - supports `thegent:` prefix for paths relative to the repo root.
- `target` (file):
  - supports `{home}`, `{cwd}`, `${HOME}`, `${CWD}`.
  - plain relative targets are interpreted under `{home}`.
- `client` (mcp):
  - supported: `cursor`, `claude-code`, `claude-desktop`, `codex`, `droid`, `all`.
  - aliases accepted: `claude`, `factory`, `cursor-ide`, `cursor-code`, `claude desktop`, `claude_desktop`.
  - `all` expands into all known MCP destinations.
- `key_path` (mcp):
  - default: `mcpServers.thegent`
- `value` (mcp):
  - optional; when omitted, it is derived from the active MCP URL + client defaults.
- `path` (mcp):
  - optional; if omitted, client defaults apply.
  - supports the same templating as `target` (`{home}`, `{cwd}`, `${HOME}`, `${CWD}`).
  - relative paths are interpreted under `{home}`.
  - for `cursor` without override, both workspace and global files are updated.

## Example style guide

- Use one bundle per external package family (`hook-collection`, `mcp-extensions`, `skill-pack`).
- Prefer explicit `type` on new bundles.
- For file bundles, keep sources stable and deterministic.
- For MCP bundles, prefer explicit `value` when policy needs non-default transport details; otherwise omit for defaults.
- Keep bundles additive and idempotent.
- Track source provenance where possible.

## Recommended starter bundle set

| Bundle name | Typical contents |
|---|---|
| `mcp-extensions` | additional MCP servers and tool config snippets |
| `hook-collection` | custom hooks and interceptors |
| `skill-pack` | domain-specific and vendor-specific skill trees |
| `agent-extras` | experimental skill stacks from web sources |

## Compatibility notes

- Existing `thegent install` behavior is unchanged when no `--bundle` is passed.
- Bundles are applied after built-in target actions and reuse the same install engine.
- Duplicate `--bundle` values are deduplicated.


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

