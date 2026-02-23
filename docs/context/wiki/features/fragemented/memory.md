# Memory

**Navigation:** home > [Features](../features/)

##### Getting Started Overview
- Quickstart
- Eval & Benchmark
##### Concepts Core Concepts & Protocol
- Architecture
##### Agent Org Agent Organization (Experimental)
##### Offline Mode Offline Mode (Experimental)
##### Usage Interactive TUI
- Headless Mode
##### Extensibility Skills
- Sub-Agents
##### Configuration Model & Provider Catalog
- Preferences
- Adding a 3rd Party Provider
##### Memory Memory
##### Reference Tools
- Website
- Discord
- GitHub
- Log Out
Ante home page Search... ⌘K Ask AI Search... Navigation Memory Memory Ante Preview Ante Preview Memory # Memory Persistent auto-memory that carries context across conversations
Ante has a persistent memory system that lets the agent build up knowledge across conversations. Insights, patterns, and lessons learned are stored in memory files and automatically loaded into the system prompt for future sessions. ## ​ How it works Each project has a memory directory (typically .claude/projects/<project-path>/memory/
). The key file is MEMORY.md — its contents are injected into the system prompt at the start of every conversation. ### ​ Automatic behavior As the agent works on your project, it: Consults
existing memory files to build on previous experience - Records
new insights when it encounters common mistakes or useful patterns - Updates
or removes memories that turn out to be wrong or outdated ### ​ MEMORY.md The main memory file. Its first 200 lines are included in the system prompt. Keep it concise — link to separate topic files for details. Copy Ask AI # Project patterns - Use `anyhow::Result` for all fallible functions - Tests go in `#[cfg(test)]` modules alongside code - See [ debugging.md ]( debugging.md ) for common issues # Known issues - The auth module needs refactoring (tracked in #123)
### ​ Topic files For detailed notes, create separate files and reference them from MEMORY.md
: Copy Ask AI memory/ ├── MEMORY.md           # Main file (auto-loaded, max 200 lines) ├── debugging.md        # Detailed debugging notes ├── patterns.md         # Code patterns and conventions └── architecture.md     # Architecture decisions ## ​ Guidelines The memory system follows these principles: Concise
— MEMORY.md is truncated after 200 lines, so keep it focused - Semantic
— Organize by topic, not chronologically - Accurate
— Update or remove outdated information - Actionable
— Record what worked, what didn’t, and why ## ​ Memory is per-project Memory is scoped to each project directory. Different projects have independent memory directories. This means the agent’s accumulated knowledge about your React frontend won’t interfere with its knowledge about your Rust backend. ​ Manual editing You can edit memory files directly — they are plain markdown. The agent can also update them using the Write
and Edit tools during a session. Previous Tools Reference for all built-in tools available to the agent Next On this page - How it works
- Automatic behavior
- MEMORY.md
- Topic files
- Guidelines
- Memory is per-project
- Manual editing
Assistant Responses are generated using AI and may contain mistakes. Memory - Ante

---

## Related Documentation

- [Core Concepts](../reference/core-concepts.md)
- [Preferences](./preferences.md)
