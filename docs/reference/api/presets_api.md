# presets API Reference

> **Source**: `src/thegent/agents/presets.py`

Preset prompt catalog for Lifecycle loops.

---

## PresetEntry

Entry in the preset catalog.

---

## get_preset

```python
get_preset(preset_id: str)
```

Return preset entry by id.

---

## list_presets

Return all presets for CLI/MCP discovery.

---

## match_preset

```python
match_preset(text: str)
```

Match text against preset trigger keywords.

---

