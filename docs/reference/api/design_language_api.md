# design_language API Reference

> **Source**: `src/thegent/design/design_language.py`

Design language system with platform-specific tokens.

---

## DesignLanguage

Design language system.

This class manages design tokens (colors, typography, spacing) and
applies them consistently across all components, with platform-specific
overrides where appropriate.

Examples:
    >>> design = DesignLanguage()
    >>> primary_color = design.get_token("color.primary")
    >>> system_font = design.get_token("font.system", platform="macos")

### Methods

#### DesignLanguage.__init__

Initialize design language system.

```python
__init__(self)
```

#### DesignLanguage.apply_to_cli

Apply design language to CLI.

Configures Rich console with design tokens.
This is a placeholder - full implementation would configure
Rich console styles based on tokens.

```python
apply_to_cli(self)
```

#### DesignLanguage.get_token

Get design token value.

Args:
    name: Token name (e.g., "color.primary")
    platform: Platform override, or None to use detected platform

Returns:
    Token value, or None if not found

```python
get_token(self, name, platform)
```

---

## DesignToken

Design token definition.

---

## apply_to_cli

Apply design language to CLI.

Configures Rich console with design tokens.
This is a placeholder - full implementation would configure
Rich console styles based on tokens.

```python
apply_to_cli(self)
```

---

## get_token

Get design token value.

Args:
    name: Token name (e.g., "color.primary")
    platform: Platform override, or None to use detected platform

Returns:
    Token value, or None if not found

```python
get_token(self, name, platform)
```

---

