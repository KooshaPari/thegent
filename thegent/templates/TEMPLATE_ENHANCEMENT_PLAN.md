# Global Template System Enhancement Plan

## Executive Summary

This plan addresses gaps in the global template system at `thegent/templates/` to make it comprehensive and complete for project initialization.

**Current State:**
- Spec templates: PRD, ADR, FR, PLAN, UJ, TRACKER, CODE_ENTITY_MAP (root level)
- Language templates: python/, typescript/, go/, bash/
- Quality: 50+ files for 25+ languages
- VitePress: minimal + full versions

**Gaps Identified:**
1. No CLAUDE.md project template
2. No unified entry point (initialize-project)
3. Missing operational templates: CI/CD, Docker, .gitignore, .env

---

## Phased Implementation Plan

### Phase 1: Reorganize Spec Templates (P1.1)

**Action:** Move spec templates to `templates/specs/` subdirectory

| Current | New Location |
|---------|--------------|
| templates/PRD_TEMPLATE.md | templates/specs/PRD_TEMPLATE.md |
| templates/ADR_TEMPLATE.md | templates/specs/ADR_TEMPLATE.md |
| templates/FR_TEMPLATE.md | templates/specs/FR_TEMPLATE.md |
| templates/PLAN_TEMPLATE.md | templates/specs/PLAN_TEMPLATE.md |
| templates/UJ_TEMPLATE.md | templates/specs/UJ_TEMPLATE.md |
| templates/TRACKER_TEMPLATE.md | templates/specs/TRACKER_TEMPLATE.md |
| templates/CODE_ENTITY_MAP_TEMPLATE.md | templates/specs/CODE_ENTITY_MAP_TEMPLATE.md |

**Rationale:** Consistent with `docs/` organization pattern, keeps templates grouped by purpose.

---

### Phase 2: Create CLAUDE.md Project Template (P2.1)

**Action:** Create `templates/claude/CLAUDE.md.template`

**Contents:**
- Universal development philosophy (extend, never duplicate, primitives first, research first)
- Library preferences table (Need → Use → NOT)
- Code quality non-negotiables
- Language-specific patterns reference
- Project type patterns (CLI, MCP server, agent mesh, etc.)

---

### Phase 3: Create Initialize-Project Template (P3.1)

**Action:** Create `templates/initialize-project/` with copier structure

```
templates/initialize-project/
├── copier.yml              # Copier configuration
├── README.md              # Usage instructions
└── {{cookiecutter.project_name }}/
    ├── CLAUDE.md          # From template
    ├── Taskfile.yml       # From language template
    ├── .gitignore        # From operational templates
    ├── .env.example       # From operational templates
    ├── docs/
    │   └── index.md       # Basic doc structure
    ├── src/               # Language-specific scaffold
    ├── tests/
    └── {{#if ci}}.github/workflows/ci.yml{{/if}}
```

**Copier Prompts:**
1. `project_name` - Name of project
2. `project_description` - One-line description
3. `author` - Author name
4. `language` - Primary language (Python, TypeScript, Go, Bash)
5. `include_docs` - Include VitePress docsite (yes/no)
6. `include_ci` - Include GitHub Actions CI (yes/no)
7. `include_docker` - Include Docker setup (yes/no)
8. `include_hooks` - Include pre-commit hooks (yes/no)

---

### Phase 4: Operational Templates (P4.1)

**Action:** Create `templates/operational/` directory

#### 4.1 Gitignore Templates
```
templates/operational/
└── gitignore/
    ├── Python.gitignore
    ├── TypeScript.gitignore
    ├── Go.gitignore
    └── Bash.gitignore
```

#### 4.2 Environment Template
```
templates/operational/
└── env/
    └── .env.example
```

#### 4.3 CI/CD Templates
```
templates/operational/
└── ci/
    ├── github-actions.yml
    ├── gitlab-ci.yml
    └── local-workflows/
        └── quality-gate.sh
```

#### 4.4 Docker Templates
```
templates/operational/
└── docker/
    ├── Dockerfile.python
    ├── Dockerfile.typescript
    ├── Dockerfile.go
    └── docker-compose.yml
```

---

### Phase 5: Integration (P5.1)

**Action:** Update thegent's CLAUDE.md to document new template structure

Add section for initialize-project usage:
```markdown
## Project Initialization

To initialize a new project with full tooling:

```bash
# Install copier if needed
pip install copier

# Run initialize-project template
copier copy thegent/templates/initialize-project ./my-new-project
```

Or manually select templates:
- CLAUDE.md: `templates/claude/CLAUDE.md.template`
- Taskfile: `templates/{language}/Taskfile.{language}.yml`
- Quality: `templates/quality/`
- VitePress: `templates/vitepress-full/`
```

---

## Execution Order (DAG)

```
P1.1 (reorganize specs) ──┬── P2.1 (CLAUDE.md template)
                            ├── P3.1 (initialize-project)
                            ├── P4.1 (operational templates)
                            └── P5.1 (integration/update docs)
```

---

## Effort Estimate

| Phase | Tasks | Parallel Agents | Wall Clock |
|-------|-------|-----------------|------------|
| P1 | 1 | 1 | 1 min |
| P2 | 1 | 1 | 2 min |
| P3 | 1 | 1 | 5 min |
| P4 | 4 | 2 | 5 min |
| P5 | 1 | 1 | 1 min |
| **Total** | **8** | **Up to 2** | **~15 min** |

---

## Verification

- [x] All spec templates moved to `templates/specs/`
- [x] CLAUDE.md template exists at `templates/claude/CLAUDE.md.template`
- [x] Initialize-project template exists with copier.yml
- [x] Operational templates exist (ci, docker)
- [ ] Operational gitignore templates (simplified - combined in initialize-project/.gitignore.template)
- [ ] thegent's CLAUDE.md updated with initialization instructions

---

## Success Criteria

After implementation:
1. New projects can be scaffolded with single `copier` command
2. All required project files have templates (CLAUDE.md, Taskfile, .gitignore, .env.example)
3. Language-specific templates are referenced by initialize-project
4. Documentation explains template usage
