# Factory Seed — Agent Orchestra Skill

Thegent invokes agents (cursor-agent, claude, copilot, codex, gemini) **directly** via their CLIs. No per-agent run scripts.

This directory contains the **agent-orchestra** skill: guidance for teaching agents how to use thegent.

## Install

Use a symlink so every runtime reads the canonical skill definition from the standalone project:

```bash
mkdir -p ~/.factory/skills
ln -sfn /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/factory-seed/agent-orchestra ~/.factory/skills/agent-orchestra
```

If you prefer a configurable location, define `THEGENT_ROOT` and use the path above.

For interactive tools that load from both `~/.factory` and `~/.claude`, keep matching symlink to the same module:

```bash
ln -sfn /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/factory-seed/agent-orchestra ~/.factory/skills/agent-orchestra
ln -sfn /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/skills/agent-orchestra ~/.claude/skills/agent-orchestra
```

## Agents

| Agent | CLI | Notes |
|-------|-----|-------|
| cursor-agent | `cursor` | `--print --trust`, `--workspace` for cwd |
| claude | `claude` | `--print`, stdin for prompt |
| copilot | `copilot` | `--stream on` |
| codex | `codex` | `stdin`, `--json` |
| gemini | `gemini` | `--output-format stream-json` |
| minimax | `codex` via CLIProxyAPIPlus | Creds from `~/.factory/config.json` merged into proxy |
| glm | `codex` via CLIProxyAPIPlus | Native GLM-5; no factory config |

## Minimax / GLM

Same backend as antigravity (CLIProxyAPIPlus). **GLM** is native (GLM-5); no extra config. **Minimax**: put MiniMax-M2.5 in `~/.factory/config.json`; creds merged into proxy config on first start.
