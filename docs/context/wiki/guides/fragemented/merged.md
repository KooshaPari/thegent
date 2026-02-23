# Merged Fragmented Markdown

## Source: docs/context/wiki/guides

## Source: adding-providers.md

# Adding a 3rd Party Provider

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
Ante home page Search... ⌘K Ask AI Search... Navigation Configuration Adding a 3rd Party Provider Ante Preview Ante Preview Configuration # Adding a 3rd Party Provider Connect Ante to third-party and custom LLM providers
Ante supports connecting to third-party LLM providers beyond the built-in catalog. Any provider that exposes an OpenAI-compatible API can be used with Ante. ## ​ Using Open Router The easiest way to access third-party models is through Open Router , which provides a unified API for hundreds of models from different providers. 1 Get an Open Router API key
Sign up at openrouter.ai and generate an API key. 2 Set your API key

Copy Ask AI export OPEN_ROUTER_API_KEY = "sk-or-..." 3 Select a model

Browse Open Router’s model list and use the model identifier: Copy Ask AI ante --provider open-router --model anthropic/claude-sonnet-4-5 ## ​ OpenAI-compatible providers Many LLM providers expose an OpenAI-compatible API (e.g., Together AI, Fireworks, Groq Cloud, Perplexity). You can connect to these through the OpenAI provider by setting a custom base URL. 1 Set the base URL
Point the OpenAI provider to your chosen service: Copy Ask AI export OPENAI_API_BASE = "https://api.together.xyz/v1" 2 Set your API key

Copy Ask AI export OPENAI_API_KEY = "your-provider-api-key" 3 Run with the OpenAI provider

Copy Ask AI ante --provider openai --model meta-llama/Llama-3-70b-chat-hf ## ​ Local models For fully offline usage with local GGUF models via the built-in llama.cpp engine, see Offline Mode . Copy Ask AI ante --provider local
## ​ Tips When using third-party providers, make sure the model you select supports tool use (function calling). Ante relies on tool use for its agent capabilities. Not all models work equally well as coding agents. Models need strong instruction following and tool use support. If you experience issues, try a larger or more capable model. Previous Memory Persistent auto-memory that carries context across conversations Next On this page Using Open Router
- OpenAI-compatible providers
- Local models
- Tips
Assistant Responses are generated using AI and may contain mistakes. Adding a 3rd Party Provider - Ante

---

## Related Documentation

- [Model Catalog](../features/model-catalog.md)
- [Skills](../features/skills.md)


---

## Source: eval-benchmark.md

# Evaluation & Benchmarking

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
Ante home page Search... ⌘K Ask AI Search... Navigation Getting Started Eval & Benchmark Ante Preview Ante Preview Getting Started # Eval & Benchmark How Ante approaches evaluation, and why we chose Terminal Bench as our primary benchmark
# ​ Eval Evaluation is the backbone of building a reliable AI agent. We were practicing the same principles Anthropic later laid out in Demystifying Evals for AI Agents before they published it. Most of the magic comes from the model — but the agent harness is the critical conduit between human and AI. We evaluate the agent
and how well it channels the model’s power — not the model itself. Which is why we chose Terminal Bench and its real-world complex task environment. ## ​ Principles Drawn from the practices in Demystifying Evals for AI Agents : Start early, start simple.
A small but honest eval set drawn from actual failures beats a large contrived one. - Grade outcomes, not trajectories.
Did the agent solve the problem? Especially for a terminal agent, many correct paths exist. - Isolate and reproduce.
Every eval run starts clean. When a score drops, we know it reflects a real regression. ## ​ Why Terminal Bench/Harbor We use Terminal Bench and Harbor as our primary external benchmark for following reasons: Rigorous.
Unambiguous task specs, deterministic grading where possible, and isolated execution environments. - Focused on core capability.
Can the agent accomplish real tasks in a real shell? Reading context, reasoning, acting, verifying — the exact loop we are building Ante around. ## ​ Terminal Bench 2.0 results Topped the Terminal Bench 1.0 leaderboard in 2025
- Topped the Terminal Bench 2.0 leaderboard in 2026 as verified agent and remain best in class for Gemini (February 2026)
Previous Core Concepts & Protocol Ante's fundamental abstractions, and the Op/Evt message protocol that connects them Next On this page - Eval
- Principles
- Why Terminal Bench/Harbor
- Terminal Bench 2.0 results
Assistant Responses are generated using AI and may contain mistakes. Eval & Benchmark - Ante

---

## Related Documentation

- [Getting Started](../getting-started.md)
- [Architecture](../advanced/architecture.md)


---

## Source: headless-mode.md

# Headless Mode

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
Ante home page Search... ⌘K Ask AI Search... Navigation Usage Headless Mode Ante Preview Ante Preview Usage # Headless Mode Run Ante as a non-interactive CLI for scripting and CI pipelines
Headless mode runs Ante without the TUI — it processes a prompt, executes the task, and exits. This is ideal for scripting, CI/CD pipelines, and automated workflows. ## ​ Basic usage Provide a prompt as an argument: Copy Ask AI ante "explain what this project does"
Or via the -p / --prompt flag: Copy Ask AI ante --prompt "add tests for the auth module" ## ​ Stdin input Pipe content from stdin: Copy Ask AI cat src/main.rs | ante "review this code for bugs"
Combine stdin with a prompt argument: Copy Ask AI echo "function add(a, b) { return a + b }" | ante "add TypeScript types" When both stdin and a prompt argument are provided, they are concatenated (stdin first, then the prompt). ## ​ CLI reference Copy Ask AI ante [OPTIONS] [--prompt <PROMPT>]
Flag Description -p , --prompt <PROMPT> The prompt to run -m , --model <MODEL> Override the model name --provider <PROVIDER> Override the API provider --yolo Skip all tool approval prompts --output-format <FORMAT> Output format: json , human , minimal (default: minimal ) --system-prompt <PROMPT> Replace the default system prompt entirely --append-system-prompt <TEXT> Append text to the system prompt --allowed-tools <TOOLS>... Only allow these tools (space-separated) --disallowed-tools <TOOLS>... Disallow these tools (space-separated) --check Run a verification pass after the main task completes ## ​ Output formats ​ Minimal (default) Shows only agent messages, info, and errors: Copy Ask AI ante "what does this project do"
### ​ Human Shows all events in a human-readable format with ANSI colors: Copy Ask AI ante --output-format human "fix the type error in main.rs"
### ​ JSON Outputs every event as a JSON object (one per line), suitable for machine consumption: Copy Ask AI ante --output-format json "list all TODO comments" | jq '.event'
## ​ Verification check The --check
flag runs a second pass after the main task, asking the agent to review its own work: Copy Ask AI ante --check "refactor the auth module to use async/await" The verification pass will: - Review what was accomplished against the original request
- Complete anything missing or incomplete
- Optimize where possible without affecting correctness
## ​ Context enrichment In headless mode, Ante automatically appends the current directory’s folder structure to your prompt. This gives the agent awareness of the project layout without you needing to describe it. ​ Headless behavior notes Streaming is disabled
— Responses are buffered for cleaner output - Yolo policy is implied
— All tool calls are auto-approved (no interactive prompts) - Authentication is checked eagerly
— If the provider isn’t authenticated, Ante exits immediately with an error ## ​ Examples ​ CI: lint and fix Copy Ask AI ante --yolo "run cargo clippy and fix all warnings"
### ​ Code generation Copy Ask AI ante --model claude-sonnet-4-5-20250514 --check \ "add comprehensive unit tests for src/core/session.rs"
### ​ Restricted tools Copy Ask AI # Read-only analysis — no file writes or shell access ante --allowed-tools Read Glob Grep \ "analyze the codebase architecture and summarize it"
### ​ Pipe a diff for review Copy Ask AI git diff HEAD~1 | ante "review this diff for bugs and security issues"
Previous Skills Give Ante new capabilities with Agent Skills — the open format for portable agent expertise Next On this page - Basic usage
- Stdin input
- CLI reference
- Output formats
- Minimal (default)
- Human
- JSON
- Verification check
- Context enrichment
- Headless behavior notes
- Examples
- CI: lint and fix
- Code generation
- Restricted tools
- Pipe a diff for review
Assistant Responses are generated using AI and may contain mistakes. Headless Mode - Ante

---

## Related Documentation

- [Interactive TUI](./interactive-tui.md)
- [Preferences](../features/preferences.md)


---

## Source: interactive-tui.md

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


---

Copied count: 4