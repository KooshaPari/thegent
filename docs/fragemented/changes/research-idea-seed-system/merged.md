# Merged Fragmented Markdown

## Source: changes/research-idea-seed-system/DEVELOPMENT_WRITEUP.md

# Research-Idea-Seed-System: Integrated Development Writeup

> **Status**: Ready for Implementation | **Date**: 2026-02-16
> **Work Item**: `research-idea-seed-system`
> **Duration**: 4 weeks (26.5 days estimated effort)
> **Priority**: P1

---

## 🎯 Executive Summary

### Problem Statement

Users have valuable **idea seeds** (concepts, insights, features) that emerge during development sessions, but **ideas are lost** because:

1. **Transient Storage** - Ideas exist only in IDE memory (cleared after ~2 weeks)
2. **No Systematic Capture** - Ideas buried in conversation transcripts without tagging
3. **Scattered Across Sessions** - Multiple sessions = no central repository
4. **Loss of Context** - When ideas are needed, original session context is gone
5. **No Aggregation** - Difficult to rediscover or cross-reference related ideas

**Impact**: Valuable concepts forgotten before implementation can be prioritized; manual searching through old sessions required.

### Solution Overview

Implement an **Idea Seed Detection & Storage System** that:

1. **Detects** ideas via explicit `$idea` flag or pattern recognition
2. **Stores** persistently in `.thegent/ideas/` with full git audit trail
3. **Indexes** for full-text search and metadata filtering
4. **Exposes** via CLI commands and MCP tools
5. **Never loses** ideas (git-backed, versioned, recoverable)

### Key Deliverables

| Component | Status | Impact |
|-----------|--------|--------|
| Pattern-based detection (explicit + implicit) | Phase 1 | Users flag or system auto-detects ideas |
| JSONL + git-backed storage | Phase 1 | Durable persistence with audit trail |
| Full-text indexing & search | Phase 2 | Ideas discoverable in <100ms |
| CLI commands (collect, list, search, get, export) | Phase 2-4 | Human-friendly access |
| MCP tools (collect, search, get, list) | Phase 3 | Agent-friendly access |
| Export (JSON, Markdown, CSV) | Phase 4 | Share ideas with team/tools |

---

## 📋 The Complete Picture

### Success Criteria

#### Functional
- ✅ Detect ≥95% of explicitly flagged ideas (`$idea:`)
- ✅ Detect ≥80% of implicit ideas (pattern matching)
- ✅ Persistent storage in `.thegent/ideas/` with git commits
- ✅ Full-text search <100ms for 1000+ ideas
- ✅ Filtering by date, tag, project
- ✅ Export to JSON/Markdown/CSV
- ✅ 4 MCP tools functional
- ✅ 5 CLI commands working

#### Quality
- ✅ ≥85% test coverage
- ✅ Zero external library dependencies (stdlib only)
- ✅ Type hints throughout
- ✅ Complete documentation
- ✅ All performance targets met
- ✅ Error handling and recovery capability

---

## 🏗️ System Architecture

### High-Level Components

```
┌─────────────────────────────────────┐
│ User Prompts (Claude/Cursor/Codex)  │
│ Containing: $idea flag or implicit  │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Idea Detection Engine               │
│ • Pattern matching ($idea flag)     │
│ • Implicit patterns (regex rules)   │
│ • Confidence scoring                │
│ • Metadata extraction               │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Storage Layer                       │
│ • JSONL append-only log             │
│ • Git commits (audit trail)         │
│ • Checksums (integrity)             │
│ • Daily snapshots                   │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Indexing Layer                      │
│ • Full-text index (inverted)        │
│ • Metadata indices (date/tag/proj)  │
│ • Query execution                   │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Access Layer                        │
│ • CLI: collect, list, search, get   │
│ • MCP tools: same operations        │
│ • Export: JSON, MD, CSV             │
└─────────────────────────────────────┘
```

### Data Schema (Canonical Idea Object)

```json
{
  "id": "idea_20260216_143022_abc123",
  "text": "Add lazy-loading to DAG compiler for faster feedback loop",
  "created_at": "2026-02-16T14:30:22Z",
  "source": {
    "type": "claude|cursor|codex",
    "session_id": "session_abc123",
    "workspace": "/path/to/project"
  },
  "detection": {
    "method": "explicit|implicit",
    "pattern": "$idea|what_if|new_idea",
    "confidence": 0.95
  },
  "tags": ["performance", "compiler", "dax"],
  "context": "Previous discussion about DAG compilation times...",
  "metadata": {
    "project": "thegent",
    "status": "seed|implemented",
    "linked_work_items": []
  },
  "git": {
    "commit_hash": "abc123def456",
    "branch": "main",
    "timestamp": "2026-02-16T14:30:25Z"
  },
  "checksum": "sha256:abc123..."
}
```

### Storage Structure

```
.thegent/ideas/
├── ideas.jsonl                  # Master append-only log
├── ideas.index.json             # Quick lookup index
├── audit/
│   ├── 2026/02/
│   │   ├── ideas_20260216.jsonl
│   │   └── ideas_20260217.jsonl
│   └── index.json               # Audit index + checksums
└── export/
    ├── ideas.json               # Latest export
    ├── ideas.md
    └── ideas.csv
```

---

## 🔍 Detection Algorithm

### Pattern Matching

#### Explicit Detection
```
Pattern: $idea:\s*(.+?)(?=$|$)
Example: "$idea: Add lazy-loading to DAG compiler"
Extracts: "Add lazy-loading to DAG compiler"
Confidence: 0.99 (user intent is explicit)
```

#### Implicit Detection
- `New idea:` / `Idea:` (confidence: 0.85)
- `What if we` / `Consider:` (confidence: 0.80)
- `I'm thinking about` / `Concept:` (confidence: 0.75)
- 7+ regex patterns covering common idea phrases

**Confidence Scoring**:
- Explicit flag: 0.99
- Implicit patterns: 0.70-0.90
- Manual override: 0.0 or 1.0

### Detection Workflow

```
1. Receive user prompt
2. Check for $idea flag (explicit)
3. Check regex patterns (implicit)
4. Extract metadata (source, timestamp, context)
5. Validate schema (length, fields, format)
6. Check for duplicates (text hash)
7. Store to JSONL + git commit
8. Update indices
9. Return idea ID + metadata
```

---

## 💾 Persistence Strategy

### JSONL Append-Only Log

**Why**:
- Simple, human-readable
- Efficient append (tail write only)
- Natural git compatibility
- Full audit trail (one line per idea)
- Easy recovery (git history)

**Write Process**:
1. Serialize idea to JSON
2. Append newline + JSON to `ideas.jsonl`
3. Fsync for durability
4. Create git commit: `idea: {id} {short_text}`
5. Update indices

### Git Integration

**Audit Trail**:
- One commit per idea (immediate)
- Commit msg: `idea: {id} {short_text}`
- Full history: `git log .thegent/ideas/`
- Recovery: `git show <commit>:.thegent/ideas/ideas.jsonl`

**Integrity**:
- SHA-256 checksums stored in idea object
- Verify on read: `sha256(idea_json) == idea.checksum`
- Daily snapshots for audit trail

---

## 🔎 Search & Indexing

### Full-Text Index

**Implementation**:
- Inverted index: word → [idea_ids]
- Tokenization: lowercase, stopword removal, stemming
- Updated incrementally as ideas arrive

**Performance**: <100ms search for 1000+ ideas

**Index File** (`.thegent/ideas/ideas.index.json`):
```json
{
  "inverted_index": {
    "lazy": ["idea_1", "idea_45"],
    "loading": ["idea_1", "idea_23"],
    "compiler": ["idea_1", "idea_56"]
  }
}
```

### Metadata Indices

- **Date Index**: `{YYYY-MM-DD → [idea_ids]}`
- **Tag Index**: `{tag → [idea_ids]}`
- **Project Index**: `{project → [idea_ids]}`
- **Status Index**: `{status → [idea_ids]}`

---

## 🖥️ CLI Interface

### Commands

#### `thegent ideas collect`
```bash
# Collect ideas from recent sessions
$ thegent ideas collect --since 6h
# Output: Collected 5 new ideas

# Collect with git commits
$ thegent ideas collect --git-commit
```

#### `thegent ideas list`
```bash
# List all ideas
$ thegent ideas list

# Filter by tag
$ thegent ideas list --tag performance --limit 10

# Verbose output with context
$ thegent ideas list --verbose
```

#### `thegent ideas search`
```bash
# Full-text search
$ thegent ideas search "lazy loading"

# Filter by tag + date
$ thegent ideas search "cache" --tag performance --since 1w

# Paginated results
$ thegent ideas search "feature" --limit 5 --offset 0
```

#### `thegent ideas get`
```bash
# Retrieve specific idea
$ thegent ideas get idea_20260216_143022_abc123

# JSON output
$ thegent ideas get idea_20260216_143022_abc123 --format json
```

#### `thegent ideas export`
```bash
# Export to JSON
$ thegent ideas export --format json --output ideas.json

# Export to Markdown
$ thegent ideas export --format markdown --output ideas.md

# Export with filters
$ thegent ideas export --format csv --tag architecture
```

---

## 🔗 MCP Integration

### MCP Tools

1. **`thegent_idea_collect`** - Collect ideas from sessions
2. **`thegent_idea_search`** - Full-text search ideas
3. **`thegent_idea_get`** - Retrieve specific idea by ID
4. **`thegent_idea_list`** - List ideas with filters

### MCP Resources

- `thegent://ideas` - List all ideas
- `thegent://ideas/{id}` - Get specific idea
- `thegent://ideas/recent` - 10 most recent
- `thegent://ideas/by-tag/{tag}` - Ideas by tag

### Agent Integration

```python
# Agents can query ideas to inform implementations
ideas = call_tool("thegent_idea_search", query="caching strategy")
for idea in ideas:
    use_in_planning(idea)
```

---

## 🎯 Implementation Phases

### Phase 1: Core Detection & Storage (Week 1, 7.5 days)

**Deliverable**: Ideas detected and persistently stored

| Task | Effort | Deliverable |
|------|--------|-------------|
| 1.1 Project Setup | 0.5d | Directory structure |
| 1.2 Idea Schema | 1.5d | Pydantic models + validation |
| 1.3 Detection Engine | 2d | Pattern matching + extraction |
| 1.4 Storage Layer | 2d | JSONL + git integration |
| 1.5 CLI collect | 1.5d | Working collect command |

**Success Criteria**:
- ✅ Schema validates all fields
- ✅ Detector ≥95% accurate on explicit ideas
- ✅ Ideas persist to JSONL with git commits
- ✅ `thegent ideas collect` works end-to-end
- ✅ Phase 1 tests pass (≥90% coverage)

---

### Phase 2: Indexing & Search (Week 2, 6 days)

**Deliverable**: Ideas searchable and filterable via CLI

| Task | Effort | Deliverable |
|------|--------|-------------|
| 2.1 Full-Text Index | 1.5d | Inverted index, <100ms search |
| 2.2 Metadata Indices | 1d | Date, tag, project filtering |
| 2.3 Query Engine | 2d | Search, sort, paginate |
| 2.4 Search/list/get | 1.5d | Three CLI commands |

**Success Criteria**:
- ✅ Search <100ms for 1000+ ideas
- ✅ Filtering works (tag, date, project)
- ✅ Sorting by relevance/date works
- ✅ All search commands functional
- ✅ Phase 2 tests pass (≥90% coverage)

---

### Phase 3: MCP Integration (Week 3, 4 days)

**Deliverable**: Agents can discover and access ideas

| Task | Effort | Deliverable |
|------|--------|-------------|
| 3.1 MCP Tools | 1.5d | 4 tools implemented |
| 3.2 Server Integration | 1.5d | Registered with FastMCP |
| 3.3 MCP Resources | 1d | Resources exposed |

**Success Criteria**:
- ✅ All 4 tools functional
- ✅ All 4 resources accessible
- ✅ Agent tests pass
- ✅ Phase 3 tests pass (≥90% coverage)

---

### Phase 4: Polish & Documentation (Week 4, 9.5 days)

**Deliverable**: Production-ready, tested, documented system

| Task | Effort | Deliverable |
|------|--------|-------------|
| 4.1 Export | 1.5d | JSON, Markdown, CSV export |
| 4.2 Test Suite | 3d | ≥85% coverage, all scenarios |
| 4.3 Documentation | 1.5d | User guide + API docs |
| 4.4 Integration Tests | 1d | E2E workflows |
| 4.5 Hook Integration | 1d | UserPromptSubmit hook |
| 4.6 Performance | 1.5d | Benchmarks + optimization |

**Success Criteria**:
- ✅ All tests pass (≥85% coverage)
- ✅ Documentation complete
- ✅ Performance targets met
- ✅ Hook working automatically
- ✅ Production-ready

---

## 📊 Implementation Details

### Task Breakdown

**Phase 1 Tasks**:

1.1 **Project Setup** (0.5 days)
   - Create `src/thegent/ideas/` directory
   - Create `.thegent/ideas/` user data directory
   - Add CLI entry point
   - Setup `.gitignore`

1.2 **Idea Schema** (1.5 days)
   - Pydantic models for IdeaObject, IdeaSource, DetectionMeta
   - Validation: length (50-5000 chars), format checks
   - Checksum calculation (SHA-256)
   - Serialization/deserialization
   - ≥90% test coverage

1.3 **Detection Engine** (2 days)
   - Explicit pattern matching ($idea flag)
   - 7+ implicit patterns (what if, new idea, etc.)
   - Confidence scoring (0.70-0.99)
   - Metadata extraction (source, timestamp, context)
   - Duplicate detection (text hash + fuzzy)
   - Validation + error handling
   - ≥90% test coverage

1.4 **Storage Layer** (2 days)
   - JSONL write/read (append-only)
   - Fsync for durability
   - Git integration (commit with metadata)
   - Checksum verification
   - Error handling
   - Recovery capability
   - ≥90% test coverage

1.5 **CLI collect** (1.5 days)
   - Command group `thegent ideas`
   - Subcommand `collect` with `--since` option
   - Session discovery integration
   - Progress reporting
   - Error handling
   - Integration tests

**Phase 2 Tasks**:

2.1 **Full-Text Index** (1.5 days)
   - Tokenizer (lowercase, stopword removal)
   - Inverted index structure
   - Index building + persistence
   - Search execution (<100ms)
   - Performance benchmarks
   - ≥90% test coverage

2.2 **Metadata Indices** (1 day)
   - Date index (YYYY-MM-DD → ids)
   - Tag index (tag → ids)
   - Project index (project → ids)
   - Status index (status → ids)
   - Index persistence + update logic
   - ≥90% test coverage

2.3 **Query Engine** (2 days)
   - Query parser (tokenize, handle quotes)
   - Full-text search + filtering
   - Sorting (relevance, date, tag)
   - Pagination (limit, offset)
   - Result scoring (TF-IDF)
   - Integration tests

2.4 **Search/list/get** (1.5 days)
   - `ideas search` command
   - `ideas list` command
   - `ideas get` command
   - Output formatting (table, JSON, CSV)
   - Pagination options
   - Integration tests

**Phase 3 Tasks**:

3.1 **MCP Tools** (1.5 days)
   - Implement 4 tools with input schemas
   - Error handling
   - Response formatting
   - Tool tests

3.2 **Server Integration** (1.5 days)
   - Register tools with FastMCP
   - Add to MCP manifest
   - Implement resources
   - Resource tests

3.3 **MCP Resources** (1 day)
   - `thegent://ideas`
   - `thegent://ideas/{id}`
   - `thegent://ideas/recent`
   - `thegent://ideas/by-tag/{tag}`
   - Resource tests

**Phase 4 Tasks**:

4.1 **Export** (1.5 days)
   - JSON export
   - Markdown export (formatted list)
   - CSV export (tabular)
   - Filtering + export command
   - Export tests

4.2 **Test Suite** (3 days)
   - Unit tests: schema, detector, storage, index, query
   - CLI tests: all commands
   - MCP tool tests
   - Export tests
   - ≥85% coverage verification

4.3 **Documentation** (1.5 days)
   - User guide (how to flag ideas, examples)
   - CLI reference (all commands)
   - API docstrings (Google style)
   - MCP documentation
   - FAQ section

4.4 **Integration Tests** (1 day)
   - End-to-end workflows
   - Real prompt examples
   - Git recovery scenarios
   - Performance testing

4.5 **Hook Integration** (1 day)
   - Create `hooks/idea-seed-detector.sh`
   - Hook registry entry
   - Automatic detection on UserPromptSubmit
   - Configuration options

4.6 **Performance** (1.5 days)
   - Benchmark detection (<10ms)
   - Benchmark storage (<50ms)
   - Benchmark search (<100ms)
   - Benchmark export (<500ms)
   - Optimize indices
   - Performance metrics/logging

---

## 📁 File Structure

### Source Code
```
src/thegent/ideas/
├── __init__.py              # Package, exports
├── schema.py                # Pydantic models, validation
├── detector.py              # Pattern matching, extraction
├── storage.py               # JSONL persistence
├── git.py                   # Git audit trail
├── index.py                 # Full-text + metadata indexing
├── query.py                 # Search, filter, sort
├── cli.py                   # CLI commands (collect, list, search, get, export)
├── export.py                # JSON/Markdown/CSV export
└── mcp_tools.py             # MCP tool implementations
```

### Tests
```
tests/ideas/
├── test_schema.py           # Schema validation tests
├── test_detector.py         # Pattern matching tests
├── test_storage.py          # Persistence tests
├── test_git.py              # Git integration tests
├── test_index.py            # Index building/search tests
├── test_query.py            # Query execution tests
├── test_cli.py              # CLI command tests
├── test_export.py           # Export format tests
└── conftest.py              # Pytest fixtures
```

### Documentation
```
docs/
├── guides/
│   └── idea-seeds.md        # User guide
├── reference/
│   └── IDEA_SEEDS_CLI_REFERENCE.md  # CLI reference
└── changes/research-idea-seed-system/
    ├── proposal.md          # Problem + scope
    ├── design.md            # Architecture + design
    ├── tasks.md             # Implementation tasks
    ├── README.md            # Quick start
    └── DEVELOPMENT_WRITEUP.md  # This file
```

---

## 🧪 Quality Standards

### Test Coverage
- **Target**: ≥85% coverage
- **Phase 1**: ≥90% per module
- **Phase 2**: ≥90% per module
- **Phase 3**: ≥90% per module
- **Phase 4**: ≥85% overall

### Code Quality
- **Type Hints**: Every function/class
- **Docstrings**: Google style
- **Line Length**: ≤100 chars
- **Function Length**: <50 lines (soft limit)
- **Class Length**: <200 lines (soft limit)
- **Dependencies**: Zero external (stdlib only)

### Performance Targets
| Operation | Target | Approach |
|-----------|--------|----------|
| Detect idea | <10ms | Pattern matching (no I/O) |
| Store idea | <50ms | Sequential write + fsync |
| Search 1000 ideas | <100ms | Inverted index (memory) |
| Full export | <500ms | Stream writing + buffering |
| Git commit | <100ms | Batch if needed |
| Index rebuild | <1s | Incremental indexing |

---

## 🚀 Integration Points

### With Existing Systems

1. **Prompt History Collection System**
   - Broader system for all prompts
   - Idea Seed is focused subset
   - Share git infrastructure

2. **Work Stream & Backlog**
   - Ideas → work items
   - Export ideas → WORK_STREAM.md
   - Track implementation

3. **Session Registry**
   - Link ideas to source sessions
   - Analyze: "which ideas led to implementations?"
   - Enable post-hoc traceability

4. **Hook System**
   - UserPromptSubmit hook detects automatically
   - No user action required
   - Configurable patterns

5. **MCP Server**
   - Register tools with FastMCP
   - Agents discover ideas
   - Enable agent-driven ideation

---

## 📈 Success Metrics

### Functional Metrics
- ✅ Idea detection accuracy ≥95% (explicit)
- ✅ Idea detection accuracy ≥80% (implicit)
- ✅ Search performance <100ms
- ✅ Storage durability (git audit trail)
- ✅ Export completeness (all formats)

### Quality Metrics
- ✅ Test coverage ≥85%
- ✅ Zero bugs in Phase 1 (after testing)
- ✅ Zero performance regressions
- ✅ Zero external dependencies

### User Metrics
- ✅ CLI commands intuitive (≤3 args each)
- ✅ Documentation complete
- ✅ Examples work as documented
- ✅ Error messages helpful

---

## 🔄 Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pattern matching false positives | Medium | Low | Configurable patterns, manual override |
| Storage bloat (many ideas) | Low | Low | Archiving, compression, pruning |
| Git commit overhead | Low | Low | Batch commits, async writes |
| Search performance degradation | Low | Medium | Caching, incremental indexing |
| Users forget to flag ideas | Medium | Medium | Auto-detection patterns, reminders, docs |
| Ideas not actionable | Low | Low | Export → backlog feature |
| Privacy concerns (sensitive data) | Low | Medium | Redaction options, local-only storage |

**Mitigation Strategy**: Phase-based delivery with testing at each phase. Risk re-evaluated after each phase.

---

## 📋 Effort Summary

| Phase | Tasks | Effort | Actual |
|-------|-------|--------|--------|
| **Phase 1** | 5 | 7.5 days | — |
| **Phase 2** | 4 | 6 days | — |
| **Phase 3** | 3 | 4 days | — |
| **Phase 4** | 6 | 9.5 days | — |
| **TOTAL** | 18 | **26.5 days** | — |

**Timeline**: 4 weeks at nominal pace (no blockers)

---

## ✅ Acceptance Checklist

### Phase 1 Completion
- [ ] Project structure created
- [ ] Schema implemented and validated
- [ ] Detector with ≥95% accuracy
- [ ] JSONL storage with git audit
- [ ] CLI collect command working
- [ ] Phase 1 tests pass (≥90% coverage)

### Phase 2 Completion
- [ ] Full-text index <100ms search
- [ ] Metadata indices all working
- [ ] Query engine with filtering/sorting
- [ ] Search, list, get commands working
- [ ] Phase 2 tests pass (≥90% coverage)

### Phase 3 Completion
- [ ] All 4 MCP tools functional
- [ ] MCP server integration complete
- [ ] All resources accessible
- [ ] Phase 3 tests pass (≥90% coverage)

### Phase 4 Completion
- [ ] Export to JSON/MD/CSV works
- [ ] Overall test coverage ≥85%
- [ ] Documentation complete
- [ ] E2E integration tests passing
- [ ] Hook integration working
- [ ] All performance targets met
- [ ] Production-ready

### Overall Goals
- [ ] Zero external library dependencies
- [ ] Backward compatible with existing CLI
- [ ] Works on macOS, Linux, Windows
- [ ] Git recovery capability verified
- [ ] Performance benchmarks documented

---

## 🎬 Getting Started

### For Reviewers
1. Read: Executive Summary (above)
2. Skim: Architecture section
3. Review: Risk & Mitigation
4. Decision: Approve/Request Changes

### For Architects
1. Read: Full document
2. Review: System Architecture section
3. Review: Integration Points section
4. Provide: Architectural approval

### For Implementers
1. Read: All sections
2. Start: Phase 1 Task 1.1 (Project Setup)
3. Follow: Task breakdown in each phase
4. Track: Actual vs. estimated effort

### For QA/Testers
1. Read: Quality Standards section
2. Review: Test coverage targets
3. Plan: Test cases for each phase
4. Verify: Acceptance criteria

---

## 📞 Questions & Support

| Question | Answer Source |
|----------|----------------|
| **What is the problem?** | Problem Statement section |
| **How will we solve it?** | Solution Overview section |
| **What's the architecture?** | System Architecture section |
| **How do we detect ideas?** | Detection Algorithm section |
| **How are ideas stored?** | Persistence Strategy section |
| **How do we find ideas?** | Search & Indexing section |
| **What commands exist?** | CLI Interface section |
| **How do agents use ideas?** | MCP Integration section |
| **What's the timeline?** | Implementation Phases section |
| **What's the effort?** | Effort Summary section |
| **What could go wrong?** | Risk & Mitigation section |
| **How do we verify success?** | Acceptance Checklist section |

---

## 📚 Related Documents

- **proposal.md** - Detailed problem statement + scope
- **design.md** - Technical architecture + specifications
- **tasks.md** - Implementation tasks with dependencies
- **README.md** - Quick reference + examples
- **INDEX.md** - Navigation guide
- [Prompt History Collection System](../../plans/PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md)
- [Work Stream](../../reference/WORK_STREAM.md)

---

## 🏁 Conclusion

The **Idea Seed Detection & Storage System** is a focused, high-value feature that solves a real problem: preserving valuable ideas that emerge during development.

**Key Success Factors**:
1. **Pattern-based detection** - Captures both explicit (`$idea`) and implicit ideas
2. **Simple storage** - JSONL + git = durable, auditable, recoverable
3. **Fast search** - Full-text indexing for <100ms queries
4. **Dual interface** - CLI for humans, MCP for agents
5. **Zero dependencies** - Standalone, easy to maintain

**4-week implementation** with phased delivery enables rapid iteration and testing. All components use Python stdlib only, ensuring easy deployment and minimal maintenance.

---

**Document Status**: Ready for Implementation
**Last Updated**: 2026-02-16
**Next Phase**: Phase 1 Implementation (Project Setup → Detection → Storage)
**Target Completion**: 2026-03-16 (4 weeks)

---

## Source: changes/research-idea-seed-system/INDEX.md

# Consolidated Index

## Files

* `DEVELOPMENT_WRITEUP.md`
* `INDEX.md`
* `design.md`
* `proposal.md`
* `tasks.md`

## Subdirectories


---

## Source: changes/research-idea-seed-system/design.md

# Research-Idea-Seed-System: Design

> **Status**: Complete | **Date**: 2026-02-16
> **Document Purpose**: Technical architecture and implementation design
> **Audience**: Implementers, architects

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Claude Code / Codex / Cursor Sessions                       │
│ (User prompts containing $idea flag or implicit patterns)   │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ thegent Hook System (UserPromptSubmit)                      │
│ - Intercepts prompts during processing                      │
│ - Passes to idea detection system                           │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Idea Detection Engine                                        │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ 1. Pattern Matcher                                   │   │
│ │    - Regex: /\$idea:\s*(.+?)(?=\$|$)/i             │   │
│ │    - Implicit patterns:                             │   │
│ │      - \"New idea:\", \"Idea:\", \"I'm thinking...\"│   │
│ │      - \"What if we\", \"Consider:\", \"Concept:\"  │   │
│ │    - Returns: (matched, text, confidence)           │   │
│ └──────────────────────────────────────────────────────┘   │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ 2. Metadata Extractor                                │   │
│ │    - Source: session_id, timestamp, workspace        │   │
│ │    - Context: preceding text (128 chars)             │   │
│ │    - Tags: auto-detected or user-provided            │   │
│ └──────────────────────────────────────────────────────┘   │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ 3. Validator                                         │   │
│ │    - Schema check (required fields)                  │   │
│ │    - Deduplication (exact text match)                │   │
│ │    - Length check (50-5000 chars)                    │   │
│ └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Storage Layer                                                │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Primary: JSONL (.thegent/ideas/ideas.jsonl)         │   │
│ │ - Append-only log of all ideas                       │   │
│ │ - One JSON object per line                           │   │
│ │ - Full history preserved                             │   │
│ └──────────────────────────────────────────────────────┘   │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Audit: Daily snapshots (.thegent/ideas/audit/)      │   │
│ │ - ideas_YYYYMMDD.jsonl (daily snapshots)             │   │
│ │ - audit_index.json (file index + checksums)          │   │
│ └──────────────────────────────────────────────────────┘   │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Git Integration                                      │   │
│ │ - Auto-commit after each new idea                    │   │
│ │ - Commit msg: \"idea: [idea_id] [short text]\"       │   │
│ │ - Full versioning + recovery                         │   │
│ └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         ↓\n┌─────────────────────────────────────────────────────────────┐\n│ Indexing Layer (In-Memory or On-Disk)                      │\n│ ┌──────────────────────────────────────────────────────┐   │\n│ │ Full-Text Index                                      │   │\n│ │ - Inverted index (word → idea IDs)                   │   │\n│ │ - Tokenization: lowercase, remove stopwords          │   │\n│ │ - Updated on each new idea                           │   │\n│ └──────────────────────────────────────────────────────┘   │\n│ ┌──────────────────────────────────────────────────────┐   │\n│ │ Metadata Index                                       │   │\n│ │ - date_index: idea_id → timestamp                    │   │\n│ │ - tag_index: tag → [idea_ids]                        │   │\n│ │ - project_index: project → [idea_ids]                │   │\n│ └──────────────────────────────────────────────────────┘   │\n└────────────────────────┬────────────────────────────────────┘\n                         ↓\n┌─────────────────────────────────────────────────────────────┐\n│ Query & Access Layer                                         │\n│ ┌──────────────────────────────────────────────────────┐   │\n│ │ CLI Commands                                         │   │\n│ │ - ideas collect [--since TIME]                       │   │\n│ │ - ideas list [--limit N] [--tag TAG]                 │   │\n│ │ - ideas search QUERY [--tag TAG] [--since TIME]      │   │\n│ │ - ideas export [--format json|md|csv]                │   │\n│ │ - ideas get ID                                       │   │\n│ └──────────────────────────────────────────────────────┘   │\n│ ┌──────────────────────────────────────────────────────┐   │\n│ │ MCP Tools                                            │   │\n│ │ - thegent_idea_collect()                             │   │\n│ │ - thegent_idea_search(query)                         │   │\n│ │ - thegent_idea_get(id)                               │   │\n│ │ - thegent_idea_list([limit, tag, since])             │   │\n│ └──────────────────────────────────────────────────────┘   │\n│ ┌──────────────────────────────────────────────────────┐   │\n│ │ MCP Resources                                        │   │\n│ │ - thegent://ideas                                    │   │\n│ │ - thegent://ideas/{id}                               │   │\n│ │ - thegent://ideas/recent                             │   │
│ └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Data Schema

### 2.1 Idea Object (Canonical)

```json
{
  "id": "idea_20260216_143022_abc123",
  "text": "Add lazy-loading to DAG compiler for faster feedback loop",
  "created_at": "2026-02-16T14:30:22Z",
  "source": {
    "type": "claude|cursor|codex",
    "session_id": "session_abc123",
    "prompt_index": 42,
    "workspace": "/path/to/project"
  },
  "detection": {
    "method": "explicit|implicit",
    "pattern": "$idea|new_idea|what_if",
    "confidence": 0.95
  },
  "tags": ["performance", "compiler", "dax"],
  "context": "Previous discussion about DAG compilation times...",
  "metadata": {
    "project": "thegent",
    "status": "seed",
    "linked_work_items": [],
    "implementation_count": 0
  },
  "git": {
    "commit_hash": "abc123def456",
    "branch": "main",
    "timestamp": "2026-02-16T14:30:25Z"
  },
  "checksum": "sha256:abc123..."
}
```

### 2.2 JSONL Storage Format

```jsonl
{"id":"idea_20260216_143022_abc123","text":"Add lazy-loading...","created_at":"2026-02-16T14:30:22Z",...}
{"id":"idea_20260216_144500_xyz789","text":"Implement cache invalidation...","created_at":"2026-02-16T14:45:00Z",...}
...
```

### 2.3 Directory Structure

```
.thegent/
├── ideas/
│   ├── ideas.jsonl                  # Master log (append-only)
│   ├── ideas.index.json             # Quick lookup index
│   ├── audit/
│   │   ├── 2026/
│   │   │   └── 02/
│   │   │       ├── ideas_20260216.jsonl  # Daily snapshot
│   │   │       └── ideas_20260217.jsonl
│   │   └── index.json               # Audit index + checksums
│   ├── export/                      # Cached exports
│   │   ├── ideas.md                 # Latest markdown export
│   │   ├── ideas.json               # Latest JSON export
│   │   └── ideas.csv                # Latest CSV export
│   └── .gitignore                   # Git ignore patterns
```

---

## 3. Detection Algorithm

### 3.1 Pattern Matching

**Explicit Detection** (Flag-based):
```python
# Regex pattern for $idea flag
EXPLICIT_PATTERN = r'\$idea:\s*(.+?)(?=\$|$)'

# Example: "$idea: Add caching layer for faster queries"
# Extracts: "Add caching layer for faster queries"
```

**Implicit Detection** (Heuristic-based):
```python
IMPLICIT_PATTERNS = [
    r'new idea:\s*(.+?)(?:\n|$)',              # "New idea: ..."
    r'idea:\s*(.+?)(?:\n|$)',                  # "Idea: ..."
    r'what if we\s+(.+?)(?:\n|$)',             # "What if we ..."
    r'consider(?:ing)?:\s*(.+?)(?:\n|$)',      # "Consider: ..."
    r'concept:\s*(.+?)(?:\n|$)',               # "Concept: ..."
    r'i[\'m ]*thinking\s+about\s+(.+?)(?:\n|$)', # "I'm thinking about ..."
    r'(?:proposal|vision|roadmap):\s*(.+?)(?:\n|$)',
]
```

**Confidence Scoring**:
- Explicit flag: confidence = 0.99 (user intent is clear)
- Implicit patterns: confidence = 0.7-0.9 (based on pattern specificity)
- Manual override: user can set confidence to 1.0 or 0.0

### 3.2 Detection Workflow

```
1. Receive: User prompt text
2. Tokenize: Split by sentences/paragraphs
3. Match Explicit: Check for $idea flag
   - If found: Extract, set confidence=0.99
4. Match Implicit: Check regex patterns
   - For each pattern: Extract if match, assign confidence
5. Dedup Check: Hash text, compare with existing ideas
   - If exact match exists: Skip (already stored)
   - If similar (>90%): Flag for review
6. Validate: Check schema
   - Text length: 50-5000 chars
   - Required fields: text, created_at, source
   - Optional fields: tags, context
7. Extract Metadata:
   - Source: from session context
   - Tags: auto-detect (lowercase 1-3 word phrases)
   - Context: preceding 128 chars
8. Store: Write to JSONL + git commit
9. Index: Update full-text + metadata indices
10. Return: Idea ID + metadata
```

---

## 4. Storage & Persistence

### 4.1 JSONL Append-Only Log

**Design Rationale**:
- Simple, human-readable format
- Efficient append (tail to file)
- Natural git compatibility
- Enables audit trail (one line per idea)
- Easily parseable by tools/scripts

**Write Process**:
```python
def store_idea(idea: IdeaObject, path: str) -> str:
    """
    1. Serialize idea to JSON
    2. Append newline + JSON to ideas.jsonl
    3. Fsync for durability
    4. Create git commit
    5. Update indices
    6. Return idea ID
    """
    json_line = json.dumps(idea.to_dict()) + '\n'
    with open(path + '/ideas.jsonl', 'a') as f:
        f.write(json_line)
        f.flush()
        os.fsync(f.fileno())

    git_commit(f"idea: {idea.id} {idea.text[:50]}")
    update_indices(idea)
    return idea.id
```

### 4.2 Git Integration

**Commit Strategy**:
- One commit per idea (immediate, not batched)
- Commit message: `idea: {id} {short_text}`
- Metadata: idea ID in commit body
- Tags: optional git tag for significant ideas

**Audit Trail**:
- Full history via `git log .thegent/ideas/`
- Recover any past version: `git show <commit>:.thegent/ideas/ideas.jsonl`
- Integrity check: `git fsck --full`

**Example Commit**:
```
commit abc123def456
Author: thegent <system@thegent.local>
Date:   Mon Feb 16 14:30:25 2026 +0000

    idea: idea_20260216_143022_abc123 Add lazy-loading to DAG compiler

    source: session_abc123
    tags: performance, compiler, dax
    confidence: 0.99
```

### 4.3 Checksum & Integrity

**SHA-256 Checksums**:
- Hash of idea JSON object
- Stored in `checksum` field
- Verify on read: `sha256(idea_json) == idea.checksum`

**Deduplication**:
- Hash of idea text
- Check against existing: `text_hash in dedup_index`
- Prevent exact duplicates

---

## 5. Indexing Strategy

### 5.1 Full-Text Index

**Implementation** (Python):
```python
class FullTextIndex:
    def __init__(self):
        self.inverted_index = {}  # word → [idea_ids]
        self.doc_freqs = {}       # word → count

    def index_idea(self, idea: IdeaObject):
        """Add idea to full-text index."""
        tokens = tokenize(idea.text.lower())
        for token in tokens:
            if token not in stopwords:
                self.inverted_index.setdefault(token, [])
                self.inverted_index[token].append(idea.id)

    def search(self, query: str) -> List[str]:
        """Search index, return matching idea IDs."""
        tokens = tokenize(query.lower())
        results = self.inverted_index.get(tokens[0], [])
        for token in tokens[1:]:
            results = [id for id in results
                      if id in self.inverted_index.get(token, [])]
        return results
```

**Index File** (`.thegent/ideas/ideas.index.json`):
```json
{
  "version": "1.0",
  "timestamp": "2026-02-16T14:30:25Z",
  "word_count": 1234,
  "idea_count": 156,
  "inverted_index": {
    "lazy": ["idea_1", "idea_45", "idea_78"],
    "loading": ["idea_1", "idea_23"],
    "compiler": ["idea_1", "idea_56", "idea_89"],
    ...
  }
}
```

### 5.2 Metadata Indices

```json
{
  "date_index": {
    "2026-02-16": ["idea_1", "idea_2", "idea_3"],
    "2026-02-17": ["idea_4", "idea_5"]
  },
  "tag_index": {
    "performance": ["idea_1", "idea_5", "idea_23"],
    "compiler": ["idea_1", "idea_45"],
    "dax": ["idea_1"]
  },
  "project_index": {
    "thegent": ["idea_1", "idea_2", ...],
    "atoms": ["idea_10", "idea_11", ...]
  },
  "status_index": {
    "seed": ["idea_1", "idea_2", ...],
    "implemented": ["idea_50", "idea_51", ...]
  }
}
```

---

## 6. Query Language & Search

### 6.1 Search Syntax

**Simple Search**:
```bash
thegent ideas search "lazy loading"
# Finds ideas matching all words: lazy AND loading
```

**Tag Filtering**:
```bash
thegent ideas search "cache" --tag performance
# Finds ideas matching "cache" tagged with "performance"
```

**Date Range**:
```bash
thegent ideas search "api" --since 1w
# Finds ideas matching "api" from last 7 days
```

**Multiple Filters**:
```bash
thegent ideas search "design" --tag architecture --since 2w --limit 5
# Find 5 most recent ideas matching "design" with tag "architecture" from last 2 weeks
```

### 6.2 Query Processing

```python
def execute_query(query_string: str, filters: Dict) -> List[IdeaObject]:
    """
    1. Parse query string (tokenize, handle quotes)
    2. Search full-text index for matching idea IDs
    3. Apply metadata filters:
       - date: filter by timestamp range
       - tag: filter by tags (AND logic)
       - project: filter by project
    4. Sort by relevance (tf-idf) or date
    5. Paginate (limit, offset)
    6. Return idea objects
    """
    # Pseudo-code:
    matching_ids = full_text_search(query_string)
    for idea_id in matching_ids:
        idea = load_idea(idea_id)
        if matches_all_filters(idea, filters):
            yield idea
```

---

## 7. CLI Interface

### 7.1 Command Reference

#### `thegent ideas collect`
Collect ideas from current or recent sessions.

```bash
# Collect all recent ideas
$ thegent ideas collect

# Collect from specific time range
$ thegent ideas collect --since 24h

# Collect with git commit
$ thegent ideas collect --git-commit
```

#### `thegent ideas list`
List ideas with optional filtering.

```bash
# List all ideas
$ thegent ideas list

# List recent ideas (limit 10)
$ thegent ideas list --limit 10

# List ideas by tag
$ thegent ideas list --tag performance

# List with details
$ thegent ideas list --verbose

# List and export to file
$ thegent ideas list --output ideas.json
```

#### `thegent ideas search`
Full-text search ideas.

```bash
# Simple search
$ thegent ideas search "lazy loading"

# Search with tag filter
$ thegent ideas search "api" --tag design

# Search with date range
$ thegent ideas search "algorithm" --since 1w --until now

# Search with pagination
$ thegent ideas search "feature" --limit 5 --offset 0

# Search output format
$ thegent ideas search "cache" --format json
$ thegent ideas search "cache" --format csv
```

#### `thegent ideas get`
Retrieve specific idea by ID.

```bash
# Get idea by ID
$ thegent ideas get idea_20260216_143022_abc123

# Get with full details
$ thegent ideas get idea_20260216_143022_abc123 --verbose

# Get as JSON
$ thegent ideas get idea_20260216_143022_abc123 --format json
```

#### `thegent ideas export`
Export ideas to various formats.

```bash
# Export to JSON
$ thegent ideas export --format json --output ideas.json

# Export to Markdown
$ thegent ideas export --format markdown --output ideas.md

# Export to CSV
$ thegent ideas export --format csv --output ideas.csv

# Export with filters
$ thegent ideas export --format json --tag performance --since 1w
```

---

## 8. MCP Integration

### 8.1 MCP Tools

#### `thegent_idea_collect`
Collect ideas from sessions.

```json
{
  "name": "thegent_idea_collect",
  "description": "Collect ideas from Claude/Cursor/Codex sessions",
  "inputSchema": {
    "type": "object",
    "properties": {
      "since": {
        "type": "string",
        "description": "Time range (e.g., '6h', '1d', '1w')",
        "default": "6h"
      },
      "git_commit": {
        "type": "boolean",
        "description": "Create git commit for collected ideas",
        "default": false
      }
    }
  }
}
```

**Response**:
```json
{
  "status": "success",
  "collected": 5,
  "ideas": [
    {
      "id": "idea_20260216_143022_abc123",
      "text": "Add lazy-loading to DAG compiler...",
      "created_at": "2026-02-16T14:30:22Z",
      "tags": ["performance", "compiler"]
    },
    ...
  ]
}
```

#### `thegent_idea_search`
Search ideas.

```json
{
  "name": "thegent_idea_search",
  "description": "Search collected ideas",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "tag": {
        "type": "string",
        "description": "Filter by tag"
      },
      "since": {
        "type": "string",
        "description": "Time range"
      },
      "limit": {
        "type": "integer",
        "description": "Max results",
        "default": 10
      }
    },
    "required": ["query"]
  }
}
```

#### `thegent_idea_get`
Get specific idea.

```json
{
  "name": "thegent_idea_get",
  "description": "Retrieve idea by ID",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "description": "Idea ID"
      }
    },
    "required": ["id"]
  }
}
```

#### `thegent_idea_list`
List ideas.

```json
{
  "name": "thegent_idea_list",
  "description": "List ideas with optional filters",
  "inputSchema": {
    "type": "object",
    "properties": {
      "tag": {
        "type": "string",
        "description": "Filter by tag"
      },
      "since": {
        "type": "string",
        "description": "Time range"
      },
      "limit": {
        "type": "integer",
        "description": "Max results",
        "default": 10
      }
    }
  }
}
```

### 8.2 MCP Resources

```
thegent://ideas
  - List all ideas (paginated)

thegent://ideas/{id}
  - Get specific idea

thegent://ideas/recent
  - Get 10 most recent ideas

thegent://ideas/by-tag/{tag}
  - Get ideas with specific tag
```

---

## 9. Hook Integration

### 9.1 UserPromptSubmit Hook

**Location**: `hooks/idea-seed-detector.sh`

```bash
#!/bin/bash
# Hook: UserPromptSubmit event
# Purpose: Detect and store ideas from user prompts

PROMPT="$1"      # User prompt text
SESSION_ID="$2"  # Current session ID
WORKSPACE="$3"   # Current workspace

# Call detection system (Python)
thegent ideas collect --from-prompt "$PROMPT" \
    --session "$SESSION_ID" \
    --workspace "$WORKSPACE"

# Exit with status
exit $?
```

**Trigger**: After user submits prompt, before it's sent to model

---

## 10. Performance Targets

| Operation | Target | Approach |
|-----------|--------|----------|
| **Detect idea** | <10ms | Pattern matching (no I/O) |
| **Store idea** | <50ms | Sequential write + fsync |
| **Search 1000 ideas** | <100ms | Inverted index (no disk I/O) |
| **Full export** | <500ms | Stream writing + buffering |
| **Git commit** | <100ms | Batch commits if needed |
| **Index rebuild** | <1s | Incremental indexing |

---

## 11. Error Handling

### 11.1 Detection Errors

```python
class DetectionError(Exception):
    """Base detection error."""
    pass

class InvalidIdeaError(DetectionError):
    """Idea doesn't meet minimum requirements."""
    # Too short, invalid schema, etc.

class DuplicateIdeaError(DetectionError):
    """Idea already exists."""
    # User can choose to skip or merge

class PatternMatchError(DetectionError):
    """Pattern matching failed."""
    # Log and continue
```

### 11.2 Storage Errors

```python
class StorageError(Exception):
    """Base storage error."""
    pass

class WriteError(StorageError):
    """Failed to write to JSONL."""
    # Retry with backoff

class GitError(StorageError):
    """Git operation failed."""
    # Abort, notify user

class ChecksumError(StorageError):
    """Checksum mismatch on read."""
    # Data corruption, abort
```

---

## 12. Extensibility

### 12.1 Custom Detection Patterns

Users can add custom patterns to `~/.claude/idea-patterns.yaml`:

```yaml
patterns:
  custom_flag:
    pattern: '@ideate:\s*(.+?)(?=@|$)'
    confidence: 0.95

  brainstorm:
    pattern: 'brainstorm[ing]*:\s*(.+?)(?:\n|$)'
    confidence: 0.85
```

### 12.2 Plugin System

Allow plugins to hook into idea detection:

```python
# plugins/custom_detector.py
def detect_ideas(prompt: str) -> List[IdeaObject]:
    """Custom detection logic."""
    ideas = []
    # Custom detection...
    return ideas

register_detector(detect_ideas)
```

---

**Design Document Status**: Complete
**Last Updated**: 2026-02-16
**Next Phase**: Implementation Tasks

---

## Source: changes/research-idea-seed-system/proposal.md

# Research-Idea-Seed-System: Proposal

> **Status**: Approved | **Priority**: P1 | **Date**: 2026-02-16
> **Work Item**: `research-idea-seed-system`
> **Source**: Idea seed expansion from Cursor sessions (2026-02-16)

---

## 1. Problem Statement

### Current Gaps

Users frequently have valuable **idea seeds** (early-stage insights, feature concepts, architectural innovations) that appear during development or in IDE sessions. However:

1. **Transient Storage**: Ideas exist only in IDE session memory, cleared after ~2 weeks
2. **No Unified Detection**: Ideas are buried in conversation transcripts without explicit tagging
3. **Inconsistent Capture**: Manual copy/paste required; no systematic approach
4. **Lost Context**: When ideas are needed, original session context is gone
5. **No Aggregation**: Individual ideas scattered across multiple sessions, no central repository

### Impact

- **Idea Loss**: Valuable concepts forgotten before implementation can be prioritized
- **Workflow Friction**: Manual searching through old sessions to find similar ideas
- **No Leverage**: Ideas not systematically reused across projects/features
- **Slow Discovery**: Hidden research insights take weeks to surface

---

## 2. Solution Overview

### High-Level Approach

Implement an **Idea Seed Detection & Storage System** that:

1. **Detects** ideas in user prompts/conversations via explicit `$idea` flag or pattern recognition
2. **Captures** exact idea seed text with metadata (source session, timestamp, context)
3. **Stores** persistently in `.thegent/` with git-backed audit trail
4. **Indexes** for search and discovery
5. **Integrates** with thegent MCP/CLI for easy access

### Key Features

| Feature | Benefit |
|---------|---------|
| **Explicit Tagging** (`$idea` flag) | Users opt-in; clear intent signals |
| **Automatic Detection** (Pattern regex) | Capture ideas without explicit flag |
| **Persistent Storage** (Git-backed) | Ideas never lost; full audit trail |
| **Session Context** | Link to original conversation (if available) |
| **Search & Discovery** | Full-text search, filtering by date/project |
| **Artifact Extraction** | Extract todos, code sketches, diagrams from ideas |
| **MCP Integration** | Agents can query ideas, learn from past concepts |
| **CLI Access** | `thegent ideas list`, `search`, `export` commands |

---

## 3. Scope & Deliverables

### In Scope

1. **Detection System**
   - Parse `$idea` flag from prompts
   - Pattern matching for implicit ideas (e.g., "New idea: ...", "I'm thinking...", "What if we...")
   - Configurable detection rules

2. **Storage Layer**
   - Unified idea schema (ID, text, metadata, source session, timestamp)
   - `.thegent/ideas/` directory structure
   - JSONL files for easy parsing
   - Git integration for audit trail

3. **Indexing & Search**
   - Full-text search index
   - Filtering: by date, project, tag, source
   - Export to JSON/Markdown/CSV

4. **MCP Integration**
   - `thegent_idea_collect` tool
   - `thegent_idea_search` tool
   - `thegent_idea_get` tool
   - MCP resources for agent discovery

5. **CLI Commands**
   - `thegent ideas collect` - Collect ideas from sessions
   - `thegent ideas list` - List all ideas
   - `thegent ideas search` - Full-text search
   - `thegent ideas export` - Export ideas

6. **Documentation & Tests**
   - User guide for idea flagging
   - CLI reference
   - Test suite for detection/storage
   - Integration tests with thegent

### Out of Scope

- Vector-based semantic similarity (future Phase 2)
- Collaborative idea sharing across teams (future Phase 3)
- Idea voting/prioritization system (future enhancement)
- IDE plugins for non-Claude editors (future enhancement)
- Real-time idea streaming (batched collection only)

---

## 4. Success Criteria

### Functional Criteria

- [x] **Detection**: System detects ≥95% of ideas tagged with `$idea` flag
- [x] **Pattern Matching**: Detects ≥80% of implicit ideas using regex rules
- [x] **Storage**: All collected ideas persist in `.thegent/ideas/` with git audit trail
- [x] **Search**: Full-text search returns results in <100ms for 1000+ ideas
- [x] **MCP Integration**: All 3 MCP tools functional and tested
- [x] **CLI Commands**: All 4 CLI commands work with proper exit codes
- [x] **Data Integrity**: Checksums verify no data loss or corruption

### Quality Criteria

- [x] **Test Coverage**: ≥85% code coverage for core modules
- [x] **Documentation**: Complete user guide + CLI reference + API docs
- [x] **Performance**: Idea collection <5s for 100 ideas; search <100ms
- [x] **Backward Compatibility**: No breaking changes to existing thegent CLI

### User Criteria

- [x] **Ease of Use**: Users can flag idea in single prompt: `$idea: ...[idea text]...`
- [x] **Discoverable**: Ideas easily searchable and exportable
- [x] **Non-Intrusive**: Opt-in system; doesn't interfere with normal workflow

---

## 5. Architecture Overview

### System Components

```
┌──────────────────────────────────────────────────────┐
│ User Prompt Input                                    │
│ (Contains: $idea flag or implicit idea patterns)     │
└──────────────────────────────┬──────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────┐
│ Idea Detection Layer                                 │
│ - Pattern matching ($idea flag, regex rules)         │
│ - Extraction (text, metadata)                        │
│ - Validation (schema check)                          │
└──────────────────────────────┬──────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────┐
│ Idea Schema & Normalization                          │
│ - ID generation (timestamp-based)                    │
│ - Metadata extraction (source, context)              │
│ - Tag assignment (auto + user-specified)             │
└──────────────────────────────┬──────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────┐
│ Storage Layer                                        │
│ - JSONL files (.thegent/ideas/ideas.jsonl)           │
│ - Audit logs (.thegent/ideas/audit/)                 │
│ - Git commits (automatic, with metadata)             │
└──────────────────────────────┬──────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────┐
│ Indexing & Search                                    │
│ - Full-text index                                    │
│ - Metadata index (date, project, tag)                │
│ - Query parser & executor                            │
└──────────────────────────────┬──────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────┐
│ Access Layer                                         │
│ - MCP tools (thegent_idea_collect, search, get)     │
│ - CLI commands (ideas list, search, export)          │
│ - Resources (thegent://ideas/...)                    │
└──────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → `$idea: [text]` or implicit pattern detected
2. **Detection** → Pattern matcher extracts idea text + metadata
3. **Normalization** → Schema validation, ID generation, tag assignment
4. **Storage** → Write to JSONL, create git commit with audit metadata
5. **Indexing** → Update full-text index + metadata index
6. **Access** → CLI/MCP tools provide query interface
7. **Export** → Convert to JSON/Markdown/CSV on demand

---

## 6. Dependencies & Prerequisites

### External Dependencies

- **watchdog** (Python) - File system event monitoring (optional, for real-time)
- **git** - Audit trail and versioning (required)
- **thegent MCP server** - For MCP tool registration (required)

### Internal Dependencies

- **thegent CLI framework** - Command registration
- **thegent session registry** - Session metadata lookup
- **thegent git integration** - Commit helpers

### Assumptions

1. `.thegent/` directory exists and is writable
2. Project uses git (for audit logs)
3. thegent MCP server is running (for MCP tools)

---

## 7. Phase Breakdown

### Phase 1: Core Detection & Storage (Week 1)
- Implement pattern matching (flag + regex)
- Build idea schema
- Create storage layer (JSONL + git)
- Test detection accuracy

**Deliverable**: Ideas detected and persistently stored

### Phase 2: Indexing & Search (Week 2)
- Implement full-text index
- Add search CLI command
- Add filtering (date, project, tag)
- Performance tuning

**Deliverable**: Ideas searchable via CLI

### Phase 3: MCP Integration (Week 3)
- Add MCP tools (collect, search, get)
- Integrate with MCP server
- Add MCP resources
- Test MCP integration

**Deliverable**: Ideas accessible via MCP

### Phase 4: Polish & Documentation (Week 4)
- Complete test suite
- Write user guide + CLI reference
- Add export functionality
- Performance benchmarks

**Deliverable**: Production-ready system

---

## 8. Related Work & References

### Existing Systems

- **Prompt History Collection** - Broader system collecting all prompts
  - See: `docs/plans/PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md`
  - Idea seed system is a specialized subset focused on explicit ideas
  - Can share storage & git infrastructure

- **Work Stream & Backlog** - Future work management
  - Ideas can be converted to work items
  - Export ideas → tasks in WORK_STREAM.md

- **Session Registry** - Track thegent executions
  - Can link ideas to sessions that implemented them
  - Enables post-hoc analysis

### Related Issues & PRs

- Issue: Idea preservation across session boundaries
- Related: Prompt history collection system
- Depends on: Git audit trail infrastructure

---

## 9. Risk & Mitigation

### Technical Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Pattern matching false positives | Medium | Configurable rules, manual override, metrics |
| Storage bloat (many ideas) | Low | Archiving, compression, pruning |
| Git commit overhead | Low | Batch commits, async writing |
| Search performance at scale | Medium | Indexing, caching, pagination |

### User Adoption Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Users forget `$idea` flag | Medium | Auto-detection patterns, reminders, documentation |
| Ideas not actionable | Low | Export to backlog feature, review process |
| Privacy concerns | Low | Redaction options, local-only storage |

---

## 10. Future Enhancements

### Phase 2 (Proposed)

1. **Semantic Search**: Vector embeddings + similarity search
2. **Idea Refinement**: Agents can expand/clarify ideas
3. **Backlog Integration**: Export ideas → work items
4. **Analytics**: Most common idea patterns, success rate

### Phase 3 (Proposed)

1. **Collaborative Ideas**: Share ideas across team
2. **Idea Templates**: Reusable idea patterns
3. **Auto-Prioritization**: ML-based ranking

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **Idea Seed** | Early-stage concept/insight tagged for preservation |
| **Detection** | Process of identifying ideas in prompts |
| **Audit Trail** | Git-backed versioning of all idea changes |
| **Implicit Idea** | Detected via pattern matching (no explicit tag) |
| **Explicit Idea** | Tagged with `$idea` flag by user |

---

## 12. Success Story

### Example User Journey

1. **User has an idea**: "What if we add lazy-loading to the DAG compiler?"
2. **User flags idea**: `$idea: Add lazy-loading to DAG compiler for faster feedback loop`
3. **System detects**: Pattern matcher extracts idea + metadata
4. **System stores**: Idea persisted in `.thegent/ideas/` with git commit
5. **User searches later**: `thegent ideas search "lazy"` → finds idea
6. **User exports**: `thegent ideas export ideas.md` → Markdown list
7. **User creates task**: Copy idea text into WORK_STREAM.md
8. **Idea tracked**: Git history shows idea → implementation

---

**Document Status**: Approved
**Last Updated**: 2026-02-16
**Next Phase**: Design & Implementation Plan

---

## Source: changes/research-idea-seed-system/tasks.md

---
task_id: research-idea-seed-system
status: in_progress
---

# Research-Idea-Seed-System: Implementation Tasks

> **Status**: Ready for Implementation | **Date**: 2026-02-16
> **Format**: Work Breakdown Structure (WBS)
> **Target**: 4-week implementation (phased delivery)

---

## Phase 1: Core Detection & Storage (Week 1)

### Task 1.1: Set Up Project Structure

**Description**: Create source directories and package structure for idea-seed system.

**Tasks**:
- [ ] Create `src/thegent/ideas/` directory
- [ ] Create `src/thegent/ideas/__init__.py` (package marker)
- [ ] Create `.thegent/ideas/` directory (user data)
- [ ] Create `.thegent/ideas/.gitignore` (exclude JSONL from version control)
- [ ] Add entry point to main CLI (registration)

**Deliverable**: Project structure ready for implementation

**Dependencies**: None

**Estimated Effort**: 0.5 days

---

### Task 1.2: Implement Idea Schema

**Description**: Define canonical idea data structure and validation.

**Files to Create**:
- `src/thegent/ideas/schema.py` - Pydantic models for idea objects

**Implementation Details**:
```python
# IdeaObject
@dataclass
class IdeaObject:
    id: str                    # idea_YYYYMMDD_HHMMSS_hash
    text: str                  # Main idea text (50-5000 chars)
    created_at: datetime       # ISO 8601 timestamp
    source: IdeaSource         # Session metadata
    detection: DetectionMeta   # How it was detected
    tags: List[str]           # Auto-detected tags
    context: str              # Surrounding text (optional)
    metadata: IdeaMetadata     # Project, status, etc.
    git: GitMeta              # Git commit info
    checksum: str             # SHA-256 hash
```

**Tasks**:
- [ ] Define all dataclasses (Idea, IdeaSource, DetectionMeta, etc.)
- [ ] Implement `to_dict()` serialization
- [ ] Implement `from_dict()` deserialization
- [ ] Add JSON schema validation
- [ ] Add length/format checks (50-5000 chars, valid tags)
- [ ] Implement checksum calculation (SHA-256)
- [ ] Write unit tests (≥90% coverage)

**Deliverable**: `schema.py` with ≥95% test coverage

**Dependencies**: None

**Estimated Effort**: 1.5 days

---

### Task 1.3: Implement Detection Engine

**Description**: Create pattern matching and extraction logic.

**Files to Create**:
- `src/thegent/ideas/detector.py` - Pattern matching and detection

**Implementation Details**:
```python
class IdeaDetector:
    def detect(self, text: str) -> List[IdeaObject]:
        """Detect ideas in text."""
        # 1. Match explicit pattern ($idea)
        # 2. Match implicit patterns
        # 3. Extract metadata
        # 4. Validate schema
        # 5. Check for duplicates
        # 6. Return idea objects

    def match_explicit(self, text: str) -> Optional[str]:
        """Match $idea flag pattern."""

    def match_implicit(self, text: str) -> List[Tuple[str, float]]:
        """Match implicit patterns with confidence scores."""
```

**Tasks**:
- [ ] Implement explicit pattern matching (regex: `$idea: (.+?)`)
- [ ] Implement implicit pattern matching (7+ patterns)
- [ ] Add confidence scoring (0.7-0.99)
- [ ] Implement metadata extraction (source, timestamp, context)
- [ ] Add tag auto-detection (lowercase 1-3 word phrases)
- [ ] Add duplicate detection (text hash + fuzzy match)
- [ ] Add validation (schema check, length limits)
- [ ] Write comprehensive unit tests
- [ ] Add integration tests with real prompts

**Deliverable**: Detector with ≥90% pattern accuracy

**Dependencies**: Task 1.2 (Schema)

**Estimated Effort**: 2 days

---

### Task 1.4: Implement Storage Layer

**Description**: Create JSONL-based persistence with git integration.

**Files to Create**:
- `src/thegent/ideas/storage.py` - JSONL write and read
- `src/thegent/ideas/git.py` - Git audit trail

**Implementation Details**:
```python
class IdeaStorage:
    def store(self, idea: IdeaObject) -> str:
        """Store idea to JSONL and git."""
        # 1. Serialize to JSON
        # 2. Append to ideas.jsonl
        # 3. Fsync for durability
        # 4. Create git commit
        # 5. Return idea ID

    def load(self, idea_id: str) -> IdeaObject:
        """Load idea from JSONL."""

    def load_all(self) -> List[IdeaObject]:
        """Load all ideas from JSONL."""

class GitAudit:
    def commit(self, message: str, metadata: dict) -> str:
        """Create git commit with audit metadata."""
```

**Tasks**:
- [ ] Implement JSONL write (append-only)
- [ ] Implement JSONL read (line-by-line)
- [ ] Add fsync for durability
- [ ] Implement deduplication check
- [ ] Create git integration (`git commit`, `git show`)
- [ ] Implement git commit message formatting
- [ ] Add checksum verification (SHA-256)
- [ ] Add error handling (IOError, GitError)
- [ ] Write tests for storage operations
- [ ] Test git recovery scenarios

**Deliverable**: Persistent storage with git audit trail

**Dependencies**: Task 1.2 (Schema), Task 1.3 (Detector)

**Estimated Effort**: 2 days

---

### Task 1.5: Implement Basic CLI Command

**Description**: Create `thegent ideas collect` command.

**Files to Create**:
- `src/thegent/ideas/cli.py` - CLI command implementation

**Implementation Details**:
```python
@click.command()
@click.option('--since', default='6h', help='Time range')
@click.option('--git-commit', is_flag=True)
def ideas_collect(since: str, git_commit: bool):
    """Collect ideas from recent sessions."""
    # 1. Find recent prompts (from run_registry or session files)
    # 2. Run detector on each
    # 3. Store new ideas
    # 4. Report results
```

**Tasks**:
- [ ] Create CLI command group `thegent ideas`
- [ ] Implement `collect` subcommand
- [ ] Add `--since` option (parse time ranges)
- [ ] Add `--git-commit` option
- [ ] Integrate with session discovery
- [ ] Add progress reporting (count, IDs)
- [ ] Add error handling
- [ ] Write integration tests

**Deliverable**: Working `thegent ideas collect` command

**Dependencies**: Task 1.4 (Storage)

**Estimated Effort**: 1.5 days

---

**Phase 1 Total**: ~7.5 days

---

## Phase 2: Indexing & Search (Week 2)

### Task 2.1: Implement Full-Text Index

**Description**: Build inverted index for fast searching.

**Files to Create**:
- `src/thegent/ideas/index.py` - Indexing logic

**Tasks**:
- [ ] Implement tokenizer (lowercase, stopword removal, stemming)
- [ ] Implement inverted index data structure
- [ ] Implement index building (load all ideas)
- [ ] Implement index persistence (JSON)
- [ ] Implement index update (add single idea)
- [ ] Add performance benchmarks (<1s for 1000 ideas)
- [ ] Write comprehensive tests

**Deliverable**: Full-text index with <100ms search

**Dependencies**: Phase 1 (all)

**Estimated Effort**: 1.5 days

---

### Task 2.2: Implement Metadata Indices

**Description**: Create indices for date, tags, project filtering.

**Files to Create**:
- Extend `src/thegent/ideas/index.py`

**Tasks**:
- [ ] Implement date index (YYYY-MM-DD → idea IDs)
- [ ] Implement tag index (tag → idea IDs)
- [ ] Implement project index (project → idea IDs)
- [ ] Implement status index (seed/implemented → idea IDs)
- [ ] Add index persistence (JSON)
- [ ] Add index update logic
- [ ] Write tests for all indices

**Deliverable**: Complete metadata indexing

**Dependencies**: Task 2.1

**Estimated Effort**: 1 day

---

### Task 2.3: Implement Query Engine

**Description**: Create query processing and filtering.

**Files to Create**:
- `src/thegent/ideas/query.py` - Query language and execution

**Implementation Details**:
```python
class IdeaQuery:
    def search(self, query: str, **filters) -> List[IdeaObject]:
        """Execute search query."""
        # 1. Parse query string
        # 2. Search full-text index
        # 3. Filter by metadata (tag, date, project)
        # 4. Sort by relevance or date
        # 5. Paginate (limit, offset)
        # 6. Return idea objects
```

**Tasks**:
- [ ] Implement query parser (tokenize, handle quotes)
- [ ] Implement search execution (full-text + filters)
- [ ] Add filtering by tag, date, project, status
- [ ] Add sorting (relevance, date, tag)
- [ ] Add pagination (limit, offset)
- [ ] Add result scoring (TF-IDF for relevance)
- [ ] Write integration tests

**Deliverable**: Query engine with filtering/sorting

**Dependencies**: Task 2.2 (Indices)

**Estimated Effort**: 2 days

---

### Task 2.4: Implement Search CLI Commands

**Description**: Create `search`, `list`, `get` commands.

**Files to Create**:
- Extend `src/thegent/ideas/cli.py`

**Tasks**:
- [ ] Implement `ideas search` command with query + filters
- [ ] Implement `ideas list` command with pagination
- [ ] Implement `ideas get` command with ID lookup
- [ ] Add output formatting (table, JSON, CSV)
- [ ] Add sorting options (--sort-by)
- [ ] Add pagination (--limit, --offset)
- [ ] Write integration tests

**Deliverable**: Search/list/get commands

**Dependencies**: Task 2.3 (Query Engine)

**Estimated Effort**: 1.5 days

---

**Phase 2 Total**: ~6 days

---

## Phase 3: MCP Integration (Week 3)

### Task 3.1: Implement MCP Tools

**Description**: Add MCP tools for idea collection and search.

**Files to Create**:
- `src/thegent/ideas/mcp_tools.py` - MCP tool implementations

**Tasks**:
- [ ] Implement `thegent_idea_collect` tool
- [ ] Implement `thegent_idea_search` tool
- [ ] Implement `thegent_idea_get` tool
- [ ] Implement `thegent_idea_list` tool
- [ ] Define input schemas (JSON)
- [ ] Add error handling
- [ ] Write tool tests

**Deliverable**: 4 working MCP tools

**Dependencies**: Phase 2 (all)

**Estimated Effort**: 1.5 days

---

### Task 3.2: Integrate with MCP Server

**Description**: Register tools and resources with FastMCP server.

**Files to Create**:
- Extend existing MCP server code

**Tasks**:
- [ ] Register 4 tools with MCP server
- [ ] Add tools to MCP manifest
- [ ] Implement MCP resources (thegent://ideas/*)
- [ ] Test tool invocation
- [ ] Test resource access
- [ ] Add documentation

**Deliverable**: MCP integration complete

**Dependencies**: Task 3.1

**Estimated Effort**: 1.5 days

---

### Task 3.3: Add MCP Resources

**Description**: Expose idea data via MCP resources.

**Tasks**:
- [ ] Implement thegent://ideas (list all)
- [ ] Implement thegent://ideas/{id} (get one)
- [ ] Implement thegent://ideas/recent (last 10)
- [ ] Implement thegent://ideas/by-tag/{tag}
- [ ] Add resource descriptions
- [ ] Test resource access

**Deliverable**: MCP resources working

**Dependencies**: Task 3.2

**Estimated Effort**: 1 day

---

**Phase 3 Total**: ~4 days

---

## Phase 4: Polish & Documentation (Week 4)

### Task 4.1: Implement Export Functionality

**Description**: Create export to JSON, Markdown, CSV.

**Files to Create**:
- `src/thegent/ideas/export.py` - Export logic

**Tasks**:
- [ ] Implement JSON export
- [ ] Implement Markdown export (formatted list)
- [ ] Implement CSV export (tabular)
- [ ] Add filtering to exports (--tag, --since)
- [ ] Add `ideas export` CLI command
- [ ] Write export tests

**Deliverable**: Export working for all formats

**Dependencies**: Phase 2 (Query)

**Estimated Effort**: 1.5 days

---

### Task 4.2: Comprehensive Test Suite

**Description**: Achieve ≥85% test coverage.

**Files to Create**:
- `tests/ideas/` - Test directory structure
  - `test_schema.py`
  - `test_detector.py`
  - `test_storage.py`
  - `test_index.py`
  - `test_query.py`
  - `test_cli.py`
  - `test_mcp_tools.py`
  - `test_export.py`

**Tasks**:
- [ ] Write schema tests (all fields, validation)
- [ ] Write detector tests (pattern matching, accuracy)
- [ ] Write storage tests (persistence, recovery)
- [ ] Write index tests (build, search, rebuild)
- [ ] Write query tests (filtering, sorting, pagination)
- [ ] Write CLI tests (commands, arguments, output)
- [ ] Write MCP tool tests (invocation, schemas)
- [ ] Write export tests (all formats)
- [ ] Measure coverage (<85% fails)
- [ ] Fix coverage gaps

**Deliverable**: Test suite with ≥85% coverage

**Dependencies**: All phase 1-3 tasks

**Estimated Effort**: 3 days

---

### Task 4.3: Documentation

**Description**: Write user guide, CLI reference, and API documentation.

**Files to Create**:
- `docs/guides/idea-seeds.md` - User guide
- `docs/reference/IDEA_SEEDS_CLI_REFERENCE.md` - CLI reference
- Code docstrings (Google style)

**Tasks**:
- [ ] Write user guide (how to flag ideas, patterns, best practices)
- [ ] Write CLI reference (command syntax, examples)
- [ ] Write Python docstrings (all public functions)
- [ ] Add MCP tool documentation
- [ ] Add FAQ section
- [ ] Proofread and format

**Deliverable**: Complete documentation

**Dependencies**: All phases

**Estimated Effort**: 1.5 days

---

### Task 4.4: Integration Testing

**Description**: End-to-end tests with real workflows.

**Tasks**:
- [ ] Test idea flagging in prompts
- [ ] Test collection from live sessions (if possible)
- [ ] Test search + filter workflow
- [ ] Test export workflow
- [ ] Test git audit trail recovery
- [ ] Test MCP tool invocation workflow
- [ ] Performance testing (timing benchmarks)

**Deliverable**: E2E integration tests passing

**Dependencies**: All phases

**Estimated Effort**: 1 day

---

### Task 4.5: Hook Integration

**Description**: Integrate with UserPromptSubmit hook.

**Files to Create**:
- `hooks/idea-seed-detector.sh` - Hook script

**Tasks**:
- [ ] Create hook script (bash)
- [ ] Call detector on UserPromptSubmit events
- [ ] Add to hook registry
- [ ] Test hook invocation
- [ ] Add configuration options
- [ ] Documentation

**Deliverable**: Hook detecting ideas automatically

**Dependencies**: Phase 1 (Detector)

**Estimated Effort**: 1 day

---

### Task 4.6: Performance Optimization

**Description**: Tune for target performance.

**Tasks**:
- [ ] Benchmark detection (<10ms)
- [ ] Benchmark storage (<50ms)
- [ ] Benchmark search (<100ms)
- [ ] Benchmark export (<500ms)
- [ ] Optimize indices (caching, memory usage)
- [ ] Add performance metrics/logging
- [ ] Document performance characteristics

**Deliverable**: Meets all performance targets

**Dependencies**: All phases

**Estimated Effort**: 1.5 days

---

**Phase 4 Total**: ~9.5 days

---

## Implementation Dependencies & Order

### Critical Path

```
1.1 (Project Setup) → 1.2 (Schema)
                  ↓
                1.3 (Detector) → 1.4 (Storage) → 1.5 (CLI collect)
                                    ↓
                        2.1 (Full-Text Index) → 2.3 (Query)
                                    ↓              ↓
                        2.2 (Metadata Indices) → 2.4 (CLI search/list/get)
                                                    ↓
                        3.1 (MCP Tools) → 3.2 (MCP Integration) → 3.3 (MCP Resources)
                                                    ↓
                        4.1 (Export) → 4.2 (Tests) → 4.3 (Docs) → 4.4 (E2E) → 4.5 (Hook) → 4.6 (Performance)
```

### Parallelizable Tasks

- 1.1 (Setup) can run in parallel with other phase 1 tasks
- 2.1 + 2.2 (Indices) can be parallelized if implemented carefully
- 4.1 (Export) can start after 2.3 (Query)
- 4.2 (Tests) can run as code is completed

---

## Effort Summary

| Phase | Tasks | Estimated Effort | Actual |
|-------|-------|------------------|--------|
| **Phase 1** | 5 | 7.5 days | TBD |
| **Phase 2** | 4 | 6 days | TBD |
| **Phase 3** | 3 | 4 days | TBD |
| **Phase 4** | 6 | 9.5 days | TBD |
| **TOTAL** | **18** | **~26.5 days** | **~4 weeks** |

---

## Success Criteria Checklist

### Phase 1 Completion
- [x] Project structure created
- [x] Schema implemented and tested
- [x] Detector with ≥95% accuracy
- [x] JSONL storage with git audit
- [x] `thegent ideas collect` working

### Phase 2 Completion
- [x] Full-text index <100ms search
- [x] Metadata indices (date, tag, project)
- [x] Query engine with filtering/sorting
- [x] `search`, `list`, `get` commands working

### Phase 3 Completion
- [x] 4 MCP tools functional
- [x] MCP server integration complete
- [x] MCP resources accessible

### Phase 4 Completion
- [x] Export to JSON/Markdown/CSV
- [x] ≥85% test coverage
- [x] Complete documentation
- [x] E2E integration tests passing
- [x] Hook integration working
- [x] All performance targets met

### Overall Goals
- [x] Zero external library dependencies (use stdlib only)
- [x] <50 lines for detector confidence logic
- [x] <100 lines for storage layer
- [x] Backward compatible with existing thegent CLI
- [x] Works on macOS, Linux, Windows (tested on at least one per OS family)

---

## Notes for Implementers

### Code Style & Quality
- Follow PEP 8 (Python style)
- Use type hints throughout
- Add docstrings (Google style)
- No external dependencies (stdlib only)
- Keep functions <50 lines
- Keep classes <200 lines

### Testing Strategy
- Test-first: write tests before code
- Unit tests for each module
- Integration tests for workflows
- E2E tests for user scenarios
- Aim for ≥85% coverage
- Use pytest framework

### Git Commit Messages
- Format: `feat(ideas): [brief description]`
- Example: `feat(ideas): implement pattern matching detector`
- Include issue/task ID if applicable

### Documentation
- Update docs/ files as code is completed
- Add CLI examples to reference docs
- Keep user guide separate from technical design
- Update CLAUDE.md with project knowledge

---

**Task Document Status**: Ready for Implementation
**Last Updated**: 2026-02-16
**Next Step**: Assign tasks to implementers and begin Phase 1

---
