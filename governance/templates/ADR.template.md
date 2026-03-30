# Architecture Decision Record (ADR)

**ADR ID**: ADR-[PROJECT]-[NNN]
**Title**: [Concise title of decision]
**Date**: [YYYY-MM-DD]
**Author**: [Team/Person making decision]
**Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

---

## Context

### Problem Statement

Describe the architectural problem or decision that needed to be made:
- What decision needed to be made?
- What triggered this decision?
- What constraints or requirements drove this?
- Who are the stakeholders?

### Background

Provide context on:
- Current system architecture
- Why the current approach is insufficient
- Technical or business pressure points

### Requirements

What must the solution satisfy?
- **Functional requirements**: What must it do?
- **Non-functional requirements**: Performance, scalability, maintainability?
- **Constraints**: Budget, timeline, team skills?
- **Quality attributes**: Security, reliability, testability?

---

## Decision

### Chosen Alternative

State the decision clearly and concisely:

> [We have decided to use/adopt/implement [DECISION] because [KEY REASON].]

### Key Details

Provide implementation details:
- **What**: What exactly are we doing?
- **How**: How will it be implemented?
- **When**: Timeline for adoption?
- **Who**: Who is responsible?

### Design Overview

High-level architecture or design:

```
┌─────────────┐
│  Component  │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Component 2 │
└─────────────┘
```

Or describe in text.

---

## Alternatives Considered

### Alternative 1: [Option A]

**Description**: [What is this option?]

**Pros**:
- Pro 1
- Pro 2
- Pro 3

**Cons**:
- Con 1
- Con 2
- Con 3

**Effort**: [S/M/L/XL]
**Risk**: [Low/Medium/High]

---

### Alternative 2: [Option B]

**Description**: [What is this option?]

**Pros**:
- Pro 1
- Pro 2

**Cons**:
- Con 1
- Con 2

**Effort**: [S/M/L/XL]
**Risk**: [Low/Medium/High]

---

### Alternative 3: [Option C]

**Description**: [What is this option?]

**Pros**:
- Pro 1

**Cons**:
- Con 1
- Con 2
- Con 3

**Effort**: [S/M/L/XL]
**Risk**: [Low/Medium/High]

---

## Rationale

Why we chose this alternative:

### Comparison Matrix

| Criteria | Weight | Alt 1 | Alt 2 | Alt 3 | Winner |
|----------|--------|-------|-------|-------|--------|
| Performance | 25% | 8 | 9 | 6 | Alt 2 |
| Maintainability | 20% | 7 | 7 | 8 | Alt 3 |
| Team Skills | 20% | 9 | 5 | 6 | Alt 1 |
| Cost | 15% | 8 | 6 | 9 | Alt 3 |
| Scalability | 20% | 7 | 8 | 5 | Alt 2 |
| **Total** | **100%** | **7.5** | **7.0** | **6.8** | **Alt 1** |

### Key Decision Factors

1. **Technical**: [Why technically superior]
2. **Business**: [Why business value]
3. **Risk**: [How we mitigate risk]
4. **Team**: [Team alignment/capability]

---

## Consequences

### Positive Consequences (Benefits)

- **Benefit 1**: [What good outcome will this bring?]
- **Benefit 2**: [Performance improvement, code maintainability, etc.]
- **Benefit 3**: [Reduced technical debt, faster feature development, etc.]

### Negative Consequences (Drawbacks)

- **Drawback 1**: [What cost will this incur?]
- **Drawback 2**: [Learning curve, migration effort, etc.]
- **Drawback 3**: [Increased complexity, breaking changes, etc.]

### Neutral Consequences

- **Consequence 1**: [Neutral impact]

---

## Implementation Plan

### Phase 1: [Phase Title]

**Timeline**: [Start date] - [End date]
**Effort**: [X person-days]

**Tasks**:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

**Deliverables**:
- [What is delivered]
- [What is delivered]

**Success Criteria**:
- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

---

### Phase 2: [Phase Title]

**Timeline**: [Start date] - [End date]
**Effort**: [X person-days]

**Tasks**:
- [ ] Task 1
- [ ] Task 2

**Deliverables**:
- [What is delivered]

**Success Criteria**:
- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

---

## Rollback Plan

What is our plan if this decision doesn't work out?

- **Rollback trigger**: [When would we rollback?]
- **Rollback steps**: [How to revert?]
- **Rollback timeline**: [How long to rollback?]
- **Rollback cost**: [Time and effort]

---

## Related Decisions

### Previous Decisions

- **ADR-001**: [Previous decision that led to this one]
- **ADR-005**: [Related architectural decision]

### Supersedes

- **ADR-XXX**: This ADR supersedes ADR-XXX because [reason]

### Superseded By

- **ADR-YYY**: ADR-YYY supersedes this decision due to [reason]

---

## Approval & Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Tech Lead | [Name] | [ ] | [ ] |
| Architecture Review | [Name] | [ ] | [ ] |
| Product Owner | [Name] | [ ] | [ ] |

---

## Monitoring & Review

### Success Metrics

How will we know this decision was the right one?

| Metric | Target | Measurement | Frequency |
|--------|--------|-------------|-----------|
| Performance | 200ms | Response time P95 | Daily |
| Availability | 99.9% | Uptime | Daily |
| Adoption | 100% | Team usage | Weekly |
| Maintainability | +20% | Code review speed | Monthly |

### Review Schedule

- **3-month review**: [Review progress and impact]
- **6-month review**: [Full evaluation]
- **Annual review**: [Long-term effectiveness]

### Decision Log

| Date | Event | Notes |
|------|-------|-------|
| [DATE] | Decision Made | Initial approval |
| [DATE] | Phase 1 Complete | Milestone met |
| [DATE] | Review | Metrics show success |

---

## Examples & References

### Code Examples

```python
# Example implementation
class MyService:
    def __init__(self, dependency):
        self.dependency = dependency

    def process(self):
        return self.dependency.execute()
```

### Links & References

- [Link to implementation code]
- [Link to PR]
- [Link to design docs]
- [Link to related research]

---

## FAQ

**Q: Why not just [alternative]?**
A: [Explain why the alternative is not suitable]

**Q: When will this be rolled out?**
A: [Implementation timeline]

**Q: How do we migrate existing code?**
A: [Migration strategy]

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DATE] | [AUTHOR] | Initial version |
| 1.1 | [DATE] | [AUTHOR] | Added implementation plan |

---

## Appendix

### A. Detailed Design

[Link to detailed architecture diagrams or design docs]

### B. Research & Analysis

[Link to technical research or POC results]

### C. Team Feedback

[Summary of team discussion and concerns raised]

### D. Competitive Analysis

[How do other projects/companies handle this?]
