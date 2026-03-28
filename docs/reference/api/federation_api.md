# federation API Reference

> **Source**: `src/thegent/governance/federation.py`

WP-13001: Multi-org policy federation.

Implements FR-FED-001 through FR-FED-006 (WL-020):
  FR-FED-001: Three-level namespace org.project.environment with hierarchy
  FR-FED-002: Federated policy resolution (env -> project -> org -> global)
  FR-FED-003: Jurisdiction profiles (EU-AI-ACT, US-SEC) as additive overlays
  FR-FED-004: Cross-namespace consent relay with SHA-256 provenance signatures
  FR-FED-005: Most-restrictive-wins conflict arbitration + policy_arbitration.jsonl
  FR-FED-006: Federation health + drift observability endpoint

---

## ArbitrationLog

Appends conflict arbitration decisions to policy_arbitration.jsonl (FR-FED-005).

### Methods

#### ArbitrationLog.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### ArbitrationLog.record

```python
record(self: Any, namespace: str, policy_id: str, key: str, competing_values: list[Any], chosen_value: Any, rule: str)
```

---

---

## ConsentRelayStore

Persists cross-namespace consent relay artifacts (FR-FED-004).

### Methods

#### ConsentRelayStore.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### ConsentRelayStore.list_active

```python
list_active(self: Any, run_id: Any)
```

---

#### ConsentRelayStore.store

```python
store(self: Any, artifact: dict[(str, Any)])
```

---

---

## FederatedPolicyManager

Manages federated policy resolution and health (WP-13001, FR-FED-001..006).

Directory layout under base_dir:
    <org>/<project>/<env>/<policy_id>.json

### Methods

#### FederatedPolicyManager.__init__

```python
__init__(self: Any, base_dir: Path, session_dir: Any)
```

---

#### FederatedPolicyManager.apply_jurisdiction_constraints

```python
apply_jurisdiction_constraints(self: Any, policy: dict[(str, Any)], region: str)
```

Apply jurisdiction overlay as additive constraints (FR-FED-003).

Profiles: EU-AI-ACT, US-SEC.  Constraints are additive (union) — the
most-restrictive value wins when both policy and profile define a key.

---

#### FederatedPolicyManager.apply_jurisdiction_profile

```python
apply_jurisdiction_profile(self: Any, policy: dict[(str, Any)], profile_name: str)
```

Apply a named jurisdiction profile directly (FR-FED-003).

---

#### FederatedPolicyManager.arbitrate_conflict

```python
arbitrate_conflict(self: Any, policies: list[dict[(str, Any)]], namespace: str, policy_id: str)
```

Arbitrate conflicts using 'most restrictive wins' (FR-FED-005).

For each conflicting key:
- Numeric thresholds where lower = stricter: take min
- Numeric limits where higher = stricter: take max
- Boolean flags where True = stricter: take OR
- Other keys: last value wins (last policy has highest precedence)

Logs each arbitration decision to policy_arbitration.jsonl.

---

#### FederatedPolicyManager.get_consent_relays

```python
get_consent_relays(self: Any, run_id: Any)
```

Return active consent relay artifacts (FR-FED-004).

---

#### FederatedPolicyManager.get_federation_health

```python
get_federation_health(self: Any)
```

Return federation health status (FR-FED-006).

---

#### FederatedPolicyManager.get_federation_health_endpoint

```python
get_federation_health_endpoint(self: Any)
```

Return the GET /governance/federation/health response payload (FR-FED-006).

Includes policy sync status across namespaces and drift detection.

---

#### FederatedPolicyManager.join_namespace

```python
join_namespace(self: Any, ns_str: str)
```

Register current node with a federated namespace (WP-13006).

---

#### FederatedPolicyManager.leave_namespace

```python
leave_namespace(self: Any, ns_str: str)
```

Remove registration for a federated namespace.

---

#### FederatedPolicyManager.relay_consent

```python
relay_consent(self: Any, ns1: PolicyNamespace, ns2: PolicyNamespace, run_id: str, approver: str)
```

Relay approval consent between namespaces with provenance signature (FR-FED-004).

Generates a traceable relay artifact with SHA-256 signature over the
payload: ns1:ns2:run_id:approver:timestamp.

---

#### FederatedPolicyManager.resolve_policy

```python
resolve_policy(self: Any, ns: PolicyNamespace, policy_id: str)
```

Resolve policy by traversing namespace hierarchy (FR-FED-002).

Resolution order: environment -> project.default -> org.default -> global
Returns the first matching policy file found.

---

---

## FederationManager

Manages policy federation across multiple organizations.

### Methods

#### FederationManager.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### FederationManager.get_effective_policy

```python
get_effective_policy(self: Any, policy_id: str)
```

Resolve a policy, considering federated overrides.

---

#### FederationManager.sync_policies

```python
sync_policies(self: Any, peer_id: str)
```

Sync governance policies from a peer organization.

---

---

## PolicyNamespace

Namespace identifier for org/project/env (FR-FED-001).

### Methods

#### PolicyNamespace.__init__

```python
__init__(self: Any, org: str, project: str, environment: str)
```

---

#### PolicyNamespace.get_hierarchy

```python
get_hierarchy(self: Any)
```

Return resolution order (FR-FED-002): env -> project.default -> org.default -> global.

---

---

## apply_jurisdiction_constraints

```python
apply_jurisdiction_constraints(self: Any, policy: dict[(str, Any)], region: str)
```

Apply jurisdiction overlay as additive constraints (FR-FED-003).

Profiles: EU-AI-ACT, US-SEC.  Constraints are additive (union) — the
most-restrictive value wins when both policy and profile define a key.

---

## apply_jurisdiction_profile

```python
apply_jurisdiction_profile(self: Any, policy: dict[(str, Any)], profile_name: str)
```

Apply a named jurisdiction profile directly (FR-FED-003).

---

## arbitrate_conflict

```python
arbitrate_conflict(self: Any, policies: list[dict[(str, Any)]], namespace: str, policy_id: str)
```

Arbitrate conflicts using 'most restrictive wins' (FR-FED-005).

For each conflicting key:
- Numeric thresholds where lower = stricter: take min
- Numeric limits where higher = stricter: take max
- Boolean flags where True = stricter: take OR
- Other keys: last value wins (last policy has highest precedence)

Logs each arbitration decision to policy_arbitration.jsonl.

---

## get_consent_relays

```python
get_consent_relays(self: Any, run_id: Any)
```

Return active consent relay artifacts (FR-FED-004).

---

## get_effective_policy

```python
get_effective_policy(self: Any, policy_id: str)
```

Resolve a policy, considering federated overrides.

---

## get_federation_health

```python
get_federation_health(self: Any)
```

Return federation health status (FR-FED-006).

---

## get_federation_health_endpoint

```python
get_federation_health_endpoint(self: Any)
```

Return the GET /governance/federation/health response payload (FR-FED-006).

Includes policy sync status across namespaces and drift detection.

---

## get_hierarchy

```python
get_hierarchy(self: Any)
```

Return resolution order (FR-FED-002): env -> project.default -> org.default -> global.

---

## join_namespace

```python
join_namespace(self: Any, ns_str: str)
```

Register current node with a federated namespace (WP-13006).

---

## leave_namespace

```python
leave_namespace(self: Any, ns_str: str)
```

Remove registration for a federated namespace.

---

## list_active

```python
list_active(self: Any, run_id: Any) -> list[dict[(str, Any)]]
```

---

## record

```python
record(self: Any, namespace: str, policy_id: str, key: str, competing_values: list[Any], chosen_value: Any, rule: str) -> None
```

---

## relay_consent

```python
relay_consent(self: Any, ns1: PolicyNamespace, ns2: PolicyNamespace, run_id: str, approver: str)
```

Relay approval consent between namespaces with provenance signature (FR-FED-004).

Generates a traceable relay artifact with SHA-256 signature over the
payload: ns1:ns2:run_id:approver:timestamp.

---

## resolve_policy

```python
resolve_policy(self: Any, ns: PolicyNamespace, policy_id: str)
```

Resolve policy by traversing namespace hierarchy (FR-FED-002).

Resolution order: environment -> project.default -> org.default -> global
Returns the first matching policy file found.

---

## store

```python
store(self: Any, artifact: dict[(str, Any)]) -> None
```

---

## sync_policies

```python
sync_policies(self: Any, peer_id: str)
```

Sync governance policies from a peer organization.

---

