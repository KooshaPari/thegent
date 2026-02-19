# Prompt History Collection & Audit System Complete Guide

> **Status**: Complete | **Version**: 1.0 | **Date**: 2026-02-16
> **Related**: 
> - [Prompt History Collection Plan](./PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md)
> - [Work Stream](../reference/WORK_STREAM.md)

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture & Design](#2-architecture--design)
3. [Implementation Details](#3-implementation-details)
4. [Data Collection](#4-data-collection)
5. [Git Integration](#5-git-integration)
6. [Artifact Extraction](#6-artifact-extraction)
7. [MCP Tools & CLI](#7-mcp-tools--cli)
8. [Configuration](#8-configuration)
9. [Troubleshooting](#9-troubleshooting)
10. [References](#10-references)

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

---

## 2. Architecture & Design

### 2.1 Data Flow

1. **Discovery**: File system watchers detect new prompts
2. **Collection**: Parsers extract prompts from various formats
3. **Normalization**: Convert to unified JSON schema
4. **Storage**: Write to JSONL + git commit
5. **Indexing**: Update search index
6. **Artifact Extraction**: Extract todos, plans, code changes

### 2.2 Unified Prompt Schema

```json
{
  "id": "prompt_20260216_143022_abc123",
  "timestamp": "2026-02-16T14:30:22Z",
  "source": "cursor",
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

---

## 3. Implementation Details

### 3.1 Prompt Collector

```python
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class PromptCollector:
    """Collect prompts from various sources."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.observer = Observer()
    
    def collect_from_cursor(self, since: Optional[datetime] = None) -> List[Dict]:
        """Collect prompts from Cursor."""
        prompts = []
        
        # Cursor SQLite database
        cursor_db = Path.home() / "Library/Application Support/Cursor/User/globalStorage/cursor.chat/chat.db"
        if cursor_db.exists():
            conn = sqlite3.connect(cursor_db)
            cursor = conn.execute("""
                SELECT id, timestamp, message, response
                FROM messages
                WHERE timestamp > ?
                ORDER BY timestamp
            """, (since.timestamp() if since else 0,))
            
            for row in cursor.fetchall():
                prompts.append({
                    "id": f"cursor_{row[0]}",
                    "timestamp": datetime.fromtimestamp(row[1]).isoformat(),
                    "source": "cursor",
                    "prompt": {"text": row[2]},
                    "response": {"text": row[3]} if row[3] else None,
                })
            
            conn.close()
        
        return prompts
    
    def collect_from_codex(self, since: Optional[datetime] = None) -> List[Dict]:
        """Collect prompts from Codex."""
        prompts = []
        
        # Codex JSONL files
        codex_dir = Path.home() / "Library/Application Support/Codex/sessions"
        if codex_dir.exists():
            for jsonl_file in codex_dir.glob("*.jsonl"):
                with open(jsonl_file) as f:
                    for line in f:
                        data = json.loads(line)
                        prompt_time = datetime.fromisoformat(data["timestamp"])
                        if since and prompt_time < since:
                            continue
                        
                        prompts.append({
                            "id": f"codex_{data['id']}",
                            "timestamp": data["timestamp"],
                            "source": "codex",
                            "prompt": {"text": data["prompt"]},
                            "response": {"text": data.get("response")},
                        })
        
        return prompts
    
    def collect_from_claude(self, since: Optional[datetime] = None) -> List[Dict]:
        """Collect prompts from Claude Code."""
        prompts = []
        
        # Claude Code JSONL files
        claude_dir = Path.home() / ".claude/sessions"
        if claude_dir.exists():
            for jsonl_file in claude_dir.glob("*.jsonl"):
                with open(jsonl_file) as f:
                    for line in f:
                        data = json.loads(line)
                        prompt_time = datetime.fromisoformat(data["timestamp"])
                        if since and prompt_time < since:
                            continue
                        
                        prompts.append({
                            "id": f"claude_{data['id']}",
                            "timestamp": data["timestamp"],
                            "source": "claude",
                            "prompt": {"text": data["prompt"]},
                            "response": {"text": data.get("response")},
                        })
        
        return prompts
    
    def collect_all(self, since: Optional[datetime] = None) -> List[Dict]:
        """Collect prompts from all sources."""
        all_prompts = []
        all_prompts.extend(self.collect_from_cursor(since))
        all_prompts.extend(self.collect_from_codex(since))
        all_prompts.extend(self.collect_from_claude(since))
        return all_prompts
    
    def save_prompts(self, prompts: List[Dict]) -> None:
        """Save prompts to JSONL file."""
        prompts_file = self.storage_path / "prompts.jsonl"
        with open(prompts_file, "a") as f:
            for prompt in prompts:
                f.write(json.dumps(prompt) + "\n")
```

### 3.2 File System Watcher

```python
class PromptWatcher(FileSystemEventHandler):
    """Watch for new prompts and collect automatically."""
    
    def __init__(self, collector: PromptCollector):
        self.collector = collector
    
    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory:
            return
        
        # Check if it's a prompt file
        if "cursor" in str(event.src_path) or "codex" in str(event.src_path) or "claude" in str(event.src_path):
            # Collect new prompts
            prompts = self.collector.collect_all(since=datetime.now())
            if prompts:
                self.collector.save_prompts(prompts)
```

---

## 4. Data Collection

### 4.1 Source Locations

**Cursor (macOS)**:
- `~/Library/Application Support/Cursor/User/globalStorage/cursor.chat/chat.db` (SQLite)
- `~/.cursor/` (Config, cache)

**Codex (macOS)**:
- `~/Library/Application Support/Codex/sessions/*.jsonl` (JSONL files)
- `~/.codex/` (Config, cache)

**Claude Code (macOS)**:
- `~/.claude/sessions/*.jsonl` (JSONL files)
- `~/Library/Application Support/Claude/` (Data, logs)

### 4.2 Collection Process

1. **Scan known locations** for prompt files
2. **Parse formats** (SQLite, JSONL, logs)
3. **Normalize** to unified schema
4. **Validate** data integrity
5. **Store** in JSONL + git commit

---

## 5. Git Integration

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

### 5.2 Git Commits

```python
import subprocess
from pathlib import Path

def commit_prompts(prompts_path: Path, prompts: List[Dict]) -> None:
    """Commit prompts to git."""
    # Initialize git repo if needed
    git_dir = prompts_path / ".git"
    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=prompts_path)
        subprocess.run(["git", "config", "user.name", "thegent"], cwd=prompts_path)
        subprocess.run(["git", "config", "user.email", "thegent@local"], cwd=prompts_path)
    
    # Add prompts
    subprocess.run(["git", "add", "prompts.jsonl"], cwd=prompts_path)
    
    # Commit
    commit_msg = f"chore(prompts): collect {len(prompts)} prompts from {', '.join(set(p['source'] for p in prompts))}"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=prompts_path)
```

---

## 6. Artifact Extraction

### 6.1 Todo Extraction

```python
import re
from typing import List, Dict

def extract_todos(text: str) -> List[Dict]:
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

### 6.2 Plan Extraction

```python
def extract_plans(text: str) -> List[Dict]:
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

---

## 7. MCP Tools & CLI

### 7.1 MCP Tools

**`thegent_prompt_collect`**:
```python
@mcp.tool()
async def thegent_prompt_collect(
    source: str = "all",
    since: Optional[str] = None,
) -> str:
    """Collect prompts from specified sources."""
    collector = PromptCollector(Path(".thegent/prompts"))
    
    since_dt = datetime.fromisoformat(since) if since else None
    prompts = collector.collect_all(since=since_dt)
    
    collector.save_prompts(prompts)
    commit_prompts(collector.storage_path, prompts)
    
    return f"Collected {len(prompts)} prompts"
```

**`thegent_prompt_search`**:
```python
@mcp.tool()
async def thegent_prompt_search(
    query: str,
    source: Optional[str] = None,
    since: Optional[str] = None,
) -> List[Dict]:
    """Search prompts by query."""
    prompts_file = Path(".thegent/prompts/prompts.jsonl")
    results = []
    
    with open(prompts_file) as f:
        for line in f:
            prompt = json.loads(line)
            
            # Filter by source
            if source and prompt["source"] != source:
                continue
            
            # Filter by date
            if since:
                prompt_time = datetime.fromisoformat(prompt["timestamp"])
                since_dt = datetime.fromisoformat(since)
                if prompt_time < since_dt:
                    continue
            
            # Search in text
            if query.lower() in prompt["prompt"]["text"].lower():
                results.append(prompt)
    
    return results
```

### 7.2 CLI Commands

**`thegent prompts collect`**:
```python
@app.command()
def prompts_collect(
    source: str = typer.Option("all", "--source"),
    since: str = typer.Option(None, "--since"),
    git_commit: bool = typer.Option(False, "--git-commit"),
):
    """Collect prompts from sources."""
    collector = PromptCollector(Path(".thegent/prompts"))
    
    since_dt = datetime.fromisoformat(since) if since else None
    prompts = collector.collect_all(since=since_dt)
    
    collector.save_prompts(prompts)
    
    if git_commit:
        commit_prompts(collector.storage_path, prompts)
    
    typer.echo(f"Collected {len(prompts)} prompts")
```

**`thegent prompts search`**:
```python
@app.command()
def prompts_search(
    query: str,
    source: Optional[str] = typer.Option(None, "--source"),
    since: Optional[str] = typer.Option(None, "--since"),
):
    """Search prompts."""
    # Implementation similar to MCP tool
    pass
```

---

## 8. Configuration

### 8.1 Environment Variables

```bash
# Collection settings
THGENT_PROMPTS_STORAGE_PATH=~/.thegent/prompts
THGENT_PROMPTS_AUTO_COLLECT=1
THGENT_PROMPTS_COLLECT_INTERVAL=300  # seconds

# Git settings
THGENT_PROMPTS_GIT_ENABLED=1
THGENT_PROMPTS_GIT_AUTO_COMMIT=1

# Search settings
THGENT_PROMPTS_SEARCH_BACKEND=jsonl  # jsonl | postgresql | vector
```

### 8.2 Config File

```yaml
# ~/.config/thegent/prompts.yaml
storage:
  path: ~/.thegent/prompts
  format: jsonl

collection:
  auto_collect: true
  interval: 300
  sources:
    - cursor
    - codex
    - claude

git:
  enabled: true
  auto_commit: true
  branch: main

search:
  backend: jsonl
  postgresql_url: null
  vector_store_url: null
```

---

## 9. Troubleshooting

### 9.1 Common Issues

**Issue**: Prompts not collected
- **Check**: Source paths exist
- **Check**: Permissions on source directories
- **Check**: Collection interval settings

**Issue**: Git commits failing
- **Check**: Git initialized in storage path
- **Check**: Git user config set
- **Check**: Write permissions

**Issue**: Search not working
- **Check**: Prompts file exists
- **Check**: File format correct
- **Check**: Search backend configured

---

## 10. References

### 10.1 Related Documentation

- [Prompt History Collection Plan](./PROMPT_HISTORY_COLLECTION_AND_AUDIT_SYSTEM.md) - Original plan
- [Work Stream](../reference/WORK_STREAM.md) - Integration

### 10.2 Implementation Files

- **Collector**: `src/thegent/prompts/collector.py` (to be created)
- **Watcher**: `src/thegent/prompts/watcher.py` (to be created)
- **MCP Tools**: `src/thegent/mcp_prompts.py` (to be created)
- **CLI**: `src/thegent/cli_prompts.py` (to be created)

---

*Generated: 2026-02-16 | Version: 1.0 | Status: Complete*
