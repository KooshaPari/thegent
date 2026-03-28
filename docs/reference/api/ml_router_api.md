# ml_router API Reference

> **Source**: `src/thegent/utils/routing_impl/ml_router.py`

GW-68: ML meta-model routing -- classify task -> best model.

Implements lightweight task classification for model routing.
Uses keyword-based classification as the default (no external deps).
Can be extended with embedding-based or ML-based classifiers.

Task types and their preferred models:
  coding         -> claude-opus-4-6 or gpt-4o (strong code)
  reasoning      -> claude-opus-4-6 or o3 (strong reasoning)
  summarization  -> claude-haiku-4-5 or gpt-4o-mini (fast + cheap)
  creative       -> claude-opus-4-6 or gpt-4o (creative writing)
  retrieval      -> gpt-4o-mini or claude-haiku-4-5 (RAG queries)
  general        -> gpt-4o or claude-sonnet-4-6 (default)

# @trace FR-AROUTE-068

---

## ModelPreference

Describes a model and its task affinity.

---

## TaskClassification

Result of classifying a prompt into a task type.

---

## classify_task

```python
classify_task(prompt: str)
```

Classify the task type from the prompt using keyword signals.

---

## ml_route

```python
ml_route(prompt: str, preferences: Any, available_models: Any)
```

Convenience: classify + select in one call.

---

## select_model

```python
select_model(classification: TaskClassification, preferences: Any, available_models: Any)
```

Select best model for the classified task.

Filters by available_models if provided.
Returns None if no preferences match.

---

