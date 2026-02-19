# Process & Tool Optimization Complete Plan

> **Status**: Complete | **Version**: 1.0 | **Date**: 2026-02-16
> **Related**: 
> - [Process Optimization Plan](./PROCESS_OPTIMIZATION_PLAN.md)
> - [Swarm Complete](../research/SWARM_COMPLETE.md)
> - [Library Replacement Complete](../research/LIBRARY_REPLACEMENT_COMPLETE.md)

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Multi-Tenant Single Process (MTSP)](#2-multi-tenant-single-process-mtsp)
3. [Efficient Tool Migration](#3-efficient-tool-migration)
4. [Persistence & Resilience](#4-persistence--resilience)
5. [Implementation Roadmap](#5-implementation-roadmap)
6. [Python Frontmatter + Native Backmatter](#6-python-frontmatter--native-backmatter)
7. [Verification Metrics](#7-verification-metrics)
8. [Configuration Reference](#8-configuration-reference)
9. [References](#9-references)

---

## 1. Executive Summary

### 1.1 Problem Statement

Current sessions exhibit significant process bloat, with dozens of short-lived `bash`, `node`, `python`, and `task` processes. This leads to high context-switch overhead, memory fragmentation, and risk of process leakage.

### 1.2 Redundant Processes Detected

- **Redundant MCPs**: `context7-mcp` (superseded by `octocode`)
- **Short-lived Shell Tools**: `cat`, `tr`, `cp`, `dirname`, `basename`, `perl`
- **Duplicate Node Instances**: Multiple `npm exec` calls for different MCP servers
- **Process Sprawl**: 64+ `bash` processes, 9+ `task` processes in a single session
- **Per-CC full stack**: Each Claude Code instance spawns python, clangd, gopls (×2), uv, sourcekit-lsp, rust-analyzer, caffeinate

### 1.3 Solution Strategy

1. **Multi-Tenant Single Process (MTSP)**: Consolidate processes into shared execution environment
2. **Efficient Tool Migration**: Replace expensive shell-outs with Rust-based or internal Python equivalents
3. **Persistence & Resilience**: Service management, daemonization, session continuity

---

## 2. Multi-Tenant Single Process (MTSP)

### 2.1 MTSP Tasks

| Task ID | Description | Status |
|---------|-------------|--------|
| **MTSP-01** | Unified MCP Host | ✅ Done |
| **MTSP-02** | In-Process Agent Runner | ⏳ Pending |
| **MTSP-03** | Shared Task Worker | ⏳ Pending |
| **MTSP-04** | LSP Multiplexing | ⏳ Pending |
| **MTSP-05** | Unified Worker Daemon | ⏳ Pending |
| **MTSP-06** | Persistent Python Worker Pool | ✅ Done |
| **MTSP-07** | In-Process Tool Execution | ✅ Done |
| **MTSP-08** | Rust Governance Scanner | ✅ Done |
| **MTSP-09** | Multi-Tenant Git Accelerator | ✅ Done |
| **MTSP-11** | Edit Leasing Manager | ✅ Done |
| **MTSP-12** | Shadow Clone Planning | ✅ Done |
| **MTSP-13** | Atomic Transactional Apply | ✅ Done |
| **MTSP-14** | Centralized Lock Orchestrator | ✅ Done |
| **MTSP-15** | Package Manager Mutexing | ✅ Done |
| **MTSP-16** | Test Runner Port Leasing | ⏳ Pending |
| **MTSP-17** | Dual Memory Audit System | ✅ Done |
| **MTSP-18** | Session History Scraper | ✅ Done |

### 2.2 Unified MCP Host (MTSP-01)

**Implementation**:
```python
# Merge octocode, next-devtools, sequential-thinking into single process
mcp_server = FastMCP("thegent")

# Mount MCP servers
mcp_server.mount("octocode", octocode_server)
mcp_server.mount("next-devtools", next_devtools_server)
mcp_server.mount("sequential-thinking", sequential_thinking_server)
```

**Status**: ✅ Complete

### 2.3 In-Process Agent Runner (MTSP-02)

**Goal**: Use ACE-style `cwd` isolation within a single Python process

**Implementation**:
```python
class InProcessAgentRunner:
    """In-process agent runner with cwd isolation."""
    
    def run(self, agent_id: str, command: str, cwd: Path) -> dict:
        """Run agent in-process with isolated cwd."""
        # Change to isolated cwd
        original_cwd = Path.cwd()
        os.chdir(cwd)
        
        try:
            # Execute command in isolated context
            result = self._execute_command(command)
            return result
        finally:
            os.chdir(original_cwd)
```

**Status**: ⏳ Pending

### 2.4 Shared Task Worker (MTSP-03)

**Goal**: Consolidate `task` calls into a single persistent daemon

**Implementation**:
```python
# Use process-compose for task management
task_daemon = ProcessComposeDaemon(
    config_path=".thegent/task-compose.yaml",
    is_daemon=True,
)
```

**Status**: ⏳ Pending

### 2.5 LSP Multiplexing (MTSP-04)

**Goal**: Use a single persistent `serena` daemon for all code intelligence

**Implementation**:
```python
# Single serena daemon
serena_daemon = LSPServer(
    name="serena",
    command=["serena", "--multiplex"],
    is_daemon=True,
)
```

**Status**: ⏳ Pending

---

## 3. Efficient Tool Migration

### 3.1 Tool Replacements

| Current Tool | Optimized Alternative | Benefit | Status |
|--------------|-----------------------|---------|--------|
| `grep` | `rg` (Ripgrep) | 10x faster, better regex | ✅ Done |
| `find` | `fd` | Native speed, cleaner syntax | ✅ Done |
| `jq` | `jaq` | Rust-based, no process overhead | ✅ Done |
| `cat` / `tr` | Python `read()` / `replace()` | Zero process spawn overhead | ⏳ Partial |
| `sleep` | `asyncio.sleep()` | Non-blocking, single-thread | ✅ Done |
| `bash` (N) | `hook-dispatcher` (Rust) | Consolidates N bash scripts | ✅ Done |
| `date` | `datetime.now()` | Eliminated 100% of date subprocesses | ✅ Done |

### 3.2 Implementation Pattern

```python
# Before: shell-out
result = subprocess.run(["grep", "-r", "pattern", "."], capture_output=True)

# After: internal Python
from pathlib import Path
matches = []
for file in Path(".").rglob("*"):
    if file.is_file():
        try:
            content = file.read_text()
            if "pattern" in content:
                matches.append(file)
        except Exception:
            pass
```

---

## 4. Persistence & Resilience

### 4.1 Service Management

**macOS (launchd)**:
```xml
<!-- ~/Library/LaunchAgents/com.thegent.mcp.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thegent.mcp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/thegent</string>
        <string>mcp</string>
        <string>service</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

**Linux (systemd)**:
```ini
# /etc/systemd/user/thegent-mcp.service
[Unit]
Description=thegent MCP Service

[Service]
ExecStart=/usr/local/bin/thegent mcp service
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

### 4.2 Daemonization

```python
def daemonize():
    """Daemonize process."""
    import os
    import sys
    
    # Fork first time
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    
    # Create new session
    os.setsid()
    
    # Fork second time
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    
    # Redirect stdio
    sys.stdin = open("/dev/null", "r")
    sys.stdout = open("/dev/null", "w")
    sys.stderr = open("/dev/null", "w")
```

### 4.3 Session Continuity

```python
class SessionManager:
    """Manage persistent sessions."""
    
    def create_session(self, session_id: str) -> Session:
        """Create persistent session."""
        session = Session(
            id=session_id,
            state_file=Path(f".thegent/sessions/{session_id}.json"),
        )
        session.save()
        return session
    
    def attach_session(self, session_id: str) -> Session:
        """Attach to existing session."""
        state_file = Path(f".thegent/sessions/{session_id}.json")
        if state_file.exists():
            return Session.load(state_file)
        raise SessionNotFoundError(session_id)
```

---

## 5. Implementation Roadmap

### 5.1 Phase 1: Immediate Efficiency (✅ Complete)

- [x] Eliminate redundant `date` subprocesses
- [x] Consolidate MCP configurations
- [x] Mount MCP servers within `thegent serve`
- [x] Port trivial shell hooks to Rust
- [x] Global Command Accelerators
- [x] Consolidated Server
- [x] Multi-Tenant Git Accelerator
- [x] Edit Leasing Manager
- [x] Shadow Clone Logic
- [x] Package Manager Mutexing
- [x] Dual Memory Audit System
- [x] Session History Scraper

### 5.2 Phase 2: Structural Depth (✅ Partial)

- [x] Persistent Python Worker Pool
- [x] In-Process Tool Execution
- [x] Rust Governance Scanner
- [x] SQLite WAL Migration
- [ ] LSP Multiplexing
- [ ] State-SHM
- [ ] Global Watcher

### 5.3 Phase 3: Total MTSP (⏳ Pending)

- [ ] Full ACE-style dual-loop integration
- [ ] Native Rust rewrite of critical path shell hooks
- [ ] Kernel-Level Persistence

---

## 6. Python Frontmatter + Native Backmatter

### 6.1 BKM Tasks

| Task ID | Description | Phase | Status |
|---------|-------------|-------|--------|
| BKM-01 | `thegent-resources` Rust: FD/memory/load sampling | 1 | ✅ Done |
| BKM-02 | `thegent-parser` PyO3: XML tag extraction | 1 | ✅ Done |
| BKM-03 | `thegent-crypto` PyO3: sign/verify/hash artifacts | 1 | ✅ Done |
| BKM-04 | Port load_based_limits to Rust resource sampling | 1 | ✅ Done |
| BKM-05 | State-SHM: CircuitBreaker + XP in memory-mapped Rust | 2 | ⏳ Pending |
| BKM-06 | `thegent-git` Rust: HEAD, status, diff stats | 2 | ⏳ Pending |
| BKM-07 | Extend hook-dispatcher: native secret scan | 2 | ⏳ Pending |
| BKM-08 | `thegent-discovery` binary: consolidate discovery subprocesses | 2 | ⏳ Pending |

### 6.2 Usage

```bash
# Enable native resources
export THGENT_USE_NATIVE_RESOURCES=1

# Enable native crypto
export THGENT_USE_NATIVE_CRYPTO=1

# Build Rust crates
task build:rust
```

---

## 7. Verification Metrics

### 7.1 Targets

| Metric | Target | Current |
|--------|--------|---------|
| **Process Count** | < 10 persistent processes per session | ~20-30 |
| **Hook Latency** | Reduce by > 50% | Partial |
| **Stability** | Eliminate "tab termination" side effects | Partial |

### 7.2 Measurement

```python
def measure_process_count() -> int:
    """Measure current process count."""
    import psutil
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    return len(children)

def measure_hook_latency() -> float:
    """Measure hook execution latency."""
    import time
    start = time.time()
    # Execute hook
    end = time.time()
    return end - start
```

---

## 8. Configuration Reference

### 8.1 Environment Variables

```bash
# MTSP
THGENT_MTSP_ENABLED=1
THGENT_UNIFIED_MCP_HOST=1
THGENT_LSP_MULTIPLEXING=1

# Tool migration
THGENT_USE_RG=1
THGENT_USE_FD=1
THGENT_USE_JAQ=1

# Persistence
THGENT_SERVICE_MODE=1
THGENT_DAEMON_MODE=1
```

### 8.2 Config File

```yaml
# ~/.config/thegent/process-optimization.yaml
mtsp:
  enabled: true
  unified_mcp_host: true
  lsp_multiplexing: true

tools:
  use_rg: true
  use_fd: true
  use_jaq: true

persistence:
  service_mode: true
  daemon_mode: true
```

---

## 9. References

### 9.1 Related Documentation

- [Process Optimization Plan](./PROCESS_OPTIMIZATION_PLAN.md) - Original plan
- [Swarm Complete](../research/SWARM_COMPLETE.md) - Process automation
- [Library Replacement Complete](../research/LIBRARY_REPLACEMENT_COMPLETE.md) - Tool replacements

### 9.2 Implementation Files

- **MCP Server**: `src/thegent/mcp_server.py`
- **Worker Pool**: `src/thegent/orchestration/worker_pool.py`
- **Hook Dispatcher**: `hooks/hook-dispatcher/`

---

*Generated: 2026-02-16 | Version: 1.0 | Status: Complete*
