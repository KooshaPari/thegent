# README

Source: docs/specs/terminal/README.md

---

# Terminal & ZMX Specification

## Overview

Terminal harness for PTY management and session control.

## Components

### ZMX Integration

| Component | Purpose | Path |
|-----------|---------|------|
| ZmxBackend | Session management | `session/zmx_backend.py` |
| ZmxSession | Session state | `muxless/zmx_session.py` |

### Terminal Operations

| Operation | Implementation |
|-----------|----------------|
| Spawn PTY | Native process |
| Capture output | Streaming |
| Send input | Direct injection |
| Resize | Window change |

## Architecture

```
User → MCP Tool → ZmxBackend → zmx binary → PTY
                        ↓
                  Terminal session
```

## Performance

| Metric | Target |
|--------|--------|
| Spawn latency | <100ms |
| Output capture | Real-time |
| Input latency | <10ms |

## Security

- Process isolation
- Resource limits
- Audit logging