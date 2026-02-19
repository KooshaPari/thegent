# handoff API Reference

> **Source**: `src/thegent/governance/handoff.py`

## HandoffIntegrity

WP-16005: Verifies that delegated prompts are complete and context-aware.

### Methods

#### HandoffIntegrity.__init__

```python
__init__(self, workspace_root)
```

#### HandoffIntegrity.analyze_prompt

Analyze a prompt for potential missing context.

```python
analyze_prompt(self, prompt)
```

#### HandoffIntegrity.suggest_improvements

Suggest ways to improve the handoff prompt.

```python
suggest_improvements(self, prompt, findings)
```

---

## analyze_prompt

Analyze a prompt for potential missing context.

```python
analyze_prompt(self, prompt)
```

---

## suggest_improvements

Suggest ways to improve the handoff prompt.

```python
suggest_improvements(self, prompt, findings)
```

---

