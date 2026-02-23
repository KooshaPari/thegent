# Eval & Benchmark

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

Getting Started

Eval & Benchmark

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Getting Started

# Eval & Benchmark

How Ante approaches evaluation, and why we chose Terminal Bench as our primary benchmark

# 

​

Eval

Evaluation is the backbone of building a reliable AI agent. We were practicing the same principles Anthropic later laid out in [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) before they published it. Most of the magic comes from the model — but the agent harness is the critical conduit between human and AI.

> We evaluate the **agent** and how well it channels the model’s power — not the model itself.

Which is why we chose [Terminal Bench](https://tbench.ai) and its real-world complex task environment.

## 

​

Principles

Drawn from the practices in [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):

  * **Start early, start simple.** A small but honest eval set drawn from actual failures beats a large contrived one.
  * **Grade outcomes, not trajectories.** Did the agent solve the problem? Especially for a terminal agent, many correct paths exist.
  * **Isolate and reproduce.** Every eval run starts clean. When a score drops, we know it reflects a real regression.

## 

​

Why Terminal Bench/Harbor

We use [Terminal Bench](https://github.com/laude-institute/terminal-bench) and [Harbor](https://github.com/laude-institute/harbor) as our primary external benchmark for following reasons:

  * **Rigorous.** Unambiguous task specs, deterministic grading where possible, and isolated execution environments.
  * **Focused on core capability.** Can the agent accomplish real tasks in a real shell? Reading context, reasoning, acting, verifying — the exact loop we are building Ante around.

## 

​

Terminal Bench 2.0 results

  * Topped the Terminal Bench 1.0 leaderboard in 2025
  * Topped the Terminal Bench 2.0 leaderboard in 2026 as verified agent and remain best in class for Gemini (February 2026)

[Previous](/start/quickstart)[Core Concepts & ProtocolAnte's fundamental abstractions, and the Op/Evt message protocol that connects themNext](/concepts/core-concepts)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * Eval
  * Principles
  * Why Terminal Bench/Harbor
  * Terminal Bench 2.0 results

Assistant

Responses are generated using AI and may contain mistakes.

Eval & Benchmark - Ante

