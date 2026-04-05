# Journey: Creating a Sandboxed Agent

**Duration**: ~10-15 minutes  
**Sandbox Tier**: Depends on agent configuration  
**Trust Level**: Configurable per agent  
**User**: Developer creating custom agent workflows

---

## Overview

This journey demonstrates how to create a custom sandboxed agent in thegent. You'll build an agent tailored to your specific workflow, configure its sandbox tier based on trust level, and verify it operates correctly within its isolation boundaries.

## Prerequisites

- thegent installed (see [Getting Started](./journey-1-getting-started.md))
- Basic understanding of thegent roles (Installer, Configurator, Verifier, Auditor)
- Familiarity with your target environment

---

## Step-by-Step Journey

### Step 1: Understand Agent Architecture

Before creating an agent, understand the components:

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Architecture                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Agent Instance                       │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Role Definition                     │  │  │
│  │  │  • Name: e.g., "my_installer"                  │  │  │
│  │  │  • Type: Installer | Configurator | etc.       │  │  │
│  │  │  • Description: Human-readable purpose          │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Tool Registry                       │  │  │
│  │  │  • InstallPackage                               │  │  │
│  │  │  • CreateSymlink                                │  │  │
│  │  │  • WriteConfig                                  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Sandbox Configuration               │  │  │
│  │  │  • Tier: 0 | 1 | 2 | 3 | 4                      │  │  │
│  │  │  • Allowed dirs: [... ]                         │  │  │
│  │  │  • Network: yes | no                            │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Design Your Agent

Define your agent's purpose and requirements:

**Agent Concept**: A "Dev Environment Setup Agent" that:
- Installs common development tools (git, node, python)
- Configures shell environment
- Sets up git signing
- Verifies installation

**Sandbox Selection Rationale**:
- Tier 1 (bubblewrap) is appropriate because:
  - Scripts are from trusted sources (official package managers)
  - Need network access for downloads
  - User owns the system, so medium isolation is acceptable

### Step 3: Create the Agent

Use thegent CLI to create a new agent:

```bash
$ thegent agent create dev-setup \
    --role installer \
    --description "Development environment setup agent" \
    --tier bubblewrap

┌─────────────────────────────────────────────────────────────┐
│  Creating Agent: dev-setup                                  │
├─────────────────────────────────────────────────────────────┤
│  Role: Installer                                            │
│  Sandbox Tier: Tier 1 (bubblewrap)                          │
│  Trust Level: Trusted                                       │
├─────────────────────────────────────────────────────────────┤
│  ✓ Agent created: agent_01HXXXXXXXXXXXXXXXXXXXXXXXXX       │
│  ✓ Default tools registered:                                │
│    • InstallPackage                                         │
│    • CreateSymlink                                          │
│    • WriteConfig                                            │
│  ✓ Sandbox configured:                                      │
│    • Tier: bubblewrap                                       │
│    • Network: allowed                                       │
│    • Read-only home: yes                                    │
└─────────────────────────────────────────────────────────────┘
```

#### List Available Tools

```bash
$ thegent agent tools list

┌─────────────────────────────────────────────────────────────┐
│  Available Tools                                             │
├─────────────────────────────────────────────────────────────┤
│  INSTALLATION                                               │
│  • InstallPackage    Install via homebrew/nix/cargo          │
│  • DetectPM          Detect available package managers       │
│  • UpdatePackage     Update installed package                │
│                                                              │
│  CONFIGURATION                                              │
│  • CreateSymlink     Create symbolic link                    │
│  • WriteConfig       Write configuration file                │
│  • EditConfig        Edit existing configuration             │
│                                                              │
│  VERIFICATION                                               │
│  • CheckSymlink      Verify symlink exists and valid         │
│  • ValidateConfig    Validate configuration syntax           │
│  • VerifyInstall     Verify package installation            │
│                                                              │
│  SECURITY                                                   │
│  • ScanPatterns       Scan for dangerous patterns            │
│  • VerifySignature    Verify script signatures               │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Configure Agent Tools

Add specific tools to your agent:

```bash
$ thegent agent tools add dev-setup \
    --tools InstallPackage,CreateSymlink,VerifyInstall,CheckSymlink

┌─────────────────────────────────────────────────────────────┐
│  Adding Tools to Agent: dev-setup                           │
├─────────────────────────────────────────────────────────────┤
│  Tools added:                                               │
│  • InstallPackage                                          │
│  • CreateSymlink                                           │
│  • VerifyInstall                                           │
│  • CheckSymlink                                            │
├─────────────────────────────────────────────────────────────┤
│  ✓ Agent tools updated                                     │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: Configure Sandbox Settings

Customize sandbox isolation for your agent:

```bash
$ thegent agent sandbox configure dev-setup \
    --tier bubblewrap \
    --read-only-home \
    --allow-network \
    --allowed-dirs /usr/local,/opt/homebrew

┌─────────────────────────────────────────────────────────────┐
│  Configuring Sandbox for: dev-setup                         │
├─────────────────────────────────────────────────────────────┤
│  Tier: bubblewrap                                           │
│  Home directory: read-only                                  │
│  Network: allowed                                           │
│  Allowed directories:                                       │
│    • /usr/local                                             │
│    • /opt/homebrew                                          │
│    • ~/.dotfiles                                            │
├─────────────────────────────────────────────────────────────┤
│  ✓ Sandbox configuration saved                              │
└─────────────────────────────────────────────────────────────┘
```

#### View Current Sandbox Configuration

```bash
$ thegent agent sandbox show dev-setup

┌─────────────────────────────────────────────────────────────┐
│  Sandbox Configuration: dev-setup                           │
├─────────────────────────────────────────────────────────────┤
│  Tier: 1 (bubblewrap)                                      │
│                                                              │
│  Namespace Isolation:                                       │
│    ✓ User namespace                                         │
│    ✓ PID namespace                                          │
│    ✓ IPC namespace                                          │
│    ✓ Network namespace                                       │
│                                                              │
│  Mount Restrictions:                                        │
│    • Home: read-only                                        │
│    • /usr: read-only                                        │
│    • /tmp: tmpfs (writable)                                 │
│                                                              │
│  Network:                                                    │
│    • Outbound: allowed                                      │
│    • Inbound: blocked                                       │
│    • DNS: allowed                                           │
│                                                              │
│  Capabilities:                                              │
│    • CAP_SYS_ADMIN: dropped                                │
│    • CAP_NET_ADMIN: dropped                                │
│    • CAP_SYS_MODULE: dropped                               │
└─────────────────────────────────────────────────────────────┘
```

### Step 6: Define Agent Task

Create a task definition for your agent:

```bash
$ cat > ~/.thegent/tasks/dev-setup-task.yaml << 'EOF'
name: development-environment-setup
description: Set up complete development environment

steps:
  - name: install_base_packages
    tool: InstallPackage
    params:
      packages:
        - git
        - curl
        - wget
        - unzip
      package_manager: auto

  - name: install_programming
    tool: InstallPackage
    params:
      packages:
        - node
        - python@3.12
        - rust
      package_manager: auto

  - name: configure_git
    tool: WriteConfig
    params:
      path: ~/.gitconfig
      content: |
        [user]
          name = Developer
          email = dev@example.com
        [core]
          editor = vim
        [alias]
          st = status
          co = checkout
          lg = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit

  - name: verify_git_config
    tool: CheckSymlink
    params:
      path: ~/.gitconfig
      expected_target: ~/.dotfiles/gitconfig

  - name: verify_packages
    tool: VerifyInstall
    params:
      packages:
        - git
        - node
        - rust
EOF

✓ Task definition saved to ~/.thegent/tasks/dev-setup-task.yaml
```

### Step 7: Test Agent in Isolation

Run your agent with full sandbox isolation:

```bash
$ thegent agent run dev-setup --task dev-setup-task.yaml

┌─────────────────────────────────────────────────────────────┐
│  Agent Execution: dev-setup                                 │
├─────────────────────────────────────────────────────────────┤
│  Agent ID: agent_01HXXXXXXXXXXXXXXXXXXXXXXXXX              │
│  Role: Installer                                            │
│  Sandbox: Tier 1 (bubblewrap)                               │
│  Task: development-environment-setup                        │
├─────────────────────────────────────────────────────────────┤
│  [ bubblewrap ] Creating sandbox environment...            │
│  [ bubblewrap ] Sandbox ready in 12ms                       │
│  [ bubblewrap ] Network: enabled                            │
│  [ bubblewrap ] Home: read-only                             │
│                                                              │
│  EXECUTING STEPS:                                           │
│                                                              │
│  Step 1/5: install_base_packages                            │
│  [ InstallPackage ] Detecting package managers...            │
│  [ InstallPackage ] Using homebrew                           │
│  [ InstallPackage ] Installing: git, curl, wget, unzip      │
│  ✓ Installed 4 packages in 2.3s                            │
│                                                              │
│  Step 2/5: install_programming                              │
│  [ InstallPackage ] Installing: node, python@3.12, rust     │
│  ✓ Installed 3 packages in 8.1s                            │
│                                                              │
│  Step 3/5: configure_git                                   │
│  [ WriteConfig ] Writing ~/.gitconfig                       │
│  ✓ Configuration written                                    │
│                                                              │
│  Step 4/5: verify_git_config                                │
│  [ CheckSymlink ] ~/.gitconfig → ~/.dotfiles/gitconfig      │
│  ✓ Symlink verified                                         │
│                                                              │
│  Step 5/5: verify_packages                                  │
│  [ VerifyInstall ] Checking: git, node, rust                │
│  ✓ All packages verified                                    │
│                                                              │
│  [ bubblewrap ] Sandbox terminated cleanly                   │
├─────────────────────────────────────────────────────────────┤
│  ✓ EXECUTION COMPLETE                                      │
│  Duration: 10.4s (sandbox: 12ms)                           │
│  Steps completed: 5/5                                       │
│  Exit code: 0                                               │
└─────────────────────────────────────────────────────────────┘
```

### Step 8: Verify Sandbox Isolation

Confirm your agent stayed within its sandbox boundaries:

```bash
$ thegent agent audit --last 1 --verbose

┌─────────────────────────────────────────────────────────────┐
│  Execution Audit: exec_XXXX                                │
├─────────────────────────────────────────────────────────────┤
│  Agent: dev-setup                                          │
│  Duration: 10.4s                                           │
│  Sandbox: Tier 1 (bubblewrap)                              │
│  Status: Success                                            │
├─────────────────────────────────────────────────────────────┤
│  SANDBOX ENFORCEMENT:                                       │
│  ✓ Namespace isolation: enforced                            │
│  ✓ Read-only home: respected (attempted write blocked)      │
│  ✓ Network egress: 12 requests allowed                      │
│  ✓ DNS queries: 3 (package manager lookups)                │
│  ✓ File access: 47 files read, 3 files written             │
│                                                              │
│  SYSCTLS RESTRICTED:                                        │
│  • kernel.modules_disabled = 1                             │
│  • dev.tty.restricted = 1                                  │
│                                                              │
│  CAPABILITIES DROPPED:                                      │
│  • CAP_SYS_ADMIN                                           │
│  • CAP_NET_ADMIN                                           │
│  • CAP_SYS_MODULE                                          │
│                                                              │
│  FILESYSTEM OPERATIONS:                                     │
│  ✓ Read: /usr/local (allowed)                              │
│  ✓ Read: /opt/homebrew (allowed)                           │
│  ✓ Write: ~/.dotfiles (allowed)                           │
│  ✗ Write: /etc/passwd (blocked - read-only home)           │
│                                                              │
│  NETWORK OPERATIONS:                                        │
│  ✓ CONNECT: api.github.com:443 (git)                       │
│  ✓ CONNECT: Homebrew API (packages)                        │
│  ✗ CONNECT: external-script.net:80 (blocked - untrusted)   │
└─────────────────────────────────────────────────────────────┘
```

---

## Advanced: Creating a Security Auditor Agent

For more sensitive operations, create an agent with stricter sandboxing:

### Step 1: Create Agent with Tier 2

```bash
$ thegent agent create security-audit \
    --role auditor \
    --description "Security auditing agent with strict isolation" \
    --tier gvisor

┌─────────────────────────────────────────────────────────────┐
│  Creating Agent: security-audit                             │
├─────────────────────────────────────────────────────────────┤
│  Role: Auditor                                              │
│  Sandbox Tier: Tier 2 (gVisor) - userspace kernel          │
│  Trust Level: Community                                     │
├─────────────────────────────────────────────────────────────┤
│  ✓ Agent created with strict sandboxing                    │
│  ✓ Tools: ScanPatterns, VerifySignature, CheckSecurity      │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Configure for Community Scripts

```bash
$ thegent agent sandbox configure security-audit \
    --tier gvisor \
    --read-only-home \
    --allow-network \
    --network-mode filtered

┌─────────────────────────────────────────────────────────────┐
│  Sandbox Configuration: security-audit                     │
├─────────────────────────────────────────────────────────────┤
│  Tier: 2 (gVisor)                                          │
│                                                              │
│  gVisor-specific settings:                                  │
│  • Platform: ptrace (default)                               │
│  • Network: filtered (outbound only)                        │
│  • File system: 9P protocol to host                         │
│                                                              │
│  Security properties:                                       │
│  • All syscalls intercepted by Sentry                      │
│  • No direct host kernel access                             │
│  • 47 syscalls filtered, 16 denied                          │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Audit a Community Script

```bash
$ thegent agent run security-audit --script ./community-template.sh

┌─────────────────────────────────────────────────────────────┐
│  Security Audit: ./community-template.sh                    │
├─────────────────────────────────────────────────────────────┤
│  Agent: security-audit                                     │
│  Sandbox: Tier 2 (gVisor)                                  │
│  Analysis: Static pattern scan                             │
├─────────────────────────────────────────────────────────────┤
│  [ ScanPatterns ] Analyzing script...                      │
│                                                              │
│  POTENTIAL ISSUES:                                          │
│  Line 23: curl | bash detected (HIGH)                      │
│    → Remote code execution risk                             │
│  Line 45: sudo without -n (MEDIUM)                         │
│    → May prompt for password                                │
│  Line 67: eval usage (MEDIUM)                              │
│    → Code injection potential                               │
│                                                              │
│  NETWORK ACCESS:                                            │
│  • github.com (allowed - trusted)                          │
│  • raw.githubusercontent.com (allowed)                      │
│  • cdn.unknown-site.net (blocked - untrusted)              │
│                                                              │
│  RECOMMENDATION: Run with Tier 3 (Firecracker)             │
├─────────────────────────────────────────────────────────────┤
│  ✓ Audit complete                                           │
│  Risk level: MEDIUM                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Advanced: Creating an Untrusted Script Agent

For maximum isolation when running unknown scripts:

### Step 1: Create Agent with Firecracker

```bash
$ thegent agent create untrusted-runner \
    --role installer \
    --description "Run untrusted scripts in microVM isolation" \
    --tier firecracker

┌─────────────────────────────────────────────────────────────┐
│  Creating Agent: untrusted-runner                           │
├─────────────────────────────────────────────────────────────┤
│  Role: Installer                                            │
│  Sandbox Tier: Tier 3 (Firecracker microVM)                 │
│  Trust Level: Untrusted                                     │
├─────────────────────────────────────────────────────────────┤
│  ✓ Agent created with VM-level isolation                   │
│  ✓ VM config: 1 vCPU, 256MB RAM                            │
│  ✓ Network: completely disabled                            │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Test with Dangerous Script

```bash
$ thegent agent run untrusted-runner --script ~/Downloads/mystery.sh

┌─────────────────────────────────────────────────────────────┐
│  Execution: ~/Downloads/mystery.sh                         │
├─────────────────────────────────────────────────────────────┤
│  Agent: untrusted-runner                                   │
│  Sandbox: Tier 3 (Firecracker microVM)                     │
│  VM: 1 vCPU, 256MB RAM                                    │
├─────────────────────────────────────────────────────────────┤
│  [ Firecracker ] Creating microVM...                        │
│  [ Firecracker ] VM ready in 142ms                         │
│  [ Firecracker ] Boot: vmlinuz + ubuntu-base               │
│  [ Firecracker ] Network: DISABLED                          │
│                                                              │
│  EXECUTING SCRIPT:                                          │
│  --- Inside MicroVM ---                                     │
│  Script requesting sudo...                                  │
│  sudo: no tty present (failed)                             │
│  Script attempting network download...                      │
│  curl: network unreachable                                 │
│  --- Script failed (expected) ---                           │
│                                                              │
│  [ Firecracker ] Execution completed: 230ms                  │
│  [ Firecracker ] VM terminated cleanly                      │
├─────────────────────────────────────────────────────────────┤
│  ✓ HOST SYSTEM PROTECTED                                   │
│  ✓ Script could not:                                       │
│    • Escalate privileges                                    │
│    • Download additional code                               │
│    • Modify system settings                                 │
│    • Access host filesystem                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Management Commands

### List All Agents

```bash
$ thegent agent list --verbose

┌─────────────────────────────────────────────────────────────┐
│  Agent Inventory                                             │
├─────────────────────────────────────────────────────────────┤
│  NAME               │ ROLE      │ TIER │ STATUS │ CREATED  │
│─────────────────────┼───────────┼──────┼────────┼──────────│
│  dev-setup          │ Installer │ 1    │ ready  │ 2026-04-04│
│  security-audit     │ Auditor   │ 2    │ ready  │ 2026-04-04│
│  untrusted-runner    │ Installer │ 3    │ ready  │ 2026-04-04│
│  dotfiles_manager    │ Installer │ 1    │ ready  │ default  │
│  security_auditor    │ Auditor   │ 2    │ ready  │ default  │
└─────────────────────────────────────────────────────────────┘
```

### Update Agent Configuration

```bash
$ thegent agent update dev-setup \
    --description "Enhanced dev environment setup" \
    --max-iterations 20

✓ Agent updated
```

### Delete an Agent

```bash
$ thegent agent delete dev-setup

┌─────────────────────────────────────────────────────────────┐
│  Deleting Agent: dev-setup                                  │
├─────────────────────────────────────────────────────────────┤
│  This will remove:                                           │
│  • Agent definition                                         │
│  • Associated tasks                                         │
│  • Execution history                                        │
├─────────────────────────────────────────────────────────────┤
│  Type 'yes' to confirm: yes                                │
│  ✓ Agent deleted                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Agent Creation Fails

**Problem**: `Error: Role 'custom' not found`

**Solution**: Use one of the built-in roles:
```bash
thegent agent create my-agent --role installer
```

### Sandbox Configuration Rejected

**Problem**: `Error: Tier 3 requires KVM support`

**Solution**: On macOS/WSL, use Lima for VM-based sandboxes:
```bash
thegent agent create my-agent --tier gvisor  # Uses Lima on macOS
```

### Tool Not Available

**Problem**: `Error: Tool 'CustomTool' not found`

**Solution**: Use available tools:
```bash
thegent agent tools list  # See available tools
```

---

## Next Steps

Now that you've created sandboxed agents:

1. **Create Agent Teams**: Group agents for coordinated work
   ```bash
   thegent team create dev-team --agents dev-setup,security-audit
   ```

2. **Explore Multi-Agent**: Run multiple agents together
   ```bash
   thegent civilization start dev-team --goal "setup complete dev env"
   ```

3. **Automate Workflows**: Connect agents to CI/CD
   ```bash
   thegent agent run security-audit --ci-mode --report-format json
   ```

---

## Summary

In this journey, you:

1. ✅ Understood thegent agent architecture
2. ✅ Created a development setup agent with Tier 1 sandboxing
3. ✅ Configured agent tools and sandbox settings
4. ✅ Defined and ran agent tasks
5. ✅ Verified sandbox isolation was enforced
6. ✅ Created a security auditor agent with Tier 2 sandboxing
7. ✅ Created an untrusted script runner with Tier 3 (Firecracker) sandboxing

Your agents now run with appropriate isolation for their trust levels!

---

**Related Journeys**:
- [Getting Started with thegent](./journey-1-getting-started.md) - Install and configure thegent
- [Multi-Agent Collaboration](./journey-3-multi-agent.md) - Coordinate multiple agents
