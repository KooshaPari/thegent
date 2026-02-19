# refactoring API Reference

> **Source**: `src/thegent/agents/refactoring.py`

WP-37002: Recursive Cognitive Refactoring.
Allows agents to analyze their own reasoning chains and refactor their logic for better performance.

---

## CognitiveRefactorer

Analyzes and optimizes agent 'thought patterns' or prompt hierarchies.

### Methods

#### CognitiveRefactorer.__init__

```python
__init__(self, agent_id)
```

#### CognitiveRefactorer.analyze_reasoning_efficiency

Analyze how efficiently the agent reaches a solution.

```python
analyze_reasoning_efficiency(self, run_history)
```

#### CognitiveRefactorer.apply_refactor

Update the agent's internal reasoning template.

```python
apply_refactor(self, refactor_plan)
```

#### CognitiveRefactorer.propose_refactor

WP-37002: Generate a refactored 'cognitive template' (refined prompt instructions).

```python
propose_refactor(self, efficiency_report)
```

---

## analyze_reasoning_efficiency

Analyze how efficiently the agent reaches a solution.

```python
analyze_reasoning_efficiency(self, run_history)
```

---

## apply_refactor

Update the agent's internal reasoning template.

```python
apply_refactor(self, refactor_plan)
```

---

## propose_refactor

WP-37002: Generate a refactored 'cognitive template' (refined prompt instructions).

```python
propose_refactor(self, efficiency_report)
```

---

