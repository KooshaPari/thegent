# Adding a 3rd Party Provider

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

Adding a 3rd Party Provider

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Configuration

# Adding a 3rd Party Provider

Connect Ante to third-party and custom LLM providers

Ante supports connecting to third-party LLM providers beyond the built-in catalog. Any provider that exposes an OpenAI-compatible API can be used with Ante.

## 

​

Using Open Router

The easiest way to access third-party models is through [Open Router](https://openrouter.ai/), which provides a unified API for hundreds of models from different providers.

1

Get an Open Router API key

Sign up at [openrouter.ai](https://openrouter.ai/) and generate an API key.

2

Set your API key

Copy

Ask AI
    
    
    export OPEN_ROUTER_API_KEY="sk-or-..."
    

3

Select a model

Browse [Open Router’s model list](https://openrouter.ai/models) and use the model identifier:

Copy

Ask AI
    
    
    ante --provider open-router --model anthropic/claude-sonnet-4-5
    

## 

​

OpenAI-compatible providers

Many LLM providers expose an OpenAI-compatible API (e.g., Together AI, Fireworks, Groq Cloud, Perplexity). You can connect to these through the OpenAI provider by setting a custom base URL.

1

Set the base URL

Point the OpenAI provider to your chosen service:

Copy

Ask AI
    
    
    export OPENAI_API_BASE="https://api.together.xyz/v1"
    

2

Set your API key

Copy

Ask AI
    
    
    export OPENAI_API_KEY="your-provider-api-key"
    

3

Run with the OpenAI provider

Copy

Ask AI
    
    
    ante --provider openai --model meta-llama/Llama-3-70b-chat-hf
    

## 

​

Local models

For fully offline usage with local GGUF models via the built-in llama.cpp engine, see [Offline Mode](/offline).

Copy

Ask AI
    
    
    ante --provider local
    

## 

​

Tips

When using third-party providers, make sure the model you select supports tool use (function calling). Ante relies on tool use for its agent capabilities.

Not all models work equally well as coding agents. Models need strong instruction following and tool use support. If you experience issues, try a larger or more capable model.

[Previous](/configuration/preference)[MemoryPersistent auto-memory that carries context across conversationsNext](/memory)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * Using Open Router
  * OpenAI-compatible providers
  * Local models
  * Tips

Assistant

Responses are generated using AI and may contain mistakes.

Adding a 3rd Party Provider - Ante

