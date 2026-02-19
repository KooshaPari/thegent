# fallback_ui API Reference

> **Source**: `src/thegent/ux/fallback_ui.py`

WP-4003: One-click safe fallback options.

---

## FallbackOption

A safe fallback action for the operator.

### Methods

#### FallbackOption.__init__

```python
__init__(self, id, label, description, command)
```

---

## FallbackRegistry

Registry of safe fallback options based on failure context.

### Methods

#### FallbackRegistry.__init__

```python
__init__(self, settings)
```

#### FallbackRegistry.get_recommendations

Return recommended fallback options based on failure type.

```python
get_recommendations(self, failure_kind)
```

---

## get_recommendations

Return recommended fallback options based on failure type.

```python
get_recommendations(self, failure_kind)
```

---

