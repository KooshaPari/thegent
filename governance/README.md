# Governance

This directory contains governance standards, templates, and quality gates for the thegent project and the broader Phenotype ecosystem.

## Structure

```
governance/
├── AGENTS.base.md              # Base template for AGENTS.md across ecosystem
├── CLAUDE.base.md              # Base template for CLAUDE.md (from PR #883)
├── standards/                  # Detailed standards and guidelines
│   ├── commit-conventions.md   # Commit message format and discipline
│   ├── pr-standards.md         # Pull request workflow and requirements
│   ├── code-style.md           # Language-specific style guidelines
│   └── testing-standards.md    # Testing requirements and patterns
├── templates/                  # Document templates
│   ├── PRD.template.md         # Product Requirements Document
│   ├── ADR.template.md         # Architecture Decision Record
│   ├── FR.template.md          # Functional Requirements
│   └── PLAN.template.md        # Implementation Plan
├── quality-gates/              # Quality gate configurations
│   └── README.md               # Index of available quality gates
└── policy-contract/            # Policy and contract documents
```

## Quick Start

### For Project Contributors

1. **Read first**: [../AGENTS.md](../AGENTS.md) — Agent rules specific to thegent
2. **Reference**: [AGENTS.base.md](AGENTS.base.md) — Base template used across Phenotype
3. **Code standards**: [standards/code-style.md](standards/code-style.md)
4. **Testing**: [standards/testing-standards.md](standards/testing-standards.md)
5. **Commits**: [standards/commit-conventions.md](standards/commit-conventions.md)
6. **PRs**: [standards/pr-standards.md](standards/pr-standards.md)

### For Project Leads

1. **Project specs**: Use templates in [templates/](templates/)
   - PRD: [templates/PRD.template.md](templates/PRD.template.md)
   - ADR: [templates/ADR.template.md](templates/ADR.template.md)
   - FR: [templates/FR.template.md](templates/FR.template.md)
   - PLAN: [templates/PLAN.template.md](templates/PLAN.template.md)

2. **Quality gates**: See [quality-gates/README.md](quality-gates/README.md)

### For Ecosystem Contributors

1. **Base templates**: [AGENTS.base.md](AGENTS.base.md) and [CLAUDE.base.md](CLAUDE.base.md)
2. **Consolidate**: Use these as bases for your project's AGENTS.md and CLAUDE.md
3. **Customize**: Adapt standards for your language/framework

## Key Standards

### Commits

- Format: `<type>(<scope>): <subject>`
- Types: feat, fix, docs, style, refactor, perf, test, chore, ci, security
- See [standards/commit-conventions.md](standards/commit-conventions.md)

### PRs

- One concern per PR
- All checks passing before merge
- Reviews completed, no pending threads
- See [standards/pr-standards.md](standards/pr-standards.md)

### Code

- Line length: 100 characters
- File size: Target ≤350 lines, hard limit ≤500
- Type hints: Explicit where practical
- No suppressions without justification
- See [standards/code-style.md](standards/code-style.md)

### Tests

- Test-first (TDD): Tests before or during implementation
- Coverage: 70% unit, 20% integration, 10% E2E (±5%)
- FR traceability: All tests reference an FR ID
- See [standards/testing-standards.md](standards/testing-standards.md)

## Document Templates

All templates are customizable; treat `[BRACKETS]` as placeholders:

| Template | Purpose | When to Use |
|----------|---------|------------|
| [PRD.template.md](templates/PRD.template.md) | Product Requirements | New feature or project |
| [ADR.template.md](templates/ADR.template.md) | Architecture Decision | Major technical decision |
| [FR.template.md](templates/FR.template.md) | Functional Requirements | Detailed specifications |
| [PLAN.template.md](templates/PLAN.template.md) | Implementation Plan | Project planning/scheduling |

**How to use**:
1. Copy template file: `cp governance/templates/PRD.template.md docs/PRD.md`
2. Replace placeholders (e.g., `[PROJECT_NAME]`, `[DATE]`)
3. Fill in project-specific sections
4. Get stakeholder approval

## Quality Gates

Available quality gates (if configured):
- Lint checking
- Type checking
- Test coverage validation
- Commit message validation
- PR format validation
- Security scanning

See [quality-gates/README.md](quality-gates/README.md) for configuration.

## Related Documents

- **[AGENTS.md](../AGENTS.md)** — thegent-specific agent rules
- **[CLAUDE.md](../CLAUDE.md)** — thegent project instructions
- **[PR #883](https://github.com/KooshaPari/phenotype-infrakit/pull/883)** — Base consolidation work

## Governance Principles

1. **Clarity**: Standards are clear and unambiguous
2. **Consistency**: Projects follow the same patterns across Phenotype
3. **Extensibility**: Standards can be customized for specific needs
4. **Simplicity**: Governance is proportional to project complexity
5. **Accountability**: Clear ownership and decision records

## Consolidation Status

As of 2026-03-29:

- ✅ **AGENTS.base.md**: Consolidated from 36+ AGENTS.md copies across Phenotype
- ✅ **CLAUDE.base.md**: Base template created in PR #883
- ✅ **standards/**: Detailed standards extracted from existing docs
- ✅ **templates/**: Templates created for PRD, ADR, FR, PLAN
- 🔄 **quality-gates/**: Configuration in progress

## Contributing to Governance

To propose changes to governance:

1. Create a branch: `feat/governance-update`
2. Make changes to relevant files
3. Update this README if structure changes
4. Create a PR with detailed rationale
5. Get approval from tech lead/PM

## Questions?

- **Standards questions**: See relevant file in [standards/](standards/)
- **Template questions**: See relevant template in [templates/](templates/)
- **Project-specific**: See [AGENTS.md](../AGENTS.md) or [CLAUDE.md](../CLAUDE.md)
- **Ecosystem governance**: See root-level governance docs

---

**Last Updated**: 2026-03-29
**Owner**: Platform team
**Version**: 1.0
