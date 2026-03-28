# impl_work_stream API Reference

> **Source**: `src/thegent/cli/plan/impl_work_stream.py`

Thegent work stream and planning implementation layer.

---

## continuity_snapshot_impl

```python
continuity_snapshot_impl(owner: str, run_ids: list[str]) -> dict[(str, Any)]
```

---

## do_next_impl

```python
do_next_impl(cd: Any, limit: int) -> dict[(str, Any)]
```

---

## harness_interact_impl

---

## harness_list_actions_impl

---

## harness_register_host_impl

---

## inbox_list_impl

```python
inbox_list_impl(owner: Any, agent: Any, event_type: Any, status: Any, sources: tuple[(str, Ellipsis)], limit: int) -> list[dict[(str, Any)]]
```

---

## inbox_wait_impl

```python
inbox_wait_impl(timeout: Any) -> dict[(str, Any)]
```

---

## incorporate_impl

```python
incorporate_impl(cd: Any, dry_run: bool) -> dict[(str, Any)]
```

---

## list_agents_impl

---

## list_droids_impl

```python
list_droids_impl(cd: Any) -> list[str]
```

---

## list_models_impl

```python
list_models_impl(provider: Any, use_scraped: bool, refresh: bool, include_contract: bool, by_model: bool) -> dict[(str, Any)]
```

---

## plan_analyze_impl

```python
plan_analyze_impl(cd: Any, pert: bool, resources: bool, continuity: bool) -> dict[(str, Any)]
```

---

## retry_impl

```python
retry_impl(run_id: str, agent_override: Any, failover: bool, cd: Any, override_reason: Any) -> dict[(str, Any)]
```

---

## spawn_next_impl

```python
spawn_next_impl(cd: Any) -> dict[(str, Any)]
```

---

## wait_next_impl

---

## work_stream_claim_impl

```python
work_stream_claim_impl(item_id: str, agent_id: str, cd: Any) -> dict[(str, Any)]
```

---

## work_stream_complete_impl

```python
work_stream_complete_impl(item_id: str, agent_id: str, cd: Any) -> dict[(str, Any)]
```

---

