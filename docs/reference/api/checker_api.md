# checker API Reference

> **Source**: `src/thegent/agents/checker.py`

Checker Agent (Head LLM) for Lifecycle loops.

---

## CheckerAgent

Head LLM that decides the next action in a loop.

### Methods

#### CheckerAgent.__init__

```python
__init__(self, settings, agent_name)
```

#### CheckerAgent.decide

Invoke the Checker Agent to make a decision.

```python
decide(self, governance_report, todo_spec, wbs_status, agent_response)
```

---

## CheckerDecision

Possible decisions by the Checker Agent.

**Inherits from**: `str, Enum`

---

## CheckerResult

Result of a Checker Agent decision.

**Inherits from**: `BaseModel`

---

## decide

Invoke the Checker Agent to make a decision.

```python
decide(self, governance_report, todo_spec, wbs_status, agent_response)
```

---

