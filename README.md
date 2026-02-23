# thegent 🎩 🚀

[![PyPI version](https://badge.fury.io/py/thegent.svg)](https://badge.fury.io/py/thegent)
[![Rust](https://img.shields.io/badge/built%20with-Rust-orange.svg)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Unified Agent Orchestration, Governance, and Lifecycle Management.**

`thegent` is a production-ready CLI and framework for managing AI agent workflows, droids, and multi-agent swarms. Built with a "Library-First" philosophy and optimized with high-performance Rust extensions, it provides a fast, reliable, and governed environment for agentic operations.

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

- ⚡ **Performance First**: Rust-powered tool detection and PATH resolution (<1ms) — 10-100x faster than traditional shell implementations.
- 🔒 **Agent Governance**: Built-in policy enforcement, cost caps, and automated quality gates.
- 🌍 **Multi-Provider Routing**: Smart routing across Claude, Gemini, OpenAI, and custom local proxies.
- 🛠️ **Unified Work Stream**: Single source of truth for task management across multiple agents and projects.
- 📦 **MCP Native**: Full support for Model Context Protocol (MCP) servers and resources.
- 🔄 **Continuous Autonomy**: Background execution and session management via `thegent plan loop`.
- 🔍 **Deep Research Protocol**: Systematic multi-source investigation (Reddit, Google, GitHub) with stealth scraping.

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
thegent setup    # Follow the wizard to log in to providers
thegent doctor   # Verify environment health
```

### 3. Run Your First Agent
```bash
thegent run "Analyze the current directory structure" free
```

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- Rust (required for building high-performance extensions)
- Homebrew (recommended for system dependencies)

### For Developers (From Source)
```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
thegent install -t all
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
thg_new_worktree <branch> [start-point] [worktree-path]
```

This helper refuses to branch from a dirty/non-main primary checkout.

### Automated Tool Management with mise

thegent integrates with [mise](https://mise.jdx.dev/) for automated, per-project tool version management. mise replaces manual `nvm`, `pyenv`, and `rbenv` usage with a single, fast tool that activates automatically when you enter a project directory.

**Install mise and register shell hooks automatically:**

```bash
thegent install --system-deps
```

This installs mise via Homebrew (or Nix with `--nix`), then writes the activation hook into your shell config (`~/.zshenv`, `~/.bashrc`, `config.fish`, etc.) so tools activate automatically in every new shell.

**Manual mise setup:**

```bash
# Via Homebrew
brew install mise
echo 'eval "$(mise activate zsh)"' >> ~/.zshenv

# Verify setup
thegent install --verify-mise

# Remove mise shell hooks without uninstalling mise
thegent install --uninstall-mise-hooks
```

**Dry-run (no system changes):**

```bash
thegent install --system-deps --dry-run
```

---

## 🛠️ Usage

| Command | Description |
|---------|-------------|
| `thegent run <prompt>` | Execute a task in the foreground with a specific agent/model. |
| `thegent run <prompt> --skill <name>` | Execute with selected skill instructions (repeat `--skill` to stack). |
| `thegent bg <prompt>` | Start a background agent session. |
| `thegent ps` | List active and historical agent sessions. |
| `thegent skill list` | List discovered skills available for `--skill` selection. |
| `thegent skill select <name>` | Validate a skill and print exact `--skill` usage for run flows. |
| `thegent plan loop` | Continuously process work items from the unified work stream. |
| `thegent plan do-next` | Find the next actionable items from project plans and specs. |
| `thegent doctor` | Verify environment health and fix performance bottlenecks. |

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

**Hardened for enterprise agentic operations:**
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
- **[Quick Start Guide](./docs/guides/QUICK_START.md)** — Get up and running in 5 minutes.
- **[Complete User Guide](./docs/guides/COMPLETE_USER_GUIDE.md)** — Deep dive into features.
- **[Installation Guide](./docs/guides/INSTALLATION.md)** — Advanced setup options.
- **[Provider Setup Guide](./docs/guides/PROVIDER_SETUP_GUIDE.md)** — cliproxy login, provider/model routing, adapter vs native behavior, and troubleshooting.
- **[Changelog](./CHANGELOG.md)** — Keep-a-Changelog release history with active `Unreleased` section.
- **[Changelog Process](./docs/guides/CHANGELOG_PROCESS.md)** — How to add, classify, and release changelog entries.
- **[Changelog Entry Template](./docs/reference/CHANGELOG_ENTRY_TEMPLATE.md)** — Copy/paste template and writing guidance for entries.
- **[Project Setup Style](./docs/guides/PROJECT_SETUP_STYLE.md)** — Standardized command/process baseline inspired by vercel/ai.
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
