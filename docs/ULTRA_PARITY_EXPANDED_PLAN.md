# Ultra-Parity 2026: Expanded Plan & Research

> **Purpose**: Master planning document—expanded phases, research, dependency graph, and implementation roadmap. Use this for deep planning and coordination.

---

## 1. Executive Summary

**Ultra-Parity 2026** aims to make Zsh the fastest, most agent-aware shell by:
- **Zero-fork** startup for agents (<2ms)
- **Structured data** exposure via MCP (parity with Nushell for agents)
- **Intelligence mesh** connecting shell ↔ Neo4j ↔ NATS ↔ Postgres AI
- **Superseding** Nushell, Cline, and Cursor in agent context richness

---

## 2. Competitive & Research Landscape

### 2.1 Nushell (38k+ stars)
| Aspect | Nushell | Ultra-Parity Zsh |
|--------|---------|------------------|
| Data model | Native tables/records | Text + MCP JSON (z-obj bridge) |
| Startup | ~50–100ms | <2ms (agent) / <40ms (human) |
| POSIX | Broken | 100% compatible |
| AI context | Buffer only | Full shell memory via Z-MCP |
| History | Local SQLite | Atuin (global, encrypted) |

**Supersede strategy**: Keep Zsh syntax; add structured output via `z-obj` and MCP tools. Agents get Nushell-like tables without learning Nu.

### 2.2 Model Context Protocol (MCP)
- **Spec**: [modelcontextprotocol.io](https://modelcontextprotocol.io/specification)
- **Current version**: 2025-11-25
- **Transport**: stdio, HTTP/SSE
- **Format**: JSON-RPC 2.0
- **Z-MCP alignment**: Tools (`zsh_get_aliases`, `zsh_get_functions`, etc.) map to MCP tool schema.

### 2.3 Agent Ecosystems
| System | Protocol | Shell integration |
|--------|----------|-------------------|
| Cursor | MCP, custom | Limited (file + exec) |
| Cline | MCP | Buffer scraping |
| AgentOp (kagentop) | ACP | iOS relay via agentopd |
| Codex CLI | ACP | Direct exec |

**Opportunity**: Z-MCP gives all MCP clients (Cursor, Cline, Codex) direct shell state—no scraping.

---

## 3. Dependency Graph (DAG)

```
                    ┌─────────────────┐
                    │   Phase A–D     │
                    │ (Zero-Fork Core)│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────────┐
        │ Phase E  │  │ Phase F  │  │ Phase K.1    │
        │ UI+Spark │  │ Observ.  │  │ z-obj shim   │
        └────┬─────┘  └────┬─────┘  └──────┬───────┘
             │             │               │
             └─────────────┼───────────────┘
                           ▼
                    ┌─────────────┐
                    │  Phase H    │
                    │ (Specs)     │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────────┐   ┌──────────┐
   │ Z-MCP    │     │ Z-Bus (NATS) │   │ Z-Graph  │
   │ (Phase I)│     │ (Phase J)    │   │ (Phase J)│
   └────┬─────┘     └──────┬───────┘   └────┬─────┘
        │                  │                │
        └──────────────────┼────────────────┘
                           ▼
                    ┌─────────────┐
                    │ Phase I     │
                    │ AgentOp     │
                    │ Integration │
                    └─────────────┘
```

---

## 4. Expanded Phase Definitions

### Phase A: Zero-Fork Core ✅
- **Status**: Done
- **Artifacts**: `.zshenv`, `.zshrc` with `zmodload zsh/datetime`, `zsh/stat`, `zsh/parameter`, `zsh/files`
- **Verification**: `vouch` uses `strftime` and `${param:t}`

### Phase B: Harness Skip-Init ✅
- **Status**: Done
- **Artifacts**: `SHARECLI_AGENT_CONTEXT`, `SHARECLI_AGENT` early exit in `.zshenv`/`.zshrc`
- **Verification**: Agent shells return in <2ms

### Phase C: Tooling Evolution
- **Status**: Partial (znap, mise, zoxide, starship via bundle)
- **Gaps**: `yazi`, `zsh-nvm-x` bridge, fzf-tab tuning

### Phase D: Plugin Compiler ✅
- **Status**: Done
- **Artifacts**: `sharecli/bin/compile_plugins`, `~/.zsh_bundle.zsh`
- **Verification**: Single `source` loads full env

### Phase E: UI & Intelligence ✅
- **Status**: Done
- **Artifacts**: `TRAPWINCH`, `zle-line-finish`, Spark bridge, `teleport_shell`, Atuin

### Phase F: Observability
- **Status**: Pending
- **Deliverables**: `profile_zsh`, fork detection, harness latency metrics
- **Dependencies**: zsh-bench patterns, harness metrics API

### Phase G: High-Performance Services
- **Status**: Specs drafted; implementation pending
- **Stack**: Postgres+pgvector, Neo4j, NATS, Temporal, Minio, Loki
- **Research**: PG.ai (Timescale), pgvectorscale

### Phase H: Intelligence Mesh Specs ✅
- **Status**: Done
- **Artifacts**: `ZSH_MCP_SERVER_SPEC.md`, `NEO4J_GRAPH_SPEC.md`, `NATS_EVENT_MESH_SPEC.md`

### Phase I: Z-MCP Implementation
- **Status**: Pending
- **Deliverables**: Go/Python daemon, MCP tools, stdio transport
- **Dependencies**: FastMCP or raw JSON-RPC

### Phase J: Z-Bus & Z-Graph
- **Status**: Pending
- **Deliverables**: NATS client in ultra-shim, Neo4j ingestion from preexec/precmd
- **Dependencies**: NATS Go client, Neo4j driver

### Phase K: Structured Output (Nushell Parity)
- **K.1**: z-obj shim ✅ (built; ls hang fixed)
- **K.2**: MCP context injection (shell state in every LLM prompt)
- **K.3**: Rich rendering (OSC/Kittens for tables in terminal)

---

## 5. Implementation Priorities

| Priority | Phase | Effort | Impact |
|----------|-------|--------|--------|
| P0 | Z-MCP (Phase I) | 2–3 days | Enables all MCP clients to read shell |
| P1 | Z-Bus (Phase J) | 1–2 days | Real-time event mesh |
| P2 | z-obj pipeline fix | 0.5 day | Verify `ls \| z-obj` after ls fix |
| P3 | Z-Graph (Phase J) | 2–3 days | Long-term agent memory |
| P4 | Phase F Observability | 1 day | Profiling, fork detection |

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| MCP spec drift | Pin to 2025-11-25; test against Cursor/Cline |
| Neo4j schema churn | Versioned nodes; migration scripts |
| NATS delivery loss | JetStream for persistence where needed |
| ultra-shim recursion | `resolveReal` excludes self; hardcoded paths |

---

## 7. Success Criteria

- [ ] Agent shell startup < 2ms (measured)
- [ ] `zsh_get_aliases` MCP tool returns in < 5ms
- [ ] `ls -l \| z-obj --type ls` returns valid JSON
- [ ] Cursor can list shell aliases via Z-MCP
- [ ] NATS receives `shell.events.*` on command execution

---

## 8. References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [Nushell Book](https://www.nushell.sh/book/)
- [Atuin](https://github.com/ellie/atuin) — history sync
- [PG.ai](https://github.com/timescale/pgai) — SQL-level LLM
- [FastMCP](https://github.com/jlowin/fastmcp) — Python MCP server framework
