# Journey: Community Template Execution

**Duration**: ~500ms  
**Sandbox Tier**: Tier 2 (gVisor)  
**Trust Level**: Community  
**User**: Developer trying a popular dotfiles template

---

## Overview

This journey demonstrates running a community dotfiles template with gVisor isolation. The overhead is higher (~100-200ms) but provides significantly stronger security through userspace kernel emulation.

## User Story

> "I found an awesome dotfiles template on GitHub with 500+ stars. Before applying it to my system, I want to review what it does—but I also want to test it safely."

## Step-by-Step Journey

### Step 1: Discover Community Template

```bash
$ thegent discover --source github --filter stars:>100 --topic dotfiles

┌─────────────────────────────────────────────────────────────┐
│  Community Templates                                        │
├─────────────────────────────────────────────────────────────┤
│  1. mathieufPoint/dotfiles ⭐ 890                        │
│     → Rust-based, minimal, macOS/Linux                     │
│                                                              │
│  2. webpro/awesome-dotfiles ⭐ 2.1k                       │
│     → Collection of the best dotfiles resources            │
│                                                              │
│  3. unixorn/awesome-zsh-plugins ⭐ 680                    │
│     → Zsh plugin manager and configs                       │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Preview Template Actions

```bash
$ thegent preview --source https://github.com/mathieufPoint/dotfiles

┌─────────────────────────────────────────────────────────────┐
│  Template Analysis                                          │
├─────────────────────────────────────────────────────────────┤
│  Repository: mathieufPoint/dotfiles                         │
│  Stars: 890 | License: MIT                                 │
│  Last updated: 2026-03-15                                  │
├─────────────────────────────────────────────────────────────┤
│  Actions to be executed:                                    │
│  1. install_homebrew.sh                                    │
│     → Installs Homebrew package manager                     │
│  2. setup_shell.sh                                         │
│     → Configures zsh with oh-my-zsh                         │
│  3. install_utils.sh                                       │
│     → git, curl, wget, fzf, delta                          │
│  4. configure_git.sh                                       │
│     → Sets up git aliases and prompt                       │
├─────────────────────────────────────────────────────────────┤
│  Trust evaluation:                                          │
│  → GitHub stars: 890 (exceeds threshold of 100)           │
│  → License: MIT (permissive)                               │
│  → Automated: Yes (CI/CD pipeline)                         │
│  → Recommended tier: Tier 2 (gVisor)                        │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Execute with gVisor Isolation

```bash
$ thegent apply --source https://github.com/mathieufPoint/dotfiles \
                --trust-level community \
                --tier gvisor

┌─────────────────────────────────────────────────────────────┐
│  thegent Agent Execution                                     │
├─────────────────────────────────────────────────────────────┤
│  Role: dotfiles_manager                                     │
│  Trust: Community (890 GitHub stars)                       │
│  Sandbox: Tier 2 (gVisor) - ~100ms overhead               │
├─────────────────────────────────────────────────────────────┤
│  ⚠ Running in userspace kernel isolation                   │
│  ⚠ Scripts cannot access host kernel directly              │
│  ✓ Full syscall filtering enabled                          │
│  ✓ Network: disabled                                       │
│  ✓ Container image: thegent/gvisor-base:latest           │
└─────────────────────────────────────────────────────────────┘

[ gVisor ] Pulling container image...
[ gVisor ] Image pulled in 1.2s
[ gVisor ] Creating sandbox environment via runsc...
[ gVisor ] Sandbox ready in 145ms
[ gVisor ] Executing: ./install.sh

✓ Installing Homebrew...
✓ Configuring zsh with oh-my-zsh...
✓ Installing utilities: git, curl, wget, fzf, delta
✓ Setting up git configuration...

[ gVisor ] Execution completed in 890ms
✓ All community dotfiles applied successfully

[ gVisor ] Sandbox terminated cleanly
```

### Step 4: Review Execution Audit Log

```bash
$ thegent audit --last --format json

{
  "execution_id": "exec_abc123",
  "timestamp": "2026-04-04T10:30:00Z",
  "trust_level": "community",
  "sandbox_tier": "gvisor",
  "duration_ms": 1035,
  "sandbox_creation_ms": 145,
  "script_execution_ms": 890,
  "syscalls_intercepted": 47,
  "syscalls_allowed": 31,
  "syscalls_denied": 16,
  "denied_syscalls": [
    "socket" (3 attempts),
    "connect" (5 attempts),
    "bind" (2 attempts),
    "ptrace" (6 attempts)
  ],
  "filesystem_ops": {
    "reads": 23,
    "writes": 8,
    "denied_writes": 0
  },
  "network_attempts_blocked": 10
}
```

## What Happened Behind the Scenes

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 2 (gVisor) Sandbox Lifecycle                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Trust Evaluation (2ms)                                 │
│     Source: GitHub (890 stars)                              │
│     Trust Level: Community                                  │
│     → Select gVisor sandbox                                │
│                                                              │
│  2. Container Image Pull (1.2s, one-time)                 │
│     thegent/gvisor-base:latest                             │
│     Contains: Ubuntu base + runsc runtime                   │
│                                                              │
│  3. Sandbox Creation via runsc (145ms)                    │
│     ┌─────────────────────────────────────────────┐        │
│     │  Application Process                         │        │
│     │         │                                     │        │
│     │         ▼                                     │        │
│     │  ┌─────────────────────────────────────────┐ │        │
│     │  │         gVisor Sentry (Go)              │ │        │
│     │  │  • Syscall interception                  │ │        │
│     │  │  • Memory management                     │ │        │
│     │  │  • Network stack (disabled)              │ │        │
│     │  │  • File system (9P protocol)            │ │        │
│     │  └──────────────────┬──────────────────────┘ │        │
│     │                     │                         │        │
│     │                     ▼                         │        │
│     │  ┌─────────────────────────────────────────┐ │        │
│     │  │         Host Kernel (Linux)             │ │        │
│     │  │  • Minimal exposure via syscall filter  │ │        │
│     │  └─────────────────────────────────────────┘ │        │
│     └─────────────────────────────────────────────┘        │
│                                                              │
│  4. Script Execution (890ms)                               │
│     All syscalls go through Sentry                          │
│     Dangerous syscalls (socket, ptrace) blocked             │
│                                                              │
│  5. Cleanup                                                 │
│     Container destroyed, no residual state                   │
│                                                              │
│  Total overhead: ~145ms (plus one-time image pull)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Security Properties

- **Userspace kernel (Sentry)**: Linux syscalls implemented in Go, not passing to host kernel
- **Syscall filtering**: 47 syscalls intercepted, 16 denied including:
  - `socket`, `connect`, `bind` (network attempts blocked)
  - `ptrace` (debugging/inspection blocked)
- **Filesystem isolation**: 9P protocol for file operations
- **No privileged operations**: Container runs as non-root

## gVisor vs bubblewrap: When to Escalate

| Scenario | Tier 1 (bubblewrap) | Tier 2 (gVisor) |
|----------|----------------------|------------------|
| Your own dotfiles | ✅ | ✅ |
| Verified community template | ❌ | ✅ |
| Scripts requesting network | ❌ | ✅ |
| Scripts with unknown behavior | ❌ | ✅ |
| Execution time | ~10ms | ~145ms |
| Memory overhead | +5MB | +50MB |

## CVE Comparison

| Technology | CVEs (2020-2025) | Critical |
|------------|-------------------|----------|
| bubblewrap | 2 | 0 |
| gVisor | 8 | 1 |

gVisor has more CVEs due to larger codebase (Go userspace kernel), but all are medium or low severity. The userspace kernel design limits blast radius—kernel exploits cannot reach the host.

---

## Next Journey

➡️ **[Untrusted Script Isolation](./journey-3-untrusted-isolation.md)** - Maximum security with Firecracker microVMs
