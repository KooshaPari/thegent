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
