# thegent Governance

## Overview

This document defines the governance rules and quality gates for thegent repository.

## 3-Group Structure

### 1. Artifacts (Container Documents)

| Artifact | Purpose | Status |
|----------|---------|--------|
| `CLAUDE.md` | AI assistant context | ✅ Required |
| `PRD.md` | Product requirements | ✅ Required |
| `ADR.md` | Architecture decisions | ✅ Required |
| `AGENTS.md` | Agent interaction rules | ✅ Required |
| `GOVERNANCE.md` | This document - governance rules | ✅ Required |
| `specs/FR-*.md` | Detailed FR specifications | ✅ Required |

**Validation:** Run `python3 validate_governance.py`

### 2. Task Items (Actionable Work)

| Item Type | Required Fields | Validation |
|-----------|-------------------|------------|
| FRs | User story, acceptance criteria, story points, work packages | Check FR spec completeness |
| User Stories | Given/When/Then format | At least 1 per P0/P1 FR |
| Work Packages | WP ID, owner, status | Tracked in FR spec |
| Story Points | Numeric estimate | Required for sprint planning |

**Required FRs:**
- FR-THEGENT-001: Router Core ✅
- FR-THEGENT-002: Policy Engine ✅
- FR-THEGENT-003: Hysteresis Manager ✅
- FR-THEGENT-004: Metrics Collection ✅
- FR-THEGENT-005: Health Checks ✅
- FR-THEGENT-006: Tier Management ✅

### 3. Governance (Enforcement)

| Mechanism | Rule | Enforcement |
|-----------|------|-------------|
| **CI/CD** | `.github/workflows/traceability.yml` | Must pass on all PRs |
| **AI Attribution** | `.phenotype/ai-traceability.yaml` | Required for all commits |
| **FR Traceability** | All test files must have `#[trace_to]` | Validated in CI |
| **Code Coverage** | ≥80% for critical paths | `cargo tarpaulin` |
| **Linting** | `cargo clippy -- -D warnings` | Zero warnings |
| **Formatting** | `cargo fmt --check` | Must pass |
| **Governance Validation** | `python3 validate_governance.py` | Must pass before merge |

## Quality Gates

### Pre-Commit Gates

```bash
# Run before every commit
make check          # Format, clippy, test
cargo test          # All tests pass
cargo clippy        # No warnings
python3 validate_governance.py  # Governance passes
```

### PR Gates

```bash
# CI/CD enforces on pull requests
.github/workflows/traceability.yml
├── Validate AI attribution
├── Check FR coverage
├── Run tests
├── Check code coverage
└── Generate FR report
```

### Release Gates

```bash
# Before release
cargo test --release
cargo bench         # Performance regression check
python3 validate_governance.py  # 100% pass rate
./AgilePlus/bin/ptrace check-drift --threshold 0  # Zero drift
```

## Agent Interaction Rules

### For AI Assistants (from AGENTS.md)

1. **Always add FR annotations** to new test functions
2. **Update PRD.md** when adding new features
3. **Create ADR** for architecture changes
4. **Run validate_governance.py** before finishing work
5. **Maintain 0% drift** - every FR must have test coverage

### For Human Developers

1. **Start with FR spec** - Write detailed spec before coding
2. **User stories first** - Define Given/When/Then
3. **Story points** - Estimate effort before sprint
4. **Work packages** - Break down into assignable units
5. **Traceability** - Add `#[trace_to("FR-XXX")]` to all tests

## Validation Checklist

Before marking work complete:

- [ ] Artifact created/updated (CLAUDE.md, PRD.md, ADR.md, FR spec)
- [ ] Task items defined (user stories, acceptance criteria, work packages)
- [ ] Story points estimated
- [ ] FR annotations added to tests
- [ ] CI/CD passes (traceability workflow)
- [ ] Governance validation passes (`python3 validate_governance.py`)
- [ ] Code coverage ≥80%
- [ ] No clippy warnings
- [ ] Code formatted

## Drift Policy

**Target: 0% drift**

Every FR must have:
1. Complete spec with user stories
2. Test coverage with FR annotations
3. Implementation that satisfies acceptance criteria

**Drift Detection:**
```bash
./AgilePlus/bin/ptrace check-drift --path . --threshold 0
```

**Remediation:**
- Drift > 0% blocks release
- Weekly drift reviews
- Sprint planning includes drift remediation

## Compliance Dashboard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Governance validation | 100% | 12/15 | 🟡 |
| FR traceability | 100% | 6/6 | 🟢 |
| Test coverage | ≥80% | TBD | 🟡 |
| Drift | 0% | 0% | 🟢 |
| Clippy warnings | 0 | TBD | 🟡 |

## Contact

- **Maintainer:** thegent-core-team
- **Governance Issues:** File issue with `governance` label
- **Validation Help:** `python3 validate_governance.py --help`

---

**Last Updated:** 2026-04-04  
**Version:** 1.0  
**Next Review:** 2026-04-18
