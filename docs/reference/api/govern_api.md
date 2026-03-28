# govern API Reference

> **Source**: `src/thegent/cli/apps/govern.py`

Logical stream: Governance approvals and escalation controls.

---

## govern_approve

```python
govern_approve(run_id: str, reason: Any) -> None
```

---

## govern_health_trend

```python
govern_health_trend(payload_type: str, all_sessions: bool, owner: Any, strict: bool, policy_profile: Any, min_healthy_ratio: float, top_blocked: int, limit: int, format: str, output: Any, export_format: Any, overwrite: bool)
```

Analyze session contract health trends.

---

## govern_negotiate

```python
govern_negotiate(contract_id: str, versions: str)
```

Negotiate a contract version.

---

## govern_register_host

```python
govern_register_host(host_id: str, harness: str, prefix: str)
```

Register a new host device for remote harness execution.

---

## govern_reject

```python
govern_reject(run_id: str, reason: str) -> None
```

---

## govern_resolve_config

```python
govern_resolve_config(tenant_id: Any, session_id: Any, key: Any)
```

Resolve configuration overrides for a tenant or session.

---

## govern_vet

```python
govern_vet(run_id: str, policy: str, session: Any, dry_run: bool, org: Any, project: Any, environment: Any, policy_id: Any, json_output: bool) -> None
```

---

