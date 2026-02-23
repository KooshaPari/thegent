# Getting Started with Ante

**Navigation:** home > [Getting Started](../getting-started.md)

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
Ante home page Search... ⌘K Ask AI Search... Navigation Getting Started Quickstart Ante Preview Ante Preview Getting Started # Quickstart Install Ante and start using it in under a minute
## ​ Prerequisites An API key or subscription from at least one LLM provider (Anthropic, OpenAI, etc.) — or use offline mode with no API key
## ​ Installation Installation instructions coming soon. ​ Quick examples ​ Interactive session Copy Ask AI # Launch the TUI — chat with the agent, approve tool calls, view diffs ante
### ​ Headless one-shot Copy Ask AI # Run a task and exit ante -p "add error handling to src/main.rs"
### ​ Pipe input from stdin Copy Ask AI # Pipe file contents for analysis cat src/lib.rs | ante -p "review this code for bugs"
### ​ Use a different provider Copy Ask AI # Override model and provider ante --provider openai --model gpt-4o -p "refactor this function"
### ​ Skip tool approvals Copy Ask AI # YOLO mode — auto-approve all tool calls ante --yolo "fix all clippy warnings"
## ​ What’s next? TUI Guide Master the interactive terminal interface. Headless Mode All CLI flags and output formats. Offline Mode Run models locally with no internet. Skills Extend Ante with portable Agent Skills. Previous Eval & Benchmark How Ante approaches evaluation, and why we chose Terminal Bench as our primary benchmark Next On this page Prerequisites
- Installation
- Quick examples
- Interactive session
- Headless one-shot
- Pipe input from stdin
- Use a different provider
- Skip tool approvals
- What’s next?
Assistant Responses are generated using AI and may contain mistakes. Quickstart - Ante

---

## Related Documentation

- [Core Concepts](./reference/core-concepts.md)
- [Features Overview](./features/)
- [Interactive TUI Guide](./guides/interactive-tui.md)
