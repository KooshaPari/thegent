# thegent Third-Party Bundle Manifest

This document defines a practical, extensible format for installing external MCP tooling,
hooks, skills, and other local assets through `thegent install`.

## Design intent

- Keep core targets (`claude-code`, `cursor`, `codex`, `droid`) stable.
- Move optional, third-party, community, and experimental items out of code into a manifest.
- Standardize install semantics with existing modes:
  - `smart` (default): copy only when source is newer.
  - `force`: overwrite existing.
  - `editable`: symlink mode.
  - `symlink` alias for `editable`.
  - `copy` alias for target mode default (`smart` by default or command mode).

## CLI entry points

- `thegent install --bundle <name> --bundle-manifest /path/to/manifest.json`
- repeatable:
  - `thegent install --bundle web-stack --bundle zit-lint-hooks`
- command-mode still applies when a bundle omits mode.
- default install mode is `smart`; to switch, use `--force` or `--editable`.
- default manifest path:
  - `~/.config/thegent/third_party_bundles.json`

## Manifest schema

```json
{
  "bundles": {
    "web-stack": [
      {
        "source": "thegent:skills/agent-orchestra",
        "target": "{home}/.thegent-extras/skills/agent-orchestra",
        "mode": "editable"
      },
      {
        "source": "/absolute/path/or/env/expanded/${HOME}/.../hook.py",
        "target": "{home}/.hooks/third-party/inspect.py",
        "mode": "smart"
      }
    ]
  }
}
```

Notes:

- `source`:
  - supports absolute and relative filesystem paths.
  - supports `thegent:` prefix for paths relative to the repo root.
- `target`:
  - supports `{home}`, `{cwd}`, `${HOME}`, `${CWD}`.
  - plain relative targets are interpreted under `{home}`.

## Recommended cross-project conventions

- Store reusable manifests in shared repos under a deterministic filename
  (`third_party_bundles.json`) and point CI/local scripts to it via `--bundle-manifest`.
- Keep item entries additive and idempotent.
- Separate high-risk bundles (hooks/scripts with side effects) from lightweight profile bundles.
- Track `source` provenance in PRD/WBS for auditability (especially MCP endpoint configs).

## Suggested starter bundle set

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
