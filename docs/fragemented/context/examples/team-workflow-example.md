# Team Workflow Example: Documentation Request Lifecycle

## Scenario: Adding "Authentication Guide" Feature Documentation

**Context**: Product team wants to add comprehensive authentication guide for new SSO feature

**Timeline**: Monday 9am - Friday 5pm (5 business days)

---

## Stage 1: Request (Monday 9:00am - 11:00am)

### Participant: Product Manager (Sarah)

**Action**: Create documentation request

**Template Used**: `governance/templates/documentation-request.md`

```markdown
# Documentation Request

**Request ID**: DOC-2024-0234
**Submitted By**: Sarah Chen, Product Manager
**Date**: Monday 9:00am
**Priority**: High
**Target Completion**: Friday EOD

## Request Details

**Title**: Add SSO Authentication Integration Guide

**Scope**: 
- Overview of SSO integration
- Step-by-step implementation guide
- Configuration reference
- Troubleshooting section

**Audience**: Engineers implementing SSO
**Estimated Length**: 3000-4000 words
**Related Features**: UserAuth, IdentityProvider

## Success Criteria
- [ ] Complete implementation guide
- [ ] Code examples included
- [ ] Configuration documented
- [ ] Troubleshooting section
- [ ] Links to related docs

## Stakeholders
- @james (Engineering Lead)
- @priya (Security Officer)
- @mike (DevOps)
```

**Output**: Request enters workflow queue

---

## Stage 2: Initial Review (Monday 11:00am - 2:00pm)

### Participants: Documentation Lead (Elena) + Quality Reviewer (Tom)

**Action**: Triage and assign documentation

**Template Used**: `governance/templates/assignment.md`

**Review Checklist**:
- [x] Scope is clear and achievable
- [x] Timeline is realistic
- [x] Stakeholders identified
- [x] Success criteria measurable
- [ ] Sensitive content flagged (no issues)

**Assignment Decision**: APPROVED FOR WRITING

```
Assigned Writer: @lisa
Assigned Reviewer: @elena
Estimated Time: 6-8 hours
Target Completion: Wednesday EOD
```

**Comment**: "Good request, scope is well-defined. Lisa is best fit for authentication docs. Start with architecture overview, then implementation steps."

---

## Stage 3: Writing (Monday 2:00pm - Wednesday 4:00pm)

### Participant: Technical Writer (Lisa)

**Action**: Draft documentation

**Process**:
1. Research existing auth docs (30 min)
2. Interview engineers about new SSO feature (1 hour)
3. Write first draft (3-4 hours)
4. Self-review against checklist (30 min)

**Template Used**: `governance/templates/documentation-content.md`

**Draft Outline**:
```
1. Overview
   - What is SSO?
   - When to use
   - Benefits

2. Architecture
   - System diagram
   - Data flow

3. Implementation Guide
   - Prerequisites
   - Installation steps
   - Configuration

4. Reference
   - Configuration options
   - Environment variables
   - API endpoints

5. Troubleshooting
   - Common issues
   - Debug steps
```

**Output**: Draft submitted Tuesday 3:00pm with self-review notes

```
Self-Review Checklist:
- [x] Grammar/spelling reviewed
- [x] Code examples tested
- [x] Links verified
- [x] Formatting consistent
- [ ] Screenshots added (planned for review round)
```

---

## Stage 4: Content Review (Tuesday 3:00pm - Thursday 10:00am)

### Participants: 
- Documentation Lead (Elena) - Content
- Security Officer (Priya) - Security review
- Engineer (James) - Technical accuracy

**Elena's Review** (Tuesday 4pm):
```
Status: CONTENT REVIEW IN PROGRESS

Comments:
- Great structure, flows well
- Add security best practices section
- Move troubleshooting to appendix
- Add quick-start box at top
- 2 code examples need minor fixes

Recommendation: REVISE, then send to security review
Timeline: +1 day
```

**Priya's Security Review** (Wednesday 9am):
```
Status: SECURITY REVIEW COMPLETE

Comments:
- ✓ No secrets in examples
- ✓ Security practices documented
- ⚠ Add warning about password reset flow
- ⚠ Document rate limiting recommendations

Recommendation: APPROVED WITH MINOR CHANGES
Timeline: Can proceed with revisions
```

**James' Technical Review** (Wednesday 10am):
```
Status: TECHNICAL REVIEW COMPLETE

Comments:
- Code examples are accurate
- Configuration options correct
- One API endpoint deprecated (v1 → v2)
- Add note about rollback procedure

Recommendation: APPROVED WITH CORRECTIONS
Timeline: 1 day to address items
```

**Consolidated Feedback Summary**:
- Content revisions needed: 5
- Security revisions needed: 2
- Technical corrections: 2

---

## Stage 5: Revision (Wednesday 1:00pm - Thursday 2:00pm)

### Participant: Technical Writer (Lisa)

**Revisions Made**:
1. Added security best practices section
2. Added password reset flow warning
3. Moved troubleshooting to appendix
4. Fixed code examples (v2 API)
5. Added rate limiting recommendations
6. Added quick-start section
7. Added rollback procedure
8. Added "What's next" section

**Revision Output**:
- Thursday 2:00pm: Updated draft submitted
- Timestamp: All changes tracked
- Version: 2.0

---

## Stage 6: Approval (Thursday 2:00pm - 3:30pm)

### Participant: Approver (Elena, Documentation Lead)

**Final Review**:
```
Status: READY FOR APPROVAL

Verification:
- [x] All reviewer comments addressed
- [x] Quality standards met
- [x] Formatting complete
- [x] Links working
- [x] Code examples valid
- [x] Security reviewed
- [x] Technical accuracy confirmed

Compliance Check:
- [x] Style guide compliant
- [x] Template format correct
- [x] Metadata complete
- [x] Cross-references updated
```

**Approval Decision**: ✅ APPROVED FOR PUBLICATION

**Approval Certificate**:
```
Documentation ID: DOC-2024-0234
Title: SSO Authentication Integration Guide
Approved By: Elena Rodriguez (Documentation Lead)
Date: Thursday 3:30pm
Effective Date: Friday 9:00am

This documentation has been reviewed and approved
for publication to the knowledge base.
```

---

## Stage 7: QA Testing (Thursday 3:30pm - Friday 11:00am)

### Participants: QA Lead (Tom) + Engineer (James)

**QA Checklist**:
- [x] All code examples execute successfully
- [x] Code examples produce expected output
- [x] All links are working
- [x] Screenshots display correctly
- [x] Formatting renders properly
- [x] Search optimization verified
- [x] Related docs linked correctly

**Testing Results**:
```
Found 1 minor issue:
- Code example 3 needs one-line fix (syntax error in env var)

Status: APPROVED FOR RELEASE (with 1 minor fix)
Time to fix: < 5 minutes
```

---

## Stage 8: Release (Friday 9:00am - 10:00am)

### Participants: DevOps (Mike) + Documentation System Admin

**Release Process**:
1. Final code example fix applied (9:05am)
2. Final QA verification (9:15am)
3. Publish to wiki (9:30am)
4. Regenerate llms.txt (9:35am)
5. Update search index (9:40am)
6. Clear CDN cache (9:45am)

**Release Confirmation**:
```
Documentation Released Successfully
ID: DOC-2024-0234
Title: SSO Authentication Integration Guide
Published: Friday 10:00am
URL: /docs/guides/authentication/sso-integration
Visibility: Public

Notifications sent to:
- Product team ✓
- Engineering team ✓
- Stakeholders ✓
```

---

## Stage 9: Post-Release (Friday 10:00am - 5:00pm)

### Participant: Documentation Lead (Elena)

**Post-Release Tasks**:
- [x] Monitor user feedback
- [x] Track documentation views
- [x] Answer initial questions
- [x] Log any issues found

**Metrics Collected**:
- Published: Friday 10:00am
- First view: Friday 10:15am (2 minutes after release)
- Views by EOD: 47 views
- Feedback: 0 issues reported
- Success score: 10/10

---

## Lifecycle Summary

| Stage | Duration | Participant(s) | Status |
|-------|----------|---|--------|
| Request | 2 hrs | Sarah (PM) | ✓ Complete |
| Initial Review | 3 hrs | Elena, Tom | ✓ Complete |
| Writing | 48 hrs | Lisa | ✓ Complete |
| Content Review | 30 hrs | Elena, Priya, James | ✓ Complete |
| Revision | 25 hrs | Lisa | ✓ Complete |
| Approval | 1.5 hrs | Elena | ✓ Complete |
| QA Testing | 8 hrs | Tom, James | ✓ Complete |
| Release | 1 hr | Mike, Admin | ✓ Complete |
| **Total Time** | **5 business days** | 5 people | **RELEASED** |

---

## Templates Used

1. **Documentation Request** (`governance/templates/documentation-request.md`)
   - Used by: Product Manager
   - When: Stage 1

2. **Assignment Form** (`governance/templates/assignment.md`)
   - Used by: Documentation Lead
   - When: Stage 2

3. **Content Template** (`governance/templates/documentation-content.md`)
   - Used by: Technical Writer
   - When: Stage 3

4. **Review Checklist** (`governance/templates/review-checklist.md`)
   - Used by: All reviewers
   - When: Stage 4

5. **Approval Certificate** (`governance/templates/approval-certificate.md`)
   - Used by: Approver
   - When: Stage 6

6. **QA Checklist** (`governance/templates/qa-checklist.md`)
   - Used by: QA Lead
   - When: Stage 7

7. **Release Notes** (`governance/templates/release-notes.md`)
   - Used by: DevOps
   - When: Stage 8

---

## Key Insights from This Example

### What Worked Well
- Clear scope in initial request
- Parallel reviews (security, technical, content)
- Effective feedback aggregation
- Rapid revision cycle
- Comprehensive QA before release

### Timeline Breakdown
- Writing: ~40% of time (2 days)
- Review/feedback: ~50% of time (2.5 days)
- Approval/QA/Release: ~10% of time (0.5 days)

### Lessons Learned
1. Parallel reviews save significant time
2. Early security review prevents rework
3. Technical accuracy feedback must be clear
4. QA testing catches small but important issues
5. Post-release monitoring validates quality

---

## Variations for Different Request Types

### Fast-Track (Low Complexity)
- Duration: 1-2 business days
- Reviews: Content only (no security/technical)
- Use for: Updates, minor additions

### Standard (Medium Complexity)
- Duration: 3-5 business days (this example)
- Reviews: Content, technical, security
- Use for: New features, significant updates

### Extended (High Complexity)
- Duration: 1-2 weeks
- Reviews: Multiple rounds, SME consultation
- Use for: Major features, compliance docs

---

## Related Documentation
- Governance Framework: `docs/context/governance/README.md`
- Approval Workflows: `docs/context/governance/workflows/`
- Template Library: `docs/context/governance/templates/`
- Best Practices: `docs/context/governance/best-practices.md`
