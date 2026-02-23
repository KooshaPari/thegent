# Sub-Agents

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

Extensibility

Sub-Agents

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Extensibility

# Sub-Agents

Delegate complex tasks to specialized sub-agents

Sub-agents are specialized agents that the main agent can spawn to handle complex, multi-step tasks. Each sub-agent runs with its own prompt, tool set, and optional model override.

## 

​

Built-in sub-agents

Ante ships with two built-in sub-agents:

### 

​

General

A general-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. The main agent delegates to this when it needs to perform a search it isn’t confident about completing in a few tries.

### 

​

Explorer

A fast agent specialized for codebase exploration. It can quickly find files by patterns, search code for keywords, and answer structural questions about the codebase.

## 

​

Creating custom sub-agents

Create a markdown file in `~/.ante/agents/` with YAML frontmatter:

Copy

Ask AI
    
    
    ---
    name: "security-reviewer"
    description: "Reviews code for security vulnerabilities and OWASP top 10 issues"
    color: "red"
    ---
    
    You are a security-focused code reviewer. Analyze the provided code for:
    
    - Injection vulnerabilities (SQL, command, XSS)
    - Authentication and authorization flaws
    - Sensitive data exposure
    - Security misconfiguration
    - Known vulnerable dependencies
    
    Provide findings with severity ratings and remediation steps.
    

### 

​

Frontmatter fields

Field| Required| Description  
---|---|---  
`name`| Yes| Unique identifier for the agent  
`description`| Yes| What this agent does (shown to the main agent for delegation decisions)  
`model`| No| Override the LLM model for this agent  
`tools`| No| Restrict which tools this agent can use  
`color`| No| Display color in the TUI  
  
## 

​

How sub-agents work

When the main agent encounters a task that matches a sub-agent’s description, it uses the `Task` tool to spawn the sub-agent:

  1. The main agent evaluates available sub-agents and their descriptions
  2. It delegates the task via the `Task` tool with a detailed prompt
  3. The sub-agent runs independently with its own context
  4. The result is returned to the main agent, which incorporates it into the conversation

Copy

Ask AI
    
    
    ┌────────────┐     Task      ┌──────────────┐
    │ Main Agent │ ────────────▶ │  Sub-Agent   │
    │            │ ◀──────────── │  (Explorer)  │
    │            │    Result     └──────────────┘
    │            │
    │            │     Task      ┌──────────────┐
    │            │ ────────────▶ │  Sub-Agent   │
    │            │ ◀──────────── │  (General)   │
    └────────────┘    Result     └──────────────┘
    

## 

​

Discovery

Sub-agents are discovered from:

  1. Built-in agents (General, Explorer)
  2. `~/.ante/agents/` directory

User-defined agents are loaded alongside the built-in ones. All available agents are registered at session initialization time.

[Previous](/extend/skills)[Model & Provider CatalogAvailable models and providers supported by AnteNext](/configuration/catalog)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * Built-in sub-agents
  * General
  * Explorer
  * Creating custom sub-agents
  * Frontmatter fields
  * How sub-agents work
  * Discovery

Assistant

Responses are generated using AI and may contain mistakes.

Sub-Agents - Ante

