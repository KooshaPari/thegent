# thegent Journeys

End-to-end user journey demonstrations for thegent's agent sandboxing capabilities.

## Available Journeys

### [Journey 1: Trusted Dotfiles Installation](./journey-1-trusted-dotfiles.md)
**Tier**: 1 (bubblewrap) | **Duration**: ~30 seconds | **Trust**: Trusted

Fast path for installing your own dotfiles with bubblewrap isolation (~10ms overhead).

> "I just got a new MacBook and need to set up my development environment with my own dotfiles."

### [Journey 2: Community Template Execution](./journey-2-community-template.md)
**Tier**: 2 (gVisor) | **Duration**: ~500ms | **Trust**: Community

Running third-party dotfiles with userspace kernel isolation (~100-200ms overhead).

> "I found an awesome dotfiles template on GitHub with 500+ stars. I want to test it safely."

### [Journey 3: Untrusted Script Isolation](./journey-3-untrusted-isolation.md)
**Tier**: 3 (Firecracker) | **Duration**: ~1-2 seconds | **Trust**: Untrusted

Maximum security with microVM isolation for dangerous scripts (~150ms overhead).

> "I found a shell script on a random blog. I'm not running that without maximum isolation."

## Quick Reference

| Journey | Trust Level | Sandbox | Overhead | When to Use |
|---------|-------------|---------|----------|-------------|
| 1 | Trusted | bubblewrap | ~10ms | Your own dotfiles |
| 2 | Community | gVisor | ~100ms | Third-party templates |
| 3 | Untrusted | Firecracker | ~150ms | Unknown scripts |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              thegent Tiered Sandboxing                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Tier 0: Env Filter (dev only)                              │
│  └── <1ms | No isolation | Fast iteration                   │
│                                                              │
│  Tier 1: bubblewrap                                         │
│  └── ~10ms | Namespace isolation | Trusted scripts          │
│                                                              │
│  Tier 2: gVisor                                             │
│  └── ~100ms | Userspace kernel | Community templates        │
│                                                              │
│  Tier 3: Firecracker                                        │
│  └── ~150ms | VM isolation | Untrusted scripts              │
│                                                              │
│  Tier 4: WASM                                               │
│  └── ~1ms | Capability-based | Plugins                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

*Each journey demonstrates the complete flow from trust evaluation through sandbox creation, execution, and audit logging.*
