# personas API Reference

> **Source**: `src/thegent/governance/personas.py`

WP-12007: Persona profiles and access constraints.

Defines role-based access limits and defaults for different operator personas.

---

## PersonaManager

Manages role-based constraints for operator personas.

### Methods

#### PersonaManager.__init__

```python
__init__(self)
```

#### PersonaManager.check_access

Verify if a persona can perform a specific operation in a specific lane.

```python
check_access(self, persona, operation, lane)
```

---

## check_access

Verify if a persona can perform a specific operation in a specific lane.

```python
check_access(self, persona, operation, lane)
```

---

