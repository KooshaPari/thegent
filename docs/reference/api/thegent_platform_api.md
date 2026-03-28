# thegent_platform API Reference

> **Source**: `src/thegent/thegent_platform.py`

Cross-platform detection and utilities.

---

## Platform

Supported platforms.

**Inherits from**: `Enum`

---

## PlatformDiagnostics

**Inherits from**: `TypedDict`

---

## detect_platform

Detect current platform.

**Returns**: Platform enum value (MACOS, LINUX, WINDOWS, WSL2, or UNKNOWN)

---

## get_platform_detection_diagnostics

Return diagnostics for platform detection edge cases.

---

## reset_platform_detection_diagnostics

Reset platform detection diagnostics (test helper).

---

