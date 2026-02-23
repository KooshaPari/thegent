# Documentation & Specification Taxonomy

## Purpose
Comprehensive taxonomy of all document types in the workspace for agentic development and human consumption.

---

## I. HUMAN-FACING DOCS

### User & Developer Guides
| Type | Pattern | Purpose |
|------|---------|----------|
| USER_GUIDE | `*_GUIDE*.md` | End-user documentation |
| QUICK_START | `*_QUICK_START*.md` | Getting started |
| TUTORIAL | `*_TUTORIAL*.md` | How-to guides |
| REFERENCE | `*_REFERENCE.md` | API/component reference |
| PLAYBOOK | `*_PLAYBOOK.md` | Operational procedures |
| RUNBOOK | `*_RUNBOOK.md` | Incident response |

### Conceptual & Explanatory
| Type | Pattern | Purpose |
|------|---------|----------|
| EXPLAINER | `*_EXPLAINER*.md` | Concept introduction |
| GUIDE | `*_GUIDE*.md` | Deep-dive documentation |
| OVERVIEW | `*_OVERVIEW.md` | High-level summary |
| HANDBOOK | `*_HANDBOOK.md` | Comprehensive manuals |

---

## II. TECHNICAL SPECIFICATIONS

### Formal Specs
| Type | Pattern | Purpose |
|------|---------|----------|
| SPEC | `*SPEC*.md`, `SPEC.md` | Technical specification |
| PROTOCOL | `*PROTOCOL*.md` | Protocol definition |
| CONTRACT | `*CONTRACT*.md` | Interface contracts |

### Architecture
| Type | Pattern | Purpose |
|------|---------|----------|
| ARCHITECTURE | `*ARCHITECTURE*.md` | System design |
| DESIGN | `*DESIGN.md` | Implementation design |
| DECISION | `ADR-*.md` | Architecture decisions |

---

## III. PLANNING & TRACKING

### Strategic
| Type | Pattern | Purpose |
|------|---------|----------|
| ROADMAP | `*ROADMAP*.md` | Long-term planning |
| MASTER_PLAN | `MASTER_PLAN*.md` | Implementation plan |
| STRATEGY | `*STRATEGY*.md` | Strategic direction |

### Tactical
| Type | Pattern | Purpose |
|------|---------|----------|
| PLAN | `*PLAN*.md` | Implementation planning |
| WBS | `*WBS.md` | Work breakdown |
| IMPLEMENTATION | `*IMPLEMENTATION*.md` | Execution plan |
| BATCH | `*BATCH*.md` | Batch planning |

### Tracking
| Type | Pattern | Purpose |
|------|---------|----------|
| TRACKER | `*TRACKER.md` | Item tracking |
| STATUS | `*STATUS.md` | Status reporting |
| PROGRESS | `*PROGRESS.md` | Progress reports |

---

## IV. RESEARCH & EXPLORATION

### Exploratory
| Type | Pattern | Purpose |
|------|---------|----------|
| RESEARCH | `*RESEARCH*.md` | Investigation findings |
| INVESTIGATION | `*INVESTIGATION*.md` | Deep-dive analysis |
| AUDIT | `*AUDIT*.md` | Code/state audit |
| ANALYSIS | `*ANALYSIS*.md` | Data analysis |
| SPARSE | `*SPrawl*.md` | Exploration sprawl |

### Synthesized
| Type | Pattern | Purpose |
|------|---------|----------|
| SYNTHESIS | `*SYNTHESIS*.md` | Combined research |
| SURVEY | `*SURVEY*.md` | Landscape survey |
| BENCHMARK | `*BENCHMARK*.md` | Performance data |
| STUDY | `*STUDY.md` | Feasibility study |

---

## V. VALIDATION & QUALITY

### Testing
| Type | Pattern | Purpose |
|------|---------|----------|
| TEST_PLAN | `*TEST*.md` | Testing strategy |
| MATRIX | `*MATRIX.md` | Coverage matrix |
| CASES | `*CASES.md` | Test cases |

### Quality Gates
| Type | Pattern | Purpose |
|------|---------|----------|
| VALIDATION | `*VALIDATION*.md` | Verification results |
| VERIFICATION | `*VERIFICATION*.md` | Check results |
| EVIDENCE | `*EVIDENCE.md` | Proof of completion |

---

## VI. OPERATIONAL

### Runbooks
| Type | Pattern | Purpose |
|------|---------|----------|
| RUNBOOK | `RUNBOOK.md` | Incident response |
| PLAYBOOK | `PLAYBOOK.md` | Operational procedures |
| CHECKLIST | `CHECKLIST.md` | Manual checks |

### Monitoring
| Type | Pattern | Purpose |
|------|---------|----------|
| OBSERVATION | `*OBSERVATION*.md` | Monitoring setup |
| ALERTING | `*ALERTING*.md` | Alert definitions |
| DASHBOARD | `DASHBOARD*.md` | Dashboards |

---

## VII. TEMPLATES & STANDARDS

### Templates
| Type | Pattern | Purpose |
|------|---------|----------|
| TEMPLATE | `*TEMPLATE*.md` | Document templates |
| TEMPLATE | `*_TEMPLATE.md` | Reusable patterns |
| STUB | `*STUB.md` | Placeholder docs |

### Standards
| Type | Pattern | Purpose |
|------|---------|----------|
| STANDARD | `*STANDARD.md` | Coding standards |
| CONVENTION | `*CONVENTION*.md` | Naming/formatting |
| POLICY | `*POLICY.md` | Team policies |
| GUIDELINES | `*GUIDELINES.md` | Best practices |

---

## VIII. INDEXES & CATALOGS

### Discovery
| Type | Pattern | Purpose |
|------|---------|----------|
| INDEX | `*INDEX.md` | Content index |
| CATALOG | `CATALOG*.md` | Item listing |
| MANIFEST | `MANIFEST.md` | Project manifest |
| REGISTRY | `REGISTRY.md` | Service registry |

---

## Document Type Hierarchy

```
Human Docs
├── Guides (USER_GUIDE, QUICK_START, TUTORIAL)
├── Reference (REFERENCE, PLAYBOOK, RUNBOOK)
└── Conceptual (EXPLAINER, OVERVIEW, HANDBOOK)

Technical Specs
├── Formal (SPEC, PROTOCOL, CONTRACT)
└── Architecture (ARCHITECTURE, DESIGN, ADR)

Planning
├── Strategic (ROADMAP, MASTER_PLAN, STRATEGY)
├── Tactical (PLAN, WBS, IMPLEMENTATION)
└── Tracking (TRACKER, STATUS, PROGRESS)

Research
├── Exploratory (RESEARCH, AUDIT, ANALYSIS)
└── Synthesized (SYNTHESIS, SURVEY, BENCHMARK)

Validation
├── Testing (TEST_PLAN, MATRIX)
└── Quality (VALIDATION, VERIFICATION)

Operational
├── Runbooks (RUNBOOK, PLAYBOOK)
└── Monitoring (OBSERVATION, DASHBOARD)
```

---

## Maintenance Guidelines

### When Creating New Docs
1. **Identify type** → Use taxonomy above
2. **Check existing** → Search INDEX files first
3. **Use template** → Reference TEMPLATE if available
4. **Add to index** → Update relevant INDEX.md

### File Naming
- Use kebab-case: `my-document-type.md`
- Prefix for grouping: `PROJECT_TYPE_description.md`
- Version in filename: `2026-02-` prefix for dated

### Location Guidance
| Doc Type | Primary Location |
|----------|-----------------|
| USER_GUIDE | docs/guides/ |
| SPEC | docs/specs/ or docs/reference/ |
| RESEARCH | docs/research/ |
| PLAN | docs/planning/ |
| RUNBOOK | docs/operations/ |
| TEMPLATE | templates/ |
| INDEX | docs/ root |
