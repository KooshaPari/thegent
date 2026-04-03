# SPECIFICATION: thegent Agent Platform

**Version**: 1.0  
**Date**: 2026-04-02  
**Status**: Draft  
**Author**: Agent  

---

## 1. Executive Summary

thegent is an agent platform for managing development environments and executing tasks across diverse platforms. It combines role-based agent orchestration with tiered sandboxing for secure, scalable automation.

**Key Differentiators**:
- Role-based agent model (inspired by CrewAI patterns)
- 4-tier sandboxing (bubblewrap to Firecracker)
- Multi-platform support (macOS, Linux, WSL)
- Rust-based performance

**Target Use Cases**:
- Dotfiles management across machines
- Environment configuration automation
- Secure execution of untrusted scripts
- Multi-tenant development environments

---

## 2. SOTA Landscape Analysis

### 2.1 Agent Frameworks

| Framework | Approach | thegent Position |
|-----------|----------|------------------|
| CrewAI | Role-based | Adopt patterns, custom impl |
| LangGraph | State machines | Control flow inspiration |
| AutoGPT | Autonomous | Too risky for infrastructure |
| AutoGen | Conversational | Less relevant for automation |

### 2.2 Sandboxing Technologies

| Tier | Technology | Startup | Overhead | Use Case |
|------|------------|---------|----------|----------|
| 1 | bubblewrap | ~10ms | +5MB | Trusted scripts |
| 2 | gVisor | ~100ms | +50MB | Community templates |
| 3 | Firecracker | ~125ms | +5MB | Maximum isolation |
| 4 | WASM | ~1ms | +1MB | Plugins |

---

## 3. Architecture

### 3.1 System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    thegent Platform                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────────┐│
│  │                 Agent Orchestrator                    ││
│  │  • Role assignment                                  ││
│  │  • Task planning                                    ││
│  │  • State machine execution                          ││
│  │  • Multi-agent coordination                         ││
│  └─────────────────────────────────────────────────────┘│
│                          │                               │
│  ┌───────────────────────▼─────────────────────────────┐│
│  │                  Agent Runtime                      ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  ││
│  │  │ Agent A │ │ Agent B │ │ Agent C │ │ Agent D │  ││
│  │  │(Install)│ │(Config) │ │(Verify) │ │(Report)│  ││
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  ││
│  │       │            │            │            │      ││
│  │       └────────────┴────────────┴────────────┘      ││
│  │                   Coordination                      ││
│  └───────────────────────┬─────────────────────────────┘│
│                          │                               │
│  ┌───────────────────────▼─────────────────────────────┐│
│  │              Sandboxing Layer                       ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  ││
│  │  │  Tier 1 │ │  Tier 2 │ │  Tier 3 │ │   WASM  │  ││
│  │  │(bwrap)  │ │(gVisor) │ │(Firecr.)│ │(Plugin) │  ││
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  ││
│  └─────────────────────────────────────────────────────┘│
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Agent Definition

```rust
pub struct Agent {
    pub id: String,
    pub role: Role,
    pub goal: String,
    pub backstory: String,
    pub tools: Vec<Box<dyn Tool>>,
    pub llm: Option<Box<dyn LLM>>,
    pub config: AgentConfig,
}

pub struct Role {
    pub name: String,
    pub description: String,
    pub allowed_sandbox_tier: SandboxTier,
}

pub struct AgentConfig {
    pub max_iterations: u32,
    pub allow_delegation: bool,
    pub verbose: bool,
    pub temperature: f32,
}

pub trait Tool: Send + Sync {
    fn name(&self) -> &str;
    fn description(&self) -> &str;
    fn execute(&self, input: ToolInput) -> BoxFuture<Result<ToolOutput>>;
}
```

### 3.3 Task Orchestration

```rust
pub struct Task {
    pub id: String,
    pub description: String,
    pub expected_output: String,
    pub agent_id: String,
    pub tools: Vec<String>,
    pub context: HashMap<String, Value>,
    pub dependencies: Vec<String>,
    pub status: TaskStatus,
}

pub enum TaskStatus {
    Pending,
    InProgress { step: usize, total: usize },
    AwaitingInput { prompt: String },
    Completed { output: TaskOutput },
    Failed { error: Error },
}

pub struct TaskGraph {
    pub tasks: Vec<Task>,
    pub edges: Vec<(String, String)>, // (from, to)
    pub execution_order: Vec<String>,
}

impl TaskGraph {
    pub fn topological_sort(&self) -> Result<Vec<String>> {
        // Topological sort for dependency resolution
    }
}
```

---

## 4. Sandboxing

### 4.1 Tier Selection Logic

```rust
pub fn select_tier(trust_level: TrustLevel, requirements: &Requirements) -> SandboxTier {
    match trust_level {
        TrustLevel::Trusted if !requirements.needs_network => {
            SandboxTier::Bubblewrap
        }
        TrustLevel::Community => SandboxTier::GVisor,
        TrustLevel::Untrusted => SandboxTier::Firecracker,
        TrustLevel::Plugin => SandboxTier::WASM,
    }
}
```

### 4.2 Tier 1: bubblewrap

```rust
pub struct BubblewrapSandbox {
    read_only_dirs: Vec<PathBuf>,
    writable_dirs: Vec<PathBuf>,
    tmpfs_dirs: Vec<PathBuf>,
    unshare_user: bool,
    unshare_ipc: bool,
    unshare_pid: bool,
    unshare_net: bool,
}

impl Sandbox for BubblewrapSandbox {
    fn execute(&self, command: &str) -> Result<Output> {
        let mut cmd = Command::new("bwrap");
        
        for dir in &self.read_only_dirs {
            cmd.arg("--ro-bind").arg(dir).arg(dir);
        }
        
        for dir in &self.writable_dirs {
            cmd.arg("--bind").arg(dir).arg(dir);
        }
        
        for dir in &self.tmpfs_dirs {
            cmd.arg("--tmpfs").arg(dir);
        }
        
        if self.unshare_user { cmd.arg("--unshare-user"); }
        if self.unshare_ipc { cmd.arg("--unshare-ipc"); }
        if self.unshare_pid { cmd.arg("--unshare-pid"); }
        if self.unshare_net { cmd.arg("--unshare-net"); }
        
        cmd.arg("--die-with-parent");
        cmd.arg("/bin/sh").arg("-c").arg(command);
        
        Ok(cmd.output()?)
    }
}
```

### 4.3 Tier 2: gVisor

```rust
pub struct GVisorSandbox {
    container_image: String,
    network: bool,
    privileged: bool,
    runsc_path: PathBuf,
}

impl Sandbox for GVisorSandbox {
    fn execute(&self, command: &str) -> Result<Output> {
        // Uses runsc (gVisor OCI runtime)
        let mut docker = Command::new("docker");
        docker.arg("run")
            .arg("--runtime=runsc")
            .arg("--rm")
            .arg(&self.container_image)
            .arg("/bin/sh")
            .arg("-c")
            .arg(command);
        
        if !self.network {
            docker.arg("--network=none");
        }
        
        Ok(docker.output()?)
    }
}
```

### 4.4 Tier 3: Firecracker

```rust
pub struct FirecrackerSandbox {
    vm_config: VMConfig,
    rootfs: PathBuf,
    kernel: PathBuf,
    firecracker_bin: PathBuf,
}

pub struct VMConfig {
    vcpus: u8,
    memory_mb: u32,
    network: bool,
}

impl Sandbox for FirecrackerSandbox {
    fn execute(&self, command: &str) -> Result<Output> {
        // 1. Create microVM via Firecracker API
        // 2. Copy script into VM
        // 3. Execute
        // 4. Return output
        todo!()
    }
}
```

---

## 5. API

### 5.1 CLI Interface

```bash
# Create and run agent
thegent agent create --name "installer" --role "dotfiles_manager"
thegent agent run installer --task "install-packages.yml"

# Execute with specific tier
thegent execute --tier gvisor --script "./setup.sh"

# List agents
thegent agent list
thegent agent inspect installer

# Sandbox management
thegent sandbox list-tiers
thegent sandbox test --tier firecracker --script "test.sh"

# Multi-tenant operations
thegent tenant create --name "team-a"
thegent tenant switch team-a
```

### 5.2 Configuration

```toml
[agent.default]
role = "general"
max_iterations = 10
allow_delegation = true
temperature = 0.7

[sandbox.default]
tier = "bubblewrap"
unshare_all = true
read_only_home = true

[sandbox.tiers.bubblewrap]
unshare_user = true
unshare_ipc = true
unshare_pid = true
unshare_net = true

[sandbox.tiers.gvisor]
runtime = "runsc"
network = false
privileged = false

[sandbox.tiers.firecracker]
vcpus = 2
memory_mb = 512
network = false
```

---

## 6. Performance Targets

| Operation | Target Latency |
|-----------|----------------|
| Agent startup | <100ms |
| Task execution (Tier 1) | <10ms overhead |
| Task execution (Tier 2) | <100ms overhead |
| Task execution (Tier 3) | <200ms overhead |
| Agent coordination | <50ms |
| Sandbox creation (Tier 1) | <50ms |
| Sandbox creation (Tier 2) | <500ms |
| Sandbox creation (Tier 3) | <1000ms |

---

## 7. Security Model

### 7.1 Threat Model

| Threat | Mitigation |
|--------|------------|
| Malicious script | Sandboxing tier selection |
| Container escape | gVisor/Firecracker (userspace kernel) |
| Privilege escalation | Unprivileged namespaces |
| Network exfiltration | Network namespace isolation |
| Resource exhaustion | cgroups limits |

### 7.2 Trust Levels

| Level | Criteria | Default Tier |
|-------|----------|--------------|
| Trusted | User-owned, signed | Tier 1 |
| Community | GitHub stars >100 | Tier 2 |
| Untrusted | Unknown source | Tier 3 |
| Plugin | WASM verified | Tier 4 |

---

## 8. References

### Internal
- ADR-001: Agent Framework Architecture
- ADR-002: Sandboxing Tier Strategy
- ADR-003: Multi-Tenant Architecture
- SOTA Research: `docs/research/AGENT_FRAMEWORKS_SOTA.md`
- SOTA Research: `docs/research/SANDBOXING_TECHNOLOGIES_SOTA.md`

### External
- CrewAI: https://github.com/crewAIInc/crewAI
- gVisor: https://gvisor.dev/
- Firecracker: https://firecracker-microvm.github.io/
- bubblewrap: https://github.com/containers/bubblewrap

---

## 9. Roadmap

### Phase 1: Core (4 weeks)
- Agent framework implementation
- Tier 1 (bubblewrap) sandboxing
- Basic CLI

### Phase 2: Expansion (4 weeks)
- Tier 2 (gVisor) integration
- Task orchestration
- Configuration system

### Phase 3: Scale (4 weeks)
- Tier 3 (Firecracker) support
- Multi-tenancy
- WASM plugins

---

*This SPEC will be updated as development progresses*
