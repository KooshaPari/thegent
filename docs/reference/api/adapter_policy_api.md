# adapter_policy API Reference

> **Source**: `src/thegent/governance/adapter_policy.py`

WP-10004: Adapter admission and trust policy.

Enforces trust-based admission rules for provider adapters.

---

## AdapterAdmissionPolicy

Policy engine for adapter admission control.

### Methods

#### AdapterAdmissionPolicy.__init__

```python
__init__(self, registry)
```

#### AdapterAdmissionPolicy.evaluate_admission

Evaluate if an adapter can be admitted to a specific lane.

```python
evaluate_admission(self, adapter_id, lane)
```

---

## evaluate_admission

Evaluate if an adapter can be admitted to a specific lane.

```python
evaluate_admission(self, adapter_id, lane)
```

---

