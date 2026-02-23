# Memory

> Generated from Ante documentation webarchive

Skip to main content

[Ante home page![light logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)![dark logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)](/)

Search...

⌘K

##### Getting Started

  * [Overview](/start/overview)
  * [Quickstart](/start/quickstart)
  * [Eval & Benchmark](/start/eval)

##### Concepts

  * [Core Concepts & Protocol](/concepts/core-concepts)
  * [Architecture](/concepts/architecture)

##### Agent Org

  * [Agent Organization (Experimental)](/agent-org)

##### Offline Mode

  * [Offline Mode (Experimental)](/offline)

##### Usage

  * [Interactive TUI](/usage/tui)
  * [Headless Mode](/usage/headless)

##### Extensibility

  * [Skills](/extend/skills)
  * [Sub-Agents](/extend/subagents)

##### Configuration

  * [Model & Provider Catalog](/configuration/catalog)
  * [Preferences](/configuration/preference)
  * [Adding a 3rd Party Provider](/configuration/third-party-provider)

##### Memory

  * [Memory](/memory)

##### Reference

  * [Tools](/tools)

  * [Website](https://antigma.ai)
  * [Discord](https://discord.gg/pqhj3DNGz2)
  * [GitHub](https://github.com/AntigmaLabs/ante-preview)
  *   * Log Out
  * 

[Ante home page![light logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)![dark logo](https://mintcdn.com/antigmalabs/cvR1z2_cg6Q1RLzi/assets/ante.png?fit=max&auto=format&n=cvR1z2_cg6Q1RLzi&q=85&s=827303a37dd6c12ec797767e55c94972)](/)

Search...

⌘KAsk AI

  * [Website](https://antigma.ai)
  * [Discord](https://discord.gg/pqhj3DNGz2)
  * [GitHub](https://github.com/AntigmaLabs/ante-preview)
  * Log Out

Search...

Navigation

Memory

Memory

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Memory

# Memory

Persistent auto-memory that carries context across conversations

Ante has a persistent memory system that lets the agent build up knowledge across conversations. Insights, patterns, and lessons learned are stored in memory files and automatically loaded into the system prompt for future sessions.

## 

​

How it works

Each project has a memory directory (typically `.claude/projects/<project-path>/memory/`). The key file is `MEMORY.md` — its contents are injected into the system prompt at the start of every conversation.

### 

​

Automatic behavior

As the agent works on your project, it:

  1. **Consults** existing memory files to build on previous experience
  2. **Records** new insights when it encounters common mistakes or useful patterns
  3. **Updates** or removes memories that turn out to be wrong or outdated

### 

​

MEMORY.md

The main memory file. Its first 200 lines are included in the system prompt. Keep it concise — link to separate topic files for details.

Copy

Ask AI
    
    
    # Project patterns
    
    - Use `anyhow::Result` for all fallible functions
    - Tests go in `#[cfg(test)]` modules alongside code
    - See [debugging.md](debugging.md) for common issues
    
    # Known issues
    
    - The auth module needs refactoring (tracked in #123)
    

### 

​

Topic files

For detailed notes, create separate files and reference them from `MEMORY.md`:

Copy

Ask AI
    
    
    memory/
    ├── MEMORY.md           # Main file (auto-loaded, max 200 lines)
    ├── debugging.md        # Detailed debugging notes
    ├── patterns.md         # Code patterns and conventions
    └── architecture.md     # Architecture decisions
    

## 

​

Guidelines

The memory system follows these principles:

  * **Concise** — `MEMORY.md` is truncated after 200 lines, so keep it focused
  * **Semantic** — Organize by topic, not chronologically
  * **Accurate** — Update or remove outdated information
  * **Actionable** — Record what worked, what didn’t, and why

## 

​

Memory is per-project

Memory is scoped to each project directory. Different projects have independent memory directories. This means the agent’s accumulated knowledge about your React frontend won’t interfere with its knowledge about your Rust backend.

## 

​

Manual editing

You can edit memory files directly — they are plain markdown. The agent can also update them using the `Write` and `Edit` tools during a session.

[Previous](/configuration/third-party-provider)[ToolsReference for all built-in tools available to the agentNext](/tools)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * How it works
  * Automatic behavior
  * MEMORY.md
  * Topic files
  * Guidelines
  * Memory is per-project
  * Manual editing

Assistant

Responses are generated using AI and may contain mistakes.

Memory - Ante

