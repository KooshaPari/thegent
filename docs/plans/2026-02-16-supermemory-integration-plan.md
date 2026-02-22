# Supermemory.ai Integration Plan (WP-5001-SM)

This document details the integration of **Supermemory.ai** as the universal memory and context layer for `thegent`.

## 1. Overview

Supermemory.ai provides a "Universal Memory API" that combines RAG, graph-based memory, and user profiles. Integrating it into `thegent` replaces the current local file-based L3 memory with a cloud-scale, cross-platform knowledge base.

## 2. Integration Architecture

### 2.1 4-Tier Memory Mapping
Supermemory will serve as the primary provider for **L3 (Long-term)** and **L4 (Archival)** memory.

| Tier | Role | Storage | thegent Integration |
|------|------|---------|---------------------|
| **L1** | Working | Context Window | Managed by Orchestrator |
| **L2** | Short-term | Redis / local JSONL | Context management service |
| **L3** | Long-term | **Supermemory (Graph)** | **Persistent knowledge, past decisions** |
| **L4** | Archival | **Supermemory (Documents)**| **Immutable audit logs, historical specs** |

### 2.2 MCP Tooling Setup
`thegent` will expose Supermemory tools via its internal MCP server and connect to Supermemory's native MCP server for external memory access.

**Server URL**: `https://mcp.supermemory.ai/mcp`

## 3. Implementation Steps

### Phase 1: Authentication & Connection (DX-SM-01)
- [ ] Implement `thegent login supermemory` using API key (`sm_...`) or OAuth.
- [ ] Configure `x-sm-project` header to scope memories to specific `thegent` projects.

### Phase 2: Memory Provider (WP-SM-02)
- [ ] Implement `SupermemoryProvider` in `src/thegent/orchestration/context.py`.
- [ ] Map `generate_continuity_packet` to Supermemory's "Conversations" API.
- [ ] Map `MAIFArtifact` persistence to Supermemory's "Documents" API.

### Phase 3: Graph Memory & Relationship Tracking (WP-SM-03)
- [ ] Use Supermemory's Knowledge Graph to track relationships between agents in a swarm.
- [ ] Implement semantic search for past decisions during the **eXplore** phase of 4X.

## 4. MCP Configuration

Add the following to `config/mcp_servers.json`:

```json
{
  "mcpServers": {
    "supermemory": {
      "url": "https://mcp.supermemory.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${THGENT_SUPERMEMORY_KEY}",
        "x-sm-project": "${THGENT_PROJECT_ID}"
      }
    }
  }
}
```

## 5. Usage in Unified Work Stream

The **Gardener** and **Incorporator** agents will use Supermemory to:
1. **Retrieve**: "Have we already explored this research seed in a previous session?"
2. **Remember**: "What were the human operator's preferences regarding library selection?"
3. **Audit**: "Retrieve the MAIF artifact signature for the change made to `execution.py` on Feb 15."

---
*Cross-ref: [CONTEXT_MANAGEMENT_DEPTH.md](../reference/CONTEXT_MANAGEMENT_DEPTH.md) | [05-ARCHITECTURE.md](./05-ARCHITECTURE.md)*


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
