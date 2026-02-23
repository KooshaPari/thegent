# Providers

`thegent` can route work across direct APIs and proxy-backed providers.

## Supported Provider Labels

| Provider | Typical default | Notes |
|----------|------------------|-------|
| `free` | `gpt-5-mini` | default convenience route |
| `claude` | `claude-haiku-4.5` | Anthropic API |
| `codex` | `gpt-5.3-codex` | OpenAI/Codex API |
| `gemini` | `gemini-3-flash` | Google API |
| `cursor` / `kiro` / custom | varies | proxy-dependent |

## Credential Setup

```bash
thegent setup --provider claude
thegent setup --provider codex
thegent setup --provider gemini
```

Manual env setup:

```bash
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
export GOOGLE_API_KEY="..."
```

## Practical Routing Patterns

```bash
# Explicit provider
thegent run "generate migration checklist" --provider claude

# Explicit model
thegent run "deep code audit" -M gpt-5.3-codex

# Cost-aware automatic routing
thegent run "summarize logs" -R cheapest
```

## Proxy Provider Example

```bash
thegent config set providers.myproxy.url "http://localhost:8317"
thegent config set providers.myproxy.model "claude-sonnet-4-6"
thegent run "health check" --provider myproxy
```

## Failure Handling

- Re-run failing commands with `--debug`.
- Confirm credentials are loaded in the active shell.
- Use [Routing Reference](/reference/routing) for route decision behavior.
