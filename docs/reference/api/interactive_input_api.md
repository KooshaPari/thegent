# interactive_input API Reference

> **Source**: `src/thegent/tui/widgets/interactive_input.py`

Interactive input widget for compositor workflows (WL-017).

---

## InteractiveInputWidget

Prompt input bar with submit button and Enter-to-send behavior.

**Inherits from**: `Widget`

### Methods

#### InteractiveInputWidget.__init__

```python
__init__(self: Any, on_submit: Any, placeholder: str)
```

---

#### InteractiveInputWidget.compose

```python
compose(self: Any)
```

---

#### InteractiveInputWidget.on_button_pressed

```python
on_button_pressed(self: Any, event: Button.Pressed)
```

---

#### InteractiveInputWidget.on_input_submitted

```python
on_input_submitted(self: Any, _: Input.Submitted)
```

---

---

## compose

```python
compose(self: Any)
```

---

## on_button_pressed

```python
on_button_pressed(self: Any, event: Button.Pressed) -> None
```

---

## on_input_submitted

```python
on_input_submitted(self: Any, _: Input.Submitted) -> None
```

---

