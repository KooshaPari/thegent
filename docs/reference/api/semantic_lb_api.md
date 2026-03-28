# semantic_lb API Reference

> **Source**: `src/thegent/utils/routing_impl/semantic_lb.py`

GW-61: Semantic load balancing — route to model best matching prompt.

Computes embedding similarity between the request prompt and pre-registered
model capability descriptions. Routes to the highest-similarity model.

Uses the same EmbeddingProvider protocol as semantic_cache.py.

# @trace FR-AROUTE-061

---

## ModelCapability

A model capability description used for semantic routing.

---

## SemanticLbResult

Result of a semantic load balancer routing decision.

---

## SemanticLoadBalancer

Maintains a registry of model capabilities and routes by similarity.

### Methods

#### SemanticLoadBalancer.__init__

```python
__init__(self: Any, capabilities: list[ModelCapability], provider: Any, min_similarity: float)
```

---

#### SemanticLoadBalancer.add_capability

```python
add_capability(self: Any, capability: ModelCapability)
```

Register a new model capability.

---

#### SemanticLoadBalancer.get_capabilities

```python
get_capabilities(self: Any)
```

Return current list of capabilities.

---

#### SemanticLoadBalancer.route

```python
route(self: Any, prompt: str)
```

Select the model most similar to the prompt.

Returns None if capabilities list is empty or all scores below min_similarity.

---

---

## add_capability

```python
add_capability(self: Any, capability: ModelCapability)
```

Register a new model capability.

---

## get_capabilities

```python
get_capabilities(self: Any)
```

Return current list of capabilities.

---

## route

```python
route(self: Any, prompt: str)
```

Select the model most similar to the prompt.

Returns None if capabilities list is empty or all scores below min_similarity.

---

## semantic_route

```python
semantic_route(prompt: str, capabilities: list[ModelCapability], provider: Any, min_similarity: float)
```

Convenience: create a one-shot SemanticLoadBalancer and route.

---

