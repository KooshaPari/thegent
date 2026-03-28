# macos_virtual_desktop API Reference

> **Source**: `src/thegent/automation/providers/macos_virtual_desktop.py`

macOS virtual desktop provider with high-performance automation.

Uses:
- CGEvent for low-latency input injection (<3ms)
- Screen recording API for capture (with user permission)
- AppleScript for window management
- Accessibility API for UI element access

---

## MacOSVirtualDesktopProvider

macOS implementation using native APIs.

**Inherits from**: `VirtualDesktopProvider`

### Methods

#### MacOSVirtualDesktopProvider.__init__

```python
__init__(self: Any)
```

---

#### MacOSVirtualDesktopProvider.name

```python
name(self: Any)
```

---

#### MacOSVirtualDesktopProvider.supports_gpu

```python
supports_gpu(self: Any)
```

---

---

## name

```python
name(self: Any) -> str
```

---

## supports_gpu

```python
supports_gpu(self: Any) -> bool
```

---

