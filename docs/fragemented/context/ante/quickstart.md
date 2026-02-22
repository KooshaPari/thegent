# ANTE: Quickstart

> Extracted from Ante docs. Fetched 2026-02-20

Ante home page

Search...



Navigation

Getting Started

Quickstart
Getting Started
Quickstart
Install Ante and start using it in under a minute
​

Prerequisites
An API key or subscription from at least one LLM provider (Anthropic, OpenAI, etc.) — or use offline mode with no API key
​

Installation

Installation instructions coming soon.
​

Quick examples
​

Interactive session

Copy

Ask AI
# Launch the TUI — chat with the agent, approve tool calls, view diffs
ante

​

Headless one-shot

Copy

Ask AI
# Run a task and exit
ante -p "add error handling to src/main.rs"

​

Pipe input from stdin

Copy

Ask AI
# Pipe file contents for analysis
cat src/lib.rs | ante -p "review this code for bugs"

​

Use a different provider

Copy

Ask AI
# Override model and provider
ante --provider openai --model gpt-4o -p "refactor this function"

​

Skip tool approvals

Copy

Ask AI
# YOLO mode — auto-approve all tool calls
ante --yolo "fix all clippy warnings"

​

What’s next?

TUI Guide
Master the interactive terminal interface.

Headless Mode
All CLI flags and output formats.

Offline Mode
Run models locally with no internet.

Skills
Extend Ante with portable Agent Skills.

Previous
Eval & Benchmark

Next

Powered by



Assistant



Responses are generated using AI and may contain mistakes.
