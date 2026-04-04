# Thegent Crates → Pheno Generics Extraction Plan

## Analysis Complete

### Thegent Crates Inventory

| Crate | Purpose | Generic? | Extraction Target |
|-------|---------|----------|-------------------|
| **thegent-crypto** | HMAC, SHA2, signing | ✅ **Highly generic** | `phenotype-crypto` |
| **thegent-fs** | High-performance file I/O | ✅ **Highly generic** | `phenotype-fs` |
| **thegent-jsonl** | JSONL streaming parser | ✅ **Highly generic** | `phenotype-jsonl` |
| **thegent-parser** | Agent file parsing | ⚠️ **Agent-specific** | Keep in thegent |
| **thegent-utils** | General utilities | ✅ **Generic** | `phenotype-utils` |
| **thegent-resources** | Resource management | ✅ **Generic** | `phenotype-resources` |
| **thegent-path-resolve** | Path resolution | ✅ **Generic** | `phenotype-path` |
| **thegent-discovery** | Service discovery | ⚠️ **Agent-specific** | Keep in thegent |
| **thegent-hooks** | Git hooks | ⚠️ **Agent-specific** | Keep in thegent |
| **thegent-git** | Git operations | ⚠️ **Agent-specific** | Keep in thegent |
| **thegent-router** | Request routing | ⚠️ **Agent-specific** | Keep in thegent |
| **thegent-tui** | Terminal UI | ⚠️ **Agent-specific** | Keep in thegent |
| **thegent-offload** | Task offloading | ⚠️ **Agent-specific** | Keep in thegent |

### Architecture Comparison

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT-SPECIFIC LAYER                     │
│  thegent: agent orchestration, discovery, routing, TUI   │
├─────────────────────────────────────────────────────────────┤
│                    GENERIC PRIMITIVES LAYER                 │
│  Extract to phenotype-infrakit or new phenotype-primitives  │
│  • crypto (HMAC, SHA2, signing)                             │
│  • fs (high-performance file I/O)                          │
│  • jsonl (streaming parser)                                │
│  • utils (common utilities)                              │
├─────────────────────────────────────────────────────────────┤
│                    HIGH-LEVEL INFRASTRUCTURE                │
│  phenotype-infrakit:                                       │
│  • observability, rate-limiting, health, contracts          │
│  • testing, validation, BDD                               │
└─────────────────────────────────────────────────────────────┘
```

### Recommendation

**Extract 4-5 crates** from thegent into phenotype-infrakit as **low-level primitives**:

1. **phenotype-crypto** ← thegent-crypto
   - Remove PyO3 bindings (agent-specific)
   - Keep core HMAC/SHA2/signing
   - Add standard Rust crypto traits

2. **phenotype-fs** ← thegent-fs
   - High-performance async file I/O
   - Streaming file operations
   - Platform abstraction

3. **phenotype-jsonl** ← thegent-jsonl
   - Streaming JSONL parser
   - Async iteration support
   - Memory-efficient

4. **phenotype-utils** ← thegent-utils
   - Common utility functions
   - Collection helpers
   - String/Path utilities

5. **phenotype-path** ← thegent-path-resolve
   - Cross-platform path resolution
   - Path canonicalization
   - Home/config dir helpers

### Benefits

- **thegent** becomes focused on agent-specific orchestration
- **phenotype-infrakit** gains low-level primitives
- Other Phenotype projects can use crypto/fs/jsonl without thegent dependency
- Clear separation of concerns

### Implementation Steps

1. [ ] Create extraction branches for each crate
2. [ ] Remove agent-specific code (PyO3, thegent-specific types)
3. [ ] Rename `thegent-*` → `phenotype-*`
4. [ ] Update Cargo.toml for phenotype-infrakit workspace
5. [ ] Add to phenotype-infrakit/crates/
6. [ ] Test integration
7. [ ] Update thegent to depend on phenotype-* crates
8. [ ] Archive thegent-* crate directories (or keep as re-exports)

### Alternative: Keep in Thegent

If the extraction effort is too high, keep all crates in thegent but document which are "generic primitives" that could be extracted later.

---
**Decision needed**: Extract to phenotype-infrakit, or keep in thegent with documentation?
