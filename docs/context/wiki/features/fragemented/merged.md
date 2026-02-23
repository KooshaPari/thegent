# Merged Fragmented Markdown

## Source: docs/context/wiki/features

## Source: agent-organization.md

# Agent Organization (Experimental)

**Navigation:** home > [Features](../features/)

## Table of Contents

- [​ Decentralized Agents run in parallel rounds, reading each other’s prior outputs and proposing refinements. After a fixed number of rounds, consensus is formed without a central coordinator. Best for:](#​-decentralized-agents-run-in-parallel-rounds,-reading-each-other’s-prior-outputs-and-proposing-refinements.-after-a-fixed-number-of-rounds,-consensus-is-formed-without-a-central-coordinator.-best-for:)
- [​ Centralized Iterative A central orchestrator decomposes the problem, dispatches agents in parallel, evaluates their results, and decides whether to refine or finish. Best for:](#​-centralized-iterative-a-central-orchestrator-decomposes-the-problem,-dispatches-agents-in-parallel,-evaluates-their-results,-and-decides-whether-to-refine-or-finish.-best-for:)
- [​ Hybrid Iterative Combines centralized orchestration with decentralized peer refinement. The orchestrator plans and dispatches agents, then agents refine each other’s work in a peer round before the orchestrator evaluates. Best for:](#​-hybrid-iterative-combines-centralized-orchestration-with-decentralized-peer-refinement.-the-orchestrator-plans-and-dispatches-agents,-then-agents-refine-each-other’s-work-in-a-peer-round-before-the-orchestrator-evaluates.-best-for:)
- [​ Choosing an architecture Architecture Coordination Iteration Use when Independent](#​-choosing-an-architecture-architecture-coordination-iteration-use-when-independent)

---

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
Ante home page Search... ⌘K Ask AI Search... Navigation Agent Org Agent Organization (Experimental) Ante Preview Ante Preview Agent Org # Agent Organization (Experimental) Multi-agent architecture patterns for orchestrating collaborative AI agents
Ante supports multiple patterns for organizing agents to work together. Each architecture trades off between autonomy, coordination overhead, and result quality. ## ​ Independent Agents work in parallel on the same problem with no interaction. An aggregator synthesizes their outputs at the end. Best for:
tasks where diverse independent perspectives improve quality (brainstorming, redundant verification). Start

Parallel fan-out

Agent 1

Agent 2

Agent 3

Barrier / sync

Aggregator Synthesis

End

## ​ Decentralized Agents run in parallel rounds, reading each other’s prior outputs and proposing refinements. After a fixed number of rounds, consensus is formed without a central coordinator. Best for:
debate-style reasoning, peer review, or negotiation where no single authority should dominate. No

Yes

Start

Initialize

Shared board proposals so far

Parallel: read & propose

Agent 1 Read board + propose delta

Agent 2 Read board + propose delta

Agent 3 Read board + propose delta

Barrier / sync

Append deltas to board

Stop? round limit or convergence

Consensus formation from board

End

## ​ Centralized Iterative A central orchestrator decomposes the problem, dispatches agents in parallel, evaluates their results, and decides whether to refine or finish. Best for:
complex tasks that benefit from top-down planning with quality gates (code generation with review, multi-step research). No: refine

Yes

Start

Setup

Workspace tasks + results

Orchestrator Decompose / refine plan

Parallel: execute tasks

Agent 1

Agent 2

Agent 3

Barrier / sync

Write results to workspace

Orchestrator Evaluate quality

Done?

Final Synthesis

End

## ​ Hybrid Iterative Combines centralized orchestration with decentralized peer refinement. The orchestrator plans and dispatches agents, then agents refine each other’s work in a peer round before the orchestrator evaluates. Best for:
high-quality collaborative output where both structured planning and peer feedback matter (collaborative writing, architecture design). No: continue

Yes

Start

Setup

Workspace drafts + notes

Orchestrator Plan

Parallel: draft

Agent 1

Agent 2

Agent 3

Barrier / sync

Write drafts to workspace

Parallel: peer refine

Peer 1 Refine using others

Peer 2 Refine using others

Peer 3 Refine using others

Barrier / sync

Write refinements to workspace

Orchestrator Evaluate quality

Done?

Final Synthesis

End

## ​ Choosing an architecture Architecture Coordination Iteration Use when Independent
None Single pass You need diverse perspectives without interaction overhead Decentralized Peer-to-peer Fixed rounds Agents should self-organize without a central authority Centralized Iterative Orchestrator-driven Quality-gated You need structured decomposition with evaluation checkpoints Hybrid Iterative Orchestrator + peers Quality-gated You want both top-down planning and bottom-up peer refinement Previous Offline Mode (Experimental) Run Ante with local models - no API keys or internet required Next On this page - Independent
- Decentralized
- Centralized Iterative
- Hybrid Iterative
- Choosing an architecture
Assistant Responses are generated using AI and may contain mistakes. Agent Organization (Experimental) - Ante

---

## Related Documentation

- [Sub-Agents](./sub-agents.md)
- [Architecture](../advanced/architecture.md)


---

## Source: memory.md

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


---

## Source: model-catalog.md

# Model & Provider Catalog

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
Ante home page Search... ⌘K Ask AI Search... Navigation Configuration Model & Provider Catalog Ante Preview Ante Preview Configuration # Model & Provider Catalog Available models and providers supported by Ante
Ante is provider-agnostic. Each provider implements a common interface for sending prompts and receiving streaming responses. Providers are resolved from a catalog at session init time. ## ​ Providers Provider Wire Format Models Anthropic Messages API Claude family OpenAI Chat Completions / Responses GPT-4o, o1, etc. Gemini Gemini API Gemini family Grok OpenAI-compatible Grok models Open Router OpenAI-compatible Multiple providers Local llama.cpp GGUF models ​ Provider identifiers Use these identifiers with --provider
or in your settings file: ID Provider anthropic Anthropic (Claude) openai OpenAI (GPT) openai-response OpenAI Responses API gemini Google Gemini open-router Open Router xai Grok (xAI) local Local models via llama.cpp ## ​ Models ​ Anthropic (Claude) The default provider. Supports the full Claude model family through the Messages API. Copy Ask AI ante --provider anthropic --model claude-sonnet-4-5-20250514
### ​ OpenAI Supports GPT models through both the Chat Completions API and the Responses API. Copy Ask AI # Chat Completions API ante --provider openai --model gpt-4o # Responses API ante --provider openai-response --model gpt-4o
### ​ Google Gemini Supports Gemini models through the Gemini API. Copy Ask AI ante --provider gemini --model gemini-2.5-pro
### ​ Grok (xAI) Uses the OpenAI-compatible wire format. Copy Ask AI ante --provider xai --model grok-3
### ​ Open Router Access multiple providers through a single API via Open Router . Copy Ask AI ante --provider open-router --model anthropic/claude-sonnet-4-5
### ​ Local models Run GGUF models locally via the built-in llama.cpp engine. No API keys or internet required. See Offline Mode for setup details. Copy Ask AI ante --provider local
## ​ Authentication Each provider requires its own authentication method: Provider Auth Method Anthropic ANTHROPIC_API_KEY
env var or OAuth OpenAI OPENAI_API_KEY env var or OAuth Gemini GEMINI_API_KEY env var Grok XAI_API_KEY env var Open Router OPEN_ROUTER_API_KEY env var Local No authentication needed Anthropic and OpenAI also support interactive OAuth flows through the TUI. ## ​ Selecting a provider You can set your provider in three ways (in order of precedence): CLI flag
— ante --provider anthropic --model claude-sonnet-4-5-20250514 - Settings file
— Set provider and model in ~/.ante/settings.json - Built-in default
— Anthropic with Claude Sonnet Previous Preferences Settings file, environment variables, and directory structure Next On this page - Providers
- Provider identifiers
- Models
- Anthropic (Claude)
- OpenAI
- Google Gemini
- Grok (xAI)
- Open Router
- Local models
- Authentication
- Selecting a provider
Assistant Responses are generated using AI and may contain mistakes. Model & Provider Catalog - Ante

---

## Related Documentation

- [Preferences](./preferences.md)
- [Offline Mode](./offline-mode.md)
- [Adding Providers](../guides/adding-providers.md)


---

## Source: offline-mode.md

# Offline Mode (Experimental)

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
Ante home page Search... ⌘K Ask AI Search... Navigation Offline Mode Offline Mode (Experimental) Ante Preview Ante Preview Offline Mode # Offline Mode (Experimental) Run Ante with local models - no API keys or internet required
Ante can run entirely offline using local GGUF models via llama.cpp (our current local inference engine). This means no API keys, no internet, and no data leaving your machine. We expect to explore additional local engines over time, but the offline workflow and model format support will remain focused on a good “it just works” experience. In parallel, we’re building toward a truly self-contained agent stack; see our ongoing Rust effort at AntigmaLabs/nanochat-rs . ## ​ How it works Ante includes an integrated inference engine currently powered by llama.cpp. When you select offline mode, Ante: Discovers GGUF models on your system
- Estimates memory requirements based on model size and context window
- Runs inference locally through the embedded engine
## ​ Setting up 1 Download a GGUF model
Download a compatible GGUF model. Ante maintains a list of verified models that are known to work well. You can also use any GGUF model file. Popular sources: - Hugging Face
- Antigma on Hugging Face
2 Launch Ante

Start Ante normally: Copy Ask AI ante Use the offline mode selector in the TUI to pick your model. 3 Or use the CLI flag

Copy Ask AI ante --provider local "your prompt here" ## ​ Model discovery Ante automatically scans for GGUF model files. It handles: Single-file models (e.g., model.gguf
) - Sharded models (e.g., Model-00001-of-00008.gguf
) - Metadata extraction (file size, shard count)
## ​ Model preferences You can configure per-model preferences: Setting Description context_window
Context window size (minimum 32K tokens) thinking Enable/disable chain-of-thought temperature Sampling temperature ## ​ Memory considerations Ante estimates memory usage based on: Model file size
— The base memory needed to load the model - KV cache
— Scales with context window size (bytes per token) - Shard count
— Multi-file models need proportional memory For large models, reduce the context window to lower memory usage. The minimum is 32K tokens. ## ​ Verified models Ante includes a curated list of verified models that are tested for compatibility and quality. These are shown prominently in the model selector. Previous Interactive TUI Using Ante's rich terminal user interface Next On this page How it works
- Setting up
- Model discovery
- Model preferences
- Memory considerations
- Verified models
Assistant Responses are generated using AI and may contain mistakes. Offline Mode (Experimental) - Ante

---

## Related Documentation

- [Preferences](./preferences.md)
- [Model Catalog](./model-catalog.md)


---

## Source: preferences.md

# Preferences

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
Ante home page Search... ⌘K Ask AI Search... Navigation Configuration Preferences Ante Preview Ante Preview Configuration # Preferences Settings file, environment variables, and directory structure
## ​ Settings file Ante stores user preferences in ~/.ante/settings.json
: Copy Ask AI { "model" : "claude-sonnet-4-5-20250514" , "provider" : "anthropic" , "theme" : "default" , "policy" : "default" , "has_completed_onboarding" : true } Field Description model Default model name provider Default API provider theme TUI color theme policy Default permission policy ( default or yolo ) has_completed_onboarding Whether the onboarding flow has been completed Settings can be overridden per-session via CLI flags. ## ​ Environment variables Variable Description ANTHROPIC_API_KEY
API key for Anthropic (Claude) OPENAI_API_KEY API key for OpenAI ANTE_HOME Override the home config directory (default: ~/.ante ) ANTE_DISABLE_STREAMING Disable streaming responses in TUI mode ## ​ Directory structure ​ User-level ( ~/.ante/
) Copy Ask AI ~/.ante/ ├── settings.json      # User preferences ├── skills/            # User-level skills └── agents/            # User-level sub-agents ### ​ Project-level ( .ante/
) Copy Ask AI .ante/ └── skills/            # Project-specific skills ### ​ Claude.ai compatibility ( .claude/
) Copy Ask AI .claude/ └── projects/ └── <path>/ └── memory/ └── MEMORY.md   # Auto-memory for this project ### ​ Temporary files Copy Ask AI /tmp/ante/<project-hash>/   # Temp files scoped per project
## ​ Precedence Configuration is resolved in this order (later overrides earlier): Built-in defaults
- ~/.ante/settings.json
- CLI flags ( --model
, --provider , etc.) Previous Adding a 3rd Party Provider Connect Ante to third-party and custom LLM providers Next On this page - Settings file
- Environment variables
- Directory structure
- User-level (~/.ante/)
- Project-level (.ante/)
- Claude.ai compatibility (.claude/)
- Temporary files
- Precedence
Assistant Responses are generated using AI and may contain mistakes. Preferences - Ante

---

## Related Documentation

- [Model Catalog](./model-catalog.md)
- [Offline Mode](./offline-mode.md)


---

## Source: skills.md

# Skills

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
Ante home page Search... ⌘K Ask AI Search... Navigation Extensibility Skills Ante Preview Ante Preview Extensibility # Skills Give Ante new capabilities with Agent Skills — the open format for portable agent expertise
Skills are folders of instructions, scripts, and resources that extend Ante’s capabilities. They follow the open Agent Skills format, making them portable across compatible agent products. ## ​ Creating a skill A skill is a directory containing a SKILL.md
file: Copy Ask AI commit/ └── SKILL.md SKILL.md uses YAML frontmatter followed by Markdown instructions: Copy Ask AI --- name : commit description : Create a git commit with a descriptive message following conventional commit format. --- Look at the current git diff and create a commit with a clear, descriptive message that follows conventional commit format. Use `git add` to stage relevant files first. ### ​ Example: review skill with tools and references Copy Ask AI review/ ├── SKILL.md └── references/ └── checklist.md
Copy Ask AI --- name : review description : Review code changes for bugs, security issues, and style. Use when the user asks for a code review. allowed-tools : - Read - Glob - Grep --- Review the code at $ARGUMENTS for: - Bugs and logic errors - Security vulnerabilities - Style and idiom issues - Missing error handling See [ checklist ]( references/checklist.md ) for the full review checklist. Provide a summary with specific line references. ## ​ Skill directories Directory Scope ~/.ante/skills/
User-level (available in all projects) agents/skills/ Project-level (available in this project) .ante/skills/ Project-level (available in this project) .claude/skills/ Project-level (available in this project) ## ​ SKILL.md frontmatter Every SKILL.md
must start with a YAML frontmatter block delimited by --- . The block can be empty, but the delimiters are required. Field Required Default Description name No Parent directory name Identifier for the skill. If omitted, the skill directory name is used. description No First paragraph of body What this skill does and when to use it. If omitted, extracted from the first paragraph of the Markdown body. argument-hint No — Hint text shown to the user for expected arguments (e.g. <path> ). user-invocable No true Whether the skill can be invoked by the user via slash command. Set to false for skills intended only for model invocation. disable-model-invocation No false When true , prevents the model from invoking this skill automatically. allowed-tools No — YAML list of pre-approved tools the skill can use (e.g. Read , Grep , Bash(git diff -- *) ). metadata No — Arbitrary key-value pairs for additional metadata. ## ​ Optional directories Skills can include additional resources alongside SKILL.md
: Copy Ask AI my-skill/ ├── SKILL.md           # Required — instructions ├── scripts/           # Executable code the agent can run ├── references/        # Additional docs loaded on demand └── assets/            # Templates, schemas, data files - scripts/
— Self-contained scripts (Python, Bash, etc.) the agent can execute - references/
— Detailed documentation loaded only when needed, keeping the main instructions lean - assets/
— Static resources like templates, schemas, or lookup tables ## ​ How skills are discovered Skills are discovered from multiple directories in precedence order. Later directories override earlier ones
if they share a skill name: - System-level (built-in skills)
- ~/.ante/skills/
(user-level) - agents/skills/
(project-level) - .ante/skills/
(project-level) - .claude/skills/
(project-level) A project-level skill overrides a user-level skill of the same name. If multiple project-level directories contain a skill with the same name, the one discovered last wins. ## ​ Using skills Invoke a skill during a session with the slash syntax: Copy Ask AI /commit
Or with arguments: Copy Ask AI /review src/core/session.rs The $ARGUMENTS placeholder in the skill instructions will be replaced with whatever you pass after the skill name. ## ​ Learn more The Agent Skills format is an open standard supported by multiple agent products. See the full specification for details on naming conventions, progressive disclosure, and validation. Previous Sub-Agents Delegate complex tasks to specialized sub-agents Next On this page Creating a skill
- Example: review skill with tools and references
- Skill directories
- SKILL.md frontmatter
- Optional directories
- How skills are discovered
- Using skills
- Learn more
Assistant Responses are generated using AI and may contain mistakes. Skills - Ante

---

## Related Documentation

- [Tools](./tools.md)
- [Sub-Agents](./sub-agents.md)
- [Adding Providers](../guides/adding-providers.md)


---

## Source: sub-agents.md

# Sub-Agents

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
Ante home page Search... ⌘K Ask AI Search... Navigation Extensibility Sub-Agents Ante Preview Ante Preview Extensibility # Sub-Agents Delegate complex tasks to specialized sub-agents
Sub-agents are specialized agents that the main agent can spawn to handle complex, multi-step tasks. Each sub-agent runs with its own prompt, tool set, and optional model override. ## ​ Built-in sub-agents Ante ships with two built-in sub-agents: ​ General A general-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. The main agent delegates to this when it needs to perform a search it isn’t confident about completing in a few tries. ​ Explorer A fast agent specialized for codebase exploration. It can quickly find files by patterns, search code for keywords, and answer structural questions about the codebase. ​ Creating custom sub-agents Create a markdown file in ~/.ante/agents/
with YAML frontmatter: Copy Ask AI --- name : "security-reviewer" description : "Reviews code for security vulnerabilities and OWASP top 10 issues" color : "red" --- You are a security-focused code reviewer. Analyze the provided code for: - Injection vulnerabilities (SQL, command, XSS) - Authentication and authorization flaws - Sensitive data exposure - Security misconfiguration - Known vulnerable dependencies Provide findings with severity ratings and remediation steps. ### ​ Frontmatter fields Field Required Description name
Yes Unique identifier for the agent description Yes What this agent does (shown to the main agent for delegation decisions) model No Override the LLM model for this agent tools No Restrict which tools this agent can use color No Display color in the TUI ## ​ How sub-agents work When the main agent encounters a task that matches a sub-agent’s description, it uses the Task
tool to spawn the sub-agent: - The main agent evaluates available sub-agents and their descriptions
- It delegates the task via the Task
tool with a detailed prompt - The sub-agent runs independently with its own context
- The result is returned to the main agent, which incorporates it into the conversation
Copy Ask AI ┌────────────┐     Task      ┌──────────────┐ │ Main Agent │ ────────────▶ │  Sub-Agent   │ │            │ ◀──────────── │  (Explorer)  │ │            │    Result     └──────────────┘ │            │ │            │     Task      ┌──────────────┐ │            │ ────────────▶ │  Sub-Agent   │ │            │ ◀──────────── │  (General)   │ └────────────┘    Result     └──────────────┘ ## ​ Discovery Sub-agents are discovered from: Built-in agents (General, Explorer)
- ~/.ante/agents/
directory User-defined agents are loaded alongside the built-in ones. All available agents are registered at session initialization time. Previous Model & Provider Catalog Available models and providers supported by Ante Next On this page - Built-in sub-agents
- General
- Explorer
- Creating custom sub-agents
- Frontmatter fields
- How sub-agents work
- Discovery
Assistant Responses are generated using AI and may contain mistakes. Sub-Agents - Ante

---

## Related Documentation

- [Agent Organization](./agent-organization.md)
- [Core Concepts](../reference/core-concepts.md)
- [Architecture](../advanced/architecture.md)


---

## Source: tools.md

# Tools

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
Ante home page Search... ⌘K Ask AI Search... Navigation Reference Tools Ante Preview Ante Preview Reference # Tools Reference for all built-in tools available to the agent
Tools are the capabilities available to the agent during a session. Each tool has a name, description, input schema, and an approval requirement. ## ​ File I/O ​ Read Read file contents. Supports text files, images (PNG, JPG), PDFs, and Jupyter notebooks. Approval required
: No - Key inputs
: file_path (absolute path), optional offset and limit for large files ### ​ Write Create or overwrite a file. Approval required
: Yes - Key inputs
: file_path , content ### ​ Edit Perform exact string replacements in files. Finds old_string
and replaces it with new_string . - Approval required
: Yes - Key inputs
: file_path , old_string , new_string , optional replace_all ### ​ Glob Find files matching a glob pattern (e.g., **/*.rs
, src/**/*.ts ). - Approval required
: No - Key inputs
: pattern , optional path (search directory) ### ​ Grep Search file contents with regex patterns. Built on ripgrep. Approval required
: No - Key inputs
: pattern (regex), optional path , glob filter, type filter, output_mode ## ​ Shell ​ Bash Execute shell commands with optional timeout (default 2 minutes, max 10 minutes). Approval required
: Yes - Key inputs
: command , optional description , timeout ### ​ BashOutput Read output from a running or completed background shell. Approval required
: No - Key inputs
: id (shell identifier) ### ​ KillShell Terminate a background shell process. Approval required
: No - Key inputs
: id (shell identifier) ## ​ Builtin ​ Task Spawn a sub-agent to handle complex, multi-step tasks autonomously. Approval required
: No - Key inputs
: prompt , subagent_type ### ​ TodoWrite Manage a task list for tracking progress on multi-step work. Approval required
: No - Key inputs
: todos (list of items with id, content, status) ### ​ WebFetch Fetch content from a URL and process it. Approval required
: No - Key inputs
: url , prompt (what to extract) ### ​ WebSearch Search the web and return results. Approval required
: No - Key inputs
: query ## ​ Tool filtering Control which tools are available in a session: Copy Ask AI # Only allow these tools ante --allowed-tools Read Glob Grep "analyze the code" # Remove these tools ante --disallowed-tools Bash Write "read-only analysis"
Supports ToolMatcher syntax for fine-grained control: Copy Ask AI # Allow Bash but only for specific patterns ante --allowed-tools "Read" "Bash(cargo test)" "Bash(cargo clippy)" Previous Memory Persistent auto-memory that carries context across conversations On this page - File I/O
- Read
- Write
- Edit
- Glob
- Grep
- Shell
- Bash
- BashOutput
- KillShell
- Builtin
- Task
- TodoWrite
- WebFetch
- WebSearch
- Tool filtering
Assistant Responses are generated using AI and may contain mistakes. Tools - Ante

---

## Related Documentation

- [Skills](./skills.md)
- [Architecture](../advanced/architecture.md)


---

Copied count: 8