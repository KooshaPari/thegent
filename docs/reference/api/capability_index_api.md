# capability_index API Reference

> **Source**: `src/thegent/agents/capability_index.py`

Agent capability indexing and recommendation engine (WL-034).

Scans ~/.claude/agents/*.md and .claude/agents/*.md files, parses YAML
frontmatter, builds an in-memory capability index, and ranks agents for
a given task description using keyword/TF-IDF overlap scoring.

---

## AgentRecommendation

A recommended agent with its relevance score.

**Inherits from**: `SerializableMixin`

---

## AgentRecord

Parsed agent definition from a frontmatter .md file.

---

## CapabilityIndex

In-memory index of agent capabilities built from frontmatter .md files.

Usage:
    index = CapabilityIndex.get()          # uses 60-second TTL singleton
    recs = index.recommend("review python code", top_n=3)
    results = index.doctor()

### Methods

#### CapabilityIndex.__init__

```python
__init__(self: Any, agents: list[AgentRecord])
```

---

#### CapabilityIndex.agents_for_capability

```python
agents_for_capability(self: Any, capability: str)
```

Return agents that declared the given capability.

---

#### CapabilityIndex.all_agents

```python
all_agents(self: Any)
```

Return all indexed agents.

---

#### CapabilityIndex.build

```python
build(cls: Any, extra_dirs: Any)
```

Build a fresh CapabilityIndex by scanning agent directories.

---

#### CapabilityIndex.doctor

```python
doctor(self: Any)
```

Validate all indexed agents for runner config and frontmatter health.

Checks:
- Frontmatter is parseable YAML (validated at load time)
- Agent has a 'model' or 'runner' field
- No dangling/invalid references in raw frontmatter

**Returns**: List of DoctorResult, one per agent.

---

#### CapabilityIndex.get

```python
get(cls: Any, extra_dirs: Any)
```

Return the cached CapabilityIndex, rebuilding if expired (TTL=60s).

---

#### CapabilityIndex.invalidate

```python
invalidate(cls: Any)
```

Force cache invalidation (useful for tests).

---

#### CapabilityIndex.recommend

```python
recommend(self: Any, task_description: str, top_n: int)
```

Recommend top-N agents for the given task description.

Uses TF-IDF keyword overlap between task_description and each agent's
description + capabilities. No LLM calls.

**Parameters**:

- `task_description`: Free-text description of the task to perform.
- `top_n`: Maximum number of recommendations to return.

**Returns**: List of AgentRecommendation sorted by score descending.

---

---

## DoctorResult

Health check result for a single agent.

### Methods

#### DoctorResult.healthy

```python
healthy(self: Any)
```

---

---

## agents_for_capability

```python
agents_for_capability(self: Any, capability: str)
```

Return agents that declared the given capability.

---

## all_agents

```python
all_agents(self: Any)
```

Return all indexed agents.

---

## build

```python
build(cls: Any, extra_dirs: Any)
```

Build a fresh CapabilityIndex by scanning agent directories.

---

## doctor

```python
doctor(self: Any)
```

Validate all indexed agents for runner config and frontmatter health.

Checks:
- Frontmatter is parseable YAML (validated at load time)
- Agent has a 'model' or 'runner' field
- No dangling/invalid references in raw frontmatter

**Returns**: List of DoctorResult, one per agent.

---

## get

```python
get(cls: Any, extra_dirs: Any)
```

Return the cached CapabilityIndex, rebuilding if expired (TTL=60s).

---

## healthy

```python
healthy(self: Any) -> bool
```

---

## invalidate

```python
invalidate(cls: Any)
```

Force cache invalidation (useful for tests).

---

## recommend

```python
recommend(self: Any, task_description: str, top_n: int)
```

Recommend top-N agents for the given task description.

Uses TF-IDF keyword overlap between task_description and each agent's
description + capabilities. No LLM calls.

**Parameters**:

- `task_description`: Free-text description of the task to perform.
- `top_n`: Maximum number of recommendations to return.

**Returns**: List of AgentRecommendation sorted by score descending.

---

