# agent_deployer API Reference

> **Source**: `src/thegent/governance/agent_deployer.py`

Agent deployment from remediation DAG.

Walks the DAG topologically, groups independent tasks into ready batches,
checks budget, and spawns agents via the canonical entry point.

---

## AgentDeployer

Deploys remediation tasks from a DAG, respecting dependencies and budget.

### Methods

#### AgentDeployer.__init__

```python
__init__(self, cost_controller, verification_gate, max_concurrent, lifecycle_mode, checker_agent_name)
```

#### AgentDeployer.deploy

Execute a full remediation plan.

Walks DAG topologically, groups ready tasks into batches,
spawns agents for each batch respecting max_concurrent.

```python
deploy(self, plan, pre_scan, cycle_id)
```

#### AgentDeployer.get_ready_batch

Get tasks ready to execute (all dependencies completed).

```python
get_ready_batch(self, plan, completed_task_ids)
```

---

## CostControllerProtocol

Protocol for cost controller.

**Inherits from**: `Protocol`

### Methods

#### CostControllerProtocol.can_spawn

```python
can_spawn(self, estimated_calls)
```

#### CostControllerProtocol.get_tier

```python
get_tier(self)
```

#### CostControllerProtocol.record_call

```python
record_call(self, dimension, agent_type)
```

---

## DeploymentResult

Result of deploying a full remediation plan.

**Inherits from**: `BaseModel`

---

## TaskExecutionResult

Result of executing a single remediation task.

**Inherits from**: `BaseModel`

---

## VerificationGateProtocol

Protocol for verification gate.

**Inherits from**: `Protocol`

### Methods

#### VerificationGateProtocol.should_reroll

```python
should_reroll(self, attempts)
```

#### VerificationGateProtocol.verify_task

```python
verify_task(self, task, execution, pre_scan)
```

---

## can_spawn

```python
can_spawn(self, estimated_calls)
```

---

## deploy

Execute a full remediation plan.

Walks DAG topologically, groups ready tasks into batches,
spawns agents for each batch respecting max_concurrent.

```python
deploy(self, plan, pre_scan, cycle_id)
```

---

## get_ready_batch

Get tasks ready to execute (all dependencies completed).

```python
get_ready_batch(self, plan, completed_task_ids)
```

---

## get_tier

```python
get_tier(self)
```

---

## record_call

```python
record_call(self, dimension, agent_type)
```

---

## should_reroll

```python
should_reroll(self, attempts)
```

---

## verify_task

```python
verify_task(self, task, execution, pre_scan)
```

---

