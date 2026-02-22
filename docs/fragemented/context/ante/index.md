# ANTE Documentation Index

> Comprehensive index of ANTE (Another Terminal, Ante) terminal AI agent documentation. Extracted 2026-02-20.

ANTE is a lightweight, self-contained terminal AI agent built in native Rust by Antigma Labs. It prioritizes security, performance, and principled design. Currently in preview, supporting macOS and Linux.

## Documentation Structure

### Core Documentation

| File | Topic | Purpose |
|------|-------|---------|
| **overview.md** | Overview | What ANTE is, core principles, and high-level architecture |
| **quickstart.md** | Quickstart | Installation and first prompt in under one minute |
| **core-concepts.md** | Core Concepts & Protocol | Sessions, tasks, turns, protocol fundamentals |
| **architecture.md** | Architecture | System design, components, and module structure |

### User Guides

| File | Topic | Purpose |
|------|-------|---------|
| **interactive-tui.md** | Interactive TUI | Using the rich terminal interface for interactive work |
| **headless-mode.md** | Headless Mode | Integration into scripts, CI/CD, and automation |
| **preferences.md** | Preferences | Configuration, settings, and user customization |
| **offline-mode.md** | Offline Mode | Operating without internet (experimental) |

### Advanced Features

| File | Topic | Purpose |
|------|-------|---------|
| **skills.md** | Skills System | Extending ANTE with custom skills and capabilities |
| **sub-agents.md** | Sub-Agents | Spawning and orchestrating sub-agents for complex tasks |
| **tools.md** | Tools | Built-in tools and tool integration |
| **memory.md** | Memory System | Long-term and session memory, retrieval, storage |

### Models & Providers

| File | Topic | Purpose |
|------|-------|---------|
| **model-provider-catalog.md** | Model & Provider Catalog | Available LLM models and providers |
| **third-party-providers.md** | Third-Party Providers | Adding custom LLM providers |

### Advanced & Experimental

| File | Topic | Purpose |
|------|-------|---------|
| **agent-organization.md** | Agent Organization | Organizing agents at scale (experimental) |
| **eval-benchmark.md** | Eval & Benchmark | Evaluation and benchmarking tools |

---

## Quick Navigation

### Getting Started (First Time Users)
1. Read **overview.md** to understand what ANTE is
2. Follow **quickstart.md** to install and run your first prompt
3. Explore **interactive-tui.md** to learn the interface
4. Review **core-concepts.md** for deeper understanding

### Extending ANTE
1. Learn **skills.md** to add custom capabilities
2. Understand **tools.md** for tool integration
3. Explore **sub-agents.md** for agent orchestration
4. Check **agent-organization.md** for large-scale setups

### Integration & Automation
1. Read **headless-mode.md** for scripting and CI/CD
2. Review **preferences.md** for configuration
3. Check **model-provider-catalog.md** for LLM options
4. Learn **third-party-providers.md** for custom providers

### Advanced Topics
1. Study **memory.md** for persistence and retrieval
2. Read **eval-benchmark.md** for testing and evaluation
3. Explore **offline-mode.md** for offline operation
4. Review **architecture.md** for deep technical understanding

---

## Key Concepts at a Glance

**Sessions** - Isolated execution contexts where ANTE operates. Each session has its own state and memory.

**Tasks** - Discrete units of work within a session, representing user requests and agent operations.

**Turns** - Individual back-and-forth exchanges between user and ANTE within a task.

**Skills** - Extensible capabilities that can be added to ANTE to perform specialized operations.

**Tools** - Executable functions that ANTE can invoke to interact with the system, API, or external services.

**Sub-Agents** - Spawned agent instances that can work independently or cooperatively on tasks.

**Memory** - Both short-term (session) and long-term (persistent) context that ANTE maintains and retrieves.

**Providers** - LLM backend services (OpenAI, Anthropic, local models, etc.) that power ANTE's reasoning.

---

## Core Principles

ANTE is built on these foundational principles:

- **Tight & Tiny Core** - Minimal, focused feature set
- **Low Cognitive Load** - Simple for both users and developers
- **Minimal Dependencies** - Both runtime and build-time
- **Principled Organization** - Structured agent design patterns
- **Close Training-Inference Loop** - Alignment between training and execution
- **Security & Performance** - Native Rust implementation
- **Resistance to AI-Generated Slop** - Quality and correctness focus

---

## File Organization

All documentation files are located in: `/thegent/docs/context/ante/`

Each document follows the format:
- **Header** identifying the topic
- **Extraction timestamp** and source
- **Structured sections** with clear headings
- **Code examples** where applicable
- **Tables and diagrams** for complex concepts

---

## Related Resources

- ANTE Homepage: https://docs.useante.com/
- ANTE GitHub: https://github.com/antigmaplex/ante
- Antigma Labs: https://antigmalabs.com/

---

*Last updated: 2026-02-20*
