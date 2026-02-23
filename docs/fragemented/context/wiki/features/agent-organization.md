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
