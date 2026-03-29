# Ultra-Parity 2026: Product Requirements Document (PRD)

## Objective
To build a zero-fork, context-aware shell environment that leverages Rust-based tooling and the ShareCLI Harness to provide the fastest possible command execution and interactive experience for both humans and AI agents.

## Core Requirements (2026 Specification)
1. **Zero-Fork Hot Path**: No external process forks (`fork()` + `exec()`) allowed during shell initialization.
2. **Context-Aware Boot**: Differential loading based on caller identity (Human vs. AI Agent).
3. **Atomic Byte-Code Mapping**: Single-file binary mapping for all plugins and configurations.
4. **Asynchronous Interactivity**: Non-blocking syntax highlighting and completion rendering.
5. **Global Persistence**: Seamless environment teleportation across SSH sessions without remote root access.
6. **Reflow-Resilience (Anti-SIGWINCH)**: Graceful handling of terminal resizing without prompt doubling.
7. **AI-Tab-Completion**: Integration of LLM-powered completion (Codex + Spark) into ZLE.

## Performance Targets
| Metric | Target |
| :--- | :--- |
| Agent Startup | < 2ms |
| Human Startup | < 40ms |
| Input Latency | < 5ms (Asynchronous) |
| Completion UI | Instant (fzf-tab cached) |

## Work Breakdown Structure (WBS) - The DAG

### Phase A: Zero-Fork Core (Migration to C-Builtins)
- [ ] Internalize Utilities: `zsh/datetime`, `zsh/stat`
- [ ] Static Environment Generation: Brew/PATH
- [ ] Replace `date`, `stat`, `basename` with Zsh internals.

### Phase B: ShareCLI Harness Integration
- [ ] Implement Agent Fast-Path in `.zshenv` (`SHARECLI_AGENT_CONTEXT`)
- [ ] Harness Command Shimming: `git`, `npm`, `python`
- [ ] Bypass 100% of interactive setup for agents.

### Phase C: Tooling Evolution (Rust Stack)
- [ ] Install `znap` Plugin Manager
- [ ] Migrate Evals to `znap`: `mise`, `zoxide`, `starship`
- [ ] Install `yazi` & `mise`
- [ ] `fzf-tab` Preview & Colors integration
- [ ] `zsh-nvm-x` Legacy Bridge

### Phase D: Plugin Compiler & Build System
- [ ] Build the "Plugin Compiler" to bundle the entire environment.
- [ ] Consolidate all plugins into `~/.zsh_bundle`.
- [ ] `zcompile` the bundle for memory-mapped loading.

### Phase E: UI Resilience & Intelligence
- [x] **Transient Prompt implementation**: Use `zle-line-init` and `zle-line-finish` to clear `RPROMPT` on command execution and window resize.
- [x] **SIGWINCH Trap: RPROMPT Throttling**: Handle terminal resizing gracefully in GPU-accelerated environments (Ghostty).
- [ ] **AI-Integrated Shell (Spark/Codex Bridge)**: 
    - [x] Create a "Spark" orchestrator to pipe context (CWD, git status, buffer) to `codex`.
    - [x] Implement ghost-text rendering for real-time AI suggestions (via `zsh-ai-cmd` integration).
- [x] **SSH Teleportation Wrapper**: Auto-sync optimized `.zshrc` and bundle to remote servers upon SSH login (via `teleport_shell` command).
- [x] **Global History Sync**: Integrated `atuin` (Rust) for cross-machine encrypted history.

### Phase F: Observability & Benchmarking
- [ ] **Integrated Profiling**: Add `profile_zsh` using `zsh-bench` logic.
- [ ] **Fork Detection**: Log and identify unexpected subshells during interactive use.
- [ ] **Latency Monitoring**: Track performance of shimmied commands via the ShareCLI harness.

### Phase G: High-Performance Service Layer
- [ ] **Postgres AI Integration**:
    - [ ] Install `pgvector` & `pgvectorscale` for 10x faster semantic search.
    - [ ] Setup `pgai` (Timescale) to enable SQL-level LLM calls and automated RAG pipelines.
- [ ] **Graph Context**: Integrate **Neo4j** for agent knowledge-graph persistence.
- [ ] **Event-Driven Coordination**: Leverage **NATS** for sub-millisecond agent-to-agent communication.
- [ ] **Durable Workflows**: Utilize **Temporal** for resilient, long-running agent task orchestration.
- [ ] **Distributed Artifacts**: Use **Minio** (S3-compatible) for local storage of generated assets.

### Phase H: The Intelligence Mesh (MCP & Connectivity)
- [x] **Zsh MCP Server (Z-MCP)**: Drafted specification for shell-as-a-service context exposure.
- [x] **Agentic Knowledge Graph (Z-Graph)**: Drafted Neo4j schema for action-intent traceability.
- [x] **Agentic Event Mesh (Z-Bus)**: Drafted NATS subject/topic taxonomy for real-time coordination.
- [ ] **Implementation of Z-MCP**: Develop a lightweight bridge (Go/Python) to expose `zsh/parameter` to agents.
- [ ] **Implementation of Z-Bus**: Integrate NATS client into the `ultra-shim` for event broadcasting.

### Phase I: Multi-Agent Orchestration (AgentOp Integration)
- [ ] **Connect AgentOp to Z-MCP**: Allow iOS/macOS clients to read shell state via MCP.
- [ ] **Hybrid RAG Memory**: Combine Neo4j (Graph) + Postgres (Vector) for unified agent memory.
- [ ] **Cross-Machine Memory**: Sync the Knowledge Graph and Atuin history via SSH Teleportation.

## Implementation Details (The "How")

### Phase 1: Zero-Fork Core (Migration to C-Builtins)
Instead of calling `/bin/date` or `/usr/bin/stat`, we will load Zsh's internal C modules.

```zsh
zmodload zsh/datetime
zmodload zsh/stat
# Old (Forks): _now=$(date +%s)
# New (Internal): _now=$EPOCHSECONDS
# Old (Forks): [[ -f $f ]] && stat -f %m $f
# New (Internal): zstat +mtime -F "%s" $f
```

### Phase 5: Solving the SIGWINCH/Reflow Mess (SIGWINCH Trap)
To prevent Zsh from redrawing the `RPROMPT` multiple times during a window drag:
1. **Transient RPROMPT**: Hook `zle-line-finish` to hide the right prompt if the window is being resized.
2. **Prompt Clearing**: On `accept-line`, strip the `RPROMPT` so history doesn't clash with terminal reflow.
3. **Ghostty Integration**: Leverage Ghostty's native OSC sequences for reporting CWD and execution state.

### Phase 6: AI Intelligence (Spark/Codex Bridge)
The "Spark" bridge acts as a context-aware proxy for Codex.
```zsh
# Concept: Spark AI Completion
spark_completion() {
  # Collect context: last 5 commands, current CWD, and git status
  local context=$(harness get_context --depth 5)
  local suggestion=$(codex complete --context "$context" --buffer "$(LBUFFER)")
  LBUFFER+="$suggestion"
}
zle -N spark_completion
bindkey '^X^E' spark_completion
```

### Phase 7: SSH Teleportation
Ensures your "Ultra-Parity" environment follows you everywhere.
```zsh
# Concept: SSH Teleport
ssh() {
  if [[ "$1" != -* ]]; then
    # Quick check for bundle on remote; if missing, teleport minimal config
    ssh "$1" "[[ -f ~/.zsh_bundle.zsh ]]" || {
      cat ~/.zsh_bundle.zsh | ssh "$1" "cat > ~/.zsh_bundle.zsh && zcompile ~/.zsh_bundle.zsh"
    }
  fi
  command ssh "$@"
}
```
