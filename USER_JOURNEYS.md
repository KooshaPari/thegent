# User Journeys — thegent

## Overview

This document captures the primary user journeys for thegent, the Phenotype developer dotfiles manager and environment orchestration tool. thegent is implemented in Rust with a plugin host architecture (Extism/WASM) and is the canonical mechanism for configuring and reproducing any development environment across machines and operating systems.

**ID format:** UJ-{N}
**Cross-references:** PRD.md epics, FUNCTIONAL_REQUIREMENTS.md FR-* IDs

---

## UJ-1: Initial Setup on a New Machine

**Actor:** Developer setting up thegent for the first time on a fresh machine (macOS, Linux, or Windows/WSL)
**Goal:** Install thegent, authenticate with the config backend, and restore a full development environment from a saved profile.
**Preconditions:**
- Target machine has internet access
- User has credentials for the config sync backend (or a local profile archive)
- Supported OS: macOS 13+, Ubuntu 22.04+, Arch Linux, Windows 11 WSL2

```
  [Fresh machine — terminal open]
          |
          | curl -fsSL https://install.thegent.dev | sh
          | OR: cargo install thegent
          v
  [thegent binary installed to ~/.local/bin or /usr/local/bin]
          |
          v
  [thegent init]
          |
  +-------+----------+
  |                  |
  | First time?      | Existing profile?
  | (no .thegent/)   | (detected ~/.thegent/config.toml)
  v                  v
  [Wizard: guided    [Offer to restore or re-init]
   first-time setup]
          |
          v
  [Step 1: Auth]
  - thegent auth login
  - Opens browser -> OAuth (GitHub or Phenotype SSO)
  - Token stored in system keychain
          |
          v
  [Step 2: Profile selection]
  - List available profiles from sync backend
  - Select profile (e.g., "macOS-dev", "linux-server", "wsl-work")
          |
          v
  [Step 3: Dependency resolution]
  - thegent plan --profile <name>
  - Prints dependency DAG: packages, plugins, symlinks, secrets
  - Shows diff vs current machine state
          |
          | user confirms plan
          v
  [Step 4: Apply]
  - thegent apply --profile <name>
  - Install packages (brew, apt, pacman, winget)
  - Symlink dotfiles (~/.zshrc -> thegent-managed path)
  - Run plugin hooks (shell config, editor setup, git identity)
  - Inject secrets from vault (if configured)
          |
          v
  [Apply complete]
  - Summary: N packages installed, M symlinks created, K plugins activated
  - Restart shell prompt recommended
          |
          v
  [thegent status]
  - All components: green
  - Dev environment ready
```

**Postconditions / Success Criteria:**
- All profile packages are installed and at correct versions
- All dotfile symlinks resolve correctly
- Shell (zsh/bash/fish) sources thegent-managed configs without error
- `thegent status` reports all components healthy
- Auth token is persisted in system keychain

**Error paths:**
- Package manager not found -> thegent bootstraps the appropriate manager (brew, apt) before continuing
- OAuth timeout -> `thegent auth login --device-code` fallback
- Package install conflict -> pause, show conflict details, prompt user to resolve or skip
- Secret vault unreachable -> skip secrets, surface warning, retry with `thegent secrets sync`
- Partial apply failure -> apply is idempotent, re-run `thegent apply` safely to resume

---

## UJ-2: Syncing Config Across Machines

**Actor:** Developer who uses thegent on multiple machines (work laptop, home desktop, remote server)
**Goal:** Make a config change on one machine, push it to the sync backend, and pull it down on another machine without conflicts.
**Preconditions:**
- thegent installed and authenticated on both machines
- A profile exists and has been applied on both machines (UJ-1 complete)
- Sync backend is reachable (Phenotype sync service or self-hosted Git remote)

```
  [Machine A — user edits a dotfile]
          |
          | vim ~/.thegent/profiles/macOS-dev/shell/aliases.zsh
          v
  [File watcher detects change (if daemon running)]
  OR
  [User runs: thegent diff]
  - Shows local changes vs last committed snapshot
          |
          v
  [thegent commit -m "add git aliases"]
  - Stages changed managed files
  - Creates versioned snapshot in local store
          |
          v
  [thegent push]
  - Pushes snapshot to sync backend
  - Backend stores as named version under profile
  - Push succeeds: "Profile 'macOS-dev' at v42 pushed"
          |

  --- (on Machine B) ---

          v
  [thegent pull]
  - Fetches latest profile snapshot from backend
  - Computes diff vs local state
  - Reports: "3 files changed, 1 plugin version updated"
          |
  +-------+----------+
  |                  |
  | No conflicts     | Conflicts detected
  v                  v
  [thegent apply     [Conflict resolution]
   --update]         - Show 3-way diff per file
  - Merge clean      - Options: keep local / take remote / edit
  - Apply plugin     - thegent resolve <file>
    version updates  - After resolution: thegent apply --update
          |                  |
          +--------+---------+
                   |
                   v
  [Machine B env updated]
  [thegent status -> all green]
```

**Postconditions / Success Criteria:**
- Both machines report the same profile version after sync
- No unresolved conflicts remain
- All dotfile symlinks on Machine B point to the updated managed files
- Sync history is queryable: `thegent log --profile macOS-dev`

**Error paths:**
- Push rejected (backend conflict, another machine pushed first) -> `thegent pull` first, then retry push
- Network interrupted mid-push -> push is transactional; backend rejects partial uploads; safe to retry
- Conflicting plugin versions -> show semver conflict, prompt user to pin or accept newer
- Sync backend authentication expired -> `thegent auth refresh`, then retry

---

## UJ-3: Installing and Configuring a Plugin

**Actor:** Developer who wants to extend thegent with a new capability (e.g., a language version manager, an editor config plugin, a secrets backend)
**Goal:** Discover a plugin in the registry, install it, configure it, and verify it integrates correctly with the existing environment.
**Preconditions:**
- thegent is installed and authenticated
- Plugin registry is reachable (registry.thegent.dev or local mirror)
- Active profile exists

```
  [User searches for a plugin]
  thegent plugin search <keyword>
  e.g.: thegent plugin search "node version"
          |
          v
  [Registry returns matching plugins]
  - thegent-plugin-mise (version managers, 1.2.0)
  - thegent-plugin-nvm (nvm wrapper, 0.9.1)
  - ... (ranked by install count, verified badge)
          |
          | thegent plugin install thegent-plugin-mise
          v
  [Plugin resolution]
  - Fetch WASM bundle from registry
  - Verify checksum + signature
  - Check compatibility: thegent ABI version match
          |
          v
  [Plugin installed to ~/.thegent/plugins/]
          |
          v
  [Plugin configuration]
  - thegent plugin configure thegent-plugin-mise
  - Opens $EDITOR with generated config schema (TOML)
  - User sets: default_node_version = "22", default_python_version = "3.13"
  - Save and exit editor
          |
          v
  [Plugin hook registration]
  - Plugin registers lifecycle hooks:
    - on_apply: installs mise, sets tool versions
    - on_status: checks mise version and tool availability
    - on_sync: exports .tool-versions to profile snapshot
          |
          v
  [thegent apply --plugin thegent-plugin-mise]
  - Runs on_apply hook
  - mise installed, tool versions set
          |
          v
  [thegent status]
  - thegent-plugin-mise: green (mise 2.x, node 22.x, python 3.13.x)
          |
          v
  [Plugin config committed to profile]
  - thegent commit -m "add mise plugin"
  - thegent push  (syncs to other machines via UJ-2)
```

**Postconditions / Success Criteria:**
- Plugin WASM bundle installed and signature verified
- Plugin configuration persisted in profile
- Plugin lifecycle hooks execute without error during `thegent apply`
- `thegent status` reports plugin as healthy
- Plugin config is included in next `thegent push`

**Error paths:**
- Checksum mismatch -> abort install, print hash comparison, recommend re-downloading
- ABI incompatibility -> show required thegent version, offer to install compatible plugin version
- Plugin hook throws error during apply -> plugin error is isolated (WASM sandbox), other hooks continue, error surfaced in status
- Registry unreachable -> install from local cache if available, else fail with clear message
- Config schema validation failure -> show validation error with line reference, re-open editor

---

## UJ-4: Creating and Sharing a Dotfile Profile

**Actor:** Developer creating a portable, shareable profile for a team or community
**Goal:** Package a curated dotfile profile (shell config, editor settings, tools), publish it to the registry or a Git URL, and allow others to install it with one command.
**Preconditions:**
- thegent installed, profile exists locally (UJ-1 complete)
- User has a registry account (for public publish) or a Git remote (for private share)

```
  [User has working local profile]
  thegent profile list
  -> macOS-dev (active)
          |
          v
  [Create exportable profile]
  thegent profile export macOS-dev --out ./my-profile
  - Exports: dotfiles/, plugins.toml, packages.toml, hooks/
  - Strips machine-specific secrets and absolute paths
  - Replaces with template variables: {{HOME}}, {{USER}}, {{OS}}
          |
          v
  [Review and clean export]
  - User inspects ./my-profile/
  - Removes any private items
  - Adds README.md describing profile purpose
          |
          v
  [Validate profile]
  thegent profile validate ./my-profile
  - Lints for absolute paths, secret leaks, broken symlink targets
  - Reports: "Profile valid. 0 warnings."
          |
          v
  [Publish to registry (public)]
  thegent profile publish ./my-profile --name kooshapari/macOS-dev --tag v1.0.0
  - Auth check -> registry upload -> checksum + sign
  - Published at: registry.thegent.dev/kooshapari/macOS-dev@v1.0.0
  OR
  [Publish to Git URL (private/team)]
  thegent profile publish ./my-profile --git git@github.com:org/dotfiles.git
          |
          v
  [Share install command]
  "thegent apply --profile kooshapari/macOS-dev@v1.0.0"
  OR
  "thegent apply --profile git@github.com:org/dotfiles.git"
          |
  --- (recipient machine) ---
          v
  [Recipient runs install command]
  thegent apply --profile kooshapari/macOS-dev@v1.0.0
  - Fetches, verifies, applies (same flow as UJ-1 Step 4)
```

**Postconditions / Success Criteria:**
- Profile archive contains no absolute paths, secrets, or machine-specific state
- Profile passes `thegent profile validate` with 0 errors
- Published profile is reachable at the registry URL or Git remote
- A recipient can apply the profile on a clean machine and reach a working environment

**Error paths:**
- Secret leak detected during validate -> abort export, list offending files and line numbers
- Absolute path detected -> suggest replacement with template variable, offer auto-fix
- Registry publish auth failure -> `thegent auth login`, retry
- Git remote push rejected (permissions) -> surface git error, suggest SSH key or token setup
- Recipient OS not supported by a plugin in the profile -> plugin skipped with warning, rest of profile applies

---

## UJ-5: Dev Environment Bootstrapping for a New Project

**Actor:** Developer starting work on a new project that requires a specific toolchain, language version, and set of dev tools
**Goal:** Create a project-local environment spec, bootstrap all dependencies, and leave the project in a reproducible, onboardable state for other contributors.
**Preconditions:**
- thegent installed and authenticated
- A project directory exists (new or cloned repo)
- User knows the required tech stack (e.g., Rust 1.78, Node 22, PostgreSQL 16)

```
  [cd /path/to/my-project]
          |
          v
  [thegent project init]
  - Detects existing marker files (Cargo.toml, package.json, go.mod, pyproject.toml, etc.)
  - Infers recommended tools and versions
  - Generates .thegent/project.toml scaffold
          |
          v
  [User reviews and edits .thegent/project.toml]
  ---
  [tools]
  rust = "1.78"
  node = "22"
  postgres = "16"

  [services]
  postgres.port = 5432

  [plugins]
  required = ["thegent-plugin-mise", "thegent-plugin-postgres"]
  ---
          |
          v
  [thegent project plan]
  - Resolves tool versions against installed state
  - Lists what will be installed/changed
  - Flags conflicts with global profile
          |
          | user confirms
          v
  [thegent project apply]
  - Install/activate required tool versions (via mise or direct)
  - Start required local services (postgres via native or container)
  - Generate .envrc (direnv) or .env from spec
  - Run project bootstrap hooks (cargo build, npm install, etc.)
          |
          v
  [Bootstrap complete]
  - thegent project status
    -> rust 1.78.0: ok
    -> node 22.x: ok
    -> postgres 16.x: running on :5432
          |
          v
  [Commit .thegent/ to project repo]
  git add .thegent/project.toml
  git commit -m "chore: add thegent project env spec"
          |
          v
  [Other contributors onboard]
  git clone <repo>
  cd <repo>
  thegent project apply
  -> reproducible environment in one command
```

**Postconditions / Success Criteria:**
- `.thegent/project.toml` is committed to the project repository
- All specified tool versions are active in the project shell context
- All specified services are running and reachable
- `thegent project status` reports all components healthy
- A second developer can clone and run `thegent project apply` to reach the same environment

**Error paths:**
- Tool version conflict with global profile -> project env takes precedence in project directory (scoped activation), global unchanged outside project dir
- Service port already in use -> report conflict, suggest alternative port, do not force-kill existing process
- Bootstrap hook (npm install) fails -> surface exit code and stdout/stderr, do not mark project as ready
- `.thegent/project.toml` missing required field -> validate on apply, list missing fields with examples
- OS-level dependency missing (e.g., libpq for postgres) -> instruct user on system package install with exact command for detected OS

---

## Journey Index

| ID   | Title                                           | Actor                        | Primary CLI Commands                     |
|------|-------------------------------------------------|------------------------------|------------------------------------------|
| UJ-1 | Initial Setup on a New Machine                  | First-time developer         | `thegent init`, `thegent apply`          |
| UJ-2 | Syncing Config Across Machines                  | Multi-machine developer      | `thegent push`, `thegent pull`           |
| UJ-3 | Installing and Configuring a Plugin             | Any authenticated developer  | `thegent plugin install/configure`       |
| UJ-4 | Creating and Sharing a Dotfile Profile          | Profile author               | `thegent profile export/publish`         |
| UJ-5 | Dev Environment Bootstrapping for a New Project | Project lead / contributor   | `thegent project init/apply`             |

---

*Cross-references: PRD.md, FUNCTIONAL_REQUIREMENTS.md, ADR.md*
*Last updated: 2026-03-26*
