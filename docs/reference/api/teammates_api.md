# teammates API Reference

> **Source**: `src/thegent/governance/teammates.py`

WP-16001/16002: Thegent Teammates orchestration and delegation protocol.

---

## DelegationRequest

Record of a delegated task to a teammate.

---

## TeammateManager

Manages discovery and delegation for the teammate swarm.

### Methods

#### TeammateManager.__init__

```python
__init__(self, storage_path)
```

#### TeammateManager.delegate

WP-16002: Delegate a task to a teammate.

```python
delegate(self, teammate_id, parent_run_id, prompt)
```

#### TeammateManager.get_delegations

List all delegations, optionally filtered by parent run.

```python
get_delegations(self, parent_run_id)
```

#### TeammateManager.list_personas

WP-16001: Discover teammates from agent markdown files.

```python
list_personas(self)
```

#### TeammateManager.update_status

Update the status of a delegation.

```python
update_status(self, req_id, status, summary)
```

---

## TeammatePersona

Specialized agent persona for the teammate swarm.

---

## delegate

WP-16002: Delegate a task to a teammate.

```python
delegate(self, teammate_id, parent_run_id, prompt)
```

---

## get_delegations

List all delegations, optionally filtered by parent run.

```python
get_delegations(self, parent_run_id)
```

---

## list_personas

WP-16001: Discover teammates from agent markdown files.

```python
list_personas(self)
```

---

## update_status

Update the status of a delegation.

```python
update_status(self, req_id, status, summary)
```

---

