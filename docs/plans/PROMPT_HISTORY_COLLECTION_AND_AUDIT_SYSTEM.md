# Prompt History Collection & Audit System: Comprehensive Plan

> **Status**: Research & Design Plan | **Version**: 1.0 | **Date**: 2026-02-16  
> **Purpose**: Standardize prompt collection from Cursor/Codex/Claude, integrate with thegent MCP/CLI, add git-backed audit logs, collect todos/artifacts

---

## Document Index

| § | Section | Content |
|---|---------|---------|
| 1 | Executive Summary | Overview, goals, architecture |
| 2 | Current State Analysis | Existing tools, data locations, gaps |
| 3 | Data Source Locations | Cursor/Codex/Claude storage paths |
| 4 | Standardized Collection System | MCP/CLI commands, data format |
| 5 | Git-Backed Audit Logs | Audit trail, versioning, integrity |
| 6 | Integration Architecture | thegent integration, aggregation |
| 7 | Todo & Artifact Collection | Plan extraction, artifact tracking |
| 8 | Implementation Roadmap | Phased implementation plan |
| 9 | API & CLI Reference | Command reference, examples |

---

## 1. Executive Summary

### 1.1 Goals

1. **Unified Prompt Collection**: Collect prompts from Cursor, Codex, and Claude Code into a single, standardized format
2. **Git-Backed Audit Logs**: All prompts, plans, and artifacts tracked in git with full audit trail
3. **thegent Integration**: MCP tools and CLI commands for easy access and querying
4. **Artifact Aggregation**: Collect todos, plans, and other useful artifacts automatically
5. **Search & Discovery**: Full-text search across all collected prompts and artifacts

### 1.2 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ Data Sources                                             │
├─────────────────────────────────────────────────────────┤
│ Cursor (~/.cursor, ~/Library/Application Support/Cursor)│
│ Codex (~/.codex, ~/Library/Application Support/Codex)   │
│ Claude Code (~/.claude, ~/Library/Application Support) │
└─────────────────────────────────────────────────────────┘
                    ↓ (Collection)
┌─────────────────────────────────────────────────────────┐
│ thegent Prompt Collector                                 │
├─────────────────────────────────────────────────────────┤
│ - Watchers (file system events)                         │
│ - Parsers (JSON, SQLite, log formats)                   │
│ - Normalizers (standardized format)                      │
│ - Validators (data integrity)                            │
└─────────────────────────────────────────────────────────┘
                    ↓ (Storage)
┌─────────────────────────────────────────────────────────┐
│ Unified Storage                                          │
├─────────────────────────────────────────────────────────┤
│ - JSONL files (.thegent/prompts/prompts.jsonl)          │
│ - Git-backed audit logs (.thegent/prompts/audit/)       │
│ - PostgreSQL (optional, for search)                     │
│ - Vector store (optional, for semantic search)           │
└─────────────────────────────────────────────────────────┘
                    ↓ (Access)
┌─────────────────────────────────────────────────────────┐
│ thegent MCP/CLI Interface                               │
├─────────────────────────────────────────────────────────┤
│ - MCP tools: thegent_prompt_search, thegent_prompt_get  │
│ - CLI: thegent prompts collect, search, export          │
│ - Git integration: automatic commits, audit trail       │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Key Features

- **Automatic Collection**: File system watchers detect new prompts
- **Standardized Format**: Unified JSON schema for all prompts
- **Git Integration**: Automatic git commits with audit metadata
- **Full-Text Search**: Search across all collected prompts
- **Artifact Extraction**: Automatically extract todos, plans, code changes
- **Cross-Platform**: Works on macOS, Linux, Windows

---

## 2. Current State Analysis

### 2.1 Existing Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **recall** | Full-text search Claude sessions | External tool, can integrate |
| **claude-code-tools** | Session continuity, Rust/Tantivy search | External tool, can integrate |
| **thegent run_registry.jsonl** | Session tracking | Existing, can extend |

### 2.2 Data Locations

**Cursor**:
- `~/.cursor/` - Config, cache
- `~/Library/Application Support/Cursor/` - Data, logs, sessions
- SQLite databases: `User/globalStorage/` (session data)
- Log files: `logs/` directory

**Codex**:
- `~/.codex/` - Config, cache
- `~/Library/Application Support/Codex/` - Data, logs, sessions
- SQLite databases: Similar to Cursor
- Log files: `logs/` directory

**Claude Code**:
- `~/.claude/` - Config, cache
- `~/Library/Application Support/Claude/` - Data, logs, sessions
- JSONL files: Session transcripts
- Log files: `logs/` directory

### 2.3 Gaps

1. **No Unified Collection**: Each tool stores data separately
2. **No Standardized Format**: Different formats (JSON, SQLite, logs)
3. **No Git Integration**: No audit trail or versioning
4. **No Search**: Difficult to find past prompts
5. **No Artifact Extraction**: Todos, plans not automatically extracted

---

## 3. Data Source Locations

### 3.1 Cursor Storage Paths

**macOS**:
```
~/.cursor/
├── User/
│   ├── globalStorage/          # SQLite databases
│   │   ├── state.vscdb         # Session state
│   │   └── workspaceStorage/   # Workspace-specific data
│   └── settings.json           # User settings
└── logs/
    └── [date]/                 # Daily log files

~/Library/Application Support/Cursor/
├── User/
│   ├── globalStorage/
│   │   ├── cursor.chat/        # Chat history (SQLite)
│   │   └── cursor.agent/       # Agent interactions
│   └── History/                # File history
└── CachedData/                 # Cached data
```

**Linux**:
```
~/.config/Cursor/
~/.local/share/Cursor/
```

**Windows**:
```
%APPDATA%\Cursor\
%LOCALAPPDATA%\Cursor\
```

### 3.2 Codex Storage Paths

**macOS**:
```
~/.codex/
├── config.json                 # Configuration
└── cache/                      # Cache files

~/Library/Application Support/Codex/
├── sessions/                   # Session data
│   └── *.jsonl                # Session transcripts
└── logs/                      # Log files
```

**Linux/Windows**: Similar structure with different base paths

### 3.3 Claude Code Storage Paths

**macOS**:
```
~/.claude/
├── config.json                # Configuration
└── sessions/                   # Session data
    └── *.jsonl                # Session transcripts

~/Library/Application Support/Claude/
├── User/
│   └── globalStorage/         # Global state
└── logs/                      # Log files
```

### 3.4 Data Formats

**SQLite (Cursor)**:
- Tables: `messages`, `sessions`, `workspaces`
- Schema: Varies by Cursor version

**JSONL (Codex/Claude)**:
- Format: One JSON object per line
- Fields: `timestamp`, `role`, `content`, `metadata`

**Log Files**:
- Format: Text logs with timestamps
- Parsing: Regex-based extraction

---

## 4. Standardized Collection System

### 4.1 Data Schema

**Unified Prompt Format** (`prompt.json`):
```json
{
  "id": "prompt_20260216_143022_abc123",
  "timestamp": "2026-02-16T14:30:22Z",
  "source": "cursor",  // "cursor" | "codex" | "claude"
  "session_id": "session_abc123",
  "workspace": "/path/to/workspace",
  "prompt": {
    "text": "Full prompt text",
    "metadata": {
      "model": "claude-3-opus",
      "temperature": 0.7,
      "max_tokens": 4096
    }
  },
  "response": {
    "text": "Response text (if available)",
    "metadata": {
      "tokens_used": 1234,
      "cost": 0.012
    }
  },
  "artifacts": {
    "todos": ["todo1", "todo2"],
    "plans": ["plan1.md"],
    "code_changes": ["file1.py", "file2.py"]
  },
  "git": {
    "commit": "abc123def456",
    "branch": "main",
    "repo": "/path/to/repo"
  }
}
```

### 4.2 Collection Process

**Step 1: Discovery**
- Scan known data locations
- Detect file system changes (watchdog)
- Parse SQLite databases, JSONL files, logs

**Step 2: Normalization**
- Convert to unified format
- Extract metadata
- Validate data integrity

**Step 3: Storage**
- Write to JSONL file (`.thegent/prompts/prompts.jsonl`)
- Create git commit with audit metadata
- Update index for search

**Step 4: Artifact Extraction**
- Extract todos from prompts/responses
- Extract plans (markdown files)
- Track code changes (git diff)

### 4.3 MCP Tools

**`thegent_prompt_collect`**:
- Collect prompts from specified sources
- Options: `--source cursor|codex|claude|all`, `--since <timestamp>`

**`thegent_prompt_search`**:
- Full-text search across collected prompts
- Options: `--query <text>`, `--source <source>`, `--since <timestamp>`

**`thegent_prompt_get`**:
- Get specific prompt by ID
- Options: `--id <prompt_id>`

**`thegent_prompt_export`**:
- Export prompts to various formats
- Options: `--format json|csv|markdown`, `--output <file>`

**`thegent_prompt_artifacts`**:
- Extract artifacts (todos, plans) from prompts
- Options: `--type todo|plan|code`, `--since <timestamp>`

### 4.4 CLI Commands

**`thegent prompts collect`**:
```bash
# Collect all prompts from last 6 hours
thegent prompts collect --since 6h

# Collect from specific source
thegent prompts collect --source cursor --since 1d

# Collect and commit to git
thegent prompts collect --git-commit
```

**`thegent prompts search`**:
```bash
# Search prompts
thegent prompts search "cache implementation"

# Search with filters
thegent prompts search "vector search" --source claude --since 1w
```

**`thegent prompts export`**:
```bash
# Export to JSON
thegent prompts export --format json --output prompts.json

# Export to markdown
thegent prompts export --format markdown --output prompts.md
```

**`thegent prompts artifacts`**:
```bash
# Extract todos
thegent prompts artifacts --type todo --since 1d

# Extract plans
thegent prompts artifacts --type plan --since 1w
```

---

## 5. Git-Backed Audit Logs

### 5.1 Audit Log Structure

```
.thegent/prompts/
├── prompts.jsonl              # Main prompt collection
├── audit/
│   ├── 2026/
│   │   └── 02/
│   │       └── 16/
│   │           └── prompts_20260216.jsonl
│   └── index.json             # Audit index
├── artifacts/
│   ├── todos/
│   │   └── todos_20260216.jsonl
│   └── plans/
│       └── plans_20260216.jsonl
└── .git/
    └── (git repository for audit trail)
```

### 5.2 Git Integration

**Automatic Commits**:
- Each collection run creates a git commit
- Commit message: `chore(prompts): collect prompts from [source] [timestamp]`
- Commit metadata includes:
  - Number of prompts collected
  - Sources scanned
  - Artifacts extracted

**Audit Trail**:
- Every prompt change tracked in git
- Full history available via `git log`
- Integrity verified via git hashes

**Branching Strategy**:
- `main`: Production prompts
- `drafts/`: Draft prompts (not yet finalized)
- `archive/`: Archived prompts (older than 1 year)

### 5.3 Integrity & Verification

**Checksums**:
- SHA-256 hash of each prompt stored in metadata
- Verification command: `thegent prompts verify`

**Signing** (Optional):
- GPG-sign commits for additional security
- Verify signatures: `git log --show-signature`

---

## 6. Integration Architecture

### 6.1 thegent Integration Points

**Session Registry** (`run_registry.jsonl`):
- Link prompts to thegent sessions
- Track which prompts led to which runs
- Correlate prompts with execution results

**MCP Server**:
- Add prompt collection tools to MCP server
- Enable agents to search past prompts
- Allow agents to learn from past interactions

**CLI Integration**:
- Add `prompts` subcommand to main CLI
- Integrate with existing commands (e.g., `thegent doctor`)

### 6.2 Aggregation Strategy

**Real-Time Collection**:
- File system watchers monitor data locations
- New prompts collected immediately
- Low latency (< 1 second)

**Batch Collection**:
- Periodic collection runs (every 5 minutes)
- More efficient for large volumes
- Configurable interval

**Hybrid Approach** (Recommended):
- Real-time watchers for active sessions
- Batch collection for historical data
- Best of both worlds

### 6.3 Storage Backends

**JSONL Files** (Primary):
- Simple, human-readable
- Easy to grep/search
- Git-friendly

**PostgreSQL** (Optional):
- For advanced queries
- Full-text search with pg_trgm
- Vector search with pgvector

**Vector Store** (Optional):
- Semantic search over prompts
- Find similar prompts
- Use pgvector or dedicated vector DB

---

## 7. Todo & Artifact Collection

### 7.1 Todo Extraction

**Patterns**:
- `- [ ]`, `- [x]` (Markdown checkboxes)
- `TODO:`, `FIXME:`, `NOTE:` (Comments)
- `@todo`, `@fixme` (Tags)

**Extraction**:
```python
def extract_todos(text: str) -> list[dict]:
    """Extract todos from prompt/response text."""
    todos = []
    # Markdown checkboxes
    for match in re.finditer(r'- \[([ x])\] (.+)', text):
        todos.append({
            "text": match.group(2),
            "completed": match.group(1) == "x",
            "source": "markdown"
        })
    # TODO comments
    for match in re.finditer(r'TODO:\s*(.+)', text, re.IGNORECASE):
        todos.append({
            "text": match.group(1),
            "completed": False,
            "source": "comment"
        })
    return todos
```

**Storage**:
- `.thegent/prompts/artifacts/todos/todos_YYYYMMDD.jsonl`
- Linked to source prompt via `prompt_id`

### 7.2 Plan Extraction

**Patterns**:
- Markdown files with plan structure
- Sections: `## Plan`, `### Phase`, `- [ ] Task`
- Code blocks with plan content

**Extraction**:
```python
def extract_plans(text: str) -> list[dict]:
    """Extract plans from prompt/response text."""
    plans = []
    # Markdown plan sections
    plan_pattern = r'##\s*Plan\s*\n(.*?)(?=##|\Z)'
    for match in re.finditer(plan_pattern, text, re.DOTALL):
        plans.append({
            "content": match.group(1),
            "format": "markdown",
            "source": "prompt"
        })
    return plans
```

**Storage**:
- `.thegent/prompts/artifacts/plans/plans_YYYYMMDD.jsonl`
- Also store as markdown files for readability

### 7.3 Code Change Tracking

**Git Integration**:
- Track git commits linked to prompts
- Extract diffs for code changes
- Correlate prompts with code changes

**Patterns**:
- File paths mentioned in prompts
- Code blocks in prompts/responses
- Git commit messages referencing prompts

---

## 8. Implementation Roadmap

### Phase 1: Core Collection (Weeks 1-2)

**Tasks**:
1. Research exact data locations for Cursor/Codex/Claude
2. Implement parsers for SQLite, JSONL, log formats
3. Create unified prompt schema
4. Implement basic collection CLI command
5. Test with sample data

**Deliverables**:
- `src/thegent/prompts/collector.py` - Collection logic
- `src/thegent/prompts/parsers.py` - Format parsers
- `src/thegent/prompts/schema.py` - Data schema
- CLI command: `thegent prompts collect`

---

### Phase 2: Git Integration (Week 3)

**Tasks**:
1. Implement git-backed audit logs
2. Add automatic git commits
3. Create audit log structure
4. Add integrity verification

**Deliverables**:
- `src/thegent/prompts/git_audit.py` - Git integration
- Audit log structure in `.thegent/prompts/audit/`
- CLI command: `thegent prompts verify`

---

### Phase 3: MCP Tools (Week 4)

**Tasks**:
1. Add MCP tools for prompt collection/search
2. Integrate with MCP server
3. Add search functionality
4. Test MCP integration

**Deliverables**:
- MCP tools: `thegent_prompt_collect`, `thegent_prompt_search`, etc.
- MCP server integration
- Documentation

---

### Phase 4: Artifact Extraction (Week 5)

**Tasks**:
1. Implement todo extraction
2. Implement plan extraction
3. Implement code change tracking
4. Add artifact storage

**Deliverables**:
- `src/thegent/prompts/artifacts.py` - Artifact extraction
- Artifact storage in `.thegent/prompts/artifacts/`
- CLI command: `thegent prompts artifacts`

---

### Phase 5: Search & Query (Week 6)

**Tasks**:
1. Implement full-text search
2. Add filtering options
3. Add export functionality
4. Performance optimization

**Deliverables**:
- `src/thegent/prompts/search.py` - Search logic
- CLI commands: `thegent prompts search`, `thegent prompts export`
- Performance benchmarks

---

### Phase 6: Real-Time Collection (Week 7)

**Tasks**:
1. Implement file system watchers
2. Add real-time collection
3. Optimize for performance
4. Add monitoring

**Deliverables**:
- `src/thegent/prompts/watchers.py` - File system watchers
- Real-time collection enabled
- Monitoring dashboard

---

### Phase 7: Integration & Polish (Week 8)

**Tasks**:
1. Integrate with existing thegent systems
2. Add documentation
3. Add tests
4. Performance tuning

**Deliverables**:
- Full integration with thegent
- Complete documentation
- Test suite
- Performance report

---

## 9. API & CLI Reference

### 9.1 CLI Commands

**`thegent prompts collect`**:
```bash
# Collect all prompts from last 6 hours
thegent prompts collect --since 6h

# Collect from specific source
thegent prompts collect --source cursor --since 1d

# Collect and commit to git
thegent prompts collect --git-commit

# Collect with artifact extraction
thegent prompts collect --extract-artifacts
```

**`thegent prompts search`**:
```bash
# Simple search
thegent prompts search "cache implementation"

# Search with filters
thegent prompts search "vector search" --source claude --since 1w

# Search with output format
thegent prompts search "todo" --format json --output results.json
```

**`thegent prompts get`**:
```bash
# Get prompt by ID
thegent prompts get prompt_20260216_143022_abc123

# Get with full details
thegent prompts get prompt_20260216_143022_abc123 --full
```

**`thegent prompts export`**:
```bash
# Export to JSON
thegent prompts export --format json --output prompts.json

# Export to markdown
thegent prompts export --format markdown --output prompts.md

# Export with filters
thegent prompts export --source cursor --since 1w --format json
```

**`thegent prompts artifacts`**:
```bash
# Extract todos
thegent prompts artifacts --type todo --since 1d

# Extract plans
thegent prompts artifacts --type plan --since 1w

# Extract all artifacts
thegent prompts artifacts --all --since 1d
```

**`thegent prompts verify`**:
```bash
# Verify integrity
thegent prompts verify

# Verify with detailed output
thegent prompts verify --verbose
```

### 9.2 MCP Tools

**`thegent_prompt_collect`**:
```json
{
  "name": "thegent_prompt_collect",
  "description": "Collect prompts from Cursor/Codex/Claude",
  "inputSchema": {
    "type": "object",
    "properties": {
      "source": {
        "type": "string",
        "enum": ["cursor", "codex", "claude", "all"],
        "default": "all"
      },
      "since": {
        "type": "string",
        "description": "Time range (e.g., '6h', '1d', '1w')",
        "default": "6h"
      },
      "git_commit": {
        "type": "boolean",
        "description": "Create git commit",
        "default": false
      }
    }
  }
}
```

**`thegent_prompt_search`**:
```json
{
  "name": "thegent_prompt_search",
  "description": "Search collected prompts",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "source": {
        "type": "string",
        "enum": ["cursor", "codex", "claude", "all"]
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

**`thegent_prompt_get`**:
```json
{
  "name": "thegent_prompt_get",
  "description": "Get specific prompt by ID",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "description": "Prompt ID"
      },
      "full": {
        "type": "boolean",
        "description": "Include full details",
        "default": false
      }
    },
    "required": ["id"]
  }
}
```

**`thegent_prompt_artifacts`**:
```json
{
  "name": "thegent_prompt_artifacts",
  "description": "Extract artifacts from prompts",
  "inputSchema": {
    "type": "object",
    "properties": {
      "type": {
        "type": "string",
        "enum": ["todo", "plan", "code", "all"],
        "default": "all"
      },
      "since": {
        "type": "string",
        "description": "Time range",
        "default": "1d"
      }
    }
  }
}
```

---

## 10. Research & Discovery

### 10.1 Data Location Research

**Next Steps**:
1. **Inspect Cursor SQLite databases**: Use `sqlite3` to explore schema
2. **Parse JSONL files**: Understand Codex/Claude formats
3. **Analyze log files**: Extract prompt patterns from logs
4. **Test file system watchers**: Verify detection of new prompts

**Tools Needed**:
- `sqlite3` - SQLite database inspection
- `jq` - JSON parsing
- `watchdog` (Python) - File system events
- `git` - Audit trail

### 10.2 Integration Research

**Existing Tools to Integrate**:
- **recall**: Full-text search (Rust/Tantivy)
- **claude-code-tools**: Session continuity
- **thegent run_registry.jsonl**: Session tracking

**Research Tasks**:
1. Analyze recall's search implementation
2. Study claude-code-tools session format
3. Design integration with run_registry.jsonl

---

## 11. Security & Privacy

### 11.1 Data Privacy

**Sensitive Data**:
- API keys in prompts
- Personal information
- Private code

**Mitigation**:
- Option to redact sensitive data
- Configurable exclusion patterns
- Encryption for stored prompts (optional)

### 11.2 Access Control

**Git Permissions**:
- Read-only for most users
- Write access for collection process
- Audit log access controlled

**CLI Permissions**:
- User-level access only
- No system-wide collection without permission

---

## 12. Performance Considerations

### 12.1 Collection Performance

**Optimizations**:
- Incremental collection (only new prompts)
- Parallel parsing (multiple sources)
- Caching parsed data
- Batch git commits

**Targets**:
- Collection: < 1 second for 100 prompts
- Search: < 100ms for full-text search
- Export: < 1 second for 1000 prompts

### 12.2 Storage Optimization

**Strategies**:
- Compression for old prompts
- Archiving prompts older than 1 year
- Indexing for fast search
- Deduplication (same prompt multiple times)

---

## 13. Future Enhancements

### 13.1 Semantic Search

- Vector embeddings for prompts
- Similarity search (find similar prompts)
- Integration with pgvector

### 13.2 Analytics

- Prompt frequency analysis
- Most common patterns
- Cost tracking (if available)
- Success rate tracking

### 13.3 Collaboration

- Share prompts across team
- Collaborative prompt library
- Prompt templates
- Best practices extraction

---

## 14. Conclusion

This plan provides a comprehensive system for collecting, storing, and searching prompts from Cursor, Codex, and Claude Code. The system includes:

1. **Standardized Collection**: Unified format for all prompts
2. **Git Integration**: Full audit trail with versioning
3. **MCP/CLI Tools**: Easy access and querying
4. **Artifact Extraction**: Automatic extraction of todos, plans, code changes
5. **Search & Discovery**: Full-text search across all prompts

**Next Steps**:
1. Research exact data locations (Phase 1)
2. Implement core collection (Phase 1)
3. Add git integration (Phase 2)
4. Build MCP tools (Phase 3)
5. Add artifact extraction (Phase 4)

---

**Document Status**: Complete | **Last Updated**: 2026-02-16


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

