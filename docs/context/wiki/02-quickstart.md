# Quickstart

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

Quickstart

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Getting Started

# Quickstart

Install Ante and start using it in under a minute

## 

​

Prerequisites

  * An API key or subscription from at least one LLM provider (Anthropic, OpenAI, etc.) — or use [offline mode](/offline) with no API key

## 

​

Installation

Installation instructions coming soon.

## 

​

Quick examples

### 

​

Interactive session

Copy

Ask AI
    
    
    # Launch the TUI — chat with the agent, approve tool calls, view diffs
    ante
    

### 

​

Headless one-shot

Copy

Ask AI
    
    
    # Run a task and exit
    ante -p "add error handling to src/main.rs"
    

### 

​

Pipe input from stdin

Copy

Ask AI
    
    
    # Pipe file contents for analysis
    cat src/lib.rs | ante -p "review this code for bugs"
    

### 

​

Use a different provider

Copy

Ask AI
    
    
    # Override model and provider
    ante --provider openai --model gpt-4o -p "refactor this function"
    

### 

​

Skip tool approvals

Copy

Ask AI
    
    
    # YOLO mode — auto-approve all tool calls
    ante --yolo "fix all clippy warnings"
    

## 

​

What’s next?

## [TUI GuideMaster the interactive terminal interface.](/usage/tui)## [Headless ModeAll CLI flags and output formats.](/usage/headless)## [Offline ModeRun models locally with no internet.](/offline)## [SkillsExtend Ante with portable Agent Skills.](/extend/skills)

[Previous](/start/overview)[Eval & BenchmarkHow Ante approaches evaluation, and why we chose Terminal Bench as our primary benchmarkNext](/start/eval)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * Prerequisites
  * Installation
  * Quick examples
  * Interactive session
  * Headless one-shot
  * Pipe input from stdin
  * Use a different provider
  * Skip tool approvals
  * What’s next?

Assistant

Responses are generated using AI and may contain mistakes.

Quickstart - Ante

