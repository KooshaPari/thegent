# probing API Reference

> **Source**: `src/thegent/agents/probing.py`

WP-33004: Black-Box Probing & Fingerprinting.
Identifies the underlying model and capabilities of black-box agents via behavioral probing.
Generates an 'agent fingerprint' to enable better steering and policy enforcement.

---

## AgentFingerprint

Behavioral fingerprint of a black-box agent.

**Inherits from**: `BaseModel`

---

## AgentProber

Probes black-box agents to identify their characteristics.

### Methods

#### AgentProber.__init__

```python
__init__(self, agent_id)
```

#### AgentProber.identify_deviations

Detect if an agent's behavior has drifted from its baseline fingerprint.

```python
identify_deviations(self, current_fp, baseline_fp)
```

#### AgentProber.probe_agent

Run a suite of behavioral probes and generate a fingerprint.

```python
probe_agent(self, proxy_fn)
```

---

## identify_deviations

Detect if an agent's behavior has drifted from its baseline fingerprint.

```python
identify_deviations(self, current_fp, baseline_fp)
```

---

## probe_agent

Run a suite of behavioral probes and generate a fingerprint.

```python
probe_agent(self, proxy_fn)
```

---

