# Offline Mode (Experimental)

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

Offline Mode

Offline Mode (Experimental)

[Ante Preview](/start/overview)

[Ante Preview](/start/overview)

Offline Mode

# Offline Mode (Experimental)

Run Ante with local models - no API keys or internet required

Ante can run entirely offline using local GGUF models via [llama.cpp](https://github.com/ggerganov/llama.cpp) (our current local inference engine). This means no API keys, no internet, and no data leaving your machine. We expect to explore additional local engines over time, but the offline workflow and model format support will remain focused on a good “it just works” experience. In parallel, we’re building toward a truly self-contained agent stack; see our ongoing Rust effort at [AntigmaLabs/nanochat-rs](https://github.com/AntigmaLabs/nanochat-rs).

## 

​

How it works

Ante includes an integrated inference engine currently powered by llama.cpp. When you select offline mode, Ante:

  1. Discovers GGUF models on your system
  2. Estimates memory requirements based on model size and context window
  3. Runs inference locally through the embedded engine

## 

​

Setting up

1

Download a GGUF model

Download a compatible GGUF model. Ante maintains a list of verified models that are known to work well. You can also use any GGUF model file.Popular sources:

  * [Hugging Face](https://huggingface.co/models?search=gguf)
  * [Antigma on Hugging Face](https://huggingface.co/Antigma)

2

Launch Ante

Start Ante normally:

Copy

Ask AI
    
    
    ante
    

Use the offline mode selector in the TUI to pick your model.

3

Or use the CLI flag

Copy

Ask AI
    
    
    ante --provider local "your prompt here"
    

## 

​

Model discovery

Ante automatically scans for GGUF model files. It handles:

  * Single-file models (e.g., `model.gguf`)
  * Sharded models (e.g., `Model-00001-of-00008.gguf`)
  * Metadata extraction (file size, shard count)

## 

​

Model preferences

You can configure per-model preferences:

Setting| Description  
---|---  
`context_window`| Context window size (minimum 32K tokens)  
`thinking`| Enable/disable chain-of-thought  
`temperature`| Sampling temperature  
  
## 

​

Memory considerations

Ante estimates memory usage based on:

  * **Model file size** — The base memory needed to load the model
  * **KV cache** — Scales with context window size (bytes per token)
  * **Shard count** — Multi-file models need proportional memory

For large models, reduce the context window to lower memory usage. The minimum is 32K tokens.

## 

​

Verified models

Ante includes a curated list of verified models that are tested for compatibility and quality. These are shown prominently in the model selector.

[Previous](/agent-org)[Interactive TUIUsing Ante's rich terminal user interfaceNext](/usage/tui)

[Powered by](https://www.mintlify.com?utm_campaign=poweredBy&utm_medium=referral&utm_source=antigmalabs)

On this page

  * How it works
  * Setting up
  * Model discovery
  * Model preferences
  * Memory considerations
  * Verified models

Assistant

Responses are generated using AI and may contain mistakes.

Offline Mode (Experimental) - Ante

