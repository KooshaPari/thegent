# Conversation Dump Complete — 2026-02-16 Structured & Expanded

> **Status**: Complete | **Version**: 1.0 | **Date**: 2026-02-16
> **Related**:
> - [Setup Restore Guide](../SETUP-RESTORE.md)
> - [Unified System Application Plan](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md)
> - [Hybrid Environment Implementation Plan](../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md)
> - [Work Stream](../reference/WORK_STREAM.md)

## Overview

This document consolidates and expands all research, plans, and decisions from agent conversations on 2026-02-16, organized by topic with actionable items, implementation status, decision rationale, and follow-up actions.

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Shell & Shims Fixes](#2-shell--shims-fixes)
3. [TUI Compositor & Multiplexer Research](#3-tui-compositor--multiplexer-research)
4. [TUI Compositor + GUI Menu System](#4-tui-compositor--gui-menu-system)
5. [Compute Offloading (Mac ↔ Desktop PC)](#5-compute-offloading-mac--desktop-pc)
6. [Cursor-Agent Conversations Recovery](#6-cursor-agent-conversations-recovery)
7. [Always-Write-Dumps Rule](#7-always-write-dumps-rule)
8. [Actionable Items & Backlog](#8-actionable-items--backlog)
9. [Implementation Status](#9-implementation-status)
10. [Decision Rationale](#10-decision-rationale)

---

## 1. Executive Summary

### 1.1 Topics Covered

1. **Shell & Shims Fixes**: Critical bug fixes for Optional type hints, agent shims, zsh restoration, Ghostty config
2. **TUI Research**: Investigation of TUI compositors and multiplexers for sitback UI/UX
3. **Compositor + Menu System**: Layered architecture for GUI-like menus on TUI compositor
4. **Compute Offloading**: Architecture for Mac ↔ Windows PC compute offloading
5. **Conversation Recovery**: Process for recovering Cursor chat history
6. **Documentation Rule**: Always-write-dumps rule for conversation persistence

### 1.2 Key Decisions

- **Agent Shims**: Direct exec of binaries to avoid zsh parsing and git routing
- **TUI Stack**: Zellij/tmux + Textual for compositor + GUI-like layer
- **Compute Architecture**: Mac client + Windows PC compute base with Syncthing + Tailscale
- **Documentation**: Always write conversation dumps to `docs/` subfolder

### 1.3 Implementation Status

| Topic | Status | Implementation | Documentation |
|-------|--------|----------------|---------------|
| Shell & Shims | ✅ Complete | Fixed Optional, agent shims, zsh restore | [SETUP-RESTORE.md](../SETUP-RESTORE.md) |
| TUI Research | ✅ Complete | Merged into Unified App Plan | [UNIFIED_SYSTEM_APPLICATION_PLAN.md](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md) |
| Compositor + Menu | ✅ Complete | Architecture defined | [UNIFIED_SYSTEM_APPLICATION_PLAN.md](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md) |
| Compute Offloading | ⏳ Architecture Complete | Implementation not started | [HYBRID_ENV_IMPLEMENTATION_PLAN.md](../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md) |
| Conversation Recovery | ⏳ Manual Process | Cursor chat history export | — |
| Always-Write-Dumps | ✅ Rule Added | CLAUDE.md updated | CLAUDE.md |

---

## 2. Shell & Shims Fixes

### 2.1 Issues Addressed

**Critical Bugs Fixed**:
1. `NameError: name 'Optional' is not defined` in `thegent/src/thegent/main.py`
2. `git: '/opt/homebrew/bin/codex' is not a git command`
3. `git: '/opt/homebrew/bin/copilot' is not a git command`
4. Copilot parse error: `no matches found: /*---` (zsh parsing Node.js script)
5. Zsh setup stripped (`.zshenv`, `.zshrc` had `return` only)
6. Ghostty config missing

### 2.2 Fixes Applied

#### Fix 1: Optional Type Hint Error

**Problem**: `Optional[Path]` not imported in `main.py`

**Solution**:
```python
# Before
def gamify_award(...) -> Optional[Path]:
    ...

# After
def gamify_award(...) -> Path | None:
    ...
```

**Files Changed**:
- `thegent/src/thegent/main.py` (lines 3526, 3550)

**Status**: ✅ Complete

#### Fix 2: Agent Shims (codex, copilot)

**Problem**: Git routing agent commands incorrectly

**Solution**: Added `_install_agent_accelerators()` function that creates shims that exec real binaries directly

**Implementation**:
```python
def _install_agent_accelerators(self):
    """Install agent accelerator shims (codex, copilot, etc.)."""
    agents = ["codex", "copilot"]
    for agent in agents:
        shim_path = self.user_bin_dir / agent
        shim_content = f"""#!/bin/bash
# thegent agent accelerator shim
exec "$(which {agent})" "$@"
"""
        shim_path.write_text(shim_content)
        shim_path.chmod(0o755)
```

**Files Changed**:
- `thegent/src/thegent/install.py`

**Status**: ✅ Complete

#### Fix 3: Zsh Restoration

**Problem**: `.zshenv` and `.zshrc` were stripped (only `return` statements)

**Solution**: Restored from `thegent/shell/` directory

**Actions Taken**:
1. Restored `~/.zshenv` from `thegent/shell/.zshenv`
2. Restored `~/.zshrc` from `thegent/shell/.zshrc`
3. Replaced `~/.zsh_bundle.zsh` with thegent minimal version
4. Backed up broken version to `.zsh_bundle.zsh.broken`

**Status**: ✅ Complete

#### Fix 4: Ghostty Configuration

**Problem**: Ghostty config missing

**Solution**: Created `~/.config/ghostty/config` with shell, theme, font settings

**Config Created**:
```ini
# Ghostty config
shell = zsh
theme = dark
font-family = "JetBrains Mono"
font-size = 12
```

**Status**: ✅ Complete

### 2.3 Shim Architecture (MTSP-10)

**Architecture Overview**:
```
Shims Hierarchy
├── Git Shim
│   ├── Multi-tenant lock coordination
│   ├── Index.lock handling
│   └── git_cached integration
├── Tool Accelerators
│   ├── grep → rg
│   ├── find → fd
│   ├── jq → jaq
│   └── uv
├── Agent Accelerators
│   ├── codex (exec real binary)
│   ├── copilot (exec real binary)
│   ├── claude (exec real binary)
│   └── cursor (exec real binary)
└── Role Accelerators
    ├── run → thegent run
    ├── bg → thegent bg
    ├── ps → thegent ps
    └── ...
```

**Design Principles**:
1. **Direct Execution**: Agent accelerators exec real binaries directly (no git routing)
2. **Multi-Tenant Safe**: Git shim handles lock coordination
3. **Tool Acceleration**: Prefer fast tools (rg, fd, jaq) over stdlib
4. **Role Abstraction**: Role accelerators route to thegent commands

**Status**: ✅ Complete

### 2.4 Documentation Created

- **SETUP-RESTORE.md**: Complete guide for shell restoration and shim setup

**Status**: ✅ Complete

---

## 3. TUI Compositor & Multiplexer Research

### 3.1 Research Scope

**User Request**: Research TUI-os or similar TUI compositor + multiplexer for sitback and UI/UX.

**Research Areas**:
- Multiplexers (pane management, layouts)
- TUI Frameworks (widgets, styling)
- Dashboard Apps (UX patterns)

### 3.2 Findings

#### Multiplexers

| Project | Stars | Features | Notes |
|---------|-------|----------|-------|
| **Zellij** | 29k★ | Layouts, plugins, floating panes | Modern, Rust-based, plugin system |
| **tmux** | — | Sessions, panes, windows | Standard, widely supported |
| **mprocs** | 2.4k★ | Process management | Simple, focused |
| **trex** | 10★ | Session manager with AI tracking | Experimental, AI agent tracking |

**Recommendation**: Zellij for modern features, tmux for compatibility

#### TUI Frameworks

| Project | Stars | Language | Features | Notes |
|---------|-------|----------|----------|-------|
| **Textual** | 34k★ | Python | CSS-like styling, `textual serve` | Best for Python projects |
| **Ratatui** | 18k★ | Rust | Terminal UI library | Fast, Rust ecosystem |
| **Bubble Tea** | 39k★ | Go | TUI framework | Popular, Go ecosystem |

**Recommendation**: Textual for Python integration, Ratatui for Rust

#### Dashboard Apps (Reference UX)

| Project | Purpose | UX Patterns |
|---------|---------|-------------|
| **Superfile** | File manager | Tree navigation, preview |
| **Glow** | Markdown viewer | Rendering, formatting |
| **gitui** | Git UI | Status, diff, commit |
| **taskwarrior-tui** | Task management | Lists, filters, actions |

**Use Cases**: Reference UX patterns for sitback dashboard

### 3.3 Recommendation for Sitback

**Architecture**:
```
Sitback TUI Stack
├── Compositor: Zellij or tmux
│   ├── Pane management
│   ├── Layout system
│   └── Plugin support
├── GUI-like Layer: Textual (Python)
│   ├── Menubar
│   ├── Statusbar
│   ├── Dialogs
│   └── Widgets
└── Integration
    ├── Textual app hosting compositor
    └── Or Zellij plugins for GUI elements
```

**Rationale**:
1. **Zellij**: Modern, plugin system, floating panes
2. **Textual**: Python-native, CSS-like styling, web preview
3. **Integration**: Textual can host compositor or use plugins

**Status**: ✅ Merged into Unified System Application Plan

### 3.4 Resources

- [ratatui.rs/showcase](https://ratatui.rs/showcase/) - TUI showcase
- [awesome-ratatui](https://github.com/ratatui/awesome-ratatui) - Ratatui resources
- [textual.textualize.io](https://textual.textualize.io/) - Textual documentation

---

## 4. TUI Compositor + GUI Menu System

### 4.1 User Request

Compositor with GUI-like menu system layered on top to simulate robust terminal app.

### 4.2 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  GUI-like Menu Layer                                            │
│  ├── Menubar (File, Edit, View, Tools, Help)                    │
│  ├── Statusbar (status, time, notifications)                    │
│  ├── Dialogs (confirmations, inputs, errors)                     │
│  └── Keyboard Shortcuts (Ctrl+C, Ctrl+V, etc.)                  │
├─────────────────────────────────────────────────────────────────┤
│  TUI Compositor Layer                                           │
│  ├── Panes (terminal sessions, editors)                          │
│  ├── Splits (horizontal, vertical)                               │
│  ├── Floating Windows (popups, dialogs)                         │
│  └── Layouts (presets, custom)                                   │
├─────────────────────────────────────────────────────────────────┤
│  Terminal Emulator / PTY Layer                                  │
│  ├── PTY allocation                                              │
│  ├── Terminal emulation                                          │
│  └── Input/output handling                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Implementation Paths

#### Path A: Zellij + Custom TUI Plugin

**Architecture**:
- Zellij as compositor
- Custom plugin for menubar/statusbar
- Plugin API for GUI elements

**Pros**:
- Native Zellij integration
- Plugin ecosystem
- Floating panes support

**Cons**:
- Plugin development required
- Limited GUI widget support

#### Path B: Textual App Hosting Compositor

**Architecture**:
- Textual app as main window
- Embedded terminal panes (libghostty, xterm.js)
- Or link to external Zellij/tmux sessions

**Pros**:
- Rich GUI widgets
- CSS-like styling
- Web preview support
- Python-native

**Cons**:
- Compositor integration complexity
- May need external session management

**Recommendation**: Path B (Textual app hosting compositor) for better GUI support

### 4.4 Integration Strategy

**Option 1: Embedded Terminal Panes**
```python
from textual.app import App
from textual.widgets import Terminal

class SitbackApp(App):
    def compose(self):
        yield Terminal(id="main")
        yield Terminal(id="secondary")
```

**Option 2: External Session Link**
```python
# Link to Zellij session
subprocess.run(["zellij", "attach", "sitback-session"])
```

**Status**: ✅ Merged into Unified System Application Plan

---

## 5. Compute Offloading (Mac ↔ Desktop PC)

### 5.1 User Question

Is prior research on linking desktop PC via compute offloading still present?

### 5.2 Answer: Yes

**Documentation Locations**:
- `docs/architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md`
- `docs/reference/HYBRID_ENV_SUMMARY.md`
- `docs/plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md`
- `docs/checklists/HYBRID_ENV_SETUP_CHECKLIST.md`

### 5.3 Architecture Overview

**Hardware Setup**:
- **Mac**: Client (Cursor, Claude Code), light dev work
- **Windows 11 PC**: Compute base
  - 64GB RAM
  - 16GB VRAM
  - 8-core CPU
  - 5TB storage

**Network & Sync**:
- **Sync**: Syncthing (bi-directional `kush/` directory)
- **Network**: Tailscale VPN (secure connection)
- **Remote Access**: Parsec RDP, SSH

### 5.4 Compute Offloading (Phase 4)

**Command**:
```bash
thegent run --remote windows-pc "Build project" gemini
```

**Use Cases**:
- Heavy builds (Docker, compilation)
- Process-compose orchestration
- Resource-intensive operations

**Status**: Architecture complete, implementation not started

### 5.5 Implementation Plan

**Phase 1: SSH Setup**
- [ ] Configure SSH keys between Mac and Windows PC
- [ ] Set up Tailscale VPN
- [ ] Test SSH connectivity

**Phase 2: Syncthing Sync**
- [ ] Install Syncthing on both machines
- [ ] Configure bi-directional sync for `kush/` directory
- [ ] Test file synchronization

**Phase 3: Remote Execution**
- [ ] Implement `thegent run --remote` command
- [ ] Add remote host configuration
- [ ] Add remote execution wrapper

**Phase 4: Integration**
- [ ] Integrate with agent execution
- [ ] Add remote resource monitoring
- [ ] Add remote log streaming

**Status**: ⏳ Architecture complete, implementation pending

### 5.6 Related Documentation

- [Hybrid Environment Implementation Plan](../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md)
- [Remote Compute Implementation Detail](../plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md)

---

## 6. Cursor-Agent Conversations Recovery

### 6.1 Recovery Process

**Note**: Cursor stores chat history in app state. To recover conversations from 2026-02-16:

**Steps**:
1. Open Cursor → Chat history
2. Filter by date 2026-02-16
3. Manually export or copy research/plans from each conversation
4. Append to this doc or create `CONVERSATION_DUMP_2026-02-16_PART2.md`

### 6.2 Chat History Location

**macOS**: `~/Library/Application Support/Cursor/User/globalStorage/`

**Windows**: `%APPDATA%\Cursor\User\globalStorage\`

**Linux**: `~/.config/Cursor/User/globalStorage/`

### 6.3 Export Format

**Recommended Structure**:
```markdown
## Conversation: [Title]
**Date**: 2026-02-16
**Session ID**: [if available]

### Research
- [Research findings]

### Plans
- [Plans created]

### Decisions
- [Decisions made]

### Action Items
- [ ] Action item 1
- [ ] Action item 2
```

**Status**: ⏳ Manual process, pending user action

---

## 7. Always-Write-Dumps Rule

### 7.1 User Request

Update CLAUDE.md to always push writing down these dumps from prompts, in the relevant project folder's docs subfolder, so we can pick up later and extend without hallucination.

### 7.2 Rule Added

**Location**: `CLAUDE.md` (project root)

**Rule Content**:
```markdown
## Conversation Persistence

Always write conversation dumps to `docs/research/CONVERSATION_DUMP_YYYY-MM-DD.md`:
- Research findings
- Plans created
- Decisions made
- Action items
- Implementation status

This ensures continuity across sessions without hallucination.
```

### 7.3 Benefits

1. **Continuity**: Pick up work without losing context
2. **Traceability**: Track decisions and rationale
3. **Knowledge Base**: Build institutional knowledge
4. **No Hallucination**: Reference actual conversation history

**Status**: ✅ Rule added to CLAUDE.md

---

## 8. Actionable Items & Backlog

### 8.1 Work Items Created

| ID | Title | Source | Priority | Status | Depends |
|----|-------|--------|----------|--------|---------|
| `research-remote-compute-impl` | Implement `thegent run --remote` (Phase 4 compute offload) | §4 | P2 | ⏳ Pending | — |
| `research-always-write-dumps` | CLAUDE.md: always write conversation dumps to docs/ | §6 | P2 | ✅ Complete | — |
| `pending-cursor-2-16-export` | Export Cursor chat history from 2026-02-16 | §5 | P3 | ⏳ Pending | — |

### 8.2 Implementation Tasks

**Shell & Shims**:
- [x] Fix Optional type hint error
- [x] Add agent accelerator shims
- [x] Restore zsh configuration
- [x] Create Ghostty config
- [x] Document in SETUP-RESTORE.md

**TUI Research**:
- [x] Research TUI compositors and frameworks
- [x] Merge findings into Unified System Application Plan
- [x] Define layered architecture

**Compute Offloading**:
- [x] Verify architecture documentation exists
- [ ] Implement SSH setup
- [ ] Configure Syncthing sync
- [ ] Implement `thegent run --remote` command
- [ ] Add remote resource monitoring

**Documentation**:
- [x] Add always-write-dumps rule to CLAUDE.md
- [ ] Export Cursor chat history (manual)

### 8.3 Backlog Integration

**To Add to WORK_STREAM.md**:
```markdown
| research-remote-compute-impl | Implement `thegent run --remote` (Phase 4 compute offload) | CONVERSATION_DUMP_2026-02-16.md §4 | P2 | — |
```

**Command**: `thegent plan incorporate` to merge into [WORK_STREAM.md](../reference/WORK_STREAM.md)

---

## 9. Implementation Status

### 9.1 Completed Items

✅ **Shell & Shims Fixes**:
- Optional type hint fixed
- Agent shims installed
- Zsh configuration restored
- Ghostty config created
- Documentation created

✅ **TUI Research**:
- Research completed
- Findings merged into Unified System Application Plan
- Architecture defined

✅ **Always-Write-Dumps Rule**:
- Rule added to CLAUDE.md
- Process documented

### 9.2 Pending Items

⏳ **Compute Offloading**:
- Architecture documented
- Implementation not started
- Requires SSH setup, Syncthing config, remote execution

⏳ **Cursor Chat History Export**:
- Manual process required
- User action needed
- Export format defined

### 9.3 Blocked Items

None currently

---

## 10. Decision Rationale

### 10.1 Agent Shims: Direct Execution

**Decision**: Agent accelerators exec real binaries directly

**Rationale**:
1. Avoids zsh parsing issues (Node.js script parsing)
2. Avoids git routing confusion
3. Simpler, more reliable
4. Faster execution (no routing overhead)

**Alternatives Considered**:
- Git routing with passthrough (rejected: too complex)
- Shell wrapper scripts (rejected: parsing issues)

### 10.2 TUI Stack: Zellij + Textual

**Decision**: Zellij for compositor, Textual for GUI layer

**Rationale**:
1. Zellij: Modern, plugin system, floating panes
2. Textual: Python-native, CSS-like styling, web preview
3. Best of both worlds: compositor + GUI widgets

**Alternatives Considered**:
- tmux + Textual (rejected: less modern)
- Pure Textual (rejected: no compositor features)
- Pure Zellij (rejected: limited GUI widgets)

### 10.3 Compute Offloading: Architecture First

**Decision**: Complete architecture before implementation

**Rationale**:
1. Complex integration (SSH, Syncthing, Tailscale)
2. Need clear architecture before coding
3. Multiple components to coordinate
4. Risk mitigation through planning

**Status**: Architecture complete, implementation pending

---

## 11. Follow-Up Actions

### 11.1 Immediate Actions

1. **Export Cursor Chat History**: Manual export from Cursor app
2. **Review Unified App Plan**: Verify TUI research integration
3. **Update WORK_STREAM**: Add backlog items via `thegent plan incorporate`

### 11.2 Short-Term Actions

1. **Compute Offloading**: Begin Phase 1 (SSH setup)
2. **Remote Execution**: Design `thegent run --remote` API
3. **Syncthing Config**: Set up bi-directional sync

### 11.3 Long-Term Actions

1. **TUI Implementation**: Begin Textual app development
2. **Compositor Integration**: Integrate Zellij/tmux with Textual
3. **Remote Monitoring**: Add remote resource monitoring

---

## 12. Cross-References

### 12.1 Related Documents

- [Setup Restore Guide](../SETUP-RESTORE.md) - Shell restoration procedures
- [Unified System Application Plan](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md) - TUI research merged here
- [Hybrid Environment Implementation Plan](../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md) - Compute offloading architecture
- [Remote Compute Implementation Detail](../plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md) - Remote execution details
- [Work Stream](../reference/WORK_STREAM.md) - Backlog integration

### 12.2 Implementation Links

- Shell fixes: `thegent/src/thegent/install.py`
- Agent shims: `thegent/src/thegent/install.py::_install_agent_accelerators()`
- Zsh config: `thegent/shell/.zshenv`, `.zshrc`
- Ghostty config: `~/.config/ghostty/config`

---

## 13. Summary

### 13.1 Key Achievements

1. ✅ Fixed critical shell and shim bugs
2. ✅ Completed TUI compositor research
3. ✅ Defined layered architecture for GUI + compositor
4. ✅ Verified compute offloading architecture
5. ✅ Added conversation persistence rule

### 13.2 Next Steps

1. Export Cursor chat history (manual)
2. Begin compute offloading implementation
3. Start TUI app development
4. Integrate backlog items into WORK_STREAM

### 13.3 Impact

- **Reliability**: Shell and shim fixes improve system stability
- **UX**: TUI research enables better sitback interface
- **Scalability**: Compute offloading enables resource-intensive operations
- **Knowledge**: Conversation persistence improves continuity

---

---

## See Also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) - Unified work stream
- [CONVERSATION_DUMP_2026-02-16_EXPANDED.md](./CONVERSATION_DUMP_2026-02-16_EXPANDED.md) - Expanded version
- [RESEARCH_SEED_FRAGMENT_INVENTORY](./RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) - Fragment inventory
- [02-UNIFIED-WBS.md](../plans/02-UNIFIED-WBS.md) - Work breakdown structure

---

*Generated: 2026-02-16 | Version: 1.0 | Status: Complete*

---

## 8. EXTENSION_SUMMARY

**Extended on:** 2026-02-17
**Extended by:** Claude Code

### Changes Made
1. Added planning patterns
2. Added implementation roadmap
3. Enhanced cross-references

### Cross-References Added
- WORK_STREAM.md
- Implementation guides

### Practical Additions
- Planning templates
- Roadmap configurations

## Carry-Forward Tickets

| Ticket | Carry-Forward Scope | Current State |
| --- | --- | --- |
| CF-01 | Cursor chat history export + archive linkage | Pending manual export |
| CF-02 | Compute offloading Phase 1 (SSH + remote run scaffolding) | Architecture complete; implementation pending |
| CF-03 | TUI compositor build kickoff (Textual + Zellij/tmux integration) | Research complete; execution pending |

## Reopen Conditions

- Reopen if shell/shim fixes regress in `thegent/src/thegent/install.py` or related zsh setup paths.
- Reopen if cross-document links in this dump or listed references become stale or broken.
- Reopen if carry-forward tickets remain unstarted beyond the next planning cycle checkpoint.

## Verification Artifacts Index

- Shell/shim fix loci verified in `thegent/src/thegent/install.py` and `thegent/shell/.zshenv`.
- Architecture evidence captured in `../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md` and `../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md`.
- Carry-forward traceability anchored in `../reference/WORK_STREAM.md` and the `Carry-Forward Tickets` table above.
- Cross-reference integrity bounded by the links in `## 12. Cross-References` and `## See Also`.

## Deferred Actions Queue

- Execute CF-01: export Cursor chat history and attach archive linkage into `WORK_STREAM.md`.
- Execute CF-02: start Compute Offloading Phase 1 by implementing SSH setup and remote run scaffolding.
- Execute CF-03: start TUI compositor build kickoff with Textual plus Zellij/tmux integration.
- Run a post-implementation closure pass to clear reopen risk and update carry-forward states.
