# hybrid_router API Reference

> **Source**: `src/thegent/models/hybrid_router.py`

WP-20002: Neural-Symbolic Hybrid Router.
Combines symbolic risk assessment with neural model capabilities for safety-first routing.

---

## HybridRouter

Combines LLM (Neural) and Symbolic (Formal) methods for model routing.

### Methods

#### HybridRouter.__init__

```python
__init__(self, dag)
```

#### HybridRouter.route_safely

Route to a model based on both neural capability and symbolic safety.

```python
route_safely(self, task_type, prompt, start_node)
```

---

## route_safely

Route to a model based on both neural capability and symbolic safety.

```python
route_safely(self, task_type, prompt, start_node)
```

---

