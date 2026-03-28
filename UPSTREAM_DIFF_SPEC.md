# Upstream Diff Spec

This document tracks all changes made against upstream repositories.

---

## cliproxyapi-plusplus (fork of cliproxyapi++)

### Summary of Changes

| Category | Files Changed | Description |
|----------|--------------|-------------|
| Import Paths | 25+ | All `github.com/router-for-me/CLIProxyAPI` → `github.com/kooshapari/cliproxyapi-plusplus` |
| SDK Config | 3 | Added config aliases |
| Internal Config | 1 | Added `ResponsesCompactEnabled` option |
| Functional | 3+ | Added antigravity backfill, sticky selector |

### Detailed Breakdown

#### 1. Import Path Migration (25 files)
All SDK packages re-pathed from upstream:
```
github.com/router-for-me/CLIProxyAPI/v6 → github.com/kooshapari/cliproxyapi-plusplus/v6
```

Key affected files:
- `sdk/auth/codex.go`
- `sdk/cliproxy/service.go`
- `sdk/cliproxy/auth/*.go`
- `sdk/cliproxy/builder.go`
- `sdk/cliproxy/providers.go`

**Note**: Fork changed some paths from `pkg/llmproxy/*` to `internal/*`:
```go
// Upstream uses:
github.com/kooshapari/cliproxyapi-plusplus/v6/pkg/llmproxy/auth/codex

// Fork changed to:
github.com/kooshapari/cliproxyapi-plusplus/v6/internal/auth/codex
```

#### 2. Config Changes

**Added** (`internal/config/config.go`):
- `ResponsesCompactEnabled *bool` - Gates responses compact feature

**Added** (`pkg/llmproxy/config/sdk_config.go`):
- `LoadConfig` alias
- `LoadConfigOptional` alias  
- `SaveConfigPreserveComments` alias

#### 3. Functional Additions (Not in upstream)

** antigravity backfill** (`sdk/cliproxy/service.go`):
- `backfillAntigravityModels()` - Backfills antigravity models for auth entries
- Added `/v1/responses` websocket route attachment for Codex compatibility

**Sticky selector**:
- Added `sticky-round-robin`, `stickyroundrobin`, `srr` selector options
- Uses `StickyRoundRobinSelector`

#### 4. Missing from Fork (Bugs) - FIXED

**X-Session-Key header forwarding** (NOW FIXED):
- Was missing in fork, now added to `sdk/api/handlers/handlers.go`
- Enables sticky routing for session continuity

### Total Diff Stats
- 343 file differences
- 26 SDK files differ
- 7 pkg files differ

---

## heliosCLI (codex-rs)

### Changes Against Upstream

| Date | File | Change Description |
|------|------|-------------------|
| 2026-02-27 | `codex-rs/core/models.json` | Added minimax-m2.5 and minimax-m2.5-highspeed model entries |

#### Details: models.json Addition

**Purpose**: Fix "Model metadata for `minimax-m2.5` not found" warning

**Added Models**:
- `minimax-m2.5` (priority 14)
  - context_window: 128000
  - visibility: list
  - supports_reasoning_summaries: false
- `minimax-m2.5-highspeed` (priority 15)
  - context_window: 128000
  - visibility: list
  - supports_reasoning_summaries: false

---

## Session Stability Issue (cliproxyapi++)

### Observed Behavior

Each invocation creates a new session (different session IDs):
- `019ca169-3b15-7033-8876-35e5f4e58e6f`
- `019ca169-a729-7f42-8028-80ed350e43a9`
- `019ca169-d896-7a93-99bb-42d2315efe99`
- `019ca16a-38c6-7361-aaaf-c300bc0dac42`

This occurs even in **persistent** (non-ephemeral) sessions.

### Status

**UNRESOLVED** - Issue appears to be in the cliproxyapi++ fork implementation.

### Investigation Needed

- [x] Compare session handling between cliproxyapi++ (upstream) and cliproxyapi-plusplus (fork)
- [x] Check if session state is being lost between requests
- [x] Verify cliproxy is maintaining session continuity
- [x] Check for breaking changes in import path migration

### Key Finding: Missing X-Session-Key Header Forwarding

**Location**: `sdk/api/handlers/handlers.go`

**Upstream (cliproxyapi++)** has code that forwards the `X-Session-Key` header for sticky routing:
```go
// Forward X-Session-Key for sticky routing.
if ctx != nil {
    if ginCtx, ok := ctx.Value("gin").(*gin.Context); ok && ginCtx != nil && ginCtx.Request != nil {
        if sessionKey := strings.TrimSpace(ginCtx.GetHeader("X-Session-Key")); sessionKey != "" {
            meta["session_key"] = sessionKey
        }
    }
}
```

**Fork (cliproxyapi-plusplus)**: This code was **MISSING**.

### FIX APPLIED

Added the missing `X-Session-Key` header forwarding to `sdk/api/handlers/handlers.go` in the fork.

This should restore session stability by enabling sticky routing.
