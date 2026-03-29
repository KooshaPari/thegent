# Design: Advanced Versioning & Shadow Audit System (Thegent 3.0)

## 1. Overview
Thegent 3.0 requires a robust, granular, and secure way to track agent work across multiple levels of abstraction. This system provides deep observability into "episodes" of agent work while maintaining a shadow system-level audit log that tracks every transaction securely, including handling of sensitive items (secrets) that should never enter the main project Git history.

## 2. Multi-Level Versioning Hierarchy

We introduce a 5-tier hierarchy to organize and version agentic work:

| Level | Entity | Description | Versioning Pattern |
|-------|--------|-------------|-------------------|
| L5 | **Product** | The overall software product (e.g., "thegent"). | SemVer (e.g., 3.0.0) |
| L4 | **Milestone** | Major feature sets or project phases. | Tag (e.g., `m-reliability`) |
| L3 | **Sprint** | Time-boxed work periods. | ISO-Date (e.g., `s-2026-W08`) |
| L2 | **Task** | A specific unit of work from the backlog. | Task-ID (e.g., `WP-3005`) |
| L1 | **Episode** | A single agent run or interaction loop. | Episode-ID (e.g., `ep-8f2a1b`) |

### 2.1 Episode Specification
An **Episode** is the atomic unit of agent work. It includes:
- **Inputs**: Prompt, system instructions, environment variables.
- **Context**: Relevant code snippets, memory nodes retrieved.
- **Transactions**: Sequence of tool calls and their results.
- **State Change**: File diffs produced during the episode.
- **Outcome**: Success/failure and a natural language summary.

## 3. Shadow System-Level Git (Audit Log)

The Shadow Audit Log is a local-only tracking mechanism that provides a more granular history than the project's main Git repository.

### 3.1 Repository Structure
- **Location**: `~/.thegent/shadow-audit/[project-hash]/`
- **Mechanism**: A hidden Git repository that mirrors the project state but records *every* file modification attempt by an agent.
- **Isolation**: Stays on-device; never pushed to remote.

### 3.2 Granular Transactions
Unlike the main Git repo which might have a single commit for a whole task, the Shadow Audit Log creates a commit for **every tool call** that modifies the filesystem.
- **Commit Message**: `[Tool: write_file] Episode: ep-123 Task: WP-1001`
- **Metadata**: Commits are tagged with the tool name and Episode ID.

### 3.3 Secret Management (Scrubbing)
The Shadow Audit Log implements a "Secret Scrubbing" layer:
1. **Detection**: Scan for patterns (regex for keys, tokens, etc.) before commit.
2. **Redaction**: Replace secrets with `<REDACTED_SECRET_[HASH]>`.
3. **Vault**: Store the actual secret value in a local, encrypted SQLite database (the "Shadow Vault") indexed by the hash, ensuring the secret can be recovered locally if needed but is never in plain text in the git history.

## 4. Architectural Components

### 4.1 `ShadowAuditLog` Module
Responsible for managing the shadow git repository and committing granular changes.
- `init_repo(path: Path)`: Initialize or clone the shadow repo.
- `commit_transaction(episode_id: str, tool: str, diff: str)`: Commit a specific change.
- `scrub_secrets(content: str) -> str`: Remove sensitive data.

### 4.2 `ProjectRegistry` (SQLite DB)
A dedicated database `~/.thegent/registry.db` to track the hierarchy:
- `products` table
- `milestones` table
- `sprints` table
- `tasks` table (mapped to `WORK_STREAM.md` or `PLAN.md`)
- `episodes` table (mapped to `episodic_log`)

### 4.3 `EpisodeController`
A context manager used in agent loops to wrap tool execution:
```python
with EpisodeController(task_id="WP-1001") as ep:
    # Agent executes tool calls here
    # Each file modification triggers a shadow commit
    pass
```

## 5. Implementation Roadmap

### Phase 1: Foundation (Current)
- [ ] Create `ProjectRegistry` SQLite schema.
- [ ] Implement `ShadowAuditLog` with basic Git commit logic.
- [ ] Update `MemoryMeshV2` to link episodes to the new hierarchy.

### Phase 2: Granularity & Security
- [ ] Implement per-tool-call commits in `ShadowAuditLog`.
- [ ] Add Secret Scrubbing regex patterns.
- [ ] Implement the "Shadow Vault" for local secret recovery.

### Phase 3: Integration
- [ ] Integrate with `cli/apps/run.py` to automatically start episodes.
- [ ] Expose audit log via `thegent audit log` command.
- [ ] Add visualization for episode history and state diffs.
