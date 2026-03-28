# eval_router API Reference

> **Source**: `src/thegent/utils/routing_impl/eval_router.py`

GW-70: Online eval routing — route to highest-scoring model per task type.

Maintains per-model, per-task-type exponentially weighted moving average (EWMA)
scores. Routes to the model with the highest score for the given task type.

# @trace FR-EVAL-070

---

## EvalRouteResult

Result of routing to the highest-scoring model for a task type.

---

## EvalRouter

Routes requests to the highest-scoring model per task type using EWMA.

Thread-safe. All state mutations are protected by a single lock.

### Methods

#### EvalRouter.__init__

```python
__init__(self: Any, alpha: float)
```

---

#### EvalRouter.get_score

```python
get_score(self: Any, model: str, task_type: str)
```

Return current EWMA score for (model, task_type), or None if no data.

---

#### EvalRouter.list_scores

```python
list_scores(self: Any, task_type: Any)
```

Return all recorded EvalScore objects, optionally filtered by task_type.

---

#### EvalRouter.record_eval

```python
record_eval(self: Any, model: str, task_type: str, score: float)
```

Update the EWMA score for (model, task_type).

First observation sets the EWMA directly to the observed score.
Subsequent: new_ewma = alpha * score + (1 - alpha) * old_ewma.

---

#### EvalRouter.reset

```python
reset(self: Any)
```

Clear all scores. Useful for testing.

---

#### EvalRouter.route

```python
route(self: Any, task_type: str, available_models: Any) -> EvalRouteResult or None if no scored models are available.
```

Select the highest-scoring model for task_type.

**Parameters**:

- `task_type`: The task category to route for.
- `available_models`: If provided, restrict candidates to this subset.

---

---

## EvalScore

Tracks the EWMA score for a (model, task_type) pair.

---

## get_eval_router

Return the module-level singleton EvalRouter, creating it if needed.

---

## get_score

```python
get_score(self: Any, model: str, task_type: str)
```

Return current EWMA score for (model, task_type), or None if no data.

---

## list_scores

```python
list_scores(self: Any, task_type: Any)
```

Return all recorded EvalScore objects, optionally filtered by task_type.

---

## record_eval

```python
record_eval(self: Any, model: str, task_type: str, score: float)
```

Update the EWMA score for (model, task_type).

First observation sets the EWMA directly to the observed score.
Subsequent: new_ewma = alpha * score + (1 - alpha) * old_ewma.

---

## reset

```python
reset(self: Any)
```

Clear all scores. Useful for testing.

---

## reset_eval_router

Replace the module-level singleton with a fresh EvalRouter instance.

---

## route

```python
route(self: Any, task_type: str, available_models: Any) -> EvalRouteResult or None if no scored models are available.
```

Select the highest-scoring model for task_type.

**Parameters**:

- `task_type`: The task category to route for.
- `available_models`: If provided, restrict candidates to this subset.

---

