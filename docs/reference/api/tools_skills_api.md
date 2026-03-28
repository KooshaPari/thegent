# tools_skills API Reference

> **Source**: `src/thegent/mcp/server/tools_skills.py`

Skill MCP tool handlers for list/activate scaffolding (WL-111).

---

## DiscoverySkillBackend

Skill backend bound to the current discovery/load implementation.

### Methods

#### DiscoverySkillBackend.activate_skill

```python
activate_skill(self: Any, skill_name: str)
```

---

#### DiscoverySkillBackend.list_skills

```python
list_skills(self: Any)
```

---

---

## SkillBackend

**Inherits from**: `Protocol`

### Methods

#### SkillBackend.activate_skill

```python
activate_skill(self: Any, skill_name: str)
```

---

#### SkillBackend.list_skills

```python
list_skills(self: Any)
```

---

---

## activate_skill

```python
activate_skill(self: Any, skill_name: str) -> Any
```

---

## list_skills

```python
list_skills(self: Any) -> list[dict[(str, Any)]]
```

---

## thegent_activate_skill_impl

---

## thegent_list_skills_impl

---

