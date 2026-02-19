# alerts API Reference

> **Source**: `src/thegent/ux/alerts.py`

WP-4004: Interruption taxonomy and fatigue controls.

---

## AlertFatigueController

Manages alert volume and prevents operator fatigue.

### Methods

#### AlertFatigueController.__init__

```python
__init__(self, settings)
```

#### AlertFatigueController.get_fatigue_level

Return fatigue level from 0.0 to 1.0.

```python
get_fatigue_level(self)
```

#### AlertFatigueController.record_alert

Record an alert and return True if it should be suppressed due to fatigue.

```python
record_alert(self, kind)
```

---

## InterruptionKind

Kinds of system interruptions.

**Inherits from**: `str`

---

## get_fatigue_level

Return fatigue level from 0.0 to 1.0.

```python
get_fatigue_level(self)
```

---

## record_alert

Record an alert and return True if it should be suppressed due to fatigue.

```python
record_alert(self, kind)
```

---

