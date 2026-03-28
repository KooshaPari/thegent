# linux_virtual_desktop API Reference

> **Source**: `src/thegent/automation/providers/linux_virtual_desktop.py`

Linux virtual desktop provider with high-performance automation.

Uses:
- Xvfb (X Virtual Framebuffer) for headless isolation
- X11 for low-latency input injection (<5ms)
- xdotool/xte for automation
- Optionally: Xpra for persistent virtual displays

---

## LinuxVirtualDesktopProvider

Linux implementation using Xvfb/Xpra.

**Inherits from**: `VirtualDesktopProvider`

### Methods

#### LinuxVirtualDesktopProvider.__init__

```python
__init__(self: Any)
```

---

#### LinuxVirtualDesktopProvider.name

```python
name(self: Any)
```

---

#### LinuxVirtualDesktopProvider.supports_gpu

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

