# optimizer API Reference

> **Source**: `src/thegent/agents/optimizer.py`

WP-20003: Automated Prompt Optimization (DSPy).
Optimizes agent prompts using logical verification and performance-driven feedback loops.
Inspired by DSPy's programmatic prompt optimization.

---

## PromptOptimizer

Optimizes agent prompts by tracking version performance and proposing improvements.

### Methods

#### PromptOptimizer.__init__

```python
__init__(self, agent_id, registry)
```

#### PromptOptimizer.get_best_prompt

Return the prompt content with the highest success rate.

```python
get_best_prompt(self)
```

#### PromptOptimizer.optimize

WP-20003: Optimize the current prompt based on feedback or performance history.

```python
optimize(self, current_prompt, feedback)
```

#### PromptOptimizer.record_run

Record the outcome of a prompt version's execution.

```python
record_run(self, version_id, result, tokens, cost)
```

---

## PromptVersion

A specific version of a prompt for an agent.

---

## get_best_prompt

Return the prompt content with the highest success rate.

```python
get_best_prompt(self)
```

---

## optimize

WP-20003: Optimize the current prompt based on feedback or performance history.

```python
optimize(self, current_prompt, feedback)
```

---

## record_run

Record the outcome of a prompt version's execution.

```python
record_run(self, version_id, result, tokens, cost)
```

---

