# control_vectors API Reference

> **Source**: `src/thegent/governance/control_vectors.py`

WP-33002: Behavioral Steering via Semantic Injection.
Influences black-box agents by proactively modifying their environment and context.
Injects 'control vectors' (semantic hints, mock tools, system state) to steer behavior.

---

## ControlVectorManager

Manages semantic injection vectors for steering black-box agents.

### Methods

#### ControlVectorManager.__init__

```python
__init__(self, agent_id)
```

#### ControlVectorManager.analyze_and_inject

Analyze prompt and state to decide which control vectors to inject.

```python
analyze_and_inject(self, prompt, agent_state)
```

#### ControlVectorManager.prepare_environment

Proactively modify the physical environment to steer behavior (e.g. mock tools).

```python
prepare_environment(self, workspace_path)
```

---

## analyze_and_inject

Analyze prompt and state to decide which control vectors to inject.

```python
analyze_and_inject(self, prompt, agent_state)
```

---

## prepare_environment

Proactively modify the physical environment to steer behavior (e.g. mock tools).

```python
prepare_environment(self, workspace_path)
```

---

