# registry API Reference

> **Source**: `src/thegent/cli/apps/registry.py`

Logical stream: Agent Registry — capability index, recommendation, and health doctor (WL-034).

---

## recommend_agent

```python
recommend_agent(task_description: str, top_n: int)
```

Public API: recommend agents for a task. Returns list of AgentRecommendation.

Used by thegent free auto-agent selection.

---

## registry_doctor

```python
registry_doctor(format: str, fail_on_issues: bool)
```

Check every agent in the registry for:

- Valid parseable YAML frontmatter
- A 'model' or 'runner' field
- No dangling or empty references

Prints a health status table. Use --fail to exit 1 if issues found.

---

## registry_list

```python
registry_list(capability: Any, format: str)
```

List agents from the capability index with their declared capabilities.

---

## registry_recommend

```python
registry_recommend(task: str, top_n: int, format: str)
```

Recommend the best agents for a task using local TF-IDF keyword scoring.

Scans ~/.claude/agents/*.md and .claude/agents/*.md for agents with
declared capabilities and description. No LLM calls required.

---

