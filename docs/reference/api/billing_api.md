# billing API Reference

> **Source**: `src/thegent/orchestration/billing.py`

WP-19004: Quota & Billing for Multi-Tenant Teams.
Enforces resource quotas (runs, tokens, storage) per team/tenant.

---

## TeamBillingManager

Manages resource quotas and billing for multi-tenant teams.

### Methods

#### TeamBillingManager.__init__

```python
__init__(self, session_dir)
```

#### TeamBillingManager.check_quota

Check if a team has enough quota for a resource.

```python
check_quota(self, team_id, resource, cost)
```

#### TeamBillingManager.get_billing_report

Generate a billing report for a team.

```python
get_billing_report(self, team_id)
```

#### TeamBillingManager.record_usage

Record resource usage for a team.

```python
record_usage(self, team_id, resource, amount)
```

---

## check_quota

Check if a team has enough quota for a resource.

```python
check_quota(self, team_id, resource, cost)
```

---

## get_billing_report

Generate a billing report for a team.

```python
get_billing_report(self, team_id)
```

---

## record_usage

Record resource usage for a team.

```python
record_usage(self, team_id, resource, amount)
```

---

