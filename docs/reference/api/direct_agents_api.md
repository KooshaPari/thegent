# direct_agents API Reference

> **Source**: `src/thegent/agents/direct_agents.py`

Direct agent invocation - cursor, claude, copilot, codex, gemini via their CLIs.

---

## DirectAgentRunner

Invokes cursor, claude, copilot, codex, gemini directly via their CLIs.

**Inherits from**: `AgentRunner`

### Methods

#### DirectAgentRunner.__init__

```python
__init__(self, agent_name, cli_cmd, default_model)
```

#### DirectAgentRunner.run

```python
run(self, prompt, cwd, mode, timeout)
```

---

## run

```python
run(self, prompt, cwd, mode, timeout)
```

---

