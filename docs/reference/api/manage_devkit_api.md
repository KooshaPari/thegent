# manage_devkit API Reference

> **Source**: `src/thegent/integration/manage_devkit.py`

Integration with manage devkit system.

---

## ManageDevkitIntegration

Integrate with manage devkit system.

This class handles integration with external "manage" devkit systems,
including path sharing, tool registration, and configuration harmonization.

Examples:
    >>> integration = ManageDevkitIntegration()
    >>> integration.integrate_paths()
    >>> integration.integrate_tools()
    >>> integration.register_with_manage()

### Methods

#### ManageDevkitIntegration.__init__

Initialize manage devkit integration.

```python
__init__(self)
```

#### ManageDevkitIntegration.integrate_paths

Integrate thegent paths with manage devkit.

Creates shared configuration structure if manage devkit uses
similar directory structure. Creates symlinks to share config.

```python
integrate_paths(self)
```

#### ManageDevkitIntegration.integrate_tools

Integrate thegent tools with manage devkit.

Creates symlink to thegent binary in manage devkit bin directory.

```python
integrate_tools(self)
```

#### ManageDevkitIntegration.register_with_manage

Register thegent with manage devkit.

Adds thegent to the list of tools in manage devkit configuration.

```python
register_with_manage(self)
```

---

## integrate_paths

Integrate thegent paths with manage devkit.

Creates shared configuration structure if manage devkit uses
similar directory structure. Creates symlinks to share config.

```python
integrate_paths(self)
```

---

## integrate_tools

Integrate thegent tools with manage devkit.

Creates symlink to thegent binary in manage devkit bin directory.

```python
integrate_tools(self)
```

---

## register_with_manage

Register thegent with manage devkit.

Adds thegent to the list of tools in manage devkit configuration.

```python
register_with_manage(self)
```

---

