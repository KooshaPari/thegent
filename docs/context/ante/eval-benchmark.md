# ANTE: Eval & Benchmark

> Extracted from Ante docs. Fetched 2026-02-20

Ante home page

Search...



Navigation

Getting Started

Eval & Benchmark
Getting Started
Eval & Benchmark
How Ante approaches evaluation, and why we chose Terminal Bench as our primary benchmark
​

Eval
Evaluation is the backbone of building a reliable AI agent. We were practicing the same principles Anthropic later laid out in Demystifying Evals for AI Agents before they published it.
Most of the magic comes from the model — but the agent harness is the critical conduit between human and AI.
We evaluate the agent and how well it channels the model’s power — not the model itself. 
Which is why we chose Terminal Bench and its real-world complex task environment.
​

Principles
Drawn from the practices in Demystifying Evals for AI Agents:
Start early, start simple. A small but honest eval set drawn from actual failures beats a large contrived one.
Grade outcomes, not trajectories. Did the agent solve the problem? Especially for a terminal agent, many correct paths exist.
Isolate and reproduce. Every eval run starts clean. When a score drops, we know it reflects a real regression.
​

Why Terminal Bench/Harbor
We use Terminal Bench and Harbor as our primary external benchmark for following reasons:
Rigorous. Unambiguous task specs, deterministic grading where possible, and isolated execution environments.
Focused on core capability. Can the agent accomplish real tasks in a real shell? Reading context, reasoning, acting, verifying — the exact loop we are building Ante around.
​

Terminal Bench 2.0 results
Topped the Terminal Bench 1.0 leaderboard in 2025
Topped the Terminal Bench 2.0 leaderboard in 2026 as verified agent and remain best in class for Gemini (February 2026)

Previous
Core Concepts & Protocol

Next

Powered by



Assistant



Responses are generated using AI and may contain mistakes.



