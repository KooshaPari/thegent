# Merged Fragmented Markdown

## Source: site/reference/configuration.md

# Configuration Reference

This page documents common configuration patterns for `thegent`.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Claude provider authentication |
| `OPENAI_API_KEY` | OpenAI/Codex provider authentication |
| `GOOGLE_API_KEY` | Gemini provider authentication |
| `THGENT_DEFAULT_ROUTING` | Default routing preference |
| `THGENT_DEBUG` | Enable debug output for runtime diagnostics |

## Set Values with CLI

```bash
thegent config set providers.myproxy.url "http://localhost:8317"
thegent config set providers.myproxy.model "claude-sonnet-4-6"
```

## Recommended Defaults

- Keep credentials in environment or secure runtime config.
- Use explicit provider/model in CI for deterministic behavior.
- Set routing policy intentionally (`prefer_direct`, `prefer_proxy`, or explicit per command).

## Validation

After config changes:

```bash
thegent doctor
thegent run "configuration smoke test" --provider codex
```

---

## Source: site/reference/routing.md

# Routing Reference

Routing decides which provider/model executes a task.

## Routing Inputs

- Requested provider (for example `--provider codex`)
- Requested model (for example `-M gpt-5.3-codex`)
- Routing policy (`-R cheapest` or default behavior)
- Provider availability and credentials

## Common Routing Modes

| Mode | Behavior | Best for |
|------|----------|----------|
| explicit provider | direct provider selection | deterministic execution |
| explicit model | specific model override | benchmark or quality-sensitive jobs |
| `-R cheapest` | lowest-cost available route | bulk/background work |

## Examples

```bash
# Explicit provider
thegent run "draft release notes" --provider claude

# Explicit model
thegent run "analyze perf regressions" -M gpt-5.3-codex

# Cost-aware route
thegent run "summarize logs" -R cheapest
```

## Troubleshooting Routing

- If routing picks an unexpected provider, specify `--provider` directly.
- If a model is unavailable, verify provider capability and credentials.
- Use `--debug` to inspect route decisions.

---
