# thegent

[![PyPI version](https://badge.fury.io/py/thegent.svg)](https://badge.fury.io/py/thegent)
[![Rust](https://img.shields.io/badge/built%20with-Rust-orange.svg)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**CLI and framework for agent orchestration, governance, and lifecycle management.**

`thegent` is a CLI and framework for managing AI agent workflows, droids, and multi-agent swarms. It follows a library-first design and uses Rust extensions for performance-sensitive paths.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Performance at Scale](#-performance-at-scale)
- [Governance & Policy](#-governance--policy)
- [Security & Hardening](#-security--hardening)
- [Documentation](#-documentation)
- [Docs Deploy](#-docs-deploy)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Key Features

- ⚡ **Performance**: Rust-backed tool detection and PATH resolution (<1ms) with 10-100x speedup over shell baselines.
- 🔒 **Agent Governance**: Built-in policy enforcement, cost caps, and automated quality gates.
- 🌍 **Multi-Provider Routing**: Routing across Claude, Gemini, OpenAI, and custom local proxies.
- 🛠️ **Unified Work Stream**: Single source of truth for task management across multiple agents and projects.
- 📦 **MCP Native**: Full support for Model Context Protocol (MCP) servers and resources.
- 🔄 **Continuous Autonomy**: Background execution and session management via `thegent run agent "Task" --loop`.
- 🔍 **Deep Research Protocol**: Multi-source investigation workflows (Reddit, Google, GitHub).

---

## 🚀 Quick Start

### 1. Install (One Command)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/install.ps1 | iex
```

### 2. Configure & Verify
```bash
thegent install -t all --scope both --full   # Bootstrap user/system assets + provider setup
thegent doctor   # Verify environment health
```

Project onboarding commands:

```bash
thegent scaffold greenfield ./new-project --profile cli_tool
thegent scaffold brownfield ./existing-project
thegent scaffold ag-dd ./existing-project
thegent scaffold none ./existing-project
```

### 3. Run Your First Agent
```bash
thegent run free "Analyze the current directory structure"
```

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- Rust (required for building performance-sensitive extensions)
- Homebrew (recommended for system dependencies)

### For Developers (From Source)
```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
thegent install -t all --scope both --setup
thegent install-shims
thegent setup --hooks
```

### Worktree Governance (Primary-main Flow)

thegent bootstrap and shell/dotfile management support a worktree-first governance model:

- Keep your primary checkout on `main`.
- Do branch development in dedicated worktrees.
- Merge/cherry-pick branch worktree commits back into `main`.

When bootstrap runs inside a git repository, it can write a marker file:

- `.thegent-primary-main` (policy marker)

Interactive shells get a helper function through managed zsh config:

```bash
thg_new_worktree <domain> <scale> <change-anchor> [start-point]
```

This helper refuses to branch from a dirty/non-main primary checkout.

CLI alternative:

```bash
thegent worktree new <domain> <scale> <change-anchor> [start-point]
thegent worktree state <change-anchor> <new-state>
thegent worktree list
thegent worktree prune [--dry-run]
thegent worktree check
thegent help worktree
thegent help git
```

### Toolchain Setup

`thegent` uses explicit setup/install surface controls (for runtime assets, shims, hooks, and profiles).  
`--system-deps`, `--verify-mise`, and `--uninstall-mise-hooks` are legacy references and are not
part of the current parser surface.

For mise/toolchain setup, use one of:

```bash
# Use the project-standard bootstrap/install flow first.
thegent install -t all --scope both --setup

# Then manage mise with your preferred shell/toolchain installer separately.
brew install mise
echo 'eval "$(mise activate zsh)"' >> ~/.zshenv
```

---

## 🛠️ Usage

| Command | Description |
|---------|-------------|
| `thegent run free <prompt>` | Execute a task in the foreground with the free agent. |
| `thegent run free <prompt> --skill <name>` | Execute with selected skill instructions (repeat `--skill` to stack). |
| `thegent run agent <prompt> --bg` | Start a background agent session. |
| `thegent ps` | List active and historical agent sessions. |
| `thegent skill list` | List discovered skills available for `--skill` selection. |
| `thegent skill select <name>` | Validate a skill and print exact `--skill` usage for run flows. |
| `thegent plan next` | Find the next actionable item from project plans and specs. |
| `thegent run agent <prompt> --loop` | Continuously process work items from the unified work stream. |
| `thegent doctor` | Verify environment health and fix performance bottlenecks. |
| `thegent registry list` | List registered personas. |
| `thegent registry recommend <intent>` | Recommend a persona for a task or role. |
| `thegent registry doctor` | Validate registry health and routing metadata. |
| `thegent govern approve <run-id>` | Approve a HITL gate. |
| `thegent govern reject <run-id>` | Reject a HITL gate. |
| `thegent govern vet <run-id>` | Vet a run before promotion. |
| `thegent worktree new <domain> <scale> <change-anchor> [start-point]` | Create a structured worktree. |
| `thegent worktree state <change-anchor> <new-state>` | Update structured worktree state. |
| `thegent worktree list` | List structured worktrees. |
| `thegent worktree prune [--dry-run]` | Prune structured worktrees. |
| `thegent worktree check` | Validate structured worktree governance. |
| `thegent sync autopilot` | Automatic bi-directional sync: `WORK_STREAM.md` <-> GitHub Projects <-> Linear. |

Harness wrappers (`dex`, `clode`, `roid`, `droid`) route through `thegent-shims`.
Use `--native` to bypass wrapper-injected defaults/proxy routing and call the underlying native CLI directly.

Skill UX examples:

```bash
thegent skill list
thegent skill select thegent-skills
thegent run agent "run with selected skill" --skill thegent-skills
```

Unknown skill handling is explicit and non-silent:

```bash
thegent skill select missing-skill
# Skill not found: missing-skill
```

### Workstream Autosync (GitHub Projects + Linear)

Enable fully automatic reflections so agents can stay unaware of board plumbing:

```text
THGENT_WORKSTREAM_AUTOSYNC_ENABLED=1
THGENT_WORKSTREAM_AUTOSYNC_INTERVAL_SEC=60

THGENT_GH_PROJECT_SYNC_ENABLED=1
THGENT_GH_PROJECT_OWNER=<org-or-user>
THGENT_GH_PROJECT_NUMBER=<project-number>

THGENT_LINEAR_SYNC_ENABLED=1
THGENT_LINEAR_API_KEY=<linear-api-key>
THGENT_LINEAR_TEAM_ID=<linear-team-id>
```

Run once:

```text
thegent sync autopilot --once
```

Run continuously:

```text
thegent sync autopilot --interval 60
```

Task entrypoints:

```text
task sync:autopilot
task sync:autopilot:once
```

---

## 📊 Performance at Scale

| Operation | Legacy (Shell) | thegent (Rust) | Improvement |
|-----------|----------------|----------------|-------------|
| Tool Detection | 60ms | **1ms** | **60x** |
| PATH Resolution | 20ms | **0.5ms** | **40x** |
| Process Scanning | 50ms | **0.5ms** | **100x** |
| Hook Execution | 200ms | **20ms** | **10x** |

---

## 🛡 Governance & Policy

`thegent` treats AI agency as a governed resource:
1. **Cost Control**: Define per-session and per-project token/dollar budgets.
2. **Quality Gates**: Automatic validation of agent outputs against defined specifications.
3. **Policy Enforcement**: Centralized `governance/` module for enforcing security and ethical constraints.
4. **Audit Logs**: Full traceability of agent actions, including tool use and thought processes.

---

## 🔐 Security & Hardening

**Security controls for agentic operations:**
- **Minimal Surface**: Core logic isolated in Rust for performance and security.
- **Stealth Scrapers**: Built-in mechanisms to bypass scraping blocks and protect agent anonymity.
- **Path Isolation**: Strict control over the execution environment via optimized shims.
- **Secret Management**: Secure storage for API keys and provider credentials.

---

## 📚 Documentation

- **[Public Docsite](./docs/site/)** — VitePress-powered public documentation. Run locally with `bun run dev` from `docs/site/`. See [docs/site/README.md](./docs/site/README.md) for full setup instructions.
- **[Docsets](./docs/docsets/)** — Audience-based documentation tracks.
  - [Developer (Internal)](./docs/docsets/developer/internal/)
  - [Developer (External)](./docs/docsets/developer/external/)
  - [Technical User](./docs/docsets/user/)
  - [Agent Operator](./docs/docsets/agent/)
- **[CLIProxyAPI Issue Board](./docs/docset/CLIProxyAPI_ISSUE_BOARD.md)** — 961 tracked GitHub issues from CLIProxyAPI/Plus with thegent solutions.
- **[Quick Start Guide](./docs/guides/QUICK_START.md)** — Get up and running in 5 minutes.
- **[Complete User Guide](./docs/guides/COMPLETE_USER_GUIDE.md)** — Deep dive into features.
- **[Installation Guide](./docs/guides/INSTALLATION.md)** — Advanced setup options.
- **[Provider Setup Guide](./docs/guides/PROVIDER_SETUP_GUIDE.md)** — cliproxy login, provider/model routing, adapter vs native behavior, troubleshooting, and provider integrations.
- **[Changelog](./CHANGELOG.md)** — Keep-a-Changelog release history with active `Unreleased` section.
- **[Changelog Process](./docs/guides/CHANGELOG_PROCESS.md)** — How to add, classify, and release changelog entries.
- **[Changelog Entry Template](./docs/reference/CHANGELOG_ENTRY_TEMPLATE.md)** — Copy/paste template and writing guidance for entries.
- **[Project Setup Style](./docs/guides/PROJECT_SETUP_STYLE.md)** — Standardized command/process baseline inspired by vercel/ai.
- **[Domain Mapping Guide](./docs/guides/DOMAIN_MAPPING_GUIDE.md)** — `thegent domain map` advisor mode for domain exposure.
- **[Release Supply Chain Controls](./docs/governance/RELEASE_SUPPLY_CHAIN_CONTROLS.md)** — SBOM, vulnerability scans, governance attestation, and release provenance artifacts.
- **[Architecture Overview](./docs/reference/ARCHITECTURE_LAYERS.md)** — Design layers and internals.
- **[Research Index](./docs/research/RESEARCH_CONSOLIDATED.md)** — Findings and experiments.

---

## 🚢 Docs Deploy

Local docs:

```bash
bun run docs:dev
bun run docs:build
```

GitHub Pages:

- Workflow: `.github/workflows/docs.yml`
- URL convention: `https://<owner>.github.io/thegent/`

---

## 🤝 Contributing

We welcome community contributions! Please see our **[CONTRIBUTING.md](CONTRIBUTING.md)** for:
- Development environment setup (using `uv`).
- Test suite execution (`task test`).
- Coding standards and PR process.

---

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

<p align="center">
  Built with ❤️ by the community
</p>
