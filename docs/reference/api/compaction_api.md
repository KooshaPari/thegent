# compaction API Reference

> **Source**: `src/thegent/agents/compaction.py`

WL-103 context compaction layer with pydantic models.

# @trace FR-CTX-103

---

## CompactionConfig

Configuration for context compaction behavior.

**Inherits from**: `BaseModel`

---

## CompactionResult

Result of a compaction operation.

**Inherits from**: `BaseModel`

---

## CompactionTrigger

When to trigger context compaction.

**Inherits from**: `StrEnum`

---

## ContextCompactor

Manages context window compaction based on configurable triggers.

### Methods

#### ContextCompactor.__init__

```python
__init__(self: Any, config: CompactionConfig)
```

---

#### ContextCompactor.build_compaction_prompt

```python
build_compaction_prompt(self: Any, window: ContextWindow)
```

Build the prompt to send to an LLM for summarization.

---

#### ContextCompactor.compact

```python
compact(self: Any, window: ContextWindow, summary: str)
```

Apply compaction: replace messages with summary, update window state.

---

#### ContextCompactor.estimate_tokens

```python
estimate_tokens(self: Any, messages: list[dict[(str, Any)]])
```

Rough token estimate: sum of len(str(m)) // 4 for each message.

---

#### ContextCompactor.should_compact

```python
should_compact(self: Any, window: ContextWindow)
```

Return True if compaction is needed based on configured trigger.

---

---

## ContextWindow

Mutable state tracking the current conversation context.

**Inherits from**: `BaseModel`

---

## build_compaction_prompt

```python
build_compaction_prompt(self: Any, window: ContextWindow)
```

Build the prompt to send to an LLM for summarization.

---

## compact

```python
compact(self: Any, window: ContextWindow, summary: str)
```

Apply compaction: replace messages with summary, update window state.

---

## estimate_tokens

```python
estimate_tokens(self: Any, messages: list[dict[(str, Any)]])
```

Rough token estimate: sum of len(str(m)) // 4 for each message.

---

## should_compact

```python
should_compact(self: Any, window: ContextWindow)
```

Return True if compaction is needed based on configured trigger.

---

