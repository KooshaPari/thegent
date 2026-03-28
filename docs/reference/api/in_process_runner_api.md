# in_process_runner API Reference

> **Source**: `src/thegent/agents/in_process_runner.py`

In-process agent runner (MTSP-02).

Provides thread-safe cwd isolation for running agents within the same process.

---

## InProcessAgentRunner

Agent runner that executes in-process with cwd isolation (MTSP-02).

### Methods

#### InProcessAgentRunner.__init__

```python
__init__(self: Any, agent_name: str, base_runner: Any)
```

---

#### InProcessAgentRunner.run

```python
run(self: Any, prompt: str, cd: Path, mode: str, timeout: int, run_id: Any, session_id: Any)
```

Run the agent with isolated cwd.

---

---

## isolated_cwd

```python
isolated_cwd(new_cwd: Path)
```

Context manager for thread-safe cwd isolation.

---

## run

```python
run(self: Any, prompt: str, cd: Path, mode: str, timeout: int, run_id: Any, session_id: Any)
```

Run the agent with isolated cwd.

---

