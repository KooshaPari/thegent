# market API Reference

> **Source**: `src/thegent/discovery/market.py`

WP-30001: Agent Service Registry (Global).
A decentralized marketplace for agent services.
Enables agents to list capabilities and for clients to discover and bind to them.

---

## AgentService

Metadata for an agent service listing.

**Inherits from**: `BaseModel`

---

## GlobalServiceRegistry

Manages global agent service listings and discovery.

### Methods

#### GlobalServiceRegistry.__init__

```python
__init__(self, storage_path)
```

#### GlobalServiceRegistry.discover_services

Find active services for a given capability.

```python
discover_services(self, capability)
```

#### GlobalServiceRegistry.list_service

Publish a service listing to the registry.

```python
list_service(self, service)
```

#### GlobalServiceRegistry.run_auction

WP-30002: Run a reverse auction for a task requirement.

```python
run_auction(self, task_id, capability, budget)
```

---

## discover_services

Find active services for a given capability.

```python
discover_services(self, capability)
```

---

## list_service

Publish a service listing to the registry.

```python
list_service(self, service)
```

---

## run_auction

WP-30002: Run a reverse auction for a task requirement.

```python
run_auction(self, task_id, capability, budget)
```

---

