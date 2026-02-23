# Interactive TUI

**Navigation:** home > [Guides](../guides/)

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
Ante home page Search... ⌘K Ask AI Search... Navigation Usage Interactive TUI Ante Preview Ante Preview Usage # Interactive TUI Using Ante’s rich terminal user interface
Launch Ante without a prompt to enter the interactive TUI: Copy Ask AI ante ## ​ Overview The TUI is built with ratatui and provides a rich chat interface directly in your terminal. It renders inline (up to 24 lines) and uses debounced rendering at approximately 100fps for smooth output. ​ Key features ​ Chat interface The main view shows a conversation between you and the agent. Type your prompt in the input area and press Enter to send. The agent’s responses stream in real-time with markdown rendering. ​ Tool approval When the agent wants to execute a tool that requires approval (like Bash
or Write ), you’ll see an approval prompt. You can: - Allow
the tool call - Deny
it and the agent will adjust its approach ### ​ Diff view When the agent proposes file edits, Ante switches to a fullscreen diff view on an alternate screen. You can review the exact changes before approving. ​ Model and provider selection Use the built-in selectors to switch models or providers during a session without restarting. ​ Theme selection Ante includes a theme system for consistent styling. Choose a theme through the theme dialog. ​ Keyboard shortcuts Key Action Enter
Send message Ctrl+C Interrupt current task / Exit Escape Cancel current input ## ​ CLI flags for TUI mode You can customize the TUI session with flags: Copy Ask AI # Use a specific model ante --model claude-sonnet-4-5-20250514 # Use a specific provider ante --provider openai # Override the system prompt ante --system-prompt "You are a Python expert" # Append to the system prompt ante --append-system-prompt "Always use type hints" # Restrict available tools ante --allowed-tools Read Grep Glob # Remove specific tools ante --disallowed-tools Bash Write
## ​ Streaming Streaming is enabled by default in TUI mode for real-time response rendering. To disable it, set the ANTE_DISABLE_STREAMING
environment variable: Copy Ask AI ANTE_DISABLE_STREAMING = 1 ante Previous Headless Mode Run Ante as a non-interactive CLI for scripting and CI pipelines Next On this page - Overview
- Key features
- Chat interface
- Tool approval
- Diff view
- Model and provider selection
- Theme selection
- Keyboard shortcuts
- CLI flags for TUI mode
- Streaming
Assistant Responses are generated using AI and may contain mistakes. Interactive TUI - Ante

---

## Related Documentation

- [Headless Mode](./headless-mode.md)
- [Getting Started](../getting-started.md)
