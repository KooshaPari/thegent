# clode_glm_policy API Reference

> **Source**: `src/thegent/clode_glm_policy.py`

GLM routing policy helpers for clode.

---

## InvalidPolicyError

Raised when a GLM policy string is invalid.

**Inherits from**: `ValueError`

---

## cost_key

```python
cost_key(backend: str) -> tuple[(float, float, str)]
```

---

## glm_offer_backends

Return GLM offer set in deterministic order.

---

## resolve_clode_token

```python
resolve_clode_token(provider: str, prefer: str, policy: str, policy_counter: Counter[str], fetch_metrics: Callable[(Any, Any)])
```

Resolve provider token for ANTHROPIC_API_KEY.

---

## validate_policy

```python
validate_policy(policy: str) -> str
```

---

