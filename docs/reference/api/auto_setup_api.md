# auto_setup API Reference

> **Source**: `src/thegent/ide/auto_setup.py`

Auto-setup and auto-configuration for IDE integrations.

---

## auto_setup_all

```python
auto_setup_all(auto_configure: bool, auto_install: bool)
```

Auto-setup all IDE integrations.

**Parameters**:

- `auto_configure`: Automatically configure integrations when possible
- `auto_install`: Automatically install missing components (IDE, plugins)

**Returns**: Dict with setup status for each integration

---

## auto_setup_ghostty_shell_integration

```python
auto_setup_ghostty_shell_integration(auto_configure: bool)
```

Auto-setup Ghostty shell integration.

**Parameters**:

- `auto_configure`: Automatically add shell integration if Ghostty is found

**Returns**: Dict with setup status

---

## auto_setup_jetbrains_integration

```python
auto_setup_jetbrains_integration(auto_install: bool)
```

Auto-setup JetBrains integration (detect IDE, verify CLI access, auto-install if needed).

**Parameters**:

- `auto_install`: Automatically install IntelliJ IDEA if not found

**Returns**: Dict with setup status and details

---

## auto_setup_serena_jetbrains_plugin

```python
auto_setup_serena_jetbrains_plugin(auto_install: bool)
```

Auto-detect and configure Serena JetBrains plugin.

**Parameters**:

- `auto_install`: Attempt to install plugin if not detected

**Returns**: Dict with setup status and instructions if needed

---
