# Journey: Multi-Agent Collaboration

**Duration**: ~15-20 minutes  
**Sandbox Tier**: Multiple (Tier 1-3 as needed)  
**Trust Level**: Mixed (trusted agents + untrusted scripts)  
**User**: Developer running coordinated multi-agent workflows

---

## Overview

This journey demonstrates how to orchestrate multiple thegent agents working together as a coordinated team. You'll create a civilization (thegent's multi-agent coordination pattern), define roles and communication, and watch agents collaborate to accomplish complex tasks.

## Prerequisites

- thegent installed (see [Getting Started](./journey-1-getting-started.md))
- At least one agent created (see [Creating a Sandboxed Agent](./journey-2-sandboxed-agent.md))
- Understanding of thegent's role system (Installer, Configurator, Verifier, Auditor)

---

## Step-by-Step Journey

### Step 1: Understand Multi-Agent Architecture

thegent uses the **Civilization Model** for multi-agent coordination:

```
┌─────────────────────────────────────────────────────────────┐
│                   CIVILIZATION                               │
│  A coordinated group of agents working toward a shared goal   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Civilization Coordinator                   │  │
│  │  • Decomposes goals into tasks                        │  │
│  │  • Manages dependencies between tasks                 │  │
│  │  • Routes artifacts between agents                    │  │
│  │  • Aggregates results                                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                  │
│  ┌─────────┬───────────────┴───────────────┬─────────┐       │
│  │         │                               │         │       │
│  ▼         ▼                               ▼         ▼       │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │
│ │Install│ │Config│ │Verify│ │Audit │ │Install│ │Config│      │
│ │Agent  │ │Agent │ │Agent │ │Agent │ │Agent │ │Agent │      │
│ │  (A)  │ │  (B) │ │  (C) │ │  (D) │ │  (E)  │ │  (F) │      │
│ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘      │
│     │         │         │         │         │         │      │
│     └─────────┴────┬────┴─────────┴─────────┴─────────┘      │
│                    │                                           │
│              ┌─────▼─────┐                                   │
│              │  ARTIFACT  │                                   │
│              │   STORE    │                                   │
│              │            │                                   │
│              │ • env_meta │                                   │
│              │ • config   │                                   │
│              │ • results  │                                   │
│              └────────────┘                                   │
└─────────────────────────────────────────────────────────────┘
```

**Key Concepts**:
- **Civilization**: The entire coordinated system
- **Coordinator**: Manages execution order and dependencies
- **Agents**: Specialized workers (Installer, Configurator, Verifier, Auditor)
- **Artifacts**: Shared data structures passed between agents
- **Roles**: Agent types with defined capabilities

### Step 2: Create a Civilization

Define a civilization for your multi-agent workflow:

```bash
$ thegent civilization create dev-env-setup \
    --goal "Set up complete development environment" \
    --agents installer@dev-setup,configurator@default,verifier@default,auditor@security-audit

┌─────────────────────────────────────────────────────────────┐
│  Creating Civilization: dev-env-setup                       │
├─────────────────────────────────────────────────────────────┤
│  Goal: Set up complete development environment             │
│                                                              │
│  Agents:                                                     │
│  • installer@dev-setup (Tier 1)                           │
│  • configurator@default (Tier 1)                           │
│  • verifier@default (Tier 1)                                │
│  • auditor@security-audit (Tier 2)                         │
├─────────────────────────────────────────────────────────────┤
│  ✓ Civilization created: civ_01HXXXXXXXXXXXXXXXXXX        │
│  ✓ Dependency graph initialized                             │
│  ✓ Artifact store ready                                     │
└─────────────────────────────────────────────────────────────┘
```

#### View Civilization Details

```bash
$ thegent civilization inspect dev-env-setup

┌─────────────────────────────────────────────────────────────┐
│  Civilization: dev-env-setup                               │
├─────────────────────────────────────────────────────────────┤
│  ID: civ_01HXXXXXXXXXXXXXXXXXX                             │
│  Goal: Set up complete development environment             │
│  Status: initialized                                       │
├─────────────────────────────────────────────────────────────┤
│  AGENTS:                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Role           │ Agent          │ Tier │ Status      │   │
│  ├────────────────┼────────────────┼──────┼─────────────┤   │
│  │ Installer      │ dev-setup      │  1   │ ready       │   │
│  │ Configurator   │ default        │  1   │ ready       │   │
│  │ Verifier       │ default        │  1   │ ready       │   │
│  │ Auditor        │ security-audit │  2   │ ready       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  COORDINATION:                                               │
│  • Dependency resolution: enabled                           │
│  • Parallel execution: enabled                             │
│  • Fault tolerance: continue on agent failure              │
│                                                              │
│  ARTIFACTS:                                                 │
│  • env_metadata (shared)                                  │
│  • package_list (Installer → Configurator)                 │
│  • config_delta (Configurator → Verifier)                  │
│  • audit_report (Auditor → Coordinator)                     │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Define Civilization Workflow

Create a workflow that coordinates your agents:

```bash
$ cat > ~/.thegent/workflows/dev-env-workflow.yaml << 'EOF'
name: complete-development-environment
description: Install tools, configure dotfiles, verify, audit

# Execution plan with dependencies
execution_plan:
  # Phase 1: Installation (can run in parallel for different package types)
  - phase: install
    agents:
      - role: Installer
        name: dev-setup
        task: install_base_packages
    outputs:
      - artifact: package_inventory
        type: PackageList

  # Phase 2: Configuration (depends on installation)
  - phase: configure
    depends_on: [install]
    agents:
      - role: Configurator
        name: default
        task: configure_dotfiles
    inputs:
      - artifact: package_inventory
        from_phase: install
    outputs:
      - artifact: config_report
        type: ConfigDelta

  # Phase 3: Verification (depends on configuration)
  - phase: verify
    depends_on: [configure]
    agents:
      - role: Verifier
        name: default
        task: verify_installation
    inputs:
      - artifact: config_report
        from_phase: configure
    outputs:
      - artifact: verify_results
        type: VerificationReport

  # Phase 4: Security Audit (parallel with verification)
  - phase: audit
    depends_on: [install]
    agents:
      - role: Auditor
        name: security-audit
        task: security_scan
    outputs:
      - artifact: audit_report
        type: SecurityReport

  # Phase 5: Final Aggregation
  - phase: aggregate
    depends_on: [verify, audit]
    agents:
      - role: Coordinator
        task: aggregate_results
EOF

✓ Workflow saved to ~/.thegent/workflows/dev-env-workflow.yaml
```

### Step 4: Execute the Civilization

Run your multi-agent workflow:

```bash
$ thegent civilization execute dev-env-setup --workflow dev-env-workflow.yaml

┌─────────────────────────────────────────────────────────────┐
│  CIVILIZATION EXECUTION                                     │
│  Civilization: dev-env-setup                                │
│  Workflow: complete-development-environment                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [COORDINATOR] Starting civilization...                      │
│  [COORDINATOR] Goal: Set up complete development env      │
│  [COORDINATOR] Analyzing dependencies...                    │
│  [COORDINATOR] 4 agents, 2 phases can run in parallel      │
│                                                              │
│  ═══════════════════════════════════════════════════════════ │
│  PHASE 1: install (parallel)                                │
│  ═══════════════════════════════════════════════════════════ │
│                                                              │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │ Agent: dev-setup   │    │ Agent: dev-setup    │        │
│  │ Role: Installer    │    │ Role: Installer     │        │
│  │ Task: dev-tools    │    │ Task: lang-tools    │        │
│  │ Tier: bubblewrap   │    │ Tier: bubblewrap   │        │
│  └─────────────────────┘    └─────────────────────┘        │
│                                                              │
│  [Installer-A] Installing: git, curl, wget, unzip          │
│  [Installer-B] Installing: node, python@3.12, rust          │
│                                                              │
│  [Installer-A] ✓ Installed: git 2.42, curl 8.4, wget 1.21  │
│  [Installer-B] ✓ Installed: node 20.9, python 3.12.1       │
│                                                              │
│  [COORDINATOR] Phase 1 complete. Moving to Phase 2...      │
│                                                              │
│  ═══════════════════════════════════════════════════════════ │
│  PHASE 2: configure + audit (parallel)                      │
│  ═══════════════════════════════════════════════════════════ │
│                                                              │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │ Agent: default     │    │ Agent: security-    │        │
│  │ Role: Configurator │    │ Role: Auditor       │        │
│  │ Tier: bubblewrap   │    │ Tier: gVisor        │        │
│  └─────────────────────┘    └─────────────────────┘        │
│                                                              │
│  [Configurator] Reading package_inventory...                 │
│  [Configurator] Creating symlinks...                         │
│  [Configurator] ✓ .zshrc linked                             │
│  [Configurator] ✓ .gitconfig linked                         │
│  [Configurator] ✓ .vimrc linked                            │
│                                                              │
│  [Auditor] Scanning installed artifacts...                   │
│  [Auditor] Checking for security patterns...                │
│  [Auditor] ✓ No dangerous patterns detected                 │
│                                                              │
│  [COORDINATOR] Phase 2 complete. Moving to Phase 3...      │
│                                                              │
│  ═══════════════════════════════════════════════════════════ │
│  PHASE 3: verify                                           │
│  ═══════════════════════════════════════════════════════════ │
│                                                              │
│  ┌─────────────────────┐                                    │
│  │ Agent: default     │                                    │
│  │ Role: Verifier     │                                    │
│  │ Tier: bubblewrap   │                                    │
│  └─────────────────────┘                                    │
│                                                              │
│  [Verifier] Verifying installation...                        │
│  [Verifier] ✓ git: installed and executable                │
│  [Verifier] ✓ node: installed and executable               │
│  [Verifier] ✓ rust: installed and executable               │
│  [Verifier] ✓ Symlinks: all valid                         │
│  [Verifier] ✓ Config files: readable                       │
│                                                              │
│  [COORDINATOR] All phases complete. Aggregating results...  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  ✓ CIVILIZATION COMPLETE                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESULTS:                                                   │
│  • Installation: SUCCESS (packages installed)                │
│  • Configuration: SUCCESS (symlinks created)                │
│  • Verification: SUCCESS (all checks passed)                 │
│  • Audit: SUCCESS (no security issues)                      │
│                                                              │
│  ARTIFACTS PRODUCED:                                        │
│  • package_inventory (5 packages)                          │
│  • config_report (3 symlinks)                              │
│  • verify_results (5 checks passed)                         │
│  • audit_report (0 issues)                                 │
│                                                              │
│  TIMING:                                                    │
│  • Total wall time: 12.3s                                  │
│  • Parallel speedup: 2.1x (vs sequential)                  │
│  • Coordination overhead: 45ms                              │
│                                                              │
│  AGENTS:                                                    │
│  • installer: 2x ran in parallel                           │
│  • configurator: 1x                                       │
│  • verifier: 1x                                            │
│  • auditor: 1x (parallel with configurator)                │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: Review Artifact Flow

See how data moved between agents:

```bash
$ thegent civilization artifacts dev-env-setup --last-run

┌─────────────────────────────────────────────────────────────┐
│  Artifact Flow: dev-env-setup                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ARTIFACT 1: package_inventory                              │
│  Produced by: Installer (dev-setup)                          │
│  Consumed by: Configurator (default)                        │
│  Data:                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ packages:                                            │   │
│  │   - name: git      version: 2.42.0                  │   │
│  │   - name: curl     version: 8.4.0                   │   │
│  │   - name: wget     version: 1.21.0                   │   │
│  │   - name: node     version: 20.9.0                   │   │
│  │   - name: python   version: 3.12.1                   │   │
│  │   - name: rust     version: 1.75.0                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ARTIFACT 2: config_report                                  │
│  Produced by: Configurator (default)                        │
│  Consumed by: Verifier (default)                            │
│  Data:                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ symlinks_created:                                    │   │
│  │   - ~/.zshrc → ~/.dotfiles/zshrc                   │   │
│  │   - ~/.gitconfig → ~/.dotfiles/gitconfig           │   │
│  │   - ~/.vimrc → ~/.dotfiles/vimrc                   │   │
│  │                                                       │   │
│  │ files_written:                                       │   │
│  │   - ~/.config/thegent/agent.json                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ARTIFACT 3: verify_results                                 │
│  Produced by: Verifier (default)                            │
│  Data:                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ checks:                                              │   │
│  │   - name: git_installed    status: PASS            │   │
│  │   - name: node_installed   status: PASS            │   │
│  │   - name: rust_installed   status: PASS            │   │
│  │   - name: symlinks_valid   status: PASS            │   │
│  │   - name: configs_readable status: PASS            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ARTIFACT 4: audit_report                                   │
│  Produced by: Auditor (security-audit)                      │
│  Data:                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ issues_found: []                                    │   │
│  │ risk_level: LOW                                     │   │
│  │ scan_duration: 234ms                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 6: Handle Agent Failure

Test how the civilization handles an agent failure:

```bash
$ thegent civilization execute dev-env-setup \
    --workflow dev-env-workflow.yaml \
    --inject-failure installer:mid-execution

┌─────────────────────────────────────────────────────────────┐
│  CIVILIZATION EXECUTION (with failure injection)            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [COORDINATOR] Starting civilization...                      │
│  [COORDINATOR] ⚠ Failure injection enabled for Installer    │
│                                                              │
│  [Installer] Installing: git, curl, wget...                 │
│  [Installer] ✓ git installed                                │
│  [Installer] ✓ curl installed                               │
│  [INJECTED FAILURE] Simulating crash...                     │
│                                                              │
│  ═══════════════════════════════════════════════════════════ │
│  FAILURE HANDLING                                           │
│  ═══════════════════════════════════════════════════════════ │
│                                                              │
│  [COORDINATOR] Agent failure detected: Installer crashed     │
│  [COORDINATOR] Evaluating fault tolerance policy...          │
│                                                              │
│  Policy: continue-on-agent-failure                          │
│  Continuing with available agents...                         │
│                                                              │
│  [COORDINATOR] Re-running installation with backup agent    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Backup Agent: default                                │   │
│  │ Role: Installer (fallback)                          │   │
│  │ Tier: bubblewrap                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  [Installer-Backup] Attempting installation...              │
│  [Installer-Backup] ✓ git installed (retry)                 │
│  [Installer-Backup] ✓ curl installed (retry)                │
│  [Installer-Backup] ✓ wget installed (retry)                │
│  [Installer-Backup] ✓ All packages recovered                │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  ✓ CIVILIZATION COMPLETE (with recovery)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  EXECUTION NOTES:                                            │
│  • Primary installer failed at step 2/5                     │
│  • Backup installer recovered successfully                  │
│  • Total time impact: +3.2s (recovery overhead)             │
│  • No data loss: artifacts preserved                        │
│                                                              │
│  FAILURE SUMMARY:                                           │
│  • Agents affected: 1/4                                    │
│  • Phases affected: 1/4                                    │
│  • Recovery: SUCCESSFUL                                     │
│  • Final status: SUCCESS (with recovery)                    │
└─────────────────────────────────────────────────────────────┘
```

### Step 7: Monitor Real-Time Execution

Watch agent execution as it happens:

```bash
$ thegent civilization watch dev-env-setup --workflow dev-env-workflow.yaml

┌─────────────────────────────────────────────────────────────┐
│  REAL-TIME CIVILIZATION MONITOR                             │
│  Civilization: dev-env-setup                                │
│  Started: 2026-04-04T15:30:00Z                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PHASE 1: install ████████████████████ 100%                 │
│  ├─ Installer-A (dev-setup)     ████████████ 100% ✓        │
│  └─ Installer-B (dev-setup)     ████████████ 100% ✓        │
│                                                              │
│  PHASE 2: configure + audit                                 │
│  ├─ Configurator (default)      ████████░░░░░░ 60% ⟳       │
│  └─ Auditor (security-audit)   ████████████ 100% ✓        │
│                                                              │
│  PHASE 3: verify (pending)                                 │
│                                                              │
│  AGENT STATUS:                                              │
│  • dev-setup (Installer): COMPLETED                         │
│  • default (Configurator): RUNNING (60%)                   │
│  • default (Verifier): PENDING                              │
│  • security-audit (Auditor): COMPLETED                     │
│                                                              │
│  ARTIFACTS:                                                 │
│  • package_inventory: READY (2 producers, 1 consumer)      │
│  • config_report: IN_PROGRESS (0/1 producers)              │
│  • audit_report: READY (1 producer, 0 consumers)           │
│                                                              │
│  RESOURCES:                                                 │
│  • CPU: 45% (2 cores active)                               │
│  • Memory: +120MB (sandboxes)                              │
│  • Network: 3 requests (allowed)                          │
│                                                              │
│  LOGS (last 5):                                            │
│  15:30:12 [Configurator] Creating symlink: ~/.zshrc        │
│  15:30:11 [Configurator] Reading package_inventory         │
│  15:30:10 [Installer-B] ✓ node 20.9 installed              │
│  15:30:09 [Installer-B] Installing node...                  │
│  15:30:08 [Installer-A] ✓ git 2.42 installed               │
│                                                              │
│  Press Ctrl+C to stop watching...                           │
```

---

## Advanced: Custom Coordination Logic

### Define Custom Artifact Types

```bash
$ cat > ~/.thegent/artifacts/DevelopmentEnvironment.yaml << 'EOF'
name: DevelopmentEnvironment
description: Complete development environment state

fields:
  - name: package_manager
    type: PackageManager
    required: true
    
  - name: installed_packages
    type: List[Package]
    required: true
    
  - name: symlinks
    type: Map[Path, Path]
    required: false
    
  - name: environment_vars
    type: Map[String, String]
    required: false
    
  - name: verification_status
    type: VerificationStatus
    required: true
EOF

✓ Artifact type registered
```

### Create Custom Coordinator

```rust
// In crates/civilization/src/coordinators/custom.rs

pub struct DevEnvCoordinator;

impl CivilizationCoordinator for DevEnvCoordinator {
    fn decompose(&self, goal: &str) -> Vec<AgentTask> {
        match goal {
            "Set up complete development environment" => vec![
                AgentTask {
                    id: "detect-env",
                    role: Role::Verifier,
                    tool: DetectEnvironment,
                    parallel: false,
                },
                AgentTask {
                    id: "install-base",
                    role: Role::Installer,
                    tool: InstallPackage,
                    parallel: true,
                    depends_on: vec!["detect-env"],
                },
                AgentTask {
                    id: "install-dev",
                    role: Role::Installer,
                    tool: InstallPackage,
                    parallel: true,
                    depends_on: vec!["detect-env"],
                },
                AgentTask {
                    id: "configure",
                    role: Role::Configurator,
                    tool: WriteConfig,
                    parallel: false,
                    depends_on: vec!["install-base", "install-dev"],
                },
            ],
            _ => vec![],  // Fallback to default
        }
    }
}
```

---

## Multi-Agent Patterns

### Pattern 1: Fan-Out, Fan-In

```
                    ┌─────────────┐
                    │ Coordinator │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │Installer │    │Installer │    │Installer │
    │   (A)    │    │   (B)    │    │   (C)    │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                  ┌─────────────┐
                  │Configurator │
                  └─────────────┘
```

Use for: Installing packages in parallel, then configuring once complete.

### Pattern 2: Pipeline

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Install  │──►│ Configure│──►│ Verify   │──►│  Audit   │
│  Agent   │   │  Agent   │   │  Agent   │   │  Agent   │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

Use for: Strict sequential dependencies where each phase must complete.

### Pattern 3: Ring

```
       ┌──────────────────────────────────────┐
       │                                      │
       ▼                                      │
┌──────────┐   ┌──────────┐   ┌──────────┐   │
│ Install  │──►│ Configure│──►│ Verify   │◄──┘
│  Agent   │   │  Agent   │   │  Agent   │
└──────────┘   └──────────┘   └──────────┘
       ▲              │
       │              │
       └──────────────┘
```

Use for: Iterative refinement where agents refine each other's outputs.

---

## Civilizations CLI Reference

### Create a Civilization

```bash
thegent civilization create <name> \
    --goal <goal> \
    --agents <agent1,agent2,...>
```

### List Civilizations

```bash
thegent civilization list
```

### Execute a Civilization

```bash
thegent civilization execute <name> \
    --workflow <workflow-file>
```

### Watch Execution

```bash
thegent civilization watch <name>
```

### Get Artifact Flow

```bash
thegent civilization artifacts <name> --last-run
```

### Stop a Civilization

```bash
thegent civilization stop <name>
```

### Delete a Civilization

```bash
thegent civilization delete <name>
```

---

## Troubleshooting

### Agents Not Communicating

**Problem**: Artifacts not flowing between agents

**Solution**:
1. Verify artifact types match between producer and consumer
2. Check that consumers are registered for the artifact
3. Ensure dependency graph is correct

```bash
thegent civilization debug dev-env-setup --check-artifacts
```

### Deadlock Detected

**Problem**: Civilization hangs with circular dependency

**Solution**:
```bash
thegent civilization debug dev-env-setup --check-dependencies

# Fix circular dependency in workflow YAML
# Example:
# BAD: A depends on B, B depends on A
# GOOD: A depends on B, B depends on C
```

### Resource Exhaustion

**Problem**: Too many agents running, system slows down

**Solution**:
```bash
# Set concurrency limits
thegent civilization config dev-env-setup \
    --max-parallel-agents 4 \
    --max-total-agents 8
```

---

## Next Steps

Now that you've run multi-agent collaboration:

1. **Persist Civilizations**: Save civilization definitions for reuse
   ```bash
   thegent civilization save dev-env-setup
   ```

2. **Schedule Civilizations**: Run on a schedule
   ```bash
   thegent civilization schedule dev-env-setup --cron "0 9 * * *"
   ```

3. **Connect to CI/CD**: Use in continuous integration
   ```bash
   thegent civilization execute dev-env-setup --ci-mode --report json
   ```

4. **Scale Horizontally**: Run civilizations across multiple machines
   ```bash
   thegent civilization distribute dev-env-setup --workers 4
   ```

---

## Summary

In this journey, you:

1. ✅ Understood the Civilization Model architecture
2. ✅ Created a civilization with 4 coordinated agents
3. ✅ Defined a multi-phase workflow with dependencies
4. ✅ Executed the civilization and observed parallel execution
5. ✅ Traced artifact flow between agents
6. ✅ Tested fault tolerance with failure injection
7. ✅ Monitored real-time execution
8. ✅ Explored multi-agent patterns (fan-out, pipeline, ring)

Multi-agent collaboration enables complex workflows that would be difficult or slow with single-agent approaches!

---

**Related Journeys**:
- [Getting Started with thegent](./journey-1-getting-started.md) - Install and configure thegent
- [Creating a Sandboxed Agent](./journey-2-sandboxed-agent.md) - Build custom agents
