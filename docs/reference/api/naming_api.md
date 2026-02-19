# naming API Reference

> **Source**: `src/thegent/design/naming.py`

Consistent naming conventions enforcement.

---

## NamingConvention

Naming convention enforcer.

This class enforces consistent naming conventions across all components:
- Commands: kebab-case
- Config keys: snake_case
- Functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE

Examples:
    >>> naming = NamingConvention()
    >>> is_valid = naming.validate("thegent-install", "command")
    >>> suggested = naming.suggest_name("thegent_install", "command")

### Methods

#### NamingConvention.__init__

Initialize naming convention enforcer.

```python
__init__(self)
```

#### NamingConvention.suggest_name

Suggest name following convention.

Converts name to follow the specified convention.

Args:
    name: Name to convert
    convention_type: Target convention type

Returns:
    Suggested name following convention

```python
suggest_name(self, name, convention_type)
```

#### NamingConvention.validate

Validate name against convention.

Args:
    name: Name to validate
    convention_type: Type of convention (command, config_key, function, class, constant)

Returns:
    True if name follows convention, False otherwise

```python
validate(self, name, convention_type)
```

---

## suggest_name

Suggest name following convention.

Converts name to follow the specified convention.

Args:
    name: Name to convert
    convention_type: Target convention type

Returns:
    Suggested name following convention

```python
suggest_name(self, name, convention_type)
```

---

## validate

Validate name against convention.

Args:
    name: Name to validate
    convention_type: Type of convention (command, config_key, function, class, constant)

Returns:
    True if name follows convention, False otherwise

```python
validate(self, name, convention_type)
```

---

