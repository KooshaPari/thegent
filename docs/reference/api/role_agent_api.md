# role_agent API Reference

> **Source**: `src/thegent/agents/role_agent.py`

Role-based agent runner - wraps another runner and injects a system prompt.

---

## RoleAgentRunner

Wraps another runner and injects a role-based system prompt.

**Inherits from**: `AgentRunner`

### Methods

#### RoleAgentRunner.__init__

```python
__init__(self, role, base_runner)
```

#### RoleAgentRunner.run

```python
run(self, prompt, cwd, mode, timeout)
```

---

## run

```python
run(self, prompt, cwd, mode, timeout)
```

---

