# Phenotype Documentation Hub

**The central documentation repository for the Phenotype polyrepo ecosystem.**

This directory contains comprehensive documentation, governance, architecture decisions, research, and process guidance for the Phenotype organization and all related projects.

---

## Quick Navigation

| Purpose | Location | Description |
|---------|----------|-------------|
| **Governance** | [`GOVERNANCE.md`](./GOVERNANCE.md) | Engineering standards, branch rules, release processes |
| **Contributing** | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Contribution guidelines and workflows |
| **Architecture** | [`architecture/`](./architecture/) | System design, architectural patterns, ADRs |
| **Engineering** | [`engineering/`](./engineering/) | Language/framework guidance, package naming, coding standards |
| **Integration Guides** | [`integration-guides/`](./integration-guides/) | Cross-repo integration, API usage, setup instructions |
| **Migration Guides** | [`migration-guides/`](./migration-guides/) | Upgrade paths, breaking changes, migration procedures |
| **Research** | [`research/`](./research/) | Analysis, investigations, reference materials |
| **Reports** | [`reports/`](./reports/) | Completion reports, summaries, audit results |
| **Security** | [`security/`](./security/) | Security policies, best practices, threat models |
| **Changes** | [`changes/`](./changes/) | Per-change proposals, designs, and implementation tasks |
| **Sessions** | [`sessions/`](./sessions/) | Session notes, investigations, daily work logs |
| **Technical Debt** | [`technical-debt/`](./technical-debt/) | Debt tracking, remediation plans, refactor guides |

---

## Directory Structure

```
docs/
├── README.md                       # This file
├── GOVERNANCE.md                   # Root-level governance rules
├── CONTRIBUTING.md                 # Contribution guidelines
├── AGENTS.md                        # AI agent instructions
├── CLAUDE.md                        # Claude-specific development rules
│
├── architecture/                   # System design & architecture
│
├── engineering/                    # Engineering standards
│
├── integration-guides/             # Cross-repo integration docs
├── migration-guides/               # Upgrade and migration paths
├── research/                       # Research & analysis
├── reports/                        # Completion & audit reports
├── security/                       # Security policies & practices
├── changes/                        # Per-change documentation
│   └── archive/                    # Completed changes
│
├── sessions/                       # Session notes & investigations
├── technical-debt/                 # Technical debt tracking
└── closeout/                       # Project closeout docs
```

---

## Key Documentation Files

### Root-Level Governance
- **`GOVERNANCE.md`** — Engineering standards, branch rules, release processes, code quality requirements
- **`CONTRIBUTING.md`** — How to contribute to the Phenotype ecosystem
- **`CLAUDE.md`** — Global Claude development rules and AI agent governance
- **`AGENTS.md`** — Instructions for AI agents working in this space

### Configuration
- **`.pre-commit-config.yaml`** — Pre-commit hooks for quality gates
- **`.env.example`** — Environment variable template

---

## Documentation Guidelines

### Adding New Documentation

1. **Determine the category** from the directory structure above
2. **Place the file** in the appropriate subdirectory
3. **Follow naming conventions:**
   - Quick starts: `*QUICK_START.md`, `*QUICKSTART.md`
   - Guides: `*GUIDE.md`
   - References: `*REFERENCE.md`, `*QUICK_REF.md`
   - Reports: `*REPORT.md`, `*SUMMARY.md`, `*COMPLETE.md`
   - Research: `*RESEARCH.md`, `*INDEX.md`
   - Checklists: `*CHECKLIST.md`
4. **Update this README** if adding a new major section

### Documentation Standards
- Use **Markdown** (`.md`)
- Include **ASCII diagrams** for flows and architecture (not images)
- Use **tables** for matrices, tracking, and summaries
- Cross-reference between related documentation
- Include **timestamps** for time-sensitive content

---

## Organization Status

### Current Structure
The documentation repository is well-organized with clear subdirectories for different content types:
- **architecture/** — System design and decision records
- **engineering/** — Standards, naming conventions, and best practices
- **reports/** — Audit results, surveys, and status summaries
- **research/** — Investigations and analysis
- **security/** — Policies and best practices
- **sessions/** — Work logs and session notes
- **technical-debt/** — Remediation plans and tracking

### Reference Files at Root
- `cleanup-log-*.md` — Historical cleanup documentation (reference only)
- `LOCAL_FIRST_INDEX_*.md` — Local-first architecture research indexes
- `worklog-template.md` — Template for work logs

These files are retained for historical reference and can be archived later if needed.

---

## Related Repositories

This documentation serves the Phenotype polyrepo ecosystem:
- Core Phenotype packages (`phenotype-*`)
- Polyrepo templates and scaffolding
- CLI tools and utilities
- Infrastructure and DevOps tooling

---

## Contributing to Documentation

1. Work in a feature branch (created via worktree)
2. Follow the directory structure and naming guidelines above
3. Add cross-references to related documentation
4. Include timestamps for investigation/session notes
5. Submit a PR with description of changes

---

## Questions or Issues?

For documentation-related questions:
- Check `GOVERNANCE.md` for process questions
- Check `CONTRIBUTING.md` for contribution guidelines
- Review relevant docs in `architecture/`, `engineering/`, or `security/`
- Consult session notes in `sessions/` for historical context

---

**Last Updated:** 2026-03-25
**Status:** Active Organization Hub
