# ANTE: Model & Provider Catalog

> Extracted from Ante docs. Fetched 2026-02-20

Ante home page

Search...



Navigation

Configuration

Model & Provider Catalog
Configuration
Model & Provider Catalog
Available models and providers supported by Ante
Ante is provider-agnostic. Each provider implements a common interface for sending prompts and receiving streaming responses. Providers are resolved from a catalog at session init time.
​

Providers
Provider
Wire Format
Models
Anthropic
Messages API
Claude family
OpenAI
Chat Completions / Responses
GPT-4o, o1, etc.
Gemini
Gemini API
Gemini family
Grok
OpenAI-compatible
Grok models
Open Router
OpenAI-compatible
Multiple providers
Local
llama.cpp
GGUF models
​

Provider identifiers
Use these identifiers with --provider or in your settings file:
ID
Provider
anthropic
Anthropic (Claude)
openai
OpenAI (GPT)
openai-response
OpenAI Responses API
gemini
Google Gemini
open-router
Open Router
xai
Grok (xAI)
local
Local models via llama.cpp
​

Models
​

Anthropic (Claude)
The default provider. Supports the full Claude model family through the Messages API.

Copy

Ask AI
ante --provider anthropic --model claude-sonnet-4-5-20250514

​

OpenAI
Supports GPT models through both the Chat Completions API and the Responses API.

Copy

Ask AI
# Chat Completions API
ante --provider openai --model gpt-4o

# Responses API
ante --provider openai-response --model gpt-4o

​

Google Gemini
Supports Gemini models through the Gemini API.

Copy

Ask AI
ante --provider gemini --model gemini-2.5-pro

​

Grok (xAI)
Uses the OpenAI-compatible wire format.

Copy

Ask AI
ante --provider xai --model grok-3

​

Open Router
Access multiple providers through a single API via Open Router.

Copy

Ask AI
ante --provider open-router --model anthropic/claude-sonnet-4-5

​

Local models
Run GGUF models locally via the built-in llama.cpp engine. No API keys or internet required. See Offline Mode for setup details.

Copy

Ask AI
ante --provider local

​

Authentication
Each provider requires its own authentication method:
Provider
Auth Method
Anthropic
ANTHROPIC_API_KEY env var or OAuth
OpenAI
OPENAI_API_KEY env var or OAuth
Gemini
GEMINI_API_KEY env var
Grok
XAI_API_KEY env var
Open Router
OPEN_ROUTER_API_KEY env var
Local
No authentication needed

Anthropic and OpenAI also support interactive OAuth flows through the TUI.
​

Selecting a provider
You can set your provider in three ways (in order of precedence):
CLI flag — ante --provider anthropic --model claude-sonnet-4-5-20250514
Settings file — Set provider and model in ~/.ante/settings.json
Built-in default — Anthropic with Claude Sonnet

Previous
Preferences

Next

Powered by



Assistant



Responses are generated using AI and may contain mistakes.
