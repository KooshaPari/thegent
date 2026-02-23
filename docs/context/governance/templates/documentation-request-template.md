# Documentation Request: [Feature/Area Name]

Use this template to request new documentation for features, areas, or content gaps in the Ante documentation. Submit completed forms to the Content Owner via the documentation review process.

## Required Information

### Summary
[One-sentence description of what needs to be documented]

**Example:** "Documentation for the new --context-size flag introduced in v0.2.0 to help users optimize memory usage."

---

### Type of Request
- [ ] New documentation (entirely new topic)
- [ ] Update to existing documentation (additions/modifications)
- [ ] Removal/deprecation (content no longer relevant)

---

### Scope Definition

**Features/Topics Covered:**
- [ ] [Feature 1]
- [ ] [Feature 2]
- [ ] [Feature 3]

**Intended Audience:**
- [ ] New users
- [ ] Existing users
- [ ] Advanced users
- [ ] System administrators
- [ ] Developers/Contributors

**Related Existing Documentation:**
List documentation that connects to or impacts this request:
- [Link to related doc 1]
- [Link to related doc 2]
- [Link to related doc 3]

---

### Rationale

**Why This Documentation is Needed:**
[Detailed explanation of the gap or need]

**Business Impact:**
- Estimated number of affected users: [Number or estimate]
- Frequency of questions/support requests: [ ] High [ ] Medium [ ] Low
- Risk if not documented: [Explain impact of missing documentation]
- Expected outcome: [How will this benefit users/team]

---

### Proposed Content

**Suggested Documentation Structure:**

```markdown
# [Main Topic]

## Overview
- What is [feature]
- When users would need this
- Key benefits/use cases

## Core Concepts
- Important terms
- Relationships to other features

## Configuration/Usage
- How to use
- Common patterns
- Basic examples

## Advanced Usage
- Less common scenarios
- Performance considerations
- Edge cases

## Limitations & Constraints
- Known limitations
- Related features

## Troubleshooting
- Common issues
- Solutions and workarounds

## See Also
- Related documentation links
```

**Key Points to Cover:**
- [ ] Feature overview and purpose
- [ ] Prerequisites and dependencies
- [ ] Configuration/setup steps
- [ ] Common use cases with examples
- [ ] Advanced/less common usage patterns
- [ ] Limitations and edge cases
- [ ] Error handling and troubleshooting
- [ ] Performance implications
- [ ] Version compatibility information

---

### Dependencies

**Documentation Dependencies:**
List other documentation that must exist or be updated first:
- [ ] [Dependency 1] - status: [planned/in-progress/complete]
- [ ] [Dependency 2] - status: [planned/in-progress/complete]
- [ ] [Dependency 3] - status: [planned/in-progress/complete]

**Feature Dependencies:**
Does this documentation depend on features being released?
- [ ] No dependencies
- [ ] Depends on v[version] release (expected: [date])
- [ ] Depends on feature branch: [branch name]

---

### Placement in Documentation Hierarchy

**Suggested Location:**
Documentation Home → [Section] → [Subsection] → [Page Name]

**Example:** Documentation Home → User Guide → Advanced Usage → Context Management

**Justification:**
[Why this location makes sense for users]

---

### Effort Estimation

**Content Volume:**
- [ ] Small (1-3 pages, < 500 lines)
- [ ] Medium (4-8 pages, 500-2000 lines)
- [ ] Large (8+ pages, 2000+ lines)

**Estimated Hours:**
[Estimate for research, writing, review, revision]

**Timeline:**
- Start date: [Proposed]
- Target completion: [Proposed]
- Release date (if tied to feature): [Date]

**Resource Requirements:**
- Primary author: [Name/role]
- Technical reviewer: [Name/role]
- QA reviewer: [Name/role]
- Content owner: [Name/role]

---

### Success Criteria

How will we know this documentation is complete and successful?

**Quality Metrics:**
- [ ] All key features/options are documented
- [ ] Code examples are tested and working
- [ ] Documentation passes QA review
- [ ] Follows all standards from STANDARDS.md
- [ ] Cross-references are complete
- [ ] No broken links or references

**Adoption Metrics:**
- [ ] [Specific measurable outcome]
- [ ] [User feedback or metric]

**User Impact:**
- [ ] Reduces support questions about [topic]
- [ ] Enables users to [specific capability]
- [ ] Improves adoption of [feature]

---

### Approval Status

**Approval Workflow:** Type B - Content Owner Approval Required

**Approver:** [Content Owner Name]
**Target Approval Date:** [Within 3 business days]

**Approval Checklist:**
- [ ] Scope is clearly defined
- [ ] Business need is justified
- [ ] Placement is appropriate
- [ ] Resources are allocated
- [ ] Timeline is realistic

---

## Submission Instructions

### How to Submit

1. **Complete all sections** in this template (leave N/A for non-applicable items)
2. **Attach supporting materials:**
   - Links to related feature documentation
   - Links to similar documentation for reference
   - Any preliminary outlines or research
3. **Save as:** `documentation-request-[YYYY-MM-DD]-[feature-name].md`
4. **Submit to:** Content Owner via [submission method]

### Review Timeline

| Phase | Timeframe | Owner |
|-------|-----------|-------|
| Initial Review | 1 business day | Content Owner |
| Approval Decision | 3 business days | Content Owner |
| Resource Allocation | 2 business days | Content Owner |
| Begin Documentation | [As scheduled] | Assigned Author |

### Questions?

- **General questions:** Contact [Content Owner Email]
- **Process questions:** Refer to governance/PROCESSES.md
- **Standards questions:** Refer to governance/STANDARDS.md

---

## Notes for Requestor

- **Be specific:** Vague requests may be rejected or delayed for clarification
- **Research first:** Check existing documentation to ensure you're not requesting duplicates
- **Provide examples:** Help the Content Owner understand the scope with concrete examples
- **Think about audience:** Consider who will read this and what they need to know
- **Early notification:** Submit requests as early as possible for better scheduling

---

## Content Owner Notes

This section is for the Content Owner to complete during review:

**Approval Status:** [ ] Approved [ ] Conditional [ ] Rejected

**Comments:**
[Feedback or questions for requestor]

**Resource Assignment:**
- Primary Author: [Name]
- Technical Reviewer: [Name]
- QA Reviewer: [Name]

**Scheduled Start Date:** [Date]

**Approval Date:** [Date] - **Signed:** [Content Owner Name]
