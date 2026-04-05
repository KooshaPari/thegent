# Journey: Getting Started with thegent

**Duration**: ~5-10 minutes  
**Sandbox Tier**: Tier 0 (env filter) for initial setup  
**Trust Level**: Trusted  
**User**: Developer new to thegent

---

## Overview

This journey guides you through installing thegent, configuring your first dotfiles source, and running your initial agent execution. By the end, you'll have a working thegent installation with your dotfiles linked to your home directory.

## Prerequisites

- A Unix-like system (macOS, Linux, or WSL on Windows)
- Git installed
- curl or wget for downloading
- Basic familiarity with command line

---

## Step-by-Step Journey

### Step 1: Install thegent

thegent can be installed via multiple methods. Choose the one that fits your workflow:

#### Option A: Install via Homebrew (macOS/Linux)

```bash
$ brew install thegent/tap/thegent

# Verify installation
$ thegent --version
thegent v0.1.0 (rust: 1.75.0)
```

#### Option B: Install via curl (Linux/macOS)

```bash
$ curl -fsSL https://get.thegent.io/install.sh | bash

# Verify installation
$ thegent --version
thegent v0.1.0 (rust: 1.75.0)
```

#### Option C: Install from source (developers)

```bash
$ git clone https://github.com/KooshaPari/thegent.git
$ cd thegent
$ cargo install --path crates/thegent-cli

# Verify installation
$ thegent --version
thegent v0.1.0 (rust: 1.75.0, debug)
```

**Expected Output**:
```
✓ Installation complete
✓ Binary location: ~/.cargo/bin/thegent
✓ Adding to PATH...
✓ Run 'thegent --version' to verify
```

---

### Step 2: Initialize Configuration

Create your thegent configuration with sensible defaults:

```bash
$ thegent init

┌─────────────────────────────────────────────────────────────┐
│  thegent Initialization                                      │
├─────────────────────────────────────────────────────────────┤
│  Welcome to thegent!                                       │
│  Setting up your agent platform...                          │
├─────────────────────────────────────────────────────────────┤
│  ✓ Created config directory: ~/.thegent/                   │
│  ✓ Default config: ~/.thegent/config.toml                   │
│  ✓ Data directory: ~/.thegent/data/                        │
│  ✓ Logs directory: ~/.thegent/logs/                         │
├─────────────────────────────────────────────────────────────┤
│  Default settings:                                         │
│  • Role: dotfiles_manager                                  │
│  • Sandbox tier: auto (trust-based selection)               │
│  • Package managers: homebrew, nix, cargo                   │
│  • Log level: info                                         │
└─────────────────────────────────────────────────────────────┘
```

#### Review Generated Configuration

```bash
$ cat ~/.thegent/config.toml

[agent]
default_role = "dotfiles_manager"
max_iterations = 10
allow_delegation = false
verbose = false

[sandbox]
default_tier = "auto"
auto_detect_trust = true

[package_managers]
enabled = ["homebrew", "nix", "cargo"]
auto_detect = true

[logging]
level = "info"
path = "~/.thegent/logs"
```

---

### Step 3: Connect Your Dotfiles Source

thegent works with any git repository containing your dotfiles. Let's connect a sample dotfiles repo:

```bash
$ thegent dotfiles link --source https://github.com/example/dotfiles.git \
                        --target ~ \
                        --name "my-config"

┌─────────────────────────────────────────────────────────────┐
│  Connecting Dotfiles Source                                 │
├─────────────────────────────────────────────────────────────┤
│  Source: https://github.com/example/dotfiles.git           │
│  Target: /home/user                                        │
│  Name: my-config                                           │
├─────────────────────────────────────────────────────────────┤
│  ✓ Git clone complete (2.1s)                              │
│  ✓ Detected dotfiles structure:                            │
│    • .zshrc                                                │
│    • .gitconfig                                            │
│    • .vimrc                                                │
│    • Brewfile                                               │
│  ✓ Adding to tracked sources...                             │
└─────────────────────────────────────────────────────────────┘

✓ Dotfiles source "my-config" linked successfully
```

#### Alternative: Link Local Dotfiles

If your dotfiles are already on your machine:

```bash
$ thegent dotfiles link --source ~/dots/my-config \
                        --target ~ \
                        --name "local-config"

✓ Local dotfiles source "local-config" linked successfully
```

---

### Step 4: Explore thegent Commands

Get familiar with the CLI by exploring available commands:

```bash
$ thegent --help

thegent - Agent platform for dotfiles management

USAGE:
    thegent [OPTIONS] <COMMAND>

COMMANDS:
    agent       Manage and run agents
    dotfiles    Manage dotfiles sources
    execute     Run scripts in sandboxed environment
    sandbox     Manage sandbox configurations
    trust      Manage trust levels
    config     View and edit configuration
    init       Initialize thegent
    help       Print this message or help for a command

Run 'thegent <command> --help' for more information on a command
```

#### Explore Agent Commands

```bash
$ thegent agent --help

┌─────────────────────────────────────────────────────────────┐
│  Agent Commands                                              │
├─────────────────────────────────────────────────────────────┤
│  thegent agent list                                         │
│      List all available agents                              │
│                                                              │
│  thegent agent create <name> --role <role>                  │
│      Create a new agent with specified role                  │
│                                                              │
│  thegent agent run <name>                                   │
│      Run an agent                                            │
│                                                              │
│  thegent agent inspect <name>                               │
│      Show agent details and status                           │
└─────────────────────────────────────────────────────────────┘
```

#### Explore Sandbox Commands

```bash
$ thegent sandbox --help

┌─────────────────────────────────────────────────────────────┐
│  Sandbox Commands                                            │
├─────────────────────────────────────────────────────────────┤
│  thegent sandbox list-tiers                                 │
│      List available sandbox tiers                           │
│                                                              │
│  thegent sandbox test --tier <tier> --script <script>       │
│      Test a script in specified tier                        │
│                                                              │
│  thegent sandbox verify --tier <tier>                      │
│      Verify sandbox tier is available                        │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 5: List Available Agents

See what pre-built agents come with thegent:

```bash
$ thegent agent list

┌─────────────────────────────────────────────────────────────┐
│  Available Agents                                           │
├─────────────────────────────────────────────────────────────┤
│  NAME              │ ROLE               │ STATUS            │
│────────────────────┼────────────────────┼──────────────────│
│  dotfiles_manager  │ Role::Installer    │ ready            │
│  security_auditor  │ Role::Auditor      │ ready            │
│  env_verifier      │ Role::Verifier     │ ready            │
│  config_editor     │ Role::Configurator │ ready            │
└─────────────────────────────────────────────────────────────┘
```

#### Inspect a Specific Agent

```bash
$ thegent agent inspect dotfiles_manager

┌─────────────────────────────────────────────────────────────┐
│  Agent: dotfiles_manager                                    │
├─────────────────────────────────────────────────────────────┤
│  ID: agent_01HXXXXXXXXXXXXXXXXXXXXXXXXX                    │
│  Role: Installer                                            │
│  Status: ready                                              │
│  Default Tier: Tier 1 (bubblewrap)                           │
├─────────────────────────────────────────────────────────────┤
│  Capabilities:                                               │
│  • InstallPackage (homebrew, nix, cargo)                    │
│  • CreateSymlink                                            │
│  • WriteConfig                                              │
│  • DetectEnvironment                                        │
├─────────────────────────────────────────────────────────────┤
│  Configuration:                                              │
│  • max_iterations: 10                                      │
│  • allow_delegation: false                                 │
│  • verbose: false                                          │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 6: List Sandbox Tiers

Understand the sandboxing options available:

```bash
$ thegent sandbox list-tiers

┌─────────────────────────────────────────────────────────────┐
│  Sandbox Tiers                                               │
├─────────────────────────────────────────────────────────────┤
│  TIER  │ TECHNOLOGY   │ STARTUP │ SECURITY │ USE CASE        │
│────────┼──────────────┼────────┼─────────┼─────────────────│
│  0     │ EnvFilter   │ <1ms   │ None    │ Development     │
│  1     │ bubblewrap   │ ~10ms  │ Medium  │ Trusted scripts │
│  2     │ gVisor      │ ~100ms │ High    │ Community       │
│  3     │ Firecracker │ ~125ms │ Very Hi │ Untrusted       │
│  4     │ WASM        │ ~1ms   │ High    │ Plugins         │
└─────────────────────────────────────────────────────────────┘

Current platform: darwin (macOS)
Note: Tiers 1-3 run via Lima VM on macOS

To select a tier: thegent execute --tier <tier> --script <script>
```

#### Verify Tier Availability

```bash
$ thegent sandbox verify --tier bubblewrap

┌─────────────────────────────────────────────────────────────┐
│  Verifying Tier 1 (bubblewrap)                              │
├─────────────────────────────────────────────────────────────┤
│  Platform: darwin (macOS)                                   │
│  Technology: Lima VM                                         │
├─────────────────────────────────────────────────────────────┤
│  ✓ Lima installed (v0.18.0)                                │
│  ✓ bwrap available in VM                                    │
│  ✓ Network namespace: supported                             │
│  ✓ User namespace: supported                                │
└─────────────────────────────────────────────────────────────┘

✓ Tier 1 is available and ready to use
```

---

### Step 7: Run Your First Execution

Execute a simple dotfiles script in a sandbox:

```bash
$ thegent execute --tier envfilter --script 'echo "Hello from thegent!"'

┌─────────────────────────────────────────────────────────────┐
│  thegent Execution                                          │
├─────────────────────────────────────────────────────────────┤
│  Tier: 0 (envfilter) - no isolation                         │
│  Script: echo "Hello from thegent!"                        │
│  Sandbox creation: <1ms                                     │
├─────────────────────────────────────────────────────────────┤
│  Hello from thegent!                                        │
├─────────────────────────────────────────────────────────────┤
│  ✓ Execution completed in 5ms                               │
│  Exit code: 0                                               │
└─────────────────────────────────────────────────────────────┘
```

#### Try with bubblewrap (Tier 1)

```bash
$ thegent execute --tier bubblewrap --script './install.sh'

┌─────────────────────────────────────────────────────────────┐
│  thegent Execution                                          │
├─────────────────────────────────────────────────────────────┤
│  Tier: 1 (bubblewrap) - namespace isolation                 │
│  Script: ./install.sh                                       │
│  Sandbox creation: 12ms                                     │
├─────────────────────────────────────────────────────────────┤
│  ✓ Symlinking .zshrc → /home/user/dots/.zshrc              │
│  ✓ Symlinking .gitconfig → /home/user/dots/.gitconfig      │
│  ✓ Creating config directory                                │
├─────────────────────────────────────────────────────────────┤
│  ✓ Execution completed in 45ms                              │
│  Exit code: 0                                               │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 8: View Execution History

Review past executions for audit and debugging:

```bash
$ thegent audit --last 5

┌─────────────────────────────────────────────────────────────┐
│  Recent Executions (last 5)                                 │
├─────────────────────────────────────────────────────────────┤
│  ID        │ TIER │ DURATION │ STATUS │ TIME               │
│────────────┼──────┼──────────┼────────┼────────────────────│
│  exec_1234 │ 1    │ 45ms     │ ✓      │ 2026-04-04 10:30   │
│  exec_1233 │ 0    │ 5ms      │ ✓      │ 2026-04-04 10:28   │
│  exec_1232 │ 1    │ 120ms    │ ✓      │ 2026-04-04 10:15   │
│  exec_1231 │ 2    │ 350ms    │ ✓      │ 2026-04-04 09:45   │
│  exec_1230 │ 1    │ 52ms     │ ✗      │ 2026-04-04 09:30   │
└─────────────────────────────────────────────────────────────┘
```

#### Get Details on a Specific Execution

```bash
$ thegent audit inspect exec_1234

┌─────────────────────────────────────────────────────────────┐
│  Execution: exec_1234                                       │
├─────────────────────────────────────────────────────────────┤
│  Timestamp: 2026-04-04T10:30:00Z                            │
│  Tier: Tier 1 (bubblewrap)                                  │
│  Duration: 45ms                                             │
│  Status: Success                                            │
├─────────────────────────────────────────────────────────────┤
│  Script: ./install.sh                                       │
│  Working dir: /home/user/dots                               │
│  Environment vars: 23 allowed, 0 filtered                    │
├─────────────────────────────────────────────────────────────┤
│  Filesystem Operations:                                     │
│  • Symlinks created: 2                                      │
│  • Directories created: 1                                   │
│  • Files written: 0                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration Deep Dive

### Customizing Package Managers

Edit your config to specify which package managers thegent should use:

```bash
$ thegent config set package_managers.enabled '["homebrew", "nix"]'

✓ Updated package_managers.enabled
✓ Restart required for changes to take effect
```

### Setting Default Sandbox Tier

```bash
$ thegent config set sandbox.default_tier "bubblewrap"

✓ Updated sandbox.default_tier
✓ Change takes effect immediately
```

### Enabling Verbose Logging

```bash
$ thegent config set logging.level "debug"

✓ Updated logging.level
✓ Logs will be written to ~/.thegent/logs/
```

---

## Troubleshooting

### Installation Issues

**Problem**: `command not found: thegent` after installation

**Solution**: 
1. Check if the binary is in your PATH:
   ```bash
   $ which thegent
   ~/.cargo/bin/thegent
   ```

2. If not found, add to your shell config:
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

### Sandbox Issues

**Problem**: `Error: Tier 1 (bubblewrap) requires Linux`

**Solution**: 
- On macOS, bubblewrap runs inside Lima VM automatically
- Verify Lima is installed: `limactl --version`
- If not, install Lima: `brew install lima`

### Permission Issues

**Problem**: `Error: bubblewrap requires CAP_SYS_ADMIN`

**Solution**:
- thegent uses unprivileged bubblewrap where possible
- For full isolation, run on Linux or use Tier 2 (gVisor) on macOS

---

## Next Steps

Now that you have thegent installed and configured:

1. **Link Your Dotfiles**: Connect your actual dotfiles repository
   ```bash
   thegent dotfiles link --source <your-repo-url> --target ~
   ```

2. **Create Custom Agents**: Build agents for your specific workflows
   ```bash
   thegent agent create my-agent --role dotfiles_manager
   ```

3. **Explore Sandboxing**: Try running scripts in different tiers
   ```bash
   thegent execute --tier gvisor --script ./community-template.sh
   ```

4. **Read More Journeys**:
   - [Creating a Sandboxed Agent](./journey-2-sandboxed-agent.md)
   - [Multi-Agent Collaboration](./journey-3-multi-agent.md)

---

## Summary

In this journey, you:

1. ✅ Installed thegent via Homebrew or curl
2. ✅ Initialized thegent configuration
3. ✅ Connected a dotfiles source
4. ✅ Explored CLI commands
5. ✅ Listed available agents and sandbox tiers
6. ✅ Ran your first sandboxed execution
7. ✅ Reviewed execution history

Your thegent installation is ready for more advanced usage!

---

**Related Journeys**:
- [Creating a Sandboxed Agent](./journey-2-sandboxed-agent.md) - Set up custom agents with sandboxing
- [Multi-Agent Collaboration](./journey-3-multi-agent.md) - Run multiple coordinated agents
