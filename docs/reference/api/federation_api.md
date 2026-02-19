# federation API Reference

> **Source**: `src/thegent/governance/federation.py`

WP-13001: Multi-org policy federation.

---

## FederatedPolicyManager

Manages federated policy resolution and health.

### Methods

#### FederatedPolicyManager.__init__

```python
__init__(self, base_dir)
```

#### FederatedPolicyManager.apply_jurisdiction_constraints

Apply jurisdiction overlay (EU-AI-ACT, US-SEC).

```python
apply_jurisdiction_constraints(self, policy, region)
```

#### FederatedPolicyManager.arbitrate_conflict

Arbitrate conflicts using 'most restrictive wins'.

```python
arbitrate_conflict(self, policies)
```

#### FederatedPolicyManager.get_federation_health

Return federation health status.

```python
get_federation_health(self)
```

#### FederatedPolicyManager.relay_consent

WP-13003: Relay approval consent between namespaces with provenance signatures.

```python
relay_consent(self, ns1, ns2, run_id, approver)
```

#### FederatedPolicyManager.resolve_policy

Resolve policy by traversing namespace hierarchy.

```python
resolve_policy(self, ns, policy_id)
```

---

## FederationManager

Manages policy federation across multiple organizations.

### Methods

#### FederationManager.__init__

```python
__init__(self, session_dir)
```

#### FederationManager.get_effective_policy

Resolve a policy, considering federated overrides.

```python
get_effective_policy(self, policy_id)
```

#### FederationManager.sync_policies

Sync governance policies from a peer organization.

```python
sync_policies(self, peer_id)
```

---

## PolicyNamespace

Namespace identifier for org/project/env.

### Methods

#### PolicyNamespace.__init__

```python
__init__(self, org, project, environment)
```

#### PolicyNamespace.get_hierarchy

Return resolution order: specific -> org default -> root default.

```python
get_hierarchy(self)
```

---

## apply_jurisdiction_constraints

Apply jurisdiction overlay (EU-AI-ACT, US-SEC).

```python
apply_jurisdiction_constraints(self, policy, region)
```

---

## arbitrate_conflict

Arbitrate conflicts using 'most restrictive wins'.

```python
arbitrate_conflict(self, policies)
```

---

## get_effective_policy

Resolve a policy, considering federated overrides.

```python
get_effective_policy(self, policy_id)
```

---

## get_federation_health

Return federation health status.

```python
get_federation_health(self)
```

---

## get_hierarchy

Return resolution order: specific -> org default -> root default.

```python
get_hierarchy(self)
```

---

## relay_consent

WP-13003: Relay approval consent between namespaces with provenance signatures.

```python
relay_consent(self, ns1, ns2, run_id, approver)
```

---

## resolve_policy

Resolve policy by traversing namespace hierarchy.

```python
resolve_policy(self, ns, policy_id)
```

---

## sync_policies

Sync governance policies from a peer organization.

```python
sync_policies(self, peer_id)
```

---

