# thg_platform API Reference

> **Source**: `src/thegent/thg_platform.py`

Cross-platform detection and utilities.

---

## Platform

Supported platforms.

**Inherits from**: `Enum`

---

## detect_platform

Detect current platform.

**Returns**: Platform enum value (MACOS, LINUX, WINDOWS, WSL2, or UNKNOWN)

**Examples**:

```python
>>> plat = detect_platform()
>>> plat == Platform.MACOS
True
```

---

## get_architecture

Get system architecture.

**Returns**: Architecture string: "x86_64", "arm64", "aarch64", "i386", etc.

**Examples**:

```python
>>> get_architecture()
'arm64'  # on Apple Silicon Mac
```

---

## get_platform_name

Get platform name as string.

**Returns**: Platform name: "macos", "linux", "windows", "wsl2", or "unknown"

**Examples**:

```python
>>> get_platform_name()
'macos'
```

---

## is_linux

Check if running on Linux (not WSL2).

**Returns**: True if Linux (not WSL2), False otherwise

**Examples**:

```python
>>> is_linux()
True  # on Linux (not WSL2)
```

---

## is_macos

Check if running on macOS.

**Returns**: True if macOS, False otherwise

**Examples**:

```python
>>> is_macos()
True  # on macOS
```

---

## is_unix

Check if running on Unix-like system (macOS, Linux, WSL2).

**Returns**: True if macOS, Linux, or WSL2, False otherwise

**Examples**:

```python
>>> is_unix()
True  # on macOS/Linux
```

---

## is_windows

Check if running on Windows (including WSL2).

**Returns**: True if Windows or WSL2, False otherwise

**Examples**:

```python
>>> is_windows()
False  # on macOS/Linux
```

---
