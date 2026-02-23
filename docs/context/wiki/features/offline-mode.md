# Offline Mode (Experimental)

**Navigation:** home > [Features](../features/)

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
Ante home page Search... ⌘K Ask AI Search... Navigation Offline Mode Offline Mode (Experimental) Ante Preview Ante Preview Offline Mode # Offline Mode (Experimental) Run Ante with local models - no API keys or internet required
Ante can run entirely offline using local GGUF models via llama.cpp (our current local inference engine). This means no API keys, no internet, and no data leaving your machine. We expect to explore additional local engines over time, but the offline workflow and model format support will remain focused on a good “it just works” experience. In parallel, we’re building toward a truly self-contained agent stack; see our ongoing Rust effort at AntigmaLabs/nanochat-rs . ## ​ How it works Ante includes an integrated inference engine currently powered by llama.cpp. When you select offline mode, Ante: Discovers GGUF models on your system
- Estimates memory requirements based on model size and context window
- Runs inference locally through the embedded engine
## ​ Setting up 1 Download a GGUF model
Download a compatible GGUF model. Ante maintains a list of verified models that are known to work well. You can also use any GGUF model file. Popular sources: - Hugging Face
- Antigma on Hugging Face
2 Launch Ante

Start Ante normally: Copy Ask AI ante Use the offline mode selector in the TUI to pick your model. 3 Or use the CLI flag

Copy Ask AI ante --provider local "your prompt here" ## ​ Model discovery Ante automatically scans for GGUF model files. It handles: Single-file models (e.g., model.gguf
) - Sharded models (e.g., Model-00001-of-00008.gguf
) - Metadata extraction (file size, shard count)
## ​ Model preferences You can configure per-model preferences: Setting Description context_window
Context window size (minimum 32K tokens) thinking Enable/disable chain-of-thought temperature Sampling temperature ## ​ Memory considerations Ante estimates memory usage based on: Model file size
— The base memory needed to load the model - KV cache
— Scales with context window size (bytes per token) - Shard count
— Multi-file models need proportional memory For large models, reduce the context window to lower memory usage. The minimum is 32K tokens. ## ​ Verified models Ante includes a curated list of verified models that are tested for compatibility and quality. These are shown prominently in the model selector. Previous Interactive TUI Using Ante's rich terminal user interface Next On this page How it works
- Setting up
- Model discovery
- Model preferences
- Memory considerations
- Verified models
Assistant Responses are generated using AI and may contain mistakes. Offline Mode (Experimental) - Ante

---

## Related Documentation

- [Preferences](./preferences.md)
- [Model Catalog](./model-catalog.md)
