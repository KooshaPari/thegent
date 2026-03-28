# balancer API Reference

> **Source**: `src/thegent/swarm/balancer.py`

Load Balancer

Distributes tasks across agents based on load and specialization.

---

## AgentLoad

Load information for an agent.

### Methods

#### AgentLoad.available_capacity

```python
available_capacity(self: Any)
```

Get remaining task capacity.

---

#### AgentLoad.utilization

```python
utilization(self: Any)
```

Get utilization ratio (0-1).

---

---

## LoadBalancer

Distributes tasks across agents.

### Methods

#### LoadBalancer.__init__

```python
__init__(self: Any)
```

---

#### LoadBalancer.assign

```python
assign(self: Any, agent_id: str)
```

Assign a task to an agent.

---

#### LoadBalancer.complete

```python
complete(self: Any, agent_id: str, duration: float)
```

Mark task as complete.

---

#### LoadBalancer.register

```python
register(self: Any, agent_id: str, specialization: str, max_tasks: int)
```

Register an agent.

---

#### LoadBalancer.select

```python
select(self: Any, task_type: str)
```

Select best agent for task type.

---

#### LoadBalancer.stats

```python
stats(self: Any)
```

Get load balancer statistics.

---

---

## assign

```python
assign(self: Any, agent_id: str)
```

Assign a task to an agent.

---

## available_capacity

```python
available_capacity(self: Any)
```

Get remaining task capacity.

---

## complete

```python
complete(self: Any, agent_id: str, duration: float)
```

Mark task as complete.

---

## register

```python
register(self: Any, agent_id: str, specialization: str, max_tasks: int)
```

Register an agent.

---

## select

```python
select(self: Any, task_type: str)
```

Select best agent for task type.

---

## stats

```python
stats(self: Any)
```

Get load balancer statistics.

---

## utilization

```python
utilization(self: Any)
```

Get utilization ratio (0-1).

---

