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
__init__(self: Any, agents_dir: Any)
```

---

#### PersonaManager.check_access

```python
check_access(self: Any, persona: str, operation: str, lane: str)
```

Verify if a persona can perform a specific operation in a specific lane.

---

#### PersonaManager.discover_teammates

```python
discover_teammates(self: Any)
```

WP-16001: Auto-discovery of teammates from the agents/ directory.

---

#### PersonaManager.list_teammates

```python
list_teammates(self: Any)
```

List all discovered teammates.

---

---

## check_access

```python
check_access(self: Any, persona: str, operation: str, lane: str)
```

Verify if a persona can perform a specific operation in a specific lane.

---

## discover_teammates

```python
discover_teammates(self: Any)
```

WP-16001: Auto-discovery of teammates from the agents/ directory.

---

## list_teammates

```python
list_teammates(self: Any)
```

List all discovered teammates.

---

