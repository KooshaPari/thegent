# Preferences

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

Configuration

Preferences

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Configuration

# Preferences

Settings file, environment variables, and directory structure

## 

​

Settings file

Ante stores user preferences in `~/.ante/settings.json`:

Copy

Ask AI
    
    
    {
      "model": "claude-sonnet-4-5-20250514",
      "provider": "anthropic",
      "theme": "default",
      "policy": "default",
      "has_completed_onboarding": true
    }
    

Field| Description  
---|---  
`model`| Default model name  
`provider`| Default API provider  
`theme`| TUI color theme  
`policy`| Default permission policy (`default` or `yolo`)  
`has_completed_onboarding`| Whether the onboarding flow has been completed  
  
Settings can be overridden per-session via CLI flags.

## 

​

Environment variables

Variable| Description  
---|---  
`ANTHROPIC_API_KEY`| API key for Anthropic (Claude)  
`OPENAI_API_KEY`| API key for OpenAI  
`ANTE_HOME`| Override the home config directory (default: `~/.ante`)  
`ANTE_DISABLE_STREAMING`| Disable streaming responses in TUI mode  
  
## 

​

Directory structure

### 

​

User-level (`~/.ante/`)

Copy

Ask AI
    
    
    ~/.ante/
    ├── settings.json      # User preferences
    ├── skills/            # User-level skills
    └── agents/            # User-level sub-agents
    

### 

​

Project-level (`.ante/`)

Copy

Ask AI
    
    
    .ante/
    └── skills/            # Project-specific skills
    

### 

​

Claude.ai compatibility (`.claude/`)

Copy

Ask AI
    
    
    .claude/
    └── projects/
        └── <path>/
            └── memory/
                └── MEMORY.md   # Auto-memory for this project
    

### 

​

Temporary files

Copy

Ask AI
    
    
    /tmp/ante/<project-hash>/   # Temp files scoped per project
    

## 

​

Precedence

Configuration is resolved in this order (later overrides earlier):

  1. Built-in defaults
  2. `~/.ante/settings.json`
  3. CLI flags (`--model`, `--provider`, etc.)

[Previous](/configuration/catalog)[Adding a 3rd Party ProviderConnect Ante to third-party and custom LLM providersNext](/configuration/third-party-provider)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * Settings file
  * Environment variables
  * Directory structure
  * User-level (~/.ante/)
  * Project-level (.ante/)
  * Claude.ai compatibility (.claude/)
  * Temporary files
  * Precedence

Assistant

Responses are generated using AI and may contain mistakes.

Preferences - Ante

