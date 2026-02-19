# autopoiesis API Reference

> **Source**: `src/thegent/agents/autopoiesis.py`

WP-37001: Self-Authoring Agent Architectures (Autopoiesis).
Enables thegent to design, code, and deploy entire new agent personas autonomously.
Uses recursive synthesis to evolve the system's own architecture.

---

## AgentPersonaSpec

Specification for a new agent persona to be authored.

**Inherits from**: `BaseModel`

---

## AutopoiesisManager

Orchestrates the self-authoring of agent architectures.

### Methods

#### AutopoiesisManager.__init__

```python
__init__(self, run_id)
```

#### AutopoiesisManager.author_persona

Autonomously author a new agent persona based on a purpose spec.

```python
author_persona(self, spec)
```

#### AutopoiesisManager.deploy_persona

Deploy the synthesized persona into the live registry.

```python
deploy_persona(self, synthesis)
```

---

## author_persona

Autonomously author a new agent persona based on a purpose spec.

```python
author_persona(self, spec)
```

---

## deploy_persona

Deploy the synthesized persona into the live registry.

```python
deploy_persona(self, synthesis)
```

---

