# maif_runner API Reference

> **Source**: `src/thegent/agents/maif_runner.py`

MAIF-aware agent runner wrapper.

---

## MAIFAgentRunner

Wraps an AgentRunner to automatically generate MAIF artifacts using ExecutionEngine.

**Inherits from**: `AgentRunner`

### Methods

#### MAIFAgentRunner.__init__

```python
__init__(self: Any, runner: AgentRunner, engine: Optional[ExecutionEngine])
```

---

#### MAIFAgentRunner.run

```python
run(self: Any, prompt: str, cwd: Any, mode: str, timeout: int)
```

Run the agent and generate MAIF artifacts.

This method overloads the base run() to accept metadata required for MAIF.

---

---

## run

```python
run(self: Any, prompt: str, cwd: Any, mode: str, timeout: int)
```

Run the agent and generate MAIF artifacts.

This method overloads the base run() to accept metadata required for MAIF.

---
