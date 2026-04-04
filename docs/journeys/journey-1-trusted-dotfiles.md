# Journey: Trusted Dotfiles Installation

**Duration**: ~30 seconds  
**Sandbox Tier**: Tier 1 (bubblewrap)  
**Trust Level**: Trusted  
**User**: Developer setting up a new machine

---

## Overview

This journey demonstrates the fastest path for installing your own dotfiles on a new machine. The agent executes with minimal overhead (~10ms sandbox creation) while still providing namespace isolation.

## User Story

> "I just got a new MacBook and need to set up my development environment. I want my dotfiles applied quickly but safely."

## Step-by-Step Journey

### Step 1: Initialize thegent

```bash
$ thegent init --profile developer

✓ Agent platform initialized
✓ Configuration stored at ~/.thegent/config.toml
✓ Default role: dotfiles_manager
✓ Sandbox tier: auto (trust-based)
```

### Step 2: Link Trusted Dotfiles

```bash
$ thegent dotfiles link --source ~/dots/main \
                        --target ~ \
                        --trust-level trusted

┌─────────────────────────────────────────────────────────────┐
│  thegent Agent Execution                                     │
├─────────────────────────────────────────────────────────────┤
│  Role: dotfiles_manager                                     │
│  Trust: Trusted (user-owned)                                │
│  Sandbox: Tier 1 (bubblewrap) - ~10ms overhead            │
├─────────────────────────────────────────────────────────────┤
│  ✓ Namespace isolation enabled                              │
│  ✓ Read-only home bind mount                                │
│  ✓ tmpfs for /tmp                                           │
│  ✓ Network: disabled                                        │
└─────────────────────────────────────────────────────────────┘

[ bubblewrap ] Creating sandbox environment...
[ bubblewrap ] Sandbox ready in 8ms
[ bubblewrap ] Executing: ./install.sh

✓ Symlinking .zshrc → ~/dots/main/.zshrc
✓ Symlinking .gitconfig → ~/dots/main/.gitconfig  
✓ Symlinking .vimrc → ~/dots/main/.vimrc
✓ Installing Homebrew packages via Brewfile

[ bubblewrap ] Execution completed in 23ms
✓ All dotfiles installed successfully
```

### Step 3: Verify Installation

```bash
$ thegent verify --checks all

┌─────────────────────────────────────────────────────────────┐
│  Verification Results                                       │
├─────────────────────────────────────────────────────────────┤
│  ✓ Shell configuration valid                                │
│  ✓ Git config detected                                      │
│  ✓ Symlinks intact                                         │
│  ✓ Package manager (Homebrew) functional                    │
│  ✓ Environment variables set                               │
└─────────────────────────────────────────────────────────────┘

Total verification time: 145ms
```

## What Happened Behind the Scenes

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1 (bubblewrap) Sandbox Lifecycle                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Trust Evaluation                                        │
│     Source: ~/dots/main (user-owned)                        │
│     Trust Level: Trusted                                    │
│     → Select bubblewrap sandbox                             │
│                                                              │
│  2. Sandbox Creation (8ms)                                  │
│     bwrap --ro-bind /home/user/dots /dots                  │
│          --ro-bind /usr /usr                                │
│          --tmpfs /tmp                                       │
│          --unshare-user                                     │
│          --unshare-pid                                      │
│          --unshare-ipc                                      │
│          --die-with-parent                                  │
│                                                              │
│  3. Script Execution                                       │
│     /bin/sh -c './install.sh'                               │
│                                                              │
│  4. Cleanup                                                 │
│     Sandbox terminated with process                          │
│                                                              │
│  Total overhead: ~10ms                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Sandbox creation | 8ms |
| Script execution | 23ms |
| Total wall time | 31ms |
| Memory overhead | +5MB |
| Trust evaluation | <1ms |

## Security Properties

- **Namespace isolation**: User, PID, IPC namespaces prevent process visibility
- **Read-only mounts**: Cannot write to bound directories except tmpfs
- **No network**: Network namespace isolated
- **Die with parent**: Sandbox dies if parent process dies

## When Tier 1 Is Appropriate

✅ **Use bubblewrap for:**
- Your own dotfiles/scripts you wrote
- Verified configurations from your own repositories
- Fast execution where security is moderate

❌ **Don't use bubblewrap for:**
- Unknown scripts from the internet
- Community templates you haven't reviewed
- Scripts requesting network access

## Alternative: Tier 0 (Env Filter Only)

For even faster execution during development:

```bash
$ thegent dotfiles link --source ~/dots/main \
                        --trust-level trusted \
                        --tier envfilter

[ envfilter ] Creating sandbox environment...
[ envfilter ] Sandbox ready in <1ms
[ envfilter ] Executing: ./install.sh

✓ Symlinking .zshrc...
```

**Trade-off**: Tier 0 has no namespace isolation but ~0ms overhead.

---

## Next Journey

➡️ **[Community Template Execution](./journey-2-community-template.md)** - Running third-party dotfiles with gVisor isolation
