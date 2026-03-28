# connector_chaos API Reference

> **Source**: `src/thegent/integrations/connector_chaos.py`

Connector Chaos Tests for resilience testing of connectors.

# @trace WL-235
Provides chaos testing scenarios for connector outages and partial-failure edge cases.
Allows injection of faults into connector operations to validate resilience.

---

## ChaosScenario

A chaos testing scenario for connector fault injection.

---

## ConnectorChaosTestSuite

Test suite for chaos testing of connectors.

### Methods

#### ConnectorChaosTestSuite.__init__

```python
__init__(self: Any)
```

Initialize the connector chaos test suite.

---

#### ConnectorChaosTestSuite.add_scenario

```python
add_scenario(self: Any, name: str, fault_type: str, probability: float)
```

Add a chaos scenario to the test suite.

**Parameters**:

- `name`: Unique name for the scenario.
- `fault_type`: Type of fault to inject (e.g., 'timeout', 'connection_drop').
- `probability`: Probability of fault injection (0.0 to 1.0). Defaults to 1.0.

**Returns**: The created ChaosScenario.

---

#### ConnectorChaosTestSuite.run

```python
run(self: Any, scenario_name: str, target_fn: Callable[(Any, Any)])
```

Run a target function under a chaos scenario.

For simplicity, this implementation calls the target function directly.
In a production system, this would inject faults based on the scenario probability.

**Parameters**:

- `scenario_name`: Name of the scenario to apply.
- `target_fn`: The function to call under the scenario.

**Returns**: The result of calling target_fn.

---

#### ConnectorChaosTestSuite.scenarios

```python
scenarios(self: Any)
```

Get all registered chaos scenarios.

**Returns**: List of all ChaosScenarios.

---

---

## add_scenario

```python
add_scenario(self: Any, name: str, fault_type: str, probability: float)
```

Add a chaos scenario to the test suite.

**Parameters**:

- `name`: Unique name for the scenario.
- `fault_type`: Type of fault to inject (e.g., 'timeout', 'connection_drop').
- `probability`: Probability of fault injection (0.0 to 1.0). Defaults to 1.0.

**Returns**: The created ChaosScenario.

---

## run

```python
run(self: Any, scenario_name: str, target_fn: Callable[(Any, Any)])
```

Run a target function under a chaos scenario.

For simplicity, this implementation calls the target function directly.
In a production system, this would inject faults based on the scenario probability.

**Parameters**:

- `scenario_name`: Name of the scenario to apply.
- `target_fn`: The function to call under the scenario.

**Returns**: The result of calling target_fn.

**Raises**:

- `KeyError`: If the scenario_name does not exist.

---

## scenarios

```python
scenarios(self: Any)
```

Get all registered chaos scenarios.

**Returns**: List of all ChaosScenarios.

---

