# thegent

**Unified Agent Orchestration, Governance, and Lifecycle Management.**

`thegent` is a production-ready CLI and framework for managing AI agent workflows, droids, and multi-agent swarms. Built with a "Library-First" philosophy and optimized with Rust extensions, it provides a fast, reliable, and governed environment for agentic operations.

> **Note**: `thegent` is 10-100x faster than traditional shell-based implementations through its high-performance Rust core and efficient PATH resolution.

---

## 🚀 Quick Start

### 1. Install (one command)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/install.ps1 | iex
```

The bootstrap installs thegent, runs `install -t all`, `install-shims`, `setup`, and `doctor` — a complete bootstrap.

Or via package manager:
```bash
pip install thegent
# or: uv tool install thegent
# or: brew install thegent  (macOS)
```

After package install, run `thegent setup` to configure providers and `thegent doctor` to verify.

### 2. Verify
```bash
thegent doctor
```

### 3. Run Your First Agent
```bash
thegent run "Analyze the current directory structure" free
```

### For Developers (from source)
```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
thegent setup --build-extensions  # Optional: Rust extensions
```

---

## ✨ Key Features

- ⚡ **Performance First**: Rust-powered tool detection and PATH resolution (<1ms).
- 🔒 **Agent Governance**: Built-in policy enforcement, cost caps, and quality gates.
- 🌍 **Multi-Provider Routing**: Smart routing across Claude, Gemini, OpenAI, and custom proxies.
- 🛠️ **Unified Work Stream**: Single source of truth for task management across multiple agents.
- 📦 **MCP Native**: Full Model Context Protocol (MCP) server support.
- 🔄 **Continuous Autonomous Work**: Background execution and session management with `thegent plan loop`.
- 🔍 **Deep Research Protocol**: Systematic multi-source investigation (Reddit, Google, GitHub) with stealth scraping to bypass blocks.

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- Rust (required for building high-performance extensions)
- Homebrew (recommended)

### Standard Installation
```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
# Or use bootstrap: curl -fsSL .../scripts/bootstrap.sh | sh -s -- install
```

### System Dependencies
Ensure core tools are available in your environment:
```bash
brew bundle  # Installs ripgrep, fd, jaq, and other optimized tools
```

---

## 🛠️ Usage

| Command | Description |
|---------|-------------|
| `thegent run <prompt>` | Execute a task in the foreground with a specific agent/model. |
| `thegent bg <prompt>` | Start a background agent session. |
| `thegent ps` | List active and historical agent sessions. |
| `thegent plan loop` | Continuously process work items from the unified work stream. |
| `thegent plan do-next` | Find the next actionable items from your project's plans and specs. |
| `thegent doctor` | Verify environment health and fix performance bottlenecks. |

---

## 📊 Performance at Scale

| Operation | Legacy (Shell) | thegent (Rust) | Improvement |
|-----------|----------------|----------------|-------------|
| Tool Detection | 60ms | **1ms** | **60x** |
| PATH Resolution | 20ms | **0.5ms** | **40x** |
| Process Scanning | 50ms | **0.5ms** | **100x** |
| Hook Execution | 200ms | **20ms** | **10x** |

---

## 📚 Documentation

- **[Installation Guide](./docs/guides/INSTALLATION.md)** — pip, uv, Nix, home-manager, devcontainer
- **[Quick Reference](./docs/guides/QUICK_REFERENCE.md)** — One-page command reference
- **[Troubleshooting](./docs/guides/TROUBLESHOOTING.md)** — Common issues and fixes
- **[Architecture Overview](./docs/reference/ARCHITECTURE_LAYERS.md)**
- **[Unified Work Stream](./docs/reference/WORK_STREAM.md)**

---

## 📄 License

MIT © [Koosha Paridehpour](https://github.com/kooshapari)
