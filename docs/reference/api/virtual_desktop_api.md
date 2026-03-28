# virtual_desktop API Reference

> **Source**: `src/thegent/automation/virtual_desktop.py`

High-performance virtual desktop automation for agents.

This module provides low-latency (<50ms) desktop automation using virtual desktop
isolation, similar to UFO2's Picture-in-Picture approach. Each agent gets its own
isolated desktop session where it can automate without colliding with the user.

Architecture:
- VirtualDesktop: Creates isolated desktop sessions per agent
- ScreenCapture: GPU-accelerated screen capture (DXGI/X11/Quartz)
- InputInjector: Low-latency input injection (direct API, not subprocess)
- DesktopSession: Manages the isolated session lifecycle

---

## DesktopConfig

Configuration for a virtual desktop session.

---

## DesktopSession

Represents a single virtual desktop session.

### Methods

#### DesktopSession.__init__

```python
__init__(self: Any, agent_id: str, desktop_id: str, provider: VirtualDesktopProvider, config: DesktopConfig)
```

---

#### DesktopSession.last_frame

```python
last_frame(self: Any)
```

---

#### DesktopSession.on_frame

```python
on_frame(self: Any, callback: Callable[(Any, None)])
```

Register a callback for new frames.

---

#### DesktopSession.state

```python
state(self: Any, value: DesktopState)
```

---

---

## DesktopState

Desktop session state.

**Inherits from**: `Enum`

---

## InputEvent

Input event for injection.

---

## ScreenFrame

A single screen frame capture.

### Methods

#### ScreenFrame.latency_ms

```python
latency_ms(self: Any)
```

Capture latency in milliseconds.

---

#### ScreenFrame.size_bytes

```python
size_bytes(self: Any)
```

---

---

## VirtualDesktopManager

Manages virtual desktop sessions for agents.

### Methods

#### VirtualDesktopManager.__init__

```python
__init__(self: Any)
```

---

---

## VirtualDesktopProvider

Abstract base for platform-specific virtual desktop implementations.

**Inherits from**: `ABC`

### Methods

#### VirtualDesktopProvider.name

```python
name(self: Any)
```

Provider name.

---

#### VirtualDesktopProvider.supports_gpu

```python
supports_gpu(self: Any)
```

Whether this provider supports GPU acceleration.

---

---

## _UnsupportedPlatformVirtualDesktopProvider

Fallback provider when running on unsupported platforms.

**Inherits from**: `VirtualDesktopProvider`

**Method Resolution Order**: `_UnsupportedPlatformVirtualDesktopProvider -> VirtualDesktopProvider`

### Methods

#### _UnsupportedPlatformVirtualDesktopProvider.__init__

```python
__init__(self: Any, system: str)
```

---

#### _UnsupportedPlatformVirtualDesktopProvider.name

```python
name(self: Any)
```

---

#### _UnsupportedPlatformVirtualDesktopProvider.supports_gpu

```python
supports_gpu(self: Any)
```

---

---

## get_desktop_manager

Get the global desktop manager.

---

## last_frame

```python
last_frame(self: Any) -> Any
```

---

## latency_ms

```python
latency_ms(self: Any)
```

Capture latency in milliseconds.

---

## name

```python
name(self: Any) -> str
```

---

## on_frame

```python
on_frame(self: Any, callback: Callable[(Any, None)])
```

Register a callback for new frames.

---

## size_bytes

```python
size_bytes(self: Any) -> int
```

---

## state

```python
state(self: Any, value: DesktopState) -> None
```

---

## supports_gpu

```python
supports_gpu(self: Any) -> bool
```

---

