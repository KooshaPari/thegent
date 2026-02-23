# Rust/Zig Migration Plan - Aggressive LOC Reduction

## Target: Reduce Python from 685K → 300K LOC

## Top Migration Candidates (by size + compute intensity)

| Module | Python LOC | Rust Crate | Priority |
|--------|-----------|------------|----------|
| execution.py | 2,196 | thegent-runtime | P0 |
| workstream_autosync.py | 2,217 | thegent-cache | P0 |
| shell_cli.py | 1,048 | thegent-shims | P1 |
| install.py | 1,772 | - | P2 |
| config.py | 1,540 | - | P2 |
| audit/shadow_audit_git.py | 1,517 | thegent-git | P1 |

## Current Rust Coverage (39K LOC)
- thegent-fs, thegent-cache, thegent-crypto, thegent-git, thegent-hooks

## Execution Path (P0 - Highest Impact)
- execution.py 2,196 LOC
- executor_integration.py
- remote_runner.py
- compute/remote_executor.py

## Migration Strategy

### 1. Execution Engine → Rust
```python
# Current: execution.py 2,196 LOC
# Target: thegent-runtime already exists - migrate execution.py
```

### 2. File Operations → Rust
```bash
# Already: thegent-fs crate exists
# Migrate: file operations from install.py, shell operations
```

### 3. Process Management → Rust
```python
# Migrate: subprocess management to thegent-shims
# Already exists: thegent-shims crate
```

## Quick Wins

### Phase 1 (Immediate)
1. [ ] Migrate execution hot paths to Rust
2. [ ] Consolidate install.py install_bundles.py 
3. [ ] Move audit/shadow_audit_git.py → thegent-git

### Phase 2 (This Month)
4. [ ] Consolidate config.py → Rust
5. [ ] Migrate shell_cli.py → thegent-shims

## Progress Tracking

| Phase | Target LOC Reduction | Status |
|-------|---------------------|--------|
| Phase 1 | -50K | Not Started |
| Phase 2 | -100K | Not Started |
| Phase 3 | -200K | Not Started |

**Goal: Python 685K → 300K (-56%)**
