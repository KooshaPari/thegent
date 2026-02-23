# Merged Fragmented Markdown

## Source: docs/context/governance

## Source: GOVERNANCE.md

# Ante LLM Context Documentation Governance Framework

## 1. Purpose and Objectives

The LLM context documentation system serves to provide authoritative, up-to-date information about the Ante CLI and its capabilities to language models. The primary objectives are:

- **Accuracy**: Maintain single-source-of-truth documentation that accurately reflects Ante functionality
- **Accessibility**: Ensure LLMs can efficiently access and utilize documentation context
- **Maintainability**: Establish clear processes for keeping documentation current with Ante releases
- **Consistency**: Maintain uniform formatting, structure, and quality across all documentation
- **Trustworthiness**: Enable confident use of documentation by both users and LLM systems
- **Compliance**: Track and ensure documentation meets organizational standards

## 2. Core Principles

### 2.1 Authority
- Documentation must accurately represent current Ante functionality
- All claims must be verifiable against actual system behavior
- Breaking changes in Ante must be immediately reflected in documentation

### 2.2 Clarity
- Documentation is written for both humans and LLMs
- Technical accuracy takes priority over marketing language
- Examples must be functional and tested

### 2.3 Completeness
- All public APIs, commands, and features must be documented
- Edge cases and limitations should be clearly noted
- Integration points and workflows must be documented

### 2.4 Maintainability
- Documentation structure must support efficient updates
- Version information must be clearly stated
- Obsolete content must be archived, not deleted
- Change tracking must be maintained

### 2.5 Consistency
- Naming conventions must be followed throughout
- Formatting standards must be applied uniformly
- Cross-references must be accurate and complete
- Terminology must be consistent across documents

## 3. Versioning Strategy

### 3.1 Documentation Versioning
- Documentation versions align with Ante release versions
- Format: `v[MAJOR].[MINOR].[PATCH]`
- Major version changes indicate breaking documentation changes
- Minor version changes indicate new features or content additions
- Patch version changes indicate corrections or clarifications

### 3.2 Content Versioning
- Each document includes metadata with:
  - Last updated date
  - Documentation version
  - Ante compatibility range
  - Status (Current, Beta, Deprecated)

### 3.3 Backward Compatibility
- Current documentation should remain valid for at least 2 minor versions
- Deprecated features must be marked and documented for 1 full release cycle
- Archive older versions in the `archive/` directory
- Migration guides required for major breaking changes

### 3.4 Version Tracking
```
---
version: 1.0.0
ante_version: ">=0.1.0"
last_updated: 2026-02-20
status: current
---
```

## 4. Decision-Making Process

### 4.1 Documentation Change Classification

**Type A: Routine Updates** (No approval required)
- Corrections of factual errors
- Clarification of existing content
- Addition of examples for documented features
- Formatting or grammatical fixes

**Type B: Feature Documentation** (Content owner approval)
- Documentation of new Ante features
- New sections or comprehensive rewrites
- Addition of new processes or procedures
- Changes affecting user workflows

**Type C: Policy Changes** (Governance council approval)
- Changes to documentation standards
- Changes to review processes
- Changes to versioning strategy
- Deprecation of documented features

### 4.2 Change Request Process

1. **Proposal**: Submit documentation change with justification
2. **Review**: Assigned reviewer examines for accuracy and standards compliance
3. **Validation**: Verify against actual Ante behavior
4. **Approval**: Governance council or content owner approves
5. **Implementation**: Changes are merged to main documentation
6. **Communication**: Users/LLMs notified of significant changes

### 4.3 Review Criteria

All changes must satisfy:
- Accuracy against current Ante version
- Compliance with documentation standards
- No contradictions with other documentation
- Completeness of related information
- Appropriate detail level for target audience

## 5. Roles and Responsibilities

### 5.1 Documentation Owner
- **Responsibility**: Overall documentation quality and coherence
- **Authority**: Approves all documentation changes
- **Accountability**: Ensures standards compliance and accuracy
- **Time Commitment**: 5-10 hours per week

### 5.2 Content Maintainers
- **Responsibility**: Keep assigned documentation sections current
- **Authority**: Can approve Type A changes within their section
- **Accountability**: Section accuracy and completeness
- **Time Commitment**: 3-5 hours per week
- **Assigned Areas**: 
  - CLI Commands and Options
  - API Reference
  - Integration Guides
  - Troubleshooting

### 5.3 LLM Context Specialists
- **Responsibility**: Optimize documentation for LLM consumption
- **Authority**: Review for clarity and LLM-accessibility
- **Accountability**: Ensure LLMs can effectively utilize documentation
- **Time Commitment**: 2-3 hours per week

### 5.4 Quality Assurance Lead
- **Responsibility**: Validate documentation accuracy
- **Authority**: Can block changes that fail quality checks
- **Accountability**: Overall documentation quality standards
- **Time Commitment**: 3-5 hours per week

### 5.5 Governance Council
- **Composition**: Documentation Owner, QA Lead, 2 Content Maintainers
- **Responsibility**: Approve Type C (policy) changes
- **Frequency**: Monthly review meetings
- **Decision Rule**: Consensus required for policy changes

## 6. Review and Approval Workflows

### 6.1 Standard Review Workflow

```
Change Proposal
    ↓
Type Classification
    ├→ Type A: Direct Implementation
    ├→ Type B: Content Owner Review → QA Validation → Merge
    └→ Type C: Council Discussion → Vote → Implementation
    ↓
Implementation
    ↓
Communication
```

### 6.2 Review Checklist

Before approval, reviewers must confirm:

- [ ] Content is accurate for current Ante version
- [ ] Documentation standards are followed
- [ ] No contradictions with existing documentation
- [ ] All related documentation is updated
- [ ] Examples are tested and functional
- [ ] Formatting and structure are consistent
- [ ] Links and references are valid
- [ ] Metadata is current

### 6.3 Approval Authority Matrix

| Change Type | Requires | Approval Time | Authority |
|------------|----------|---------------|-----------|
| Type A (Routine) | Submitter review | N/A | Self-approved |
| Type B (Feature) | Content owner | 3 business days | Content maintainer |
| Type C (Policy) | Council vote | 5 business days | Governance council |
| Emergency fixes | Documentation owner | Same day | Owner + 1 other |

### 6.4 Documentation Review SLA
- Type A changes: Same day feedback
- Type B changes: 3 business day turnaround
- Type C changes: 5 business day turnaround
- Emergency updates: 2 hour turnaround

## 7. Integration Points with Ante Development

### 7.1 Release Synchronization
- Documentation updates must align with Ante releases
- Breaking changes in Ante require immediate documentation updates
- Release notes should reference documentation changes
- Documentation version increments with Ante version

### 7.2 Change Request Notification
- Ante maintainers notify Documentation Owner of breaking changes
- 2-week lead time for major version updates
- 1-week lead time for minor version updates
- Same-day notification for critical fixes

### 7.3 Documentation as Code
- Documentation changes follow same review process as code
- Documentation changes can be included in release PRs
- Testing/validation of examples is part of CI process
- Documentation builds are part of release validation

## 8. Documentation Organization

### 8.1 Directory Structure
```
docs/context/
├── governance/          # This governance framework
├── llm-context/        # LLM-optimized documentation
├── wiki/               # User-facing wiki documentation
├── archive/            # Deprecated documentation versions
└── llms.txt           # LLM system context file
```

### 8.2 Content Ownership Map

| Area | Owner | Backup |
|------|-------|--------|
| CLI Documentation | [Content Maintainer] | [Documentation Owner] |
| API Reference | [Content Maintainer] | [Documentation Owner] |
| Integration Guides | [Content Maintainer] | [LLM Specialist] |
| LLM Context | [LLM Specialist] | [Documentation Owner] |
| Standards & Governance | [Documentation Owner] | [Governance Council] |

## 9. Escalation and Conflict Resolution

### 9.1 Escalation Path
1. **Content Disagreement**: Discussion between maintainers and submitter
2. **Standards Question**: Documentation Owner makes determination
3. **Policy Dispute**: Governance Council votes (3/4 majority required)
4. **Critical Issues**: Emergency council session within 24 hours

### 9.2 Dispute Resolution Process
- Document disagreement in change request comments
- All parties present their rationale
- Documentation Owner or Council makes final determination
- Decision is documented for future reference
- Losing party can request reconsideration after 30 days with new evidence

## 10. Metrics and Reporting

### 10.1 Tracked Metrics
- Documentation coverage percentage
- Average review time by change type
- Number of errors found in production documentation
- LLM accuracy on documented features
- Documentation debt aging

### 10.2 Reporting Frequency
- Weekly: Change volume and review times
- Monthly: Quality metrics and outstanding debt
- Quarterly: Coverage analysis and strategic updates

### 10.3 Governance Review Schedule
- Monthly: Routine metrics review (1st Tuesday)
- Quarterly: Strategy and standards review (1st Thursday)
- Annually: Complete governance framework review

## 11. Compliance and Auditing

### 11.1 Audit Requirements
- All changes must have documented justification
- Review decisions must be recorded
- Version compatibility must be verifiable
- Accuracy claims must be testable

### 11.2 Compliance Verification
- Monthly automated checks of documentation links
- Quarterly manual accuracy validation against Ante behavior
- Bi-annual standards compliance audit
- Annual external documentation review

## 12. Document Amendment Process

This governance framework may be amended through:
1. Proposal submission with justification
2. 2-week comment period for all stakeholders
3. Governance Council discussion and vote
4. 2/3 majority required for approval
5. 30-day grace period before implementation
6. Communication of changes to all stakeholders


---

## Source: MAINTENANCE.md

# Ante LLM Context Documentation Maintenance Procedures

## 1. Synchronization with Ante Releases

### 1.1 Pre-Release Synchronization (2 weeks before release)

**Notification and Planning**
1. Documentation Owner receives release notification from Ante team
2. Review release notes and changelog for documentation impact
3. Assess scope of documentation changes needed
4. Create documentation update plan
5. Assign documentation tasks

**Review Process**
```
Release announced
    ↓
Review scope of changes
    ↓
Create update plan
    ↓
Assign tasks to team
    ↓
Begin documentation updates
```

**Documentation impact assessment template:**
```markdown
# Release: v[X.Y.Z] Documentation Impact

## New Features
- [Feature]: Requires new documentation in [section]
- [Feature]: Requires new documentation in [section]

## Changed Features
- [Feature]: Documentation update required
- [Feature]: Documentation update required

## Removed Features
- [Feature]: Archive documentation
- [Feature]: Create migration guide

## Breaking Changes
- [Change]: Major documentation updates needed
- [Change]: Migration guide required

## Estimated Effort
- New documentation: [X hours]
- Updates: [X hours]
- Migration guides: [X hours]
- Testing/QA: [X hours]
- Total: [X hours]

## Timeline
- Documentation ready by: [Date]
- Review deadline: [Date]
- Merge deadline: [Date]
```

### 1.2 Development Phase (1 week before release)

**Documentation Updates**
1. Create new documentation sections for new features
2. Update existing sections for changed features
3. Prepare deprecation notices for removed features
4. Write migration guides for breaking changes
5. Update examples to use new syntax

**Testing and Validation**
1. Test all code examples against pre-release version
2. Verify command examples produce expected output
3. Validate API documentation against actual behavior
4. Check all cross-references and links
5. Run automated quality checks

**Review and Approval**
1. Submit documentation for technical review
2. Address reviewer feedback
3. QA testing of examples
4. LLM accessibility review
5. Final approval from Documentation Owner

### 1.3 Release Phase (On release day)

**Merge and Publish**
1. Merge all approved documentation changes
2. Merge documentation to main branch
3. Update llms.txt file with new documentation
4. Update version metadata
5. Update CHANGELOG.md with release notes
6. Tag documentation version matching Ante version

**Communication**
1. Send documentation update notification
2. Link to new features documentation
3. Link to migration guides if needed
4. Provide changelog summary
5. Answer initial questions

**Verification**
1. Verify all links are working
2. Spot-check examples in published documentation
3. Confirm LLM context is updated
4. Monitor for immediate issues

### 1.4 Post-Release Phase (1 week after release)

**Monitoring and Adjustment**
1. Monitor user questions and feedback
2. Address clarification requests
3. Fix any incorrect documentation
4. Update examples based on user experience
5. Document any edge cases discovered

**Debt Resolution**
1. Address any incomplete documentation
2. Fix any inaccuracies found
3. Improve examples based on feedback
4. Update FAQ with common questions
5. Close documentation tasks

**Metrics and Analysis**
1. Analyze documentation accuracy
2. Review user feedback and questions
3. Identify areas needing improvement
4. Update documentation plans for next release
5. Report metrics to governance council

### 1.5 Release Synchronization Checklist

**Pre-Release (2 weeks before)**
- [ ] Release notification received
- [ ] Documentation impact assessed
- [ ] Update plan created
- [ ] Tasks assigned
- [ ] Team alignment meeting held

**Development (1 week before)**
- [ ] New documentation created
- [ ] Existing docs updated
- [ ] Migration guides written
- [ ] Examples tested
- [ ] All changes reviewed and approved

**Release Day**
- [ ] All changes merged
- [ ] Version numbers updated
- [ ] llms.txt updated
- [ ] Notification sent
- [ ] Links verified

**Post-Release (1 week after)**
- [ ] User feedback reviewed
- [ ] Issues fixed
- [ ] Metrics reported
- [ ] Next steps planned

## 2. Updating the llms.txt Context File

### 2.1 When to Update llms.txt

Update llms.txt when:
- New major features are released
- Core functionality changes
- Command syntax or options change
- Examples become outdated
- Documentation structure changes significantly
- Monthly routine update (minimum)

### 2.2 llms.txt Structure

```
# Ante LLM Context
## Version: [X.Y.Z]
## Last Updated: [Date]
## Ante Compatibility: [X.Y.Z]

## Overview
[Brief description of Ante and purpose]

## Core Commands
[Commands and basic usage]

## Common Options
[Most frequently used options]

## Workflows
[Common user workflows]

## Examples
[Practical examples]

## Limitations
[Known limitations]

## See Also
[Links to detailed documentation]
```

### 2.3 Content Selection Process

**Priority 1: Core Commands (100% coverage)**
- Essential Ante commands
- Basic usage patterns
- Most common options
- Key parameters

**Priority 2: Common Workflows (80% coverage)**
- Typical user workflows
- Best practices
- Common patterns
- Practical examples

**Priority 3: Advanced Features (50% coverage)**
- Less common commands
- Advanced options
- Power user features
- Integration points

**Priority 4: Edge Cases (reference only)**
- Unusual scenarios
- Rare options
- Links to detailed docs
- Support information

**Priority 5: Troubleshooting (25% coverage)**
- Common issues
- Solutions
- Where to find help
- Error messages

### 2.4 LLM Context Optimization

**Formatting for LLM comprehension:**
1. Use clear section headers
2. Keep explanations concise and technical
3. Provide concrete examples
4. Use consistent terminology
5. Link to detailed documentation
6. Include version-specific information
7. Note limitations and edge cases

**Example optimization:**

**Before (verbose):**
```
The Ante CLI tool provides many options for customizing its behavior. 
One important option is the context size flag, which allows users to 
specify how much context the system should maintain. This is useful when 
working with large documents or when memory is a concern.
```

**After (LLM-optimized):**
```
Context size option:
--context-size [bytes]
- Controls memory usage for context maintenance
- Default: 32KB
- Used when memory is constrained
- See: docs/reference/options#context-size
```

### 2.5 llms.txt Update Process

1. **Content Extraction**
   - Identify documentation to include
   - Extract relevant sections
   - Restructure for brevity
   - Optimize for LLM parsing

2. **Consolidation**
   - Combine related sections
   - Remove redundancy
   - Maintain clear organization
   - Add cross-references

3. **Testing**
   - Test with sample LLM queries
   - Verify accurate responses
   - Check edge case handling
   - Validate completeness

4. **Validation**
   - Accuracy check against Ante source
   - Link validity check
   - Version compatibility check
   - Completeness verification

5. **Publication**
   - Update version and date
   - Merge to main documentation
   - Notify LLM systems of update
   - Document changes in changelog

### 2.6 llms.txt Update Template

```markdown
# llms.txt Update Request

## Scope
[What sections of llms.txt need updating]

## Changes Required
[Specific changes and additions]

## Content Source
[Links to documentation sources]

## Validation Plan
[How we'll test the updated context]

## Target Completion
[When this should be complete]

## Approval
[Who needs to review]
```

## 3. Refreshing Wiki Documentation

### 3.1 Wiki Content Scope

The wiki documentation serves as:
- User-facing reference documentation
- How-to guides and tutorials
- Troubleshooting and FAQ
- Community contributions
- Examples and best practices

### 3.2 Wiki Refresh Schedule

**Monthly Refresh (minimum)**
- Review most-visited pages
- Check for outdated information
- Update examples
- Fix broken links
- Improve clarity based on feedback

**Quarterly Comprehensive Review**
- Audit all wiki pages
- Check version compatibility
- Validate all examples
- Review user feedback
- Plan major updates

**Annual Reorganization**
- Assess overall structure
- Identify missing topics
- Consolidate redundant content
- Plan next year's improvements

### 3.3 Wiki Update Workflows

**Routine Updates (Type A)**
```
Issue identified
    ↓
Fix applied locally
    ↓
Self-review
    ↓
Direct commit/merge
```

**Content Updates (Type B)**
```
Update planned
    ↓
Content updated/created
    ↓
Submit for review
    ↓
Revise per feedback
    ↓
Merge after approval
```

**Structural Changes (Type C)**
```
Proposal submitted
    ↓
Council discussion
    ↓
Vote on changes
    ↓
Implementation if approved
```

### 3.4 Wiki Quality Checks

Regular quality checks should include:

**Content Quality**
- [ ] Information is accurate and current
- [ ] Examples work with current version
- [ ] No broken links
- [ ] Proper grammar and spelling
- [ ] Clear, understandable writing

**Technical Accuracy**
- [ ] Commands are correct
- [ ] Outputs are accurate
- [ ] Options are current
- [ ] Syntax is correct
- [ ] Edge cases are noted

**Maintenance**
- [ ] Last updated date is recent
- [ ] Version compatibility is clear
- [ ] No TBD or incomplete sections
- [ ] Metadata is current

**User Experience**
- [ ] Navigation is clear
- [ ] Search terms are appropriate
- [ ] Related links are helpful
- [ ] Examples are practical
- [ ] Next steps are suggested

### 3.5 Wiki Maintenance Checklist

Monthly:
- [ ] Review top 10 most-viewed pages
- [ ] Check for outdated examples
- [ ] Validate links (automated)
- [ ] Address user feedback
- [ ] Update version information

Quarterly:
- [ ] Full wiki audit
- [ ] User satisfaction survey
- [ ] Traffic analysis
- [ ] Performance assessment
- [ ] Update planning

Annually:
- [ ] Complete content review
- [ ] Structure reorganization
- [ ] Outdated content archival
- [ ] New content planning

## 4. Validating Documentation Accuracy

### 4.1 Validation Approach

Validation uses multiple methods:

**Automated Validation**
- Link checking
- Syntax validation
- Code example extraction and testing
- Metadata verification

**Manual Validation**
- Technical accuracy review
- Example testing
- Behavior verification
- Edge case checking

**User Validation**
- Feedback collection
- Usage monitoring
- Question analysis
- Error reporting

### 4.2 Automated Validation Tools

**Link Validation**
```bash
# Check all documentation links
link-checker docs/

# Validate reference format
grep -r "\[.*\](.*)" docs/ | validate-refs
```

**Markdown Validation**
```bash
# Check markdown syntax
find docs -name "*.md" -exec markdownlint {} \;

# Check frontmatter
find docs -name "*.md" -exec validate-frontmatter {} \;
```

**Code Example Validation**
```bash
# Extract and test code examples
extract-code-blocks docs/ > code-samples.txt
test-code-samples code-samples.txt
```

### 4.3 Manual Validation Procedure

**For each documented feature:**

1. **Setup**
   - Get latest Ante version
   - Set up clean test environment
   - Prepare test data if needed

2. **Testing**
   - Execute documented commands
   - Verify output matches documentation
   - Test all documented options
   - Test error conditions
   - Test edge cases

3. **Validation**
   - Compare actual behavior to documentation
   - Note any discrepancies
   - Check example completeness
   - Verify error messages
   - Test version compatibility

4. **Documentation**
   - Create validation report
   - Document findings
   - File issues for corrections
   - Track validation date

5. **Correction**
   - Fix identified inaccuracies
   - Update examples
   - Note any limitations found
   - Re-validate after fixes

### 4.4 Validation Report Template

```markdown
# Documentation Validation Report

## Document
[Document name and version]

## Validation Date
[Date performed]

## Features Tested
- [ ] Feature 1: [Status - Pass/Fail/Partial]
- [ ] Feature 2: [Status - Pass/Fail/Partial]
- [ ] Feature 3: [Status - Pass/Fail/Partial]

## Test Environment
- Ante version: [X.Y.Z]
- OS: [OS and version]
- Test date: [Date]

## Issues Found

### Critical Issues
[Issues that must be fixed before release]

### High Priority Issues
[Issues that should be fixed soon]

### Low Priority Issues
[Minor improvements]

## Evidence
[Links to test results, examples, errors]

## Recommendations
[Suggested corrections and improvements]

## Sign-Off
- Validated by: [Name]
- Date: [Date]
- Status: [Validated/Needs Revision/Blocked]
```

### 4.5 Validation Schedule

**Monthly Validation** (1st Thursday)
- Core commands documentation
- Most-used features
- Recent updates
- Critical documentation

**Quarterly Validation** (Every 3 months)
- Complete feature set
- All documented options
- Edge cases and limitations
- Examples and tutorials

**Bi-Annual Validation** (Every 6 months)
- Full documentation audit
- All sections
- Version compatibility check
- Completeness assessment

## 5. Handling Documentation Debt

### 5.1 Documentation Debt Definition

Documentation debt includes:
- Outdated information not yet fixed
- Incomplete sections needing finishing
- Examples that don't work with current version
- Broken links and references
- Missing documentation for features
- Inconsistent formatting or structure
- Technical inaccuracies
- Performance or usability issues

### 5.2 Debt Tracking System

Use issue tracking to manage debt:

**Issue Template:**
```markdown
# Documentation Issue: [Type] [Summary]

## Type
- [ ] Outdated content
- [ ] Incomplete section
- [ ] Broken example
- [ ] Missing documentation
- [ ] Inaccuracy
- [ ] Format/structure issue

## Severity
- [ ] Critical (blocks users)
- [ ] High (significant impact)
- [ ] Medium (affects usability)
- [ ] Low (minor issue)

## Description
[Detailed description of the issue]

## Location
[Document path and section]

## Related Issues
[Links to related issues]

## Solution
[Proposed fix]

## Estimated Effort
[Small/Medium/Large]

## Created
[Date]

## Priority
[1-5, with 1 being highest]
```

### 5.3 Debt Reduction Process

**Assessment Phase**
1. Identify all documentation debt
2. Categorize by type and severity
3. Estimate effort for each item
4. Track in centralized system
5. Prioritize by impact and effort

**Planning Phase**
1. Create debt reduction roadmap
2. Allocate resources
3. Set timelines
4. Include in regular maintenance
5. Track progress

**Reduction Phase**
1. Address highest-impact items first
2. Follow normal documentation processes
3. Regular progress updates
4. Monthly debt review
5. Archive resolved issues

**Prevention Phase**
1. Review sources of new debt
2. Improve processes to prevent debt
3. Increase documentation quality gates
4. Better maintenance scheduling
5. Team training on standards

### 5.4 Debt Metrics

Track:
- Total debt items
- Debt by severity
- Average age of items
- Reduction rate
- New debt rate
- Time to resolution

**Target metrics:**
- Critical issues: Resolution within 1 week
- High issues: Resolution within 2 weeks
- Medium issues: Resolution within 1 month
- Low issues: Resolution within 1 quarter
- Zero new debt from releases

### 5.5 Debt Review Meeting (Monthly)

**Agenda:**
1. New debt identified this month
2. Debt resolved this month
3. Progress on roadmap
4. High-priority items for next month
5. Resource allocation adjustments
6. Discussion of debt prevention

**Output:**
- Updated debt list
- Prioritized work for next month
- Resource assignments
- Metrics report

## 6. Deprecation Procedures

### 6.1 Deprecation Lifecycle

**Phase 1: Announcement** (Release N)
- Feature deprecation announced
- Documentation marked as deprecated
- Migration path documented
- Timeline for removal provided

**Phase 2: Maintenance** (Release N+1)
- Deprecated feature still documented
- Clear warnings and migration guides
- Links to alternatives prominent
- Timeline updated

**Phase 3: Removal** (Release N+2)
- Feature removed from Ante
- Documentation moved to archive
- Migration guide remains accessible
- Cross-references updated

### 6.2 Deprecation Documentation

**Mark deprecated content:**
```markdown
> ⚠️ **Deprecated in v0.3.0**
> 
> This feature is deprecated and will be removed in v0.5.0.
> Use [Alternative Feature](link) instead.
> See [Migration Guide](link) for migration steps.
```

**Create migration guide:**
```markdown
# Migration Guide: Deprecated Feature

## Overview
[Why feature was deprecated]

## Timeline
- Deprecated in: v0.3.0
- Final support: v0.4.x
- Removed in: v0.5.0

## Alternative
[Recommended replacement]

## Migration Steps
1. [Step 1]
2. [Step 2]
3. [Verification]

## Questions?
[Support information]
```

### 6.3 Deprecation Communication

**Timeline:**
- At announcement: Email to users
- 1 month in: Reminder email
- 2 months in: Warning in documentation
- At removal: Final notice in release notes

**Channels:**
- Release notes
- Email notification
- Documentation warnings
- Support documentation
- FAQ section

### 6.4 Deprecation Checklist

**Announcement:**
- [ ] Feature removal scheduled
- [ ] Migration guide written
- [ ] Documentation updated
- [ ] Alternative documented
- [ ] Release notes prepared
- [ ] User notification sent

**Maintenance Period:**
- [ ] Migration guide is accessible
- [ ] Links to alternatives visible
- [ ] Support for migration questions
- [ ] Metrics on migration progress

**Removal:**
- [ ] Documentation archived
- [ ] Cross-references updated
- [ ] Links to archive maintained
- [ ] Final user notification sent
- [ ] Support period ended

## 7. Documentation Debt Reduction Roadmap

### 7.1 Current Debt Status

[To be filled in with actual assessment]

```markdown
# Documentation Debt Inventory

## Critical Issues (Must fix before release)
- Issue 1: [Description] - [Created: Date] - [Owner: Name]
- Issue 2: [Description] - [Created: Date] - [Owner: Name]

## High Priority (Fix within 2 weeks)
- Issue 1: [Description] - [Created: Date] - [Owner: Name]
- Issue 2: [Description] - [Created: Date] - [Owner: Name]

## Medium Priority (Fix within 1 month)
- Issue 1: [Description] - [Created: Date] - [Owner: Name]

## Low Priority (Fix within 1 quarter)
- Issue 1: [Description] - [Created: Date] - [Owner: Name]

## Summary
- Total items: [Number]
- By severity: Critical [X], High [X], Medium [X], Low [X]
- Estimated effort: [X hours]
- Average age: [X days]
```

### 7.2 Reduction Timeline

**Month 1:** Address all critical items
**Month 2:** Resolve high-priority items
**Month 3:** Complete medium-priority items
**Ongoing:** Prevent new debt through process improvements

## 8. Maintenance Automation

### 8.1 Scheduled Checks

Implement automated checks for:

**Daily**
- Link validation
- Syntax errors
- Build checks

**Weekly**
- Example code testing
- Version consistency checks
- Metadata validation

**Monthly**
- Full quality checks
- Coverage analysis
- Performance metrics

### 8.2 Maintenance Scripts

```bash
#!/bin/bash
# daily-checks.sh
# Run automated documentation checks

check_links() {
  echo "Checking links..."
  link-checker docs/
}

check_syntax() {
  echo "Checking syntax..."
  find docs -name "*.md" -exec markdownlint {} \;
}

check_examples() {
  echo "Validating code examples..."
  extract-code-blocks docs/ | test-code-samples
}

main() {
  check_links
  check_syntax
  check_examples
  echo "Daily checks complete"
}

main "$@"
```

## 9. Documentation Health Dashboard

Track and monitor:
- Documentation coverage (%)
- Error rate (%)
- Average age of updates (days)
- Debt items by severity
- Mean time to resolution
- User satisfaction score
- LLM accuracy on documentation

Update dashboard monthly for stakeholder visibility.


---

## Source: PROCESSES.md

# Ante LLM Context Documentation Operational Processes

## 1. Adding New Documentation

### 1.1 Process Overview

Adding new documentation follows this workflow:

```
Request/Identify Gap
    ↓
Create Outline
    ↓
Write Draft
    ↓
Submit for Review
    ↓
Revise Based on Feedback
    ↓
Final Approval
    ↓
Merge to Main Documentation
```

### 1.2 Step-by-Step Process

#### Step 1: Identify Documentation Need
- Document the gap or missing information
- Provide rationale for why documentation is needed
- Identify impact (number of users, frequency of questions)
- Suggest placement in documentation hierarchy

Example:
```
Need: Documentation for the --context-size flag in the new v0.2.0 release
Impact: Critical for users trying to optimize memory usage
Related documentation: CLI flags section, configuration guide
Suggested placement: CLI Reference > Options > Context and Memory
```

#### Step 2: Request Approval (Type B Feature)
- Submit documentation request to Content Owner
- Include scope, audience, and outline
- Estimate content volume
- Note any dependencies on other documentation
- Target approval time: 3 business days

#### Step 3: Research and Plan
- Review related Ante source code or features
- Test features being documented
- Identify edge cases and limitations
- Gather examples for demonstration
- Create detailed outline

Outline template:
```markdown
# New Feature/Area Title

## Overview
- What is this feature
- When would users use it
- Key benefits

## Core Concepts
- Important terms and definitions
- Relationships to other features

## Configuration/Usage
- How to use the feature
- Common patterns
- Examples

## Advanced Usage
- Less common scenarios
- Performance considerations

## Limitations
- Known limitations
- Related features

## Troubleshooting
- Common issues and solutions

## See Also
- Related documentation
- Related features
```

#### Step 4: Write Initial Draft
- Follow documentation standards (see STANDARDS.md)
- Use clear, technical language
- Include practical examples
- Add code blocks with language specification
- Include all necessary context for LLM understanding

Content checklist:
- [ ] All features mentioned are covered
- [ ] Examples are complete and runnable
- [ ] Edge cases are documented
- [ ] Limitations are clearly noted
- [ ] Related features are cross-referenced
- [ ] Metadata is complete
- [ ] Formatting follows standards

#### Step 5: Internal Review
- Assign to Content Maintainer for technical accuracy
- Assign to QA Lead for completeness check
- Assign to LLM Specialist for accessibility review
- Expected turnaround: 3-5 business days

Review comments should include:
- Technical accuracy issues
- Missing sections or edge cases
- Clarity improvements
- Standard compliance issues

#### Step 6: Revise
- Address all review comments
- Track changes in commit messages
- Re-submit for approval if significant changes made
- Minor revisions can proceed to merge

#### Step 7: Final Approval
- Content Owner verifies all issues resolved
- Confirms documentation is ready for merge
- Approves version number assignment
- Schedules merge with release if applicable

#### Step 8: Merge and Update Index
- Merge documentation to main branch
- Update documentation index/navigation
- Update llms.txt context file
- Publish change notification
- Update version history

### 1.3 Documentation Request Template

```markdown
# Documentation Request: [Feature/Area Name]

## Summary
[One-sentence description of what needs to be documented]

## Scope
- Features covered: [List]
- Audience: [Intended readers]
- Related documentation: [Existing docs it connects to]

## Rationale
[Why this documentation is needed]
- Number of affected users: [Estimate]
- Frequency of questions: [High/Medium/Low]
- Impact if not documented: [Explanation]

## Outline
[High-level sections/topics to cover]

## Suggested Placement
[Where in documentation hierarchy]

## Dependencies
[Other documentation or features this depends on]

## Estimated Effort
- Content volume: [Small/Medium/Large]
- Estimated hours: [Estimate]
- Timeline: [Proposed dates]

## Success Criteria
[How we'll know this documentation is complete and successful]
```

## 2. Updating Existing Documentation

### 2.1 Update Types

#### Type A: Routine Updates (No approval needed)
- Fixing typos or grammar
- Clarifying existing content
- Adding examples to existing sections
- Updating links or references
- Minor formatting improvements

Process:
1. Make changes locally
2. Self-review against standards
3. Commit with clear message
4. Direct merge or quick PR if following git workflow

#### Type B: Significant Updates (Content Owner approval)
- Adding new sections to existing documents
- Rewriting major sections
- Reorganizing document structure
- Updating feature descriptions for new releases
- Significant restructuring of information

Process:
1. Review governance classification with Documentation Owner
2. Create draft in branch
3. Submit for review (3 business days)
4. Revise based on feedback
5. Merge after approval

#### Type C: Policy/Structure Changes (Council approval)
- Changing documentation standards
- Reorganizing major document structure
- Deprecating large sections
- Major version updates

Process:
1. Submit proposal to Governance Council
2. 2-week discussion period
3. Council votes (2/3 majority)
4. If approved, implement following Type B process

### 2.2 Update Process for Feature Changes

When Ante releases a new feature or changes existing functionality:

1. **Notification Phase** (On announcement)
   - Documentation Owner receives notification
   - Assess documentation impact
   - Identify affected documents

2. **Planning Phase** (Within 3 days)
   - Create update plan
   - Allocate resources
   - Schedule completion

3. **Development Phase** (Before release)
   - Update documentation for changed features
   - Add documentation for new features
   - Test all examples
   - Get review approval

4. **Release Phase** (On release)
   - Merge documentation changes
   - Update version numbers
   - Update llms.txt file
   - Publish change summary

5. **Verification Phase** (Post-release)
   - Validate examples against new version
   - Monitor for questions about changes
   - Adjust documentation based on user feedback

### 2.3 Update Documentation Checklist

Before updating documentation:

- [ ] Understand the change in detail
- [ ] Test the change against actual system
- [ ] Review all affected documentation sections
- [ ] Check for contradictions in related docs
- [ ] Update examples with new syntax/behavior
- [ ] Update version compatibility information
- [ ] Add changelog entry
- [ ] Get necessary approvals
- [ ] Test all cross-references
- [ ] Verify formatting consistency

### 2.4 Update Request Template

```markdown
# Documentation Update Request

## What's Changing
[Description of the change in Ante]

## Documentation Impact
- Documents affected: [List]
- Type of update: [Routine/Significant/Policy]
- Complexity: [Simple/Moderate/Complex]

## Changes Required
[Specific updates needed in each affected document]

## Timeline
- Change available: [Date]
- Documentation ready by: [Date]
- Release planned: [Date]

## Approval Requirements
[Type A/B/C and required approvers]

## Related Issues/PRs
[Links to Ante changes being documented]
```

## 3. Archiving Outdated Content

### 3.1 When to Archive

Content should be archived when:
- Feature is removed in latest version
- Feature is deprecated (and deprecation period ended)
- Information is superseded by newer content
- Section becomes irrelevant to current users
- Information was incorrect and cannot be salvaged

### 3.2 Archival Process

1. **Mark as Deprecated** (1 release before removal)
   ```markdown
   > ⚠️ **Deprecated**: This feature was removed in v0.3.0
   > See [Migration Guide](link) for alternatives.
   ```

2. **Move to Archive** (Release where feature removed)
   - Move document to `archive/[version]/` directory
   - Keep full metadata and history
   - Add deprecation notice at top
   - Update cross-references in current docs

3. **Update Navigation**
   - Remove from current documentation index
   - Add link in "Archived Documentation" section
   - Maintain backward compatibility links

4. **Archive Directory Structure**
   ```
   archive/
   ├── v0.1.0/
   │   ├── deprecated-feature.md
   │   └── old-workflow.md
   ├── v0.2.0/
   │   └── replaced-feature.md
   └── README.md (index of archived docs)
   ```

### 3.3 Archive Retention Policy

- Keep archived documentation indefinitely
- Maintain version compatibility information
- Keep archive searchable and accessible
- Document why content was archived
- Provide migration paths where applicable

### 3.4 Archive Request Template

```markdown
# Archive Request

## Content to Archive
[Document/section name]

## Reason for Archival
[Why this content is being archived]

## Availability of Alternatives
[New documentation or resources available]

## Backward Compatibility
[How existing links will be handled]

## Archive Location
[Proposed path in archive/]

## Approval Status
[Type A/B/C approval needed]
```

## 4. Quality Assurance Procedures

### 4.1 QA Review Checklist

**Accuracy**
- [ ] Feature behavior matches current Ante version
- [ ] Code examples run without errors
- [ ] Command examples produce expected output
- [ ] No deprecated features without notices
- [ ] API signatures are current
- [ ] Version compatibility information is correct

**Completeness**
- [ ] All documented features are covered
- [ ] All options and parameters are listed
- [ ] Examples cover common use cases
- [ ] Edge cases are mentioned
- [ ] Limitations are documented
- [ ] Related features are cross-referenced
- [ ] Error conditions are mentioned

**Consistency**
- [ ] Terminology is consistent across docs
- [ ] Formatting follows standards
- [ ] Code style is consistent
- [ ] Link format is consistent
- [ ] Examples follow same pattern
- [ ] Metadata is present and accurate

**Clarity**
- [ ] Technical language is precise
- [ ] Explanations are clear
- [ ] Examples are self-explanatory
- [ ] Assumptions are stated
- [ ] Prerequisites are listed
- [ ] Next steps are suggested

**Structure**
- [ ] Headings follow hierarchy
- [ ] Logical flow of information
- [ ] Proper use of lists and formatting
- [ ] Appropriate section length
- [ ] Good use of white space
- [ ] Tables/diagrams are clear

### 4.2 Automated QA Checks

Implement automated validation:

```bash
# Link validation
find docs/ -name "*.md" -exec check-links {} \;

# Markdown syntax
find docs/ -name "*.md" -exec markdownlint {} \;

# Spellcheck
find docs/ -name "*.md" -exec aspell check {} \;

# Code block language specification
grep -r "^```$" docs/ --color=never

# Version string consistency
grep -r "v0\.[0-9]\.[0-9]" docs/ --color=never
```

### 4.3 Manual Testing Procedure

For documentation with code examples:

1. **Extract Example Code**
   - Copy code from documentation
   - Save to test file

2. **Execute Against Current Version**
   - Run against latest Ante version
   - Capture actual output
   - Note any errors or warnings

3. **Compare to Documentation**
   - Verify output matches documented behavior
   - Check error messages match
   - Confirm all flags work as documented

4. **Document Results**
   - Record test date and version
   - Note any discrepancies
   - File issues for needed corrections

### 4.4 Quality Gates

Documentation cannot be merged if:
- Contains broken links (critical)
- Contains code examples that don't run (critical)
- Missing required metadata (high)
- Contradicts current Ante behavior (critical)
- Fails basic formatting checks (medium)
- Incomplete sections (medium)

## 5. Integration with Ante Updates

### 5.1 Release Documentation Lifecycle

**Pre-Release (2 weeks before)**
- [ ] Review release notes
- [ ] Identify documentation impacts
- [ ] Create documentation plan
- [ ] Assign documentation tasks

**Preparation (1 week before)**
- [ ] Begin documentation updates
- [ ] Test examples against pre-release
- [ ] Get early reviews
- [ ] Identify missing documentation

**Documentation Ready (3-5 days before)**
- [ ] All updates complete
- [ ] All reviews approved
- [ ] Examples tested and working
- [ ] Version numbers updated
- [ ] Ready for merge on release day

**Release Day**
- [ ] Merge documentation PRs
- [ ] Update llms.txt
- [ ] Update version history
- [ ] Publish change summary

**Post-Release (1 week after)**
- [ ] Monitor for clarification questions
- [ ] Fix any documentation issues
- [ ] Update examples based on user feedback
- [ ] Close documentation tasks

### 5.2 Breaking Change Documentation

When Ante introduces breaking changes:

1. **Create Migration Guide**
   ```markdown
   # Migration Guide: v0.X.0
   
   ## Breaking Changes
   - [Removed feature]: Use [alternative] instead
   - [Changed syntax]: Old `foo` → New `bar`
   - [Renamed command]: `old-cmd` → `new-cmd`
   
   ## Migration Steps
   1. [Step by step]
   2. [Check results]
   3. [Update scripts]
   ```

2. **Update Related Documentation**
   - Add migration notes to affected sections
   - Link to migration guide prominently
   - Update all examples with new syntax

3. **Archive Old Documentation**
   - Move old docs to archive
   - Add deprecation notices
   - Link to migration guide

### 5.3 Documentation Change Log

Maintain a CHANGELOG.md:

```markdown
# Documentation Changelog

## [1.0.0] - 2026-02-20

### Added
- New section on [feature]
- Integration guide for [tool]

### Changed
- Restructured [section]
- Updated [feature] documentation for v0.2.0

### Fixed
- Fixed broken links in [section]
- Corrected example in [page]

### Deprecated
- Removed documentation for [old feature]
- See migration guide for details
```

## 6. Documentation Maintenance Schedule

### 6.1 Weekly Tasks (Every Monday)
- Review change requests
- Process routine updates
- Update metrics dashboard
- Address urgent feedback

### 6.2 Bi-Weekly Tasks (Every 2 weeks)
- Conduct team sync meeting
- Review in-progress changes
- Check link validity
- Update documentation index

### 6.3 Monthly Tasks (1st Tuesday)
- Review all updated documentation
- Run full quality checks
- Report metrics to stakeholders
- Address documentation debt
- Governance council meeting

### 6.4 Quarterly Tasks (Every 3 months)
- Comprehensive accuracy validation
- Coverage analysis update
- Deprecation review
- Strategic documentation planning

### 6.5 Annually Tasks (Fiscal year start)
- Complete documentation audit
- Review governance framework
- Plan major documentation improvements
- Update roles and responsibilities

### 6.6 Maintenance Calendar Template

```
Week of [Date]:
- [ ] Monitor Ante development
- [ ] Review change requests
- [ ] Address urgent issues
- [ ] Update metrics

Month of [Date]:
- [ ] Full QA review
- [ ] Governance council meeting
- [ ] Stakeholder reporting
- [ ] Debt review

Quarter of [Date]:
- [ ] Accuracy validation
- [ ] Coverage analysis
- [ ] Strategic planning
- [ ] Team assessment
```

## 7. Review Checklist for New Content

### Pre-Submission Checklist

Before submitting for review, author must verify:

**Content Quality**
- [ ] All information is accurate and current
- [ ] Content is complete for the scope
- [ ] No contradictions with other documentation
- [ ] Examples are tested and working
- [ ] Edge cases and limitations are noted

**Format and Standards**
- [ ] Follows documentation standards (STANDARDS.md)
- [ ] Markdown syntax is correct
- [ ] Code blocks have language specified
- [ ] All links are relative and valid
- [ ] Images are optimized and referenced
- [ ] Metadata is complete

**Structure**
- [ ] Clear heading hierarchy
- [ ] Logical flow of information
- [ ] Appropriate section length
- [ ] Good use of lists and formatting
- [ ] TOC entries if applicable

**Accessibility**
- [ ] Content is understandable to target audience
- [ ] Technical terms are defined
- [ ] Assumptions are stated
- [ ] Prerequisites are listed
- [ ] LLM-friendly formatting used

**Cross-References**
- [ ] Links to related documentation are correct
- [ ] No orphaned sections
- [ ] Navigation aids are present
- [ ] "See Also" sections are complete

### Reviewer Checklist

Reviewers must verify all pre-submission items plus:

**Technical Accuracy**
- [ ] Behavior matches current Ante version
- [ ] Code examples produce expected output
- [ ] API signatures are current
- [ ] No deprecated patterns without notes

**Completeness**
- [ ] All required sections are present
- [ ] No TBD or incomplete markers
- [ ] Examples cover common scenarios
- [ ] Error conditions are handled

**Consistency**
- [ ] Terminology matches other docs
- [ ] Format matches similar sections
- [ ] Metadata is consistent
- [ ] Version information is correct

**Impact Assessment**
- [ ] Related documentation reviewed
- [ ] Cross-references updated
- [ ] Navigation structure updated
- [ ] llms.txt needs updating

### Sign-Off Template

```markdown
## Review Sign-Off

- [ ] **Technical Accuracy**: [Reviewer name] - [Date]
- [ ] **QA & Completeness**: [Reviewer name] - [Date]
- [ ] **LLM Accessibility**: [Reviewer name] - [Date]
- [ ] **Final Approval**: [Owner name] - [Date]

### Notes
[Any special conditions or contingencies]
```

## 8. Integration with llms.txt

The llms.txt file serves as the primary LLM context source. Updates to documentation must be reflected in llms.txt:

### 8.1 Update Process

1. **When to Update**
   - New major feature documentation
   - Significant restructuring of content
   - Breaking changes
   - Monthly sync (minimum)

2. **How to Update**
   - Extract key information from documentation
   - Restructure for LLM comprehension
   - Add examples and common patterns
   - Remove redundant or verbose sections
   - Test LLM understanding

3. **Testing Updated Context**
   - Run sample questions to LLMs
   - Verify accurate responses
   - Check edge case handling
   - Validate command completeness

### 8.2 Content Priorities for llms.txt

1. **Core commands and options** (100% coverage)
2. **Common workflows** (80% coverage)
3. **Advanced features** (50% coverage)
4. **Edge cases** (reference to detailed docs)
5. **Troubleshooting tips** (25% coverage)

## 9. Communication and Notifications

### 9.1 Change Notifications

Notify stakeholders of:
- New major documentation sections
- Breaking changes and migrations
- Deprecations of major features
- Documentation policy changes

**Notification channels:**
- Documentation announcement email
- Release notes
- Internal wiki/intranet
- Slack/chat channel

### 9.2 Notification Templates

```markdown
# Documentation Update: [Title]

## Summary
[What changed and why]

## Impact
[Who is affected]

## Details
[Link to documentation]

## Action Required
[If any user action is needed]

## Questions?
[Contact information]
```


---

## Source: STANDARDS.md

# Ante LLM Context Documentation Standards

## 1. Markdown Formatting Standards

### 1.1 File Structure

**Document metadata (required):**
```markdown
---
title: Document Title
description: Brief description of content
version: 1.0.0
ante_version: ">=0.1.0"
last_updated: 2026-02-20
status: current
---

# Document Title

Content begins here...
```

**Metadata fields:**
- `title`: Descriptive document title
- `description`: 1-2 sentence summary
- `version`: Documentation version (X.Y.Z)
- `ante_version`: Ante compatibility range
- `last_updated`: ISO 8601 date format
- `status`: current|beta|deprecated|archived

### 1.2 Heading Hierarchy

**Rules:**
- Use H1 (#) only once per document for the main title
- Use H2 (##) for major sections
- Use H3 (###) for subsections
- Use H4 (####) for detailed sections
- Don't skip heading levels
- Keep heading text concise and descriptive

**Examples:**
```markdown
# Main Document Title

## Major Section
Content about major section

### Subsection
Related content

#### Detailed Subsection
More specific content
```

### 1.3 Text Formatting

**Emphasis:**
- Use `*italic*` for emphasis
- Use `**bold**` for strong emphasis
- Avoid excessive formatting
- Don't overuse ALL CAPS

**Code:**
- Inline code: `command` or `variable`
- Code blocks: Use triple backticks with language
- File paths: Use backticks `` `/path/to/file` ``
- Command options: Use backticks `` `--option` ``

**Lists:**
- Use `-` for unordered lists
- Use numbers (1., 2., 3.) for ordered lists
- Indent nested lists by 2 spaces
- Leave blank line before lists
- End list items with period if they're sentences

**Examples:**

Unordered list:
```markdown
- Item one
- Item two
  - Nested item
  - Another nested
- Item three
```

Ordered list:
```markdown
1. First step
2. Second step
   1. Substep a
   2. Substep b
3. Third step
```

### 1.4 Code Blocks

**Format:**
```markdown
\`\`\`[language]
code content
\`\`\`
```

**Supported languages:**
- `bash` - Shell commands
- `shell` - Shell scripts
- `json` - JSON data
- `yaml` - YAML configuration
- `markdown` - Markdown examples
- `text` - Plain text output
- `javascript` or `js` - JavaScript
- `python` - Python code
- `go` - Go code
- `rust` - Rust code

**Examples:**

Bash command:
```markdown
\`\`\`bash
ante run --context-size 32kb script.txt
\`\`\`
```

Output/Result:
```markdown
\`\`\`text
Output from command
Line 2 of output
\`\`\`
```

Configuration:
```markdown
\`\`\`yaml
context-size: 32kb
max-tokens: 8000
\`\`\`
```

### 1.5 Links

**Format:**
- Relative links: `[Text](../path/to/file.md)`
- Anchor links: `[Text](#section-heading)`
- External links: `[Text](https://example.com)`

**Rules:**
- Use descriptive link text, not "click here"
- Use relative paths for internal links
- Use HTTPS for external links
- Validate all links work
- Update links when documents move

**Examples:**
```markdown
See [Configuration Guide](./configuration.md) for details.

For more, see the [Advanced Options](#advanced) section below.

Read the [Ante Documentation](https://docs.antigma.ai).
```

### 1.6 Block Quotes

**Format:**
```markdown
> This is a quoted block
> that continues on multiple lines
```

**Use for:**
- Important notes
- Warnings or cautions
- Tips and tricks
- Highlighted information

**Examples:**

Note:
```markdown
> **Note:** This is an important note about the feature.
```

Warning:
```markdown
> ⚠️ **Warning:** This could impact performance.
```

Tip:
```markdown
> 💡 **Tip:** You can use this shortcut to save time.
```

### 1.7 Tables

**Format:**
```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

**Rules:**
- Header row required
- Use pipes (|) to separate columns
- Use dashes (-) for row separators
- Align content for readability
- Include 3+ rows for tables
- Use lists for 2-row content

**Example:**
```markdown
| Option | Type | Default |
|--------|------|---------|
| `--context-size` | string | 32kb |
| `--max-tokens` | integer | 8000 |
| `--model` | string | gpt-4 |
```

### 1.8 Horizontal Rules

Use for visual separation between major sections:
```markdown
---
```

Guidelines:
- Use sparingly
- Don't use at document start or end
- Use between major topic shifts
- Alternative to extra headings

## 2. Code Example Standards

### 2.1 Example Quality Requirements

**Completeness:**
- Includes all necessary setup/imports
- Shows realistic usage
- Includes expected output or result
- Includes error handling if relevant
- Is self-contained and runnable

**Clarity:**
- Comments explain non-obvious code
- Variable names are descriptive
- Following code style conventions
- Realistic data/values
- Not overly complex

**Accuracy:**
- Works with current Ante version
- Output matches documentation
- All options are correct
- Edge cases handled
- Error messages are accurate

### 2.2 Command Line Examples

**Format:**
```markdown
\`\`\`bash
ante [command] [options]
\`\`\`

Output:
\`\`\`text
Expected output here
\`\`\`
```

**Rules:**
- Show full command with all relevant options
- Include realistic data
- Show typical output
- Highlight important parts with comments
- Document assumptions

**Example:**
```markdown
Get context information:

\`\`\`bash
ante context --format json --limit 100
\`\`\`

Output:
\`\`\`json
{
  "items": [
    {"id": 1, "name": "item1", "size": 1024}
  ],
  "total": 1,
  "limit": 100
}
\`\`\`
```

### 2.3 Error Examples

**Format:**
```markdown
When [condition], you get:

\`\`\`bash
ante [command] --invalid-option
\`\`\`

This produces:
\`\`\`text
Error: Unknown option '--invalid-option'
Did you mean '--validate'?
\`\`\`

Solution: [Fix description]
```

### 2.4 Multi-Step Examples

**Format:**
```markdown
\`\`\`bash
# Step 1: Description
ante command --option1

# Step 2: Description
ante command --option2
\`\`\`
```

**Rules:**
- Use comments for step descriptions
- Show intermediate results if relevant
- Number steps in comments
- Explain what happens at each step
- Note any prerequisites

### 2.5 Pseudo-code and Conceptual Examples

**Use when:**
- Feature not yet released
- Cross-platform examples needed
- Conceptual clarity needed
- Avoiding language-specific details

**Format:**
```markdown
\`\`\`text
# Pseudocode example
INITIALIZE context
FOR EACH document IN collection
  CALCULATE relevance
  IF relevance > threshold
    ADD TO results
  END IF
END FOR
RETURN results
\`\`\`
```

### 2.6 Configuration Examples

**Format:**
```markdown
\`\`\`yaml
# Example configuration file
setting1: value1
setting2: value2
section:
  subsetting: value
\`\`\`
```

**Rules:**
- Show realistic values
- Comment non-obvious settings
- Include all required settings
- Show optional settings separately
- Validate syntax

**Example:**
```markdown
# Basic configuration:
\`\`\`yaml
ante:
  context-size: 32kb
  max-tokens: 8000
\`\`\`

# Advanced configuration:
\`\`\`yaml
ante:
  context-size: 64kb
  max-tokens: 16000
  performance:
    cache-enabled: true
    compression: gzip
\`\`\`
```

## 3. Link and Reference Standards

### 3.1 Internal Links

**Format:**
```markdown
[Link text](../path/to/file.md)
[Link text](#section-anchor)
[Link text](./file.md#section-anchor)
```

**Rules:**
- Use relative paths (start with `./` or `../`)
- Never use absolute paths
- Link text should be descriptive
- Verify links work before committing
- Update links when documents move

**Examples:**
```markdown
See the [CLI Reference](../reference/cli.md) for more options.

For advanced usage, see [Configuration](./config.md#advanced).

Related: [Performance Tips](../guides/performance.md#optimization)
```

### 3.2 External Links

**Format:**
```markdown
[Link text](https://example.com/path)
```

**Rules:**
- Always use HTTPS
- Use descriptive link text
- Don't link to URLs that might change
- Prefer official documentation
- Test links periodically

**Examples:**
```markdown
See the [Python documentation](https://docs.python.org/).

For more, visit [Ante GitHub](https://github.com/AntigmaLabs/ante).
```

### 3.3 Link Anchors

**Format:**
```markdown
# Section Title
Content here

[Link to section](#section-title)
```

**Rules:**
- Anchors are lowercase version of heading
- Replace spaces with hyphens
- Remove special characters
- Keep anchors consistent
- Use meaningful heading text

**Examples:**
```markdown
# Advanced Configuration
Content...

[Back to Advanced Configuration](#advanced-configuration)

# Performance Optimization Tips
Content...

[Skip to Performance Tips](#performance-optimization-tips)
```

### 3.4 See Also Sections

**Format:**
```markdown
## See Also
- [Related Topic](link)
- [Another Topic](link)
- [More Information](link)
```

**Rules:**
- Include at end of document
- List 2-5 related topics
- Use descriptive link text
- Organize by relevance
- Keep descriptions brief

**Example:**
```markdown
## See Also
- [Configuration Guide](./configuration.md) - How to configure Ante
- [CLI Reference](../reference/cli.md) - Full command reference
- [Performance Tuning](./performance.md) - Optimization tips
- [Troubleshooting](../guides/troubleshooting.md) - Common issues
```

### 3.5 Reference Format

**When referring to:**
- Commands: Use backticks and full syntax
- Options: Use backticks with leading dashes
- Functions: Use backticks
- Files: Use backticks with path
- Variables: Use backticks

**Examples:**
```markdown
Use the `ante run` command to execute scripts.

The `--context-size` option controls memory usage.

See the `calculate_score()` function for details.

Edit the `~/.ante/config.yaml` configuration file.

Set the `$ANTE_HOME` variable to customize paths.
```

## 4. Naming Conventions for Files

### 4.1 File Naming Rules

**Use lowercase with hyphens:**
```
good-file-name.md
AVOID CamelCase.md
AVOID file_with_underscores.md
AVOID spaces in filename.md
```

**Rules:**
- Use lowercase letters, numbers, and hyphens only
- Use hyphens to separate words
- No special characters
- No spaces in filenames
- Descriptive but concise
- No version numbers in filename

### 4.2 File Organization

```
docs/context/
├── governance/              # This framework
│   ├── GOVERNANCE.md
│   ├── PROCESSES.md
│   ├── MAINTENANCE.md
│   └── STANDARDS.md
├── llm-context/            # LLM-optimized documentation
│   ├── overview.md
│   ├── commands.md
│   └── workflows.md
├── wiki/                   # User-facing documentation
│   ├── getting-started.md
│   ├── guides/
│   │   ├── configuration.md
│   │   ├── performance.md
│   │   └── troubleshooting.md
│   ├── reference/
│   │   ├── cli.md
│   │   ├── api.md
│   │   └── options.md
│   ├── examples/
│   │   ├── basic-usage.md
│   │   ├── advanced-patterns.md
│   │   └── integration.md
│   └── faq.md
├── archive/                # Deprecated versions
│   ├── v0.1.0/
│   ├── v0.2.0/
│   └── README.md
└── llms.txt               # LLM context file
```

### 4.3 Naming Specific Document Types

**Guides:**
- `getting-started.md`
- `configuration.md`
- `installation.md`
- `advanced-usage.md`

**Reference:**
- `cli-reference.md` or `cli.md`
- `api-reference.md` or `api.md`
- `options-reference.md` or `options.md`

**Examples:**
- `basic-examples.md`
- `advanced-patterns.md`
- `integration-examples.md`

**Administration:**
- `governance.md`
- `processes.md`
- `standards.md`

### 4.4 Directory Naming

**Rules:**
- Use lowercase with hyphens
- Singular or plural consistently (use plural for collections)
- Descriptive but concise
- No version numbers

**Examples:**
```
guides/          (plural: collection of guides)
tutorials/       (plural: collection of tutorials)
examples/        (plural: collection of examples)
reference/       (singular: comprehensive reference)
governance/      (singular: the governance framework)
```

## 5. Content Structure Requirements

### 5.1 Standard Document Structure

**Recommended structure:**
```
---
title: ...
description: ...
version: ...
ante_version: ...
last_updated: ...
status: ...
---

# Main Title

## Overview
[What this document covers and why it matters]

## Prerequisites
[What users should know before reading]

## Core Concepts
[Important definitions and relationships]

## Main Content
[Organized into logical sections]

### Subsection 1
Details...

### Subsection 2
Details...

## Examples
[Practical examples]

## Common Issues
[Troubleshooting section]

## Advanced Topics
[Optional: for power users]

## Limitations
[What this feature cannot do]

## See Also
[Related documentation]
```

### 5.2 Section Guidelines

**Overview:**
- 1-3 sentences
- Explain purpose and audience
- Set expectations
- Indicate document scope

**Prerequisites:**
- List required knowledge
- Link to prerequisite documents
- List software/tools needed
- Indicate skill level

**Core Concepts:**
- Define important terms
- Explain relationships
- Show mental models
- Use diagrams if helpful

**Main Content:**
- Logical organization
- Progressive complexity
- Clear headings
- Helpful examples
- Related features cross-referenced

**Examples:**
- Realistic scenarios
- Working code/commands
- Expected output
- Variation examples
- Error examples

**Common Issues:**
- Frequently asked questions
- Common mistakes
- Troubleshooting steps
- Where to get help

**Advanced Topics:**
- Optional section
- For experienced users
- Less common patterns
- Performance considerations
- Edge cases

**See Also:**
- 2-5 related documents
- Brief description of each
- Organized by relevance

### 5.3 Completeness Checklist

Before marking document complete:

**Content**
- [ ] All features mentioned
- [ ] Examples are provided
- [ ] Edge cases documented
- [ ] Limitations listed
- [ ] Prerequisites stated
- [ ] Related features linked

**Quality**
- [ ] No placeholder text (TODO, TBD)
- [ ] Spelling and grammar correct
- [ ] Formatting consistent
- [ ] Code examples tested
- [ ] Links validated
- [ ] Metadata complete

**Standards Compliance**
- [ ] Metadata present
- [ ] Follows style guide
- [ ] Proper heading hierarchy
- [ ] Tables/lists formatted correctly
- [ ] File name follows convention
- [ ] No broken links

**LLM Optimization**
- [ ] Clear section headers
- [ ] Concise explanations
- [ ] Practical examples
- [ ] Consistent terminology
- [ ] Version information clear

## 6. Code Style and Formatting Standards

### 6.1 Bash/Shell Examples

**Style:**
```bash
#!/bin/bash
# Clear comment explaining what this does

# Use meaningful variable names
context_size="32kb"

# Use quotes around variables
echo "Context size: $context_size"

# Use full command names (not aliases)
ls -la /path/to/directory
```

**Rules:**
- Use full command names (not aliases)
- Use meaningful variable names
- Quote variables
- Add comments for non-obvious lines
- Use `#!/bin/bash` for scripts
- Handle errors appropriately

### 6.2 JSON Examples

**Style:**
```json
{
  "name": "example",
  "version": "1.0.0",
  "settings": {
    "context-size": "32kb",
    "max-tokens": 8000
  }
}
```

**Rules:**
- Consistent indentation (2 spaces)
- Quotes around all strings
- Trailing comma in last item (check JSON spec)
- Descriptive key names
- Realistic values

### 6.3 YAML Examples

**Style:**
```yaml
# Configuration file
application:
  name: ante
  version: 1.0.0
settings:
  context-size: 32kb
  max-tokens: 8000
```

**Rules:**
- Use 2-space indentation
- Clear comments
- Consistent key naming (lowercase with hyphens)
- Realistic values
- Show nested structure clearly

## 7. Document Versioning and Status

### 7.1 Version Numbering

**Format:** X.Y.Z (semantic versioning)

- X (Major): Breaking changes to documentation structure
- Y (Minor): New sections, significant additions
- Z (Patch): Corrections, clarifications, minor updates

**Examples:**
- Initial release: 1.0.0
- Add new section: 1.1.0
- Fix typo: 1.0.1
- Reorganize structure: 2.0.0

### 7.2 Status Field

**Allowed values:**

- `current` - Current, maintained documentation
- `beta` - Experimental, subject to change
- `deprecated` - Will be archived soon
- `archived` - Older version, reference only

### 7.3 Ante Compatibility

**Format:** Specify Ante version compatibility

```yaml
ante_version: ">=0.1.0"
ante_version: ">=0.2.0, <0.3.0"
ante_version: "0.2.x"
```

## 8. Accessibility and LLM Optimization

### 8.1 LLM-Friendly Formatting

**Principles:**
1. Clear section hierarchy
2. Descriptive headings
3. Concise, technical language
4. Practical examples
5. Complete context
6. Explicit assumptions

**Example - Not optimized:**
```markdown
Ante can do stuff with files and things. You just run it and it works.
See the guide for more info.
```

**Example - LLM-optimized:**
```markdown
## Processing Files with Ante

The `ante process` command handles file analysis:

\`\`\`bash
ante process --input file.txt --output result.json
\`\`\`

This command:
- Reads the input file
- Analyzes content
- Outputs structured results as JSON
- Returns exit code 0 on success, non-zero on error
```

### 8.2 Explicit Context

**Always include:**
- Command full name and syntax
- Expected inputs/outputs
- Exit codes and errors
- Version limitations
- Related commands/features

### 8.3 Consistency for LLM Parsing

**Use consistent patterns:**

For commands:
```markdown
## Command: [name]

Syntax:
\`\`\`
[full syntax]
\`\`\`

Description: [What it does]

Options:
- \`--option1\`: Description
- \`--option2\`: Description

Example:
\`\`\`bash
[example]
\`\`\`
```

For features:
```markdown
## Feature: [name]

Overview: [Brief description]

When to use: [Common scenarios]

Example:
\`\`\`
[example]
\`\`\`

Limitations: [What it can't do]
```

## 9. Quality Assurance Checklist

Before submitting any documentation for review:

**Content Quality**
- [ ] No placeholder text (TODO, TBD, [PENDING])
- [ ] All information is accurate
- [ ] Examples work with current version
- [ ] Edge cases are documented
- [ ] Limitations are noted
- [ ] Prerequisites are stated

**Format and Standards**
- [ ] Metadata is complete
- [ ] Heading hierarchy is correct
- [ ] No lines exceed 120 characters
- [ ] Code blocks have language specified
- [ ] Lists are formatted correctly
- [ ] Tables are aligned properly

**Links and References**
- [ ] All links are valid relative paths
- [ ] No broken anchors
- [ ] External links use HTTPS
- [ ] Cross-references are accurate
- [ ] See Also section present (if applicable)

**Writing Quality**
- [ ] No spelling errors
- [ ] No grammar errors
- [ ] Clear, concise language
- [ ] Technical terms defined
- [ ] Consistent terminology
- [ ] Good paragraph structure

**LLM Optimization**
- [ ] Clear section headers
- [ ] Descriptive headings
- [ ] Explicit command syntax
- [ ] Complete examples
- [ ] Assumptions stated
- [ ] Version information clear

**Standards Compliance**
- [ ] Follows STANDARDS.md
- [ ] File name follows convention
- [ ] Version number appropriate
- [ ] Status field correct
- [ ] All required metadata present

## 10. Common Mistakes to Avoid

**Don't:**
- Use CamelCase in file names
- Create orphaned documents (not linked from index)
- Write vague section headings
- Use `click here` as link text
- Include placeholder content
- Forget to test examples
- Use outdated Ante syntax
- Create overly long documents (>3000 words)
- Write for search engines instead of users
- Break internal links when reorganizing

**Do:**
- Use lowercase with hyphens
- Link all documents from index
- Use descriptive, specific headings
- Write meaningful link text
- Complete all sections before publishing
- Test all code examples
- Keep examples current
- Break long content into multiple files
- Write for human and LLM readers
- Update cross-references when moving documents


---

## Source: templates/README.md

# Documentation Governance Implementation Templates

This directory contains practical templates for implementing the documentation governance processes defined in `governance/PROCESSES.md`. Each template is ready to use immediately by your team.

---

## Overview

These templates operationalize the governance framework by providing:
- Structured forms for standardized processes
- Built-in checklists to ensure quality
- Clear workflows and sign-offs
- Traceability and accountability measures

All templates follow the standards in `governance/STANDARDS.md` and support the processes in `governance/PROCESSES.md`.

---

## Template Reference Guide

### 1. **documentation-request-template.md**

**Purpose:** Request new documentation or documentation updates  
**When to Use:** At the start of any new documentation project  
**Process Stage:** Phase 1 - Identify & Request  
**Key Sections:**
- Feature/topic scope definition
- Business justification
- Dependencies and placement
- Effort estimation
- Success criteria

**Workflow:**
1. Author completes request
2. Submit to Content Owner
3. Content Owner approves/requests changes
4. Approval within 3 business days

**Output:** Approved documentation request → Schedule documentation work

---

### 2. **content-submission-template.md**

**Purpose:** Submit completed documentation content for review  
**When to Use:** When documentation is written and ready for technical review  
**Process Stage:** Phase 2-3 - Write & Submit for Review  
**Key Sections:**
- Pre-submission quality checklist
- Completeness verification points
- Author sign-off
- Reviewer assignments
- Testing evidence

**Workflow:**
1. Author completes pre-submission checklist
2. All code examples tested and verified
3. All sections complete
4. Submit with supporting artifacts
5. Assigned to reviewers
6. 3-5 business day review period

**Output:** Submitted content → Technical review process

**Critical:** Do not submit until ALL pre-submission checklist items are verified.

---

### 3. **technical-review-checklist.md**

**Purpose:** Conduct thorough technical review of documentation  
**When to Use:** When reviewing submitted documentation content  
**Process Stage:** Phase 4 - Internal Review  
**Reviewer Roles:**
- Technical Reviewer - Accuracy & completeness
- QA Reviewer - Standards & consistency
- LLM Specialist - LLM accessibility
- Content Owner - Final approval

**Key Sections:**
- Accuracy verification (7 sub-sections)
- Completeness assessment
- Code example validation
- Link & reference validation
- Standards compliance
- Consistency checks
- LLM accessibility review

**Workflow:**
1. Assigned to appropriate reviewers
2. Complete all applicable sections
3. Document all issues with severity
4. Provide clear feedback
5. Sign off when approved

**Quality Gates:** Documentation cannot merge if critical issues remain.

---

### 4. **release-notes-template.md**

**Purpose:** Document documentation releases tied to Ante version releases  
**When to Use:** When publishing documentation for a new Ante release  
**Process Stage:** Phase 7-8 - Approval & Publication  
**Key Sections:**
- Release metadata and summary
- Type A/B/C change categorization
- Detailed change log
- Feature documentation status
- Breaking changes & migration guides
- Quality assurance results
- Author & reviewer credits
- User-facing release notes

**Workflow:**
1. Create before Ante release
2. Document all changes made
3. Categorize by type (A/B/C)
4. QA sign-off required
5. Publish on release day
6. Notify users of changes

**Output:** Published release notes → User awareness of documentation changes

---

### 5. **documentation-update-planning.md**

**Purpose:** Plan documentation updates to coincide with Ante releases  
**When to Use:** 2-3 weeks before Ante release date  
**Process Stage:** Pre-release planning & coordination  
**Key Sections:**
- Feature impact assessment
- Timeline and milestones
- Dependency mapping
- Resource allocation
- Content planning worksheet
- Testing & validation plan
- Risk management
- Status tracking

**Workflow:**
1. Create plan when Ante release is announced
2. Assess documentation impact
3. Assign resources and tasks
4. Create detailed timeline
5. Weekly status tracking
6. Publish release notes on release day

**Critical Dates:**
- Plan created: 2-3 weeks before release
- Draft content due: 1 week before release
- All reviews complete: 3-5 days before release
- Ready to publish: Release day

---

### 6. **governance-exception-request.md**

**Purpose:** Request exceptions to governance standards and processes  
**When to Use:** When you cannot follow standard processes or meet requirements  
**Process Stage:** Ad-hoc governance decisions  
**Approval Levels:**
- **Type A** (Process exception) - Content Owner approval
- **Type B** (Standards modification) - Governance Council review
- **Type C** (Framework change) - Executive sponsor + Council

**Key Sections:**
- Standard/process being requested
- Justification and alternatives considered
- Impact assessment on quality
- Mitigation and risk management
- Scope and duration
- Conditions and monitoring
- Rollback plan

**Workflow:**
1. Complete request thoroughly
2. Obtain manager approval (if needed)
3. Submit with supporting documentation
4. Council reviews (usually 1-2 weeks)
5. Decision communicated
6. Monitoring plan implemented

**Important:** Exceptions require clear justification and risk mitigation.

---

## Implementation Workflow Map

```
Documentation Lifecycle → Template to Use
├── 1. Identify Documentation Need
│   └── documentation-request-template.md
│
├── 2. Get Approval
│   └── [Approval step - no template]
│
├── 3. Research & Plan
│   └── [Planning step - for releases, use documentation-update-planning.md]
│
├── 4. Write Documentation
│   └── [Writing step - no template]
│
├── 5. Pre-Review Quality Check
│   └── content-submission-template.md (pre-submission checklist)
│
├── 6. Submit for Review
│   └── content-submission-template.md (full submission)
│
├── 7. Technical Review
│   └── technical-review-checklist.md
│
├── 8. Revisions
│   └── [Revision step - no template]
│
├── 9. Final Approval
│   └── [Approval step - no template]
│
└── 10. Publish & Release
    └── release-notes-template.md

Special Cases:
├── Planning Ante Release Documentation
│   └── documentation-update-planning.md (early phase)
│
├── Need Process Exception
│   └── governance-exception-request.md
└── [Standard process otherwise applies]
```

---

## Using These Templates

### For Authors

1. **Start with:** `documentation-request-template.md`
   - Request approval for your documentation work
   - Define scope and get buy-in

2. **Then:** Write your documentation following `governance/STANDARDS.md`

3. **Before submitting:** Use `content-submission-template.md`
   - Complete the pre-submission checklist
   - Test all code examples
   - Verify all sections are complete

4. **Submit:** The completed submission template with your documentation

### For Reviewers

1. **Use:** `technical-review-checklist.md`
   - Verify accuracy against running Ante
   - Check completeness of content
   - Validate code examples
   - Verify links and references
   - Check standards compliance
   - Document all findings

2. **Sign off** when all issues are resolved

### For Release Coordination

1. **3 weeks before release:** Create `documentation-update-planning.md`
   - Assess documentation impact
   - Assign resources
   - Set timeline

2. **During release:** Track progress with status updates

3. **At release:** Create `release-notes-template.md`
   - Document all changes
   - Publish release notes

### For Governance Decisions

1. **If you need an exception:** Complete `governance-exception-request.md`
   - Justify the exception
   - Assess impact
   - Propose mitigation
   - Submit to Council for review

---

## Template Customization

These templates are designed to be comprehensive but can be adapted to your needs:

- **Remove sections** that don't apply to your process
- **Add custom fields** specific to your organization
- **Adjust approval workflows** based on your team structure
- **Modify timelines** for your release schedule
- **Adapt checklists** to match your standards

However, maintain the core structure and intent of each template.

---

## Quality Standards Supported

These templates support the quality standards in `governance/STANDARDS.md`:

- **Accuracy** - Verified through technical review
- **Completeness** - Checked via completeness assessment
- **Consistency** - Validated in consistency checks
- **Clarity** - Reviewed in LLM accessibility section
- **Structure** - Confirmed in standards compliance checks

---

## Integration with Other Governance Documents

| Template | Related to | Reference |
|---|---|---|
| documentation-request-template.md | PROCESSES.md § 1.2-1.3 | Process workflow |
| content-submission-template.md | PROCESSES.md § 7 | Review checklist |
| technical-review-checklist.md | PROCESSES.md § 4 | QA procedures |
| release-notes-template.md | PROCESSES.md § 5.3 | Documentation changelog |
| documentation-update-planning.md | PROCESSES.md § 5 | Release lifecycle |
| governance-exception-request.md | GOVERNANCE.md | Exception framework |

---

## Common Scenarios

### Scenario 1: New Feature Documentation

1. Create `documentation-request-template.md` → Get approval
2. Plan documentation with `documentation-update-planning.md`
3. Write documentation
4. Complete pre-submission checklist in `content-submission-template.md`
5. Submit and assign reviewers
6. Reviewers use `technical-review-checklist.md`
7. Revise based on feedback
8. Publish with `release-notes-template.md`

### Scenario 2: Bug Fix/Clarification

- If Type A (routine): Can update directly, minimal review
- If Type B (significant): Use `documentation-request-template.md` → review → publish
- If Type C (policy): Use `governance-exception-request.md` for approval

### Scenario 3: Planned Release

1. Create `documentation-update-planning.md` 2-3 weeks before release
2. Track progress with weekly status updates
3. Submit completed content with `content-submission-template.md`
4. Reviews use `technical-review-checklist.md`
5. Publish with `release-notes-template.md` on release day

### Scenario 4: Need Process Exception

1. Complete `governance-exception-request.md`
2. Submit to Governance Council
3. Council reviews and votes
4. If approved, implement with stated conditions
5. Monitor per the exception requirements

---

## Support & Resources

**Questions about templates?**
- Review the process guide: `governance/PROCESSES.md`
- Check the standards: `governance/STANDARDS.md`
- Review the governance framework: `governance/GOVERNANCE.md`

**Need help with a specific template?**
- Each template includes instructions and examples
- Use the templates provided by Content Owner as reference
- Contact your Content Owner for guidance

**Feedback on templates?**
- Report issues or suggestions: [GitHub Issues]
- Propose improvements to Content Owner
- Help us improve the governance framework

---

## Version History

| Date | Version | Changes |
|---|---|---|
| [2026-02-20] | 1.0 | Initial creation of template suite |

---

## File Index

```
templates/
├── README.md (this file)
├── documentation-request-template.md (6.3 KB)
├── content-submission-template.md (10 KB)
├── technical-review-checklist.md (17 KB)
├── release-notes-template.md (14 KB)
├── documentation-update-planning.md (14 KB)
└── governance-exception-request.md (14 KB)

Total: 6 practical templates (~75 KB)
```

---

*All templates are ready for immediate use. Copy, fill out, and submit following the workflows defined in `governance/PROCESSES.md`.*


---

## Source: templates/content-submission-template.md

# Content Submission Template

Use this template when submitting documentation content for review. Complete all sections and run through the pre-submission checklist before submitting.

---

## Submission Information

**Document Title:** [Full title of documentation being submitted]

**Submission Date:** [YYYY-MM-DD]

**Submission ID:** [Auto-generated or provided by system]

---

## Author Information

**Primary Author:** [Full name]
- **Email:** [Email address]
- **Role:** [Position/Title]
- **Contact Method:** [Preferred contact method]

**Contributing Authors:**
- [Name 1] - [Contribution description]
- [Name 2] - [Contribution description]

---

## Content Summary

### Overview
[One-paragraph summary of what this documentation covers]

### Scope
**Topics Covered:**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Intended Audience:**
- [ ] New users
- [ ] Experienced users
- [ ] System administrators
- [ ] Developers
- [ ] [Other: ___________]

**Approximate Length:** [Number of words/lines/pages]

### Relationship to Existing Documentation
List how this documentation relates to, complements, or supersedes existing content:
- [Existing doc 1]: [Relationship]
- [Existing doc 2]: [Relationship]

---

## Pre-Submission Quality Assurance Checklist

**Complete this checklist before submitting. All items must be checked.**

### Content Quality

**Accuracy & Currency**
- [ ] All technical information is accurate for Ante [version]
- [ ] Feature descriptions match current implementation
- [ ] API/command signatures are current and tested
- [ ] No deprecated features are documented without notice
- [ ] Version compatibility information is accurate
- [ ] All code examples have been executed and verified

**Completeness**
- [ ] All features/options mentioned in scope are documented
- [ ] No sections contain "TODO", "TBD", or incomplete placeholders
- [ ] Edge cases and limitations are documented
- [ ] Common use cases are covered with examples
- [ ] Error conditions and error messages are documented
- [ ] Prerequisites and dependencies are listed
- [ ] Related features are cross-referenced

**Clarity & Accessibility**
- [ ] Content is understandable to target audience
- [ ] Technical terms are defined on first use
- [ ] Assumptions about user knowledge are stated
- [ ] Written in clear, concise technical language
- [ ] Sentences are appropriately structured
- [ ] No excessive jargon without explanation

### Format & Standards Compliance

**Markdown & Structure**
- [ ] Valid Markdown syntax throughout
- [ ] Proper heading hierarchy (no skipped levels)
- [ ] Code blocks have language specified (e.g., ```python)
- [ ] Consistent formatting and style
- [ ] Appropriate use of emphasis (bold/italic)
- [ ] Lists are properly formatted

**Metadata**
- [ ] Document has proper YAML front matter
- [ ] All required metadata fields are present:
  - [ ] `title:`
  - [ ] `description:`
  - [ ] `audience:`
  - [ ] `version:`
  - [ ] `updated:`
  - [ ] `author:`
- [ ] Metadata values are accurate and complete

**Code Examples**
- [ ] All code blocks are tested and working
- [ ] Output examples match actual behavior
- [ ] Code comments are clear and helpful
- [ ] Examples demonstrate intended usage patterns
- [ ] Example output is clearly marked
- [ ] Edge cases in examples are explained

**Links & References**
- [ ] All internal links use relative paths
- [ ] Links are formatted consistently
- [ ] No broken links (all targets verified)
- [ ] External links are current and appropriate
- [ ] "See Also" sections list relevant documentation
- [ ] Cross-references are bidirectional where appropriate

### Standards Compliance

**Standards Reference:** Refer to governance/STANDARDS.md

- [ ] Follows terminology standards
- [ ] Matches documentation style guide
- [ ] Uses consistent code formatting
- [ ] Follows naming conventions
- [ ] Adheres to document structure guidelines
- [ ] Image/diagram standards met (if applicable)
- [ ] Table formatting is correct
- [ ] Spacing and layout follows conventions

### Testing & Validation

**Code Examples**
- [ ] Examples tested on current Ante version
- [ ] Output verified against documentation claims
- [ ] Examples work with described prerequisites met
- [ ] Error cases produce expected error messages
- [ ] All command-line flags work as documented

**Links & Navigation**
- [ ] Clicked through all internal links
- [ ] Verified external links are accessible
- [ ] Navigation from/to this document is correct
- [ ] Documentation index includes this content
- [ ] Related documents link back to this content

**Consistency Checks**
- [ ] Terminology is consistent with other docs
- [ ] Examples follow same patterns as similar sections
- [ ] Formatting matches similar documentation
- [ ] Version numbers are consistent throughout
- [ ] No contradictions with other documentation

---

## Completeness Verification Points

### Core Documentation Elements

**For all documentation, verify:**
- [ ] Title clearly describes content
- [ ] Opening paragraph explains purpose and audience
- [ ] Prerequisites are clearly stated
- [ ] Main content is logically organized
- [ ] Key concepts are explained with examples
- [ ] Limitations and edge cases are documented
- [ ] Troubleshooting section for common issues
- [ ] "See Also" section links to related content
- [ ] Updated date reflects submission date

**For feature/command documentation, additionally verify:**
- [ ] All available options are documented
- [ ] All required parameters are clearly marked
- [ ] Default values are specified
- [ ] Parameter types and formats are explained
- [ ] Version compatibility info is present
- [ ] Return values/outputs are documented
- [ ] Possible error conditions are listed
- [ ] Common error messages are explained

**For tutorial/how-to documentation, additionally verify:**
- [ ] Clear step-by-step instructions
- [ ] Expected output at each step
- [ ] Prerequisites are listed upfront
- [ ] Estimated time to complete is provided
- [ ] Troubleshooting for common mistakes
- [ ] Next steps or related topics suggested

**For conceptual documentation, additionally verify:**
- [ ] Core concepts are clearly explained
- [ ] Relationships between concepts are shown
- [ ] Real-world examples illustrate concepts
- [ ] Motivation for the concept is clear
- [ ] Common misconceptions are addressed

---

## Submission Artifacts

**Documents Included:**

```
📄 documentation-request-[feature-name].md (documentation request approval)
📄 [main-document].md (primary content)
📄 [supporting-doc-1].md (if applicable)
📄 [supporting-doc-2].md (if applicable)
```

**Associated Files:**

- [ ] Code examples (test files, test results)
- [ ] Screenshots/diagrams
- [ ] Reference materials
- [ ] Testing evidence
- [ ] Approval documentation

---

## Testing Evidence

### Tested Against
- **Ante Version:** [version number]
- **Test Date:** [YYYY-MM-DD]
- **Test Environment:** [OS/platform]
- **Tester:** [Name]

### Test Results Summary
[Brief summary of testing completed]

### Test Artifacts
- [ ] Code example output captured
- [ ] Commands verified to work
- [ ] Links tested
- [ ] Screenshots taken and included
- [ ] Error conditions validated

**Test Log:** [Link to or attachment of test results]

---

## Author Sign-Off

By submitting this documentation, I certify that:

- [ ] I have completed all pre-submission checklist items
- [ ] I have tested all code examples against Ante [version]
- [ ] I have reviewed all links and verified they are correct
- [ ] I have checked consistency with existing documentation
- [ ] The content is accurate to the best of my knowledge
- [ ] I have obtained approval from technical experts for accuracy (if needed)
- [ ] The documentation is ready for technical review

**Author Name:** ________________________

**Signature/Approval:** ________________________

**Date:** ________________________

---

## Reviewer Information (Completed by Reviewer)

### Technical Review Assignment

**Assigned Reviewers:**
- **Technical Reviewer:** [Name] - Email: [Email]
- **QA Reviewer:** [Name] - Email: [Email]
- **LLM Specialist:** [Name] - Email: [Email] (if applicable)

**Review Start Date:** [Date]

**Target Review Completion:** [Date + 3-5 business days]

### Initial Assessment

**Reviewer Notes:**
[Any initial observations before detailed review]

**Document Status:**
- [ ] Ready for technical review
- [ ] Needs preliminary revision before review
- [ ] Incomplete or missing required information

---

## Review Guidelines for Reviewers

### Technical Accuracy Review
- [ ] Feature behavior matches Ante [version]
- [ ] Code examples produce expected output
- [ ] No deprecated patterns without notices
- [ ] API signatures are current
- [ ] Error messages are accurate
- [ ] Version compatibility info is correct

### Completeness Review
- [ ] All scope items are documented
- [ ] No placeholder or incomplete sections
- [ ] Examples cover primary use cases
- [ ] Edge cases are mentioned
- [ ] Limitations are clearly noted
- [ ] Error conditions are explained

### Consistency Review
- [ ] Terminology matches other docs
- [ ] Format matches similar sections
- [ ] Metadata is consistent
- [ ] Version numbers are consistent
- [ ] No contradictions found

### LLM Accessibility Review
- [ ] Content is LLM-friendly
- [ ] Technical concepts are explained clearly
- [ ] Examples are self-contained
- [ ] Assumptions are stated
- [ ] Format supports LLM understanding

---

## Next Steps After Submission

1. **Acknowledgment** - Content Owner confirms receipt (within 1 business day)
2. **Assignment** - Reviewers are assigned
3. **Review Period** - Technical and QA review (3-5 business days)
4. **Feedback** - Review comments provided to author
5. **Revisions** - Author addresses feedback
6. **Final Approval** - Content Owner approves for merge
7. **Publication** - Documentation is merged and published

---

## Questions or Issues

**Have questions about the submission process?**
- Refer to governance/PROCESSES.md for detailed process information
- Contact Content Owner: [Email]

**Have questions about standards?**
- Refer to governance/STANDARDS.md
- Contact Standards Coordinator: [Email]

**Need technical help with Markdown/formatting?**
- See documentation template examples
- Contact Documentation Coordinator: [Email]


---

## Source: templates/documentation-request-template.md

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


---

## Source: templates/documentation-update-planning.md

# Documentation Update Planning Template

Use this template to plan documentation updates corresponding to Ante feature releases. Complete this form 2-3 weeks before the scheduled Ante release.

---

## Planning Information

**Planning Document Title:** Documentation Update Plan for Ante v[VERSION]

**Plan Created:** [YYYY-MM-DD]

**Plan Status:** [ ] Draft [ ] Approved [ ] In Execution [ ] Complete

---

## Ante Release Information

### Release Details

| Property | Value |
|---|---|
| **Ante Version** | v[VERSION] |
| **Release Type** | [ ] Major [ ] Minor [ ] Patch [ ] Release Candidate |
| **Planned Release Date** | [YYYY-MM-DD] |
| **Release Branch** | [branch name] |
| **Feature Freeze Date** | [YYYY-MM-DD] |
| **Release Candidate Date** | [YYYY-MM-DD] (if applicable) |
| **Documentation Deadline** | [YYYY-MM-DD] |

### Release Overview

[Brief overview of major features/changes in this release]

**Key Features Being Added:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

**Breaking Changes:**
- [ ] No breaking changes
- [Breaking change 1]: [Description]
- [Breaking change 2]: [Description]

**Deprecations:**
- [ ] No deprecations
- [Deprecation 1]: [Description]
- [Deprecation 2]: [Description]

---

## Documentation Impact Assessment

### Feature-by-Feature Impact Analysis

**Feature:** [Feature Name]
- **Type:** [ ] New Feature [ ] Enhancement [ ] Bug Fix [ ] Internal Change
- **Documentation Needed:** [ ] New [ ] Update Existing [ ] No docs needed
- **Affected Documentation:**
  - [Document 1] - [Type of change]
  - [Document 2] - [Type of change]
- **Complexity:** [ ] Low [ ] Medium [ ] High
- **Estimated Effort:** [Hours]
- **Assigned To:** [Name]
- **Status:** [ ] Not Started [ ] In Progress [ ] Complete

**Feature:** [Feature Name]
- **Type:** [ ] New Feature [ ] Enhancement [ ] Bug Fix [ ] Internal Change
- **Documentation Needed:** [ ] New [ ] Update Existing [ ] No docs needed
- **Affected Documentation:**
  - [Document 1] - [Type of change]
- **Complexity:** [ ] Low [ ] Medium [ ] High
- **Estimated Effort:** [Hours]
- **Assigned To:** [Name]
- **Status:** [ ] Not Started [ ] In Progress [ ] Complete

### Documentation Scope Summary

| Category | Count | Effort (Hours) | Notes |
|---|---|---|---|
| **New Documents** | [N] | [Hours] | [Description] |
| **Significant Updates** | [N] | [Hours] | [Type B changes] |
| **Routine Updates** | [N] | [Hours] | [Type A changes] |
| **Archive/Deprecate** | [N] | [Hours] | [To be archived] |
| **TOTAL** | [N] | [Hours] | |

---

## Timeline & Milestones

### Release Timeline

```
Week 1 (Planning Week):
  - [ ] [Date] - This plan completed and approved
  - [ ] [Date] - Team kickoff meeting
  - [ ] [Date] - Resource allocation confirmed
  - [ ] [Date] - Draft content outline completed

Week 2-3 (Development Phase):
  - [ ] [Date] - Draft documentation written
  - [ ] [Date] - Code examples created and tested
  - [ ] [Date] - Internal review started
  - [ ] [Date] - Revisions based on feedback

Week 4 (Pre-Release):
  - [ ] [Date] - All documentation complete
  - [ ] [Date] - Final QA review
  - [ ] [Date] - Approval for release
  - [ ] [Date] - Ready for merge

Release Day:
  - [ ] [Date] - Ante v[VERSION] released
  - [ ] [Date] - Documentation merged
  - [ ] [Date] - llms.txt updated
  - [ ] [Date] - Change notification published

Post-Release:
  - [ ] [Date] - Verify examples work
  - [ ] [Date] - Address user feedback
  - [ ] [Date] - Close documentation issues
```

### Critical Dates

| Milestone | Date | Owner | Status |
|---|---|---|---|
| **Planning Complete** | [Date] | [Name] | [ ] On Track [ ] At Risk [ ] Delayed |
| **Feature Finalization** | [Date] | [Name] | [ ] On Track [ ] At Risk [ ] Delayed |
| **Draft Content Complete** | [Date] | [Name] | [ ] On Track [ ] At Risk [ ] Delayed |
| **Internal Review Complete** | [Date] | [Name] | [ ] On Track [ ] At Risk [ ] Delayed |
| **QA Approval** | [Date] | [Name] | [ ] On Track [ ] At Risk [ ] Delayed |
| **Ready for Release** | [Date] | [Name] | [ ] On Track [ ] At Risk [ ] Delayed |
| **Ante Release Date** | [Date] | Product Team | [ ] On Track [ ] At Risk [ ] Delayed |
| **Docs Merged & Published** | [Date] | [Name] | [ ] On Track [ ] At Risk [ ] Delayed |

---

## Dependency Mapping

### Documentation Dependencies

**New documentation depends on:**
- [Doc 1] - Existing or concurrent development
- [Doc 2] - Existing or concurrent development

**Documentation that depends on this release:**
- [Doc 1] - To be updated
- [Doc 2] - To be updated

### Feature Dependencies

**Documentation blocked by:**
- [ ] No blocking dependencies
- [Feature 1] - [Why blocked]
- [Feature 2] - [Why blocked]

**Features documented in this release:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

### Cross-Team Dependencies

**Dependencies on Product Team:**
- [ ] Feature specs finalized by: [Date]
- [ ] API/CLI signatures finalized by: [Date]
- [ ] Testing environment available by: [Date]
- [ ] Pre-release builds available by: [Date]

**Dependencies on QA:**
- [ ] Test coverage available by: [Date]
- [ ] Edge case documentation by: [Date]
- [ ] Error scenarios documented by: [Date]

---

## Resource Allocation

### Team & Assignments

**Core Documentation Team:**

| Role | Name | Availability | Hours Available | Assignment |
|---|---|---|---|---|
| **Content Owner** | [Name] | [%] | [Hours] | Planning & Approval |
| **Lead Author** | [Name] | [%] | [Hours] | Core content |
| **Technical Writer 1** | [Name] | [%] | [Hours] | Feature docs |
| **Technical Writer 2** | [Name] | [%] | [Hours] | Examples & tutorials |
| **QA Lead** | [Name] | [%] | [Hours] | Review & testing |
| **Editor** | [Name] | [%] | [Hours] | Formatting & polish |

**Extended Team Support:**

| Role | Name | Support Area | Hours |
|---|---|---|---|
| **Product Manager** | [Name] | Feature briefings | [Hours] |
| **Engineering Lead** | [Name] | Technical accuracy | [Hours] |
| **UX Lead** | [Name] | User workflows | [Hours] |

### Hours by Phase

| Phase | Estimated Hours | Actual Hours | Notes |
|---|---|---|---|
| **Planning** | [Hours] | [Hours] | Planning & kickoff |
| **Research** | [Hours] | [Hours] | Understanding features |
| **Writing** | [Hours] | [Hours] | Content creation |
| **Testing** | [Hours] | [Hours] | Example verification |
| **Review** | [Hours] | [Hours] | Technical review |
| **Revision** | [Hours] | [Hours] | Addressing feedback |
| **Final QA** | [Hours] | [Hours] | Final checks |
| **Merge & Publish** | [Hours] | [Hours] | Release tasks |
| **TOTAL** | [Hours] | [Hours] | |

---

## Content Planning Worksheet

### New Documentation to Create

**Document 1: [Title]**

| Item | Details |
|---|---|
| **Purpose** | [What this documents] |
| **Scope** | [Features/topics covered] |
| **Target Audience** | [Intended readers] |
| **Estimated Length** | [Pages/words] |
| **Type** | [ ] Guide [ ] Tutorial [ ] Reference [ ] Conceptual |
| **Primary Author** | [Name] |
| **Content Outline** | 1. [Section 1]<br>2. [Section 2]<br>3. [Section 3] |
| **Code Examples** | [Number needed] |
| **Related Docs** | [Cross-references] |
| **Estimated Hours** | [Hours] |
| **Start Date** | [Date] |
| **Due Date** | [Date] |
| **Status** | [ ] Planned [ ] Drafted [ ] Under Review [ ] Complete |

**Document 2: [Title]**

| Item | Details |
|---|---|
| **Purpose** | [What this documents] |
| **Scope** | [Features/topics covered] |
| **Target Audience** | [Intended readers] |
| **Estimated Length** | [Pages/words] |
| **Type** | [ ] Guide [ ] Tutorial [ ] Reference [ ] Conceptual |
| **Primary Author** | [Name] |
| **Content Outline** | 1. [Section 1]<br>2. [Section 2] |
| **Code Examples** | [Number needed] |
| **Related Docs** | [Cross-references] |
| **Estimated Hours** | [Hours] |
| **Start Date** | [Date] |
| **Due Date** | [Date] |
| **Status** | [ ] Planned [ ] Drafted [ ] Under Review [ ] Complete |

### Existing Documentation to Update

**Document: [Title]**

| Item | Details |
|---|---|
| **Current Status** | [Current version/date] |
| **Changes Needed** | [What needs updating] |
| **Type of Update** | [ ] Type A (Routine) [ ] Type B (Significant) |
| **Sections Affected** | [Which sections] |
| **New Examples** | [Number to add] |
| **Breaking Changes** | [ ] Yes [ ] No |
| **Primary Author** | [Name] |
| **Estimated Hours** | [Hours] |
| **Start Date** | [Date] |
| **Due Date** | [Date] |
| **Status** | [ ] Planned [ ] Drafted [ ] Under Review [ ] Complete |

**Document: [Title]**

| Item | Details |
|---|---|
| **Current Status** | [Current version/date] |
| **Changes Needed** | [What needs updating] |
| **Type of Update** | [ ] Type A (Routine) [ ] Type B (Significant) |
| **Sections Affected** | [Which sections] |
| **New Examples** | [Number to add] |
| **Breaking Changes** | [ ] Yes [ ] No |
| **Primary Author** | [Name] |
| **Estimated Hours** | [Hours] |
| **Start Date** | [Date] |
| **Due Date** | [Date] |
| **Status** | [ ] Planned [ ] Drafted [ ] Under Review [ ] Complete |

### Migration Guides (if needed)

**Migration Guide: Upgrading from v[PREV] to v[VERSION]**

| Item | Details |
|---|---|
| **Breaking Changes** | [List of breaking changes] |
| **Migration Steps** | [Step 1, 2, 3...] |
| **Examples** | [Number needed] |
| **Author** | [Name] |
| **Estimated Hours** | [Hours] |
| **Start Date** | [Date] |
| **Due Date** | [Date] |
| **Status** | [ ] Planned [ ] Drafted [ ] Under Review [ ] Complete |

---

## Testing & Validation Plan

### Code Example Testing Strategy

**Testing Scope:**
- [ ] All new examples will be tested
- [ ] Updated examples will be retested
- [ ] Routine updates (Type A) - spot check

**Testing Details:**

| Example/Test | Type | Test Date | Tester | Result | Notes |
|---|---|---|---|---|---|
| [Example 1] | [ ] New [ ] Updated | [Date] | [Name] | [ ] Pass [ ] Fail | |
| [Example 2] | [ ] New [ ] Updated | [Date] | [Name] | [ ] Pass [ ] Fail | |
| [Example 3] | [ ] New [ ] Updated | [Date] | [Name] | [ ] Pass [ ] Fail | |

### Documentation Testing Matrix

| Test Area | Coverage | Schedule | Responsible |
|---|---|---|---|
| **Code Examples** | 100% of new | Week 3 | [Name] |
| **Links** | 100% of changed | Week 4 | [Name] |
| **Consistency** | 100% of scope | Week 4 | [Name] |
| **Accuracy** | 100% of technical | Week 4 | [Name] |

### Quality Gates

Documentation cannot be released if:
- [ ] Broken links exist (critical)
- [ ] Code examples don't run (critical)
- [ ] Information contradicts current Ante version (critical)
- [ ] Required sections are missing (high)
- [ ] Formatting is inconsistent (medium)

---

## Status Tracking

### Weekly Status Report

**Week of [Date]:**

| Task | Planned | Completed | % Complete | Notes |
|---|---|---|---|---|
| [Task 1] | [Hours] | [Hours] | [%] | [Status] |
| [Task 2] | [Hours] | [Hours] | [%] | [Status] |
| [Task 3] | [Hours] | [Hours] | [%] | [Status] |

**Risks Identified:**
- [ ] No risks
- [Risk 1]: [Impact] - [Mitigation]
- [Risk 2]: [Impact] - [Mitigation]

**Issues/Blockers:**
- [ ] No issues
- [Issue 1]: [Description] - [Resolution]
- [Issue 2]: [Description] - [Resolution]

**Next Week Priorities:**
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

---

## Risk Management

### Identified Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| [Risk 1] | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Medium [ ] Low | [Plan] | [Name] |
| [Risk 2] | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Medium [ ] Low | [Plan] | [Name] |

### Risk Contingencies

**If [Risk occurs]:**
- Contingency plan: [What we'll do]
- Alternative approach: [Alternative]
- Escalation: [Who to notify]

---

## Communication Plan

### Stakeholder Updates

| Stakeholder | Update Frequency | Method | Owner |
|---|---|---|---|
| **Product Team** | Weekly | [Email/Slack/Meeting] | [Name] |
| **Content Owner** | Bi-weekly | [Email/Slack/Meeting] | [Name] |
| **QA Team** | Weekly | [Email/Slack/Meeting] | [Name] |
| **LLM Specialists** | As needed | [Email/Slack] | [Name] |

### Status Report Template

```markdown
## Documentation Update Plan Status - Week of [Date]

**Overall Status:** [ ] On Track [ ] At Risk [ ] Behind Schedule

### Progress
- [Metric 1]: [Value]
- [Metric 2]: [Value]

### Completed This Week
- [Item 1]
- [Item 2]

### In Progress
- [Item 1]
- [Item 2]

### Next Week
- [Priority 1]
- [Priority 2]

### Risks/Issues
- [Issue/Risk]
```

---

## Approval & Sign-Off

### Plan Approval

**This plan has been reviewed and approved by:**

**Content Owner:**
- Name: ________________________
- Signature: ________________________
- Date: ________________________

**Technical Lead (Product Team):**
- Name: ________________________
- Signature: ________________________
- Date: ________________________

**QA Lead:**
- Name: ________________________
- Signature: ________________________
- Date: ________________________

### Plan Amendments

If changes are needed to this plan after approval, document them here:

| Date | Change | Rationale | Approver |
|---|---|---|---|
| [Date] | [Change made] | [Why] | [Approved by] |
| [Date] | [Change made] | [Why] | [Approved by] |

---

## Post-Release Checklist

**Activities to complete after release:**

- [ ] Verify documentation is published
- [ ] Check all examples work for users
- [ ] Monitor for questions/issues
- [ ] Collect feedback from users
- [ ] Fix critical issues if found
- [ ] Update llms.txt with final content
- [ ] Archive any deprecated documentation
- [ ] Publish release notes
- [ ] Send change notification
- [ ] Close documentation issues
- [ ] Document lessons learned
- [ ] Schedule retrospective meeting

---

## Lessons Learned (Post-Release)

**Completed after release is published**

**What Went Well:**
- [Success 1]
- [Success 2]
- [Success 3]

**What Could Be Improved:**
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

**For Next Release:**
- [Action 1]
- [Action 2]
- [Action 3]

---

## References & Resources

**Planning Resources:**
- Ante release plan: [Link]
- Feature specifications: [Link]
- API documentation: [Link]
- Standards guide: governance/STANDARDS.md
- Processes guide: governance/PROCESSES.md

**Contact Information:**
- Product Lead: [Email]
- Content Owner: [Email]
- Tech Lead: [Email]

---

*This plan was created on [YYYY-MM-DD] and last updated on [YYYY-MM-DD]*


---

## Source: templates/governance-exception-request.md

# Governance Exception Request Template

Use this template to request exceptions or waivers from the documentation governance standards, processes, or procedures defined in the governance framework. Submit to the Governance Council for review and approval.

---

## Request Information

**Request ID:** [Auto-generated or assigned]

**Request Date:** [YYYY-MM-DD]

**Request Status:** [ ] Draft [ ] Submitted [ ] Under Review [ ] Approved [ ] Rejected [ ] Expired

**Submission Deadline:** [YYYY-MM-DD] (If not submitted by this date, request expires)

---

## Requestor Information

**Requestor Name:** [Full name]
- **Email:** [Email address]
- **Role/Title:** [Position]
- **Department/Team:** [Team name]
- **Phone:** [Phone number]

**Requestor Manager (if applicable):** [Manager name]
- **Manager Email:** [Email]

**Affected Stakeholders:**
- [Stakeholder 1] - [Role]
- [Stakeholder 2] - [Role]

---

## Exception Details

### What Standard/Process is Being Requested?

**Select the governance area:**
- [ ] Documentation Standards (STANDARDS.md)
- [ ] Operational Processes (PROCESSES.md)
- [ ] Governance Framework (GOVERNANCE.md)
- [ ] Maintenance Schedule (MAINTENANCE.md)
- [ ] Review Requirements
- [ ] Quality Gates
- [ ] Other: ___________________

**Specific Standard/Process:**
[Quote the exact standard or process requirement]

**Governance Reference:**
- Document: [STANDARDS.md / PROCESSES.md / etc.]
- Section: [Section number and name]
- Location: [Page number or link]

### Description of Requested Exception

**What exception are you requesting?**
[Detailed description of what you want to do differently]

**Specific Request:**
- [ ] Waiver from [standard/process]
- [ ] Modification of [standard/process]
- [ ] One-time exception to [standard/process]
- [ ] Permanent exemption from [standard/process]
- [ ] Different timeline for [process]
- [ ] Different approval workflow for [type]

**How would this differ from standard?**

| Item | Standard Requirement | Requested Exception | Difference |
|---|---|---|---|
| [Item 1] | [Standard] | [Exception] | [How different] |
| [Item 2] | [Standard] | [Exception] | [How different] |

---

## Justification

### Why is this exception needed?

**Business Justification:**
[Detailed explanation of why the standard cannot be followed]

**Supporting Context:**
- Affected project: [Project name]
- Affected documentation: [Document names]
- Timeline: [Timeframe for this exception]
- Severity: [ ] Critical [ ] High [ ] Medium [ ] Low

### Rationale for Exception

**Why can't we follow the standard as-is?**

- [ ] Timeline constraints: [Explanation]
- [ ] Resource constraints: [Explanation]
- [ ] Technical constraints: [Explanation]
- [ ] Business requirements: [Explanation]
- [ ] External dependencies: [Explanation]
- [ ] Other: [Explanation]

**Detailed Rationale:**
[Comprehensive explanation of the situation]

### Alternative Approaches Considered

**Have other approaches been evaluated?**

| Approach | Why Not Suitable | Evaluation |
|---|---|---|
| [Approach 1] | [Why not] | [ ] Considered [ ] Rejected |
| [Approach 2] | [Why not] | [ ] Considered [ ] Rejected |
| [Requested Approach] | N/A | [ ] Preferred |

---

## Impact Assessment

### Impact on Documentation Quality

**How might this exception affect documentation quality?**

| Quality Attribute | Expected Impact | Severity | Mitigation |
|---|---|---|---|
| **Accuracy** | [ ] None [ ] Low [ ] Medium [ ] High | [Severity] | [How to mitigate] |
| **Completeness** | [ ] None [ ] Low [ ] Medium [ ] High | [Severity] | [How to mitigate] |
| **Consistency** | [ ] None [ ] Low [ ] Medium [ ] High | [Severity] | [How to mitigate] |
| **Clarity** | [ ] None [ ] Low [ ] Medium [ ] High | [Severity] | [How to mitigate] |
| **LLM Accessibility** | [ ] None [ ] Low [ ] Medium [ ] High | [Severity] | [How to mitigate] |

**Overall Quality Impact:** [ ] Minimal [ ] Minor [ ] Moderate [ ] Significant

### Impact on Governance

**How might this exception affect the governance framework?**

**Governance Impact:**
- [ ] Sets precedent for other exceptions: [Details]
- [ ] Could create inconsistency: [Details]
- [ ] May weaken standards: [Details]
- [ ] Could affect compliance: [Details]
- [ ] No significant governance impact
- [ ] Other: [Details]

**Sustainability:**
- [ ] One-time exception (will not recur)
- [ ] Temporary (until [date])
- [ ] Permanent change to standards
- [ ] May become ongoing: [Details]

### Stakeholder Impact

**Who is affected by this exception?**

| Stakeholder | Impact | Concern | Mitigation |
|---|---|---|---|
| [Stakeholder 1] | [How affected] | [Concern] | [Plan] |
| [Stakeholder 2] | [How affected] | [Concern] | [Plan] |
| [Users] | [How affected] | [Concern] | [Plan] |

**Notification Plan:**
- [ ] Notification to: [Who]
- [ ] When: [Timeline]
- [ ] Method: [Email/Meeting/Other]

---

## Mitigation & Risk Management

### Mitigating Factors

**What measures will ensure quality despite the exception?**

**Quality Assurance Plan:**
- [ ] Enhanced review process: [Details]
- [ ] Additional testing: [Details]
- [ ] Extended review timeline: [Details]
- [ ] Specialized expertise: [Details]
- [ ] Additional sign-offs: [Details]
- [ ] Post-release monitoring: [Details]

**Risk Mitigation:**
- [Mitigation 1]: [How it reduces risk]
- [Mitigation 2]: [How it reduces risk]
- [Mitigation 3]: [How it reduces risk]

### Conditions of Exception

**This exception is granted only if:**

- [ ] [Condition 1]
- [ ] [Condition 2]
- [ ] [Condition 3]
- [ ] [Condition 4]

**Monitoring & Enforcement:**
- Monitoring method: [How will compliance be verified]
- Monitoring frequency: [How often]
- Responsible party: [Who monitors]
- Report schedule: [When reports are due]

### Rollback Plan

**If problems occur, how will we return to standard?**

**Rollback Triggers:**
- [ ] Specific issue occurs: [Description]
- [ ] Quality metric drops below: [Threshold]
- [ ] User complaints reach: [Number]
- [ ] Timeline reaches: [Date]

**Rollback Process:**
1. [Step 1 - Detection]
2. [Step 2 - Notification]
3. [Step 3 - Review]
4. [Step 4 - Correction]

---

## Scope & Duration

### Scope of Exception

**What specific documentation/projects does this apply to?**

**In Scope:**
- [Document 1]
- [Document 2]
- [Project A]
- [Work Area B]

**Out of Scope:**
- [Document 1]
- [Document 2]
- [Project A]

**Scope Boundaries:**
[Clear description of what is and isn't included]

### Duration

**Requested Duration:**
- [ ] One-time exception for: [Specific work]
- [ ] Temporary (expires on): [YYYY-MM-DD]
- [ ] Temporary (until): [Event or milestone]
- [ ] Permanent change to governance
- [ ] Trial period (duration): [Days/weeks/months]

**Timeline:**
- Effective Date: [YYYY-MM-DD]
- Expiration Date: [YYYY-MM-DD]
- Review Date: [YYYY-MM-DD]

**Renewal:**
- [ ] Automatic expiration (no renewal)
- [ ] Manual renewal required: [Process]
- [ ] Renewable until: [Date]

---

## Approval & Review

### Required Approvals

**This exception requires approval from:**

**Type A (Process exception - Content Owner approval):**
- [ ] Content Owner only

**Type B (Standards modification - Governance Council review):**
- [ ] Governance Council (majority vote)

**Type C (Framework change - Executive approval):**
- [ ] Executive sponsor
- [ ] Governance Council

**Approval Status:** [ ] Submitted [ ] Under Review [ ] Approved [ ] Rejected

### Reviewer Assignments

| Reviewer Role | Name | Email | Status |
|---|---|---|---|
| **Content Owner** | [Name] | [Email] | [ ] Received [ ] Reviewing [ ] Approved [ ] Rejected |
| **Council Chair** | [Name] | [Email] | [ ] Received [ ] Reviewing [ ] Approved [ ] Rejected |
| **Product Lead** | [Name] | [Email] | [ ] Received [ ] Reviewing [ ] Approved [ ] Rejected |
| **QA Lead** | [Name] | [Email] | [ ] Received [ ] Reviewing [ ] Approved [ ] Rejected |

### Review Timeline

**Expected Review Schedule:**

| Activity | Deadline | Owner | Status |
|---|---|---|---|
| **Submission Complete** | [Date] | [You] | [ ] Done |
| **Initial Review** | [Date] | [Reviewer] | [ ] Done |
| **Questions/Clarification** | [Date] | [You] | [ ] Done |
| **Council Discussion** | [Date] | Council | [ ] Done |
| **Vote/Decision** | [Date] | Council | [ ] Pending |
| **Notification of Decision** | [Date] | [Owner] | [ ] Pending |

**Target Decision Date:** [YYYY-MM-DD] (within [N] business days of submission)

---

## Supporting Documentation

### Attachments & Evidence

**Supporting documents attached:**
- [ ] [Document 1]: [Description]
- [ ] [Document 2]: [Description]
- [ ] [Email/Chat history]: [Description]
- [ ] [Data/metrics]: [Description]
- [ ] [Other evidence]: [Description]

### References

**Related requests or decisions:**
- [Prior request 1]: [Link/reference]
- [Council decision 1]: [Link/reference]
- [Similar exception 1]: [Link/reference]

**Governance documents referenced:**
- governance/STANDARDS.md
- governance/PROCESSES.md
- governance/GOVERNANCE.md
- governance/MAINTENANCE.md

---

## Requestor Sign-Off

**I have completed this exception request and certify that:**

- [ ] The information provided is accurate and complete
- [ ] I have considered impact on documentation quality
- [ ] I have explored alternative approaches
- [ ] I understand the potential risks
- [ ] I am prepared to implement mitigation measures
- [ ] I have notified affected stakeholders

**Requestor Signature:** ________________________

**Date:** ________________________

**Requestor Name (printed):** ________________________

---

## Manager Approval (if applicable)

**This exception request has been reviewed and approved by my manager:**

**Manager Name:** ________________________

**Manager Signature:** ________________________

**Date:** ________________________

**Manager Email:** ________________________

---

## Review Summary (Completed by Reviewer)

### Initial Reviewer Assessment

**Reviewer:** [Name] - **Role:** [Title]

**Date Received:** [YYYY-MM-DD]

**Initial Assessment:** [ ] Complete & Ready for Review [ ] Needs Clarification [ ] Incomplete

**Questions for Requestor:**
- [Question 1]
- [Question 2]
- [Question 3]

**Response Deadline:** [YYYY-MM-DD]

---

## Governance Council Decision

### Council Review & Discussion

**Council Meeting Date:** [YYYY-MM-DD]

**Council Members Present:**
- [Member 1]: [ ] Yes [ ] No
- [Member 2]: [ ] Yes [ ] No
- [Member 3]: [ ] Yes [ ] No
- [Member 4]: [ ] Yes [ ] No

**Discussion Summary:**
[Summary of council discussion and considerations]

**Questions Raised:**
- [Question 1] - [Response]
- [Question 2] - [Response]

### Council Decision

**Decision:** 
- [ ] **APPROVED** - Exception granted as requested
- [ ] **APPROVED WITH CONDITIONS** - Exception granted with modifications
- [ ] **REJECTED** - Exception not approved
- [ ] **DEFERRED** - Pending additional information

**Conditions (if applicable):**
- [Condition 1]
- [Condition 2]
- [Condition 3]

**Vote Details:**
- Voting members: [Number]
- Voted in favor: [Number]
- Voted against: [Number]
- Abstained: [Number]
- Result: [Passed/Failed]

### Council Approval

**Council Chair:**
- Name: ________________________
- Signature: ________________________
- Date: ________________________

**Council Authority:** [Reference to governance document granting authority]

---

## Decision Communication

### Notification Plan

**Requestor Notification:**
- [ ] Email sent: [Date]
- [ ] Decision explanation: [Date]
- [ ] Next steps provided: [Date]

**Stakeholder Notification:**
- [ ] Content Owner: [Date]
- [ ] Affected teams: [Date]
- [ ] Documentation: [Date]
- [ ] Public announcement: [Date/No]

### Implementation Plan

**If Approved:**

**Implementation Timeline:**
- [ ] Effective immediately
- [ ] Effective on: [Date]
- [ ] Implementation deadline: [Date]

**Implementation Responsibilities:**
- [Responsible party 1]: [Their role]
- [Responsible party 2]: [Their role]

**Success Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

## Tracking & Monitoring

### Exception Status Tracking

**Current Status:** [ ] Active [ ] Completed [ ] Expired [ ] Revoked

**Status History:**

| Date | Status | Notes | Owner |
|---|---|---|---|
| [Date] | [Status] | [Notes] | [Owner] |
| [Date] | [Status] | [Notes] | [Owner] |

### Monitoring Schedule

**Check-In Points:**
- [ ] Mid-point check: [Date]
- [ ] Completion check: [Date]
- [ ] Quarterly review: [Dates]
- [ ] Annual review: [Date]

**Monitoring Responsibilities:**
- Monitor: [Name]
- Report to: [Name]
- Escalation: [Contact]

### Issue Tracking

**Issues encountered:**
- [ ] No issues
- [Issue 1]: [Description] - [Resolution]
- [Issue 2]: [Description] - [Resolution]

---

## Archive & Retention

**Document Location:** [Where this request is filed]

**Retention Period:** [How long to keep]

**Archival Date:** [When archived]

**Reference Links:**
- Related governance updates: [Links]
- Related decision memos: [Links]
- Related policy changes: [Links]

---

## Templates & Forms

### Request Submission Checklist

Before submitting, verify:
- [ ] All required sections completed
- [ ] Justification is clear and compelling
- [ ] Impact assessment is thorough
- [ ] Mitigation plan is realistic
- [ ] Supporting documentation is attached
- [ ] Requestor has signed
- [ ] Manager approval obtained (if required)
- [ ] No sensitive information included inappropriately

### Submission Instructions

1. **Complete all sections** in this template
2. **Attach supporting documentation** as needed
3. **Obtain manager approval** if required
4. **Submit to:** [Governance Council email]
5. **Subject line:** "Governance Exception Request: [Brief Title]"
6. **By deadline:** [Submission deadline date]

### Questions?

- **Process questions:** Contact [Governance Coordinator Email]
- **Content questions:** Contact [Content Owner Email]
- **Technical questions:** Contact [Technical Lead Email]

---

## References & Resources

**Governance Documents:**
- governance/GOVERNANCE.md - Overall framework
- governance/STANDARDS.md - Documentation standards
- governance/PROCESSES.md - Operational processes
- governance/MAINTENANCE.md - Maintenance schedule

**Related Policies:**
- Exception Approval Policy
- Quality Gates Policy
- Review Requirements Policy

---

*This exception request was created on [YYYY-MM-DD] and last updated on [YYYY-MM-DD]*

**Request Version:** 1.0  
**Archival Status:** [ ] Active [ ] Archived [ ] Expired


---

## Source: templates/release-notes-template.md

# Documentation Release Notes Template

Use this template to document documentation releases corresponding to Ante version releases. Create a new file for each documentation release using the naming convention: `RELEASE-NOTES-[VERSION].md`

---

## Header Information

# Documentation Release Notes: v[VERSION]

**Documentation Version:** [VERSION]  
**Release Date:** [YYYY-MM-DD]  
**Ante Version Covered:** [VERSION]  
**Status:** [ ] Draft [ ] Ready for Review [ ] Approved [ ] Published

---

## Executive Summary

[1-2 paragraph summary of major documentation changes in this release]

**Example:**
```
This documentation release accompanies Ante v0.2.0 and includes comprehensive 
documentation for the new context management features, updated CLI reference 
with all v0.2.0 options, and new troubleshooting guides based on user feedback. 
A total of 8 new documents have been added and 12 existing documents have been 
updated. All examples have been tested against v0.2.0.
```

---

## Release Metadata

| Property | Value |
|---|---|
| **Release Version** | v[VERSION] |
| **Documentation Release Date** | [YYYY-MM-DD] |
| **Ante Version** | v[VERSION] |
| **Total Documents** | [Number] |
| **New Documents** | [Number] |
| **Updated Documents** | [Number] |
| **Deprecated Documents** | [Number] |
| **Testing Completion** | [Percentage]% |
| **Review Status** | [ ] In Progress [ ] Complete |

---

## Changes Summary

### Document Statistics

| Category | Count | Details |
|---|---|---|
| **New Documents** | [N] | [Brief list of new docs] |
| **Updated Documents** | [N] | [Major sections updated] |
| **Archived Documents** | [N] | [Moved to archive/] |
| **Deleted Documents** | [N] | [Fully removed] |
| **Modified Sections** | [N] | [Significant rewrites] |
| **Code Examples Updated** | [N] | [Examples retested] |

### Content Changes by Type

#### Type A: Routine Updates (Minor changes, no approval required)
- [ ] Typo fixes and grammar corrections: [Number of documents]
- [ ] Link updates: [Number of links fixed]
- [ ] Formatting improvements: [Number of documents]
- [ ] Example additions: [Number of examples added]

**Documents Affected (Type A):**
- [Document 1]
- [Document 2]
- [Document 3]

#### Type B: Significant Updates (Content Owner approval required)
- [ ] New sections added: [Number of sections]
- [ ] Major rewrites: [Number of documents]
- [ ] Structural reorganization: [Number of documents]
- [ ] Feature documentation added: [Number of new features]

**Documents Affected (Type B):**
- [Document 1] - [Changes made]
- [Document 2] - [Changes made]
- [Document 3] - [Changes made]

**Approvals Obtained:**
- [ ] Content Owner: [Name] - [Date]
- [ ] Technical Lead: [Name] - [Date]
- [ ] QA Lead: [Name] - [Date]

#### Type C: Policy/Structure Changes (Governance Council approval required)
- [ ] Documentation standards updated: [ ] Yes [ ] No
- [ ] Major restructuring: [ ] Yes [ ] No
- [ ] Version numbering changes: [ ] Yes [ ] No

**Type C Changes (if applicable):**
- [Change 1] - [Impact]
- [Change 2] - [Impact]

**Council Approval:**
- [ ] Governance Council approval obtained: [Date]
- [ ] Council members voting: [Names and votes]

---

## Detailed Change Log

### New Documentation

#### [Category/Section Name]

**New Document:** [Document Title]
- **File Path:** `docs/[path]/[document].md`
- **Content:** [Brief description of content]
- **Audience:** [Target audience]
- **Length:** [Approximate word count or sections]
- **Examples Included:** [ ] Yes [ ] No - [Number]
- **Author:** [Author name]
- **Status:** [ ] Draft [ ] Under Review [ ] Approved

**New Document:** [Document Title]
- **File Path:** `docs/[path]/[document].md`
- **Content:** [Brief description of content]
- **Audience:** [Target audience]
- **Length:** [Approximate word count or sections]
- **Examples Included:** [ ] Yes [ ] No - [Number]
- **Author:** [Author name]
- **Status:** [ ] Draft [ ] Under Review [ ] Approved

### Modified Documentation

#### [Category/Section Name]

**Updated Document:** [Document Title]
- **File Path:** `docs/[path]/[document].md`
- **Changes Made:**
  - [Change 1]: [Description]
  - [Change 2]: [Description]
  - [Change 3]: [Description]
- **Reason for Update:** [Why this change was made]
- **Breaking Changes:** [ ] Yes [ ] No
- **User Impact:** [How users are affected]
- **Reviewer:** [Reviewer name]
- **Approval Date:** [Date]

**Updated Document:** [Document Title]
- **File Path:** `docs/[path]/[document].md`
- **Changes Made:**
  - [Change 1]: [Description]
  - [Change 2]: [Description]
- **Reason for Update:** [Why this change was made]
- **Breaking Changes:** [ ] Yes [ ] No
- **User Impact:** [How users are affected]
- **Reviewer:** [Reviewer name]
- **Approval Date:** [Date]

### Deprecated Documentation

**Document:** [Document Title]
- **File Path:** `docs/[path]/[document].md` → `archive/v[old-version]/[document].md`
- **Reason for Deprecation:** [Why deprecated]
- **Replacement Documentation:** [Link to replacement]
- **Archive Location:** `archive/v[version]/`
- **Migration Guide:** [Link if available]
- **Deprecation Date:** [Date moved to archive]

---

## Feature Documentation

This section documents what Ante features are covered and their documentation status.

### New Features Documented

**Feature:** [Feature Name]
- **Ante Version:** [Introduced in version]
- **Documentation Added:** [ ] Comprehensive [ ] Basic [ ] Reference Only
- **Sections Created:**
  - Overview
  - Configuration/Usage
  - Examples
  - Advanced Usage
  - Troubleshooting
- **Code Examples:** [Number of examples]
- **Test Status:** [ ] Fully Tested [ ] Partially Tested
- **Reviewer:** [Name]

**Feature:** [Feature Name]
- **Ante Version:** [Introduced in version]
- **Documentation Added:** [ ] Comprehensive [ ] Basic [ ] Reference Only
- **Sections Created:**
  - [Section 1]
  - [Section 2]
- **Code Examples:** [Number of examples]
- **Test Status:** [ ] Fully Tested [ ] Partially Tested
- **Reviewer:** [Name]

### Updated Feature Documentation

**Feature:** [Feature Name]
- **Documentation Status:** Updated for Ante v[version]
- **Changes Made:** [Description of updates]
- **Breaking Changes Documented:** [ ] Yes [ ] No
- **Examples Updated:** [Number of examples]
- **Test Status:** [ ] Fully Tested [ ] Spot-checked

**Feature:** [Feature Name]
- **Documentation Status:** Updated for Ante v[version]
- **Changes Made:** [Description of updates]
- **Breaking Changes Documented:** [ ] Yes [ ] No
- **Examples Updated:** [Number of examples]
- **Test Status:** [ ] Fully Tested [ ] Spot-checked

### Undocumented Features

**Features still awaiting documentation:**
- [Feature 1] - [Status/planned date]
- [Feature 2] - [Status/planned date]

---

## Breaking Changes & Migration

### Breaking Changes Documentation

**Breaking Change:** [Description]
- **Ante Version:** [Version where change occurred]
- **Affected Documentation:** [Documents updated]
- **Migration Guide:** [ ] Yes [ ] No - [Link if yes]
- **User Action Required:** [What users need to do]
- **Transition Timeline:** [Timeline for migration]

**Breaking Change:** [Description]
- **Ante Version:** [Version where change occurred]
- **Affected Documentation:** [Documents updated]
- **Migration Guide:** [ ] Yes [ ] No - [Link if yes]
- **User Action Required:** [What users need to do]
- **Transition Timeline:** [Timeline for migration]

### Migration Guides Created

- [ ] Migration Guide for v[VERSION]
  - **File Path:** `docs/[path]/migration-v[version].md`
  - **Topics Covered:** [Topics]
  - **Examples Provided:** [ ] Yes [ ] No
  - **Author:** [Name]
  - **Test Status:** [ ] Verified

---

## Quality Assurance

### Testing Summary

**Overall Test Status:** [Percentage]% complete

**Testing Performed:**
- [ ] Code example execution: [Number of examples] tested
- [ ] Link validation: [Number of links] verified
- [ ] Cross-reference validation: [Number of references] verified
- [ ] Consistency checks: [Coverage]
- [ ] Accuracy validation: Tested against Ante v[version]
- [ ] LLM accessibility testing: [ ] Yes [ ] No

### Test Results by Category

| Category | Tests Completed | Pass Rate | Issues Found |
|---|---|---|---|
| Code Examples | [N] | [%] | [N] |
| Links | [N] | [%] | [N] |
| Formatting | [N] | [%] | [N] |
| Accuracy | [N] | [%] | [N] |
| Cross-references | [N] | [%] | [N] |

### Critical Issues Found & Resolved

**Pre-Release Issues (all resolved):**
- [ ] No critical issues found
- [ ] [Issue 1]: [Description] - Status: [ ] RESOLVED [ ] BLOCKED
- [ ] [Issue 2]: [Description] - Status: [ ] RESOLVED [ ] BLOCKED

**Known Issues (if any remain):**
- [ ] No known issues
- [ ] [Issue 1]: [Description] - Severity: [ ] High [ ] Medium

### QA Approval

- [ ] QA Lead Sign-Off: [Name] - Date: [YYYY-MM-DD]
- [ ] Release Approved for Publication: [ ] Yes [ ] No

---

## Content Review Status

### Review Assignments

| Reviewer Role | Name | Status | Review Date |
|---|---|---|---|
| Technical Lead | [Name] | [ ] Complete [ ] In Progress [ ] Pending | [Date] |
| QA Lead | [Name] | [ ] Complete [ ] In Progress [ ] Pending | [Date] |
| LLM Specialist | [Name] | [ ] Complete [ ] In Progress [ ] Pending | [Date] |
| Content Owner | [Name] | [ ] Complete [ ] In Progress [ ] Pending | [Date] |

### Review Feedback Summary

**Technical Review:** [Summary of findings]
- Issues found: [Number]
- Issues resolved: [Number]

**QA Review:** [Summary of findings]
- Issues found: [Number]
- Issues resolved: [Number]

**LLM Accessibility Review:** [Summary of findings]
- Issues found: [Number]
- Issues resolved: [Number]

---

## Integration with Ante Release

### Release Coordination

| Item | Status | Details |
|---|---|---|
| **Ante v[VERSION] Release Date** | [Date] | [Link to release] |
| **Documentation Ready Date** | [Date] | [Ready X days before release] |
| **Merge to Main** | [ ] Yes [ ] Pending | [Date/Scheduled] |
| **Publishing** | [ ] Complete [ ] Pending | [Date] |
| **llms.txt Updated** | [ ] Yes [ ] No | [Date if yes] |
| **Change Notification Sent** | [ ] Yes [ ] No | [Date if yes] |

### Related Releases

**Previous Documentation Release:**
- Version: [Version]
- Release Date: [Date]
- Link: [Link to release notes]

**Next Planned Release:**
- Planned Version: [Version]
- Planned Date: [Date]
- Status: [Planned/In Development]

---

## Updates to llms.txt Context File

**Changes Made to llms.txt:**
- [ ] New content added: [Summary]
- [ ] Content updated: [Summary]
- [ ] Content removed: [Summary]
- [ ] Structure reorganized: [ ] Yes [ ] No

**llms.txt Update Date:** [Date]

**Testing:** [ ] LLM tested with updated context [ ] Pending

---

## Authors & Contributors

### Primary Contributors

| Name | Role | Contribution | Hours |
|---|---|---|---|
| [Author 1] | Primary Author | [Topics/docs written] | [Hours] |
| [Author 2] | Contributor | [Topics/docs written] | [Hours] |
| [Reviewer 1] | Technical Reviewer | [Review provided] | [Hours] |
| [Reviewer 2] | QA Reviewer | [Review provided] | [Hours] |

### Acknowledgments

[Any special thanks or acknowledgments]

---

## Release Notes for Users

### What's New in the Documentation

**For this Ante v[VERSION] release:**

- **[Number] new guides** covering [features/topics]
- **[Number] updated sections** reflecting v[VERSION] changes
- **[Number] new code examples** added for common use cases
- **[Number] fixes** to outdated information and broken links

### Documentation Improvements

**What we improved:**
- Better organization of [topic area]
- New troubleshooting section for [common issues]
- Expanded examples for [feature area]
- Clarified [complex concept]
- Added [new resource type]

### For New Users

Start with these new documentation resources:
- [New Quick Start Guide] - Get up and running in [minutes]
- [New Installation Guide] - Complete setup instructions
- [New Tutorials] - Learn [key features] by example

### For Experienced Users

Upgrade guidance:
- [Migration Guide] - Guide for upgrading from v[prev] to v[current]
- [What's New] - Overview of v[current] feature additions
- [Breaking Changes] - Important changes to be aware of

---

## Feedback & Issues

### How to Report Issues

Found an error in the documentation?

- **Report via:** [Issue tracker/GitHub/Email]
- **Include:** [What to include in bug report]
- **Response time:** [Expected response time]

### Feedback Channels

- Email: [Support email]
- GitHub Issues: [Link to issues]
- Slack Channel: [Channel name]
- Community Forum: [Link if applicable]

---

## Approval & Sign-Off

### Review Sign-Offs

**Content Owner:**
- Name: ________________________
- Signature: ________________________
- Date: ________________________

**Technical Lead:**
- Name: ________________________
- Signature: ________________________
- Date: ________________________

**QA Lead:**
- Name: ________________________
- Signature: ________________________
- Date: ________________________

### Release Authorization

This documentation release is:

- [ ] **APPROVED** for publication
- [ ] **APPROVED WITH CONDITIONS** - [Conditions:]
- [ ] **REJECTED** - [Reason:]

**Final Authorization:**
- Name: ________________________ (Release Manager)
- Signature: ________________________
- Date: ________________________
- Time: ________________________

---

## Archive & Version Control

**Repository Location:** [Full path in repo]

**Tag:** `docs/v[VERSION]`

**Previous Release:** v[PREV-VERSION] - [Link or date]

**Next Planned Release:** v[NEXT-VERSION] - [Planned date]

---

## Post-Release Tasks

### Immediate Post-Release (Within 1 week)

- [ ] Monitor for user questions about new documentation
- [ ] Collect initial feedback
- [ ] Fix critical issues if found
- [ ] Verify examples work for users
- [ ] Update llms.txt if needed based on feedback

### Short-term (Within 1 month)

- [ ] Analyze documentation usage metrics
- [ ] Identify common questions
- [ ] Plan clarifications based on feedback
- [ ] Update troubleshooting based on user reports
- [ ] Address any reported inaccuracies

### Ongoing

- [ ] Monitor documentation issues on GitHub
- [ ] Track documentation improvement requests
- [ ] Plan next release content
- [ ] Maintain accuracy as Ante evolves

---

## Additional Resources

- **Documentation Standards:** governance/STANDARDS.md
- **Processes & Procedures:** governance/PROCESSES.md
- **Governance Framework:** governance/GOVERNANCE.md
- **Maintenance Schedule:** governance/MAINTENANCE.md

---

## Change Log

| Date | Version | Change | Author |
|---|---|---|---|
| [Date] | [Version] | [Change made] | [Author] |
| [Date] | [Version] | [Change made] | [Author] |

---

*This release notes document was created on [YYYY-MM-DD] and last updated on [YYYY-MM-DD]*


---

## Source: templates/technical-review-checklist.md

# Technical Review Checklist

Use this checklist when performing technical review of documentation submissions. Reviewers should verify all items and provide detailed feedback where items are not met.

---

## Review Information

**Document Under Review:** [Title]

**Submission ID:** [ID from submission]

**Reviewer Name:** [Full name]

**Reviewer Role:** [Technical Reviewer / QA Reviewer / LLM Specialist]

**Review Date:** [YYYY-MM-DD]

**Review Version:** [Ante version being reviewed against]

---

## SECTION 1: Accuracy Verification

This section verifies that the documented information accurately reflects the actual behavior of Ante.

### Feature/Behavior Accuracy

**Tested Against:** Ante [version]

**Testing Method:**
- [ ] Manual testing against running instance
- [ ] Code review against source
- [ ] Testing against pre-release version
- [ ] Testing against stable release
- [ ] Testing against [version]:

**Test Results:**

| Feature/Command | Documented Behavior | Actual Behavior | Match? | Notes |
|---|---|---|---|---|
| [Feature 1] | [Description] | [Actual output] | [ ] Yes [ ] No | [Any issues] |
| [Feature 2] | [Description] | [Actual output] | [ ] Yes [ ] No | [Any issues] |
| [Feature 3] | [Description] | [Actual output] | [ ] Yes [ ] No | [Any issues] |

**Test Environment Details:**
- OS: [Operating system]
- Ante Version: [Version]
- Prerequisites met: [ ] Yes [ ] No
- Special configuration: [Any special setup]

### Code Examples Validation

**Code Example Testing:**

- [ ] All code examples have been extracted and executed
- [ ] Examples run without errors
- [ ] Example output matches documented output
- [ ] Examples work with stated prerequisites
- [ ] Command-line flags work as documented
- [ ] Output formatting matches documentation claims

**Code Example Test Log:**

```
Example 1: [Example name/reference]
  Status: [ ] PASS [ ] FAIL
  Command used: [command]
  Expected output: [expected]
  Actual output: [actual]
  Notes: [any issues]

Example 2: [Example name/reference]
  Status: [ ] PASS [ ] FAIL
  Command used: [command]
  Expected output: [expected]
  Actual output: [actual]
  Notes: [any issues]
```

**Code Example Issues Found:**
- [ ] No issues
- [ ] [Issue 1]: Severity: [ ] Critical [ ] High [ ] Medium [ ] Low
- [ ] [Issue 2]: Severity: [ ] Critical [ ] High [ ] Medium [ ] Low

### API/Command Signature Accuracy

For documentation of APIs, commands, or functions:

- [ ] All parameters/arguments are listed
- [ ] Parameter types are correct
- [ ] Default values are accurate
- [ ] Required vs. optional parameters are correctly marked
- [ ] Parameter order is correct
- [ ] No parameters are missing
- [ ] No deprecated parameters without notices
- [ ] Return types/values are correct
- [ ] Error conditions are accurately described
- [ ] Error messages match actual output

**Parameter Verification Table:**

| Parameter | Type | Required? | Default | Documented | Accurate? | Notes |
|---|---|---|---|---|---|---|
| [param1] | [type] | [Y/N] | [default] | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| [param2] | [type] | [Y/N] | [default] | [ ] Yes [ ] No | [ ] Yes [ ] No | |

### Version Compatibility

- [ ] Version information is accurate for Ante [version]
- [ ] "New in version X" statements are correct
- [ ] "Deprecated in version X" statements are correct
- [ ] Compatibility notes are accurate
- [ ] Breaking changes are correctly noted
- [ ] Version-specific behavior is clearly marked
- [ ] No forward references to unreleased features without warnings

**Version Compatibility Details:**
- Feature introduced in: [version]
- Last tested in: [version]
- Known issues in versions: [versions]
- Deprecated in version: [version/N/A]

### Deprecated Features

For any documented deprecated features:

- [ ] Deprecation is clearly marked
- [ ] Deprecation timeline is provided
- [ ] Replacement/alternative is documented
- [ ] Migration path is explained
- [ ] Version where feature was deprecated is stated
- [ ] Links to migration guides are provided

---

## SECTION 2: Completeness Assessment

This section verifies that the documentation covers all necessary information for the scope.

### Feature Coverage

For documentation claiming to cover specific features:

- [ ] All claimed features are actually documented
- [ ] No claimed features are missing
- [ ] Feature descriptions are complete
- [ ] All options/parameters are listed
- [ ] All use cases are covered
- [ ] Edge cases are mentioned

**Scope Verification:**

Claimed scope:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Verification:
- [ ] Feature 1 is fully documented
- [ ] Feature 2 is fully documented
- [ ] Feature 3 is fully documented
- [ ] No additional undocumented features found

### Content Completeness

- [ ] Opening section explains purpose clearly
- [ ] Prerequisites are listed upfront
- [ ] Main content covers primary use cases
- [ ] Advanced/uncommon use cases are explained
- [ ] Limitations and constraints are documented
- [ ] Edge cases are addressed
- [ ] Error handling/troubleshooting is included
- [ ] No sections are marked "TODO" or "TBD"
- [ ] No incomplete sentence fragments
- [ ] Conclusion/summary is provided

**Missing Content Identified:**

- [ ] No major gaps identified
- [Gap 1]: [Description of missing content]
- [Gap 2]: [Description of missing content]

### Examples & Demonstrations

**Example Coverage:**

- [ ] At least one example for each major feature
- [ ] Examples demonstrate primary use cases
- [ ] Examples show common patterns
- [ ] Advanced examples are included
- [ ] Error cases are demonstrated
- [ ] Output examples are provided

**Example Assessment:**

| Scenario | Example Provided? | Adequate? | Notes |
|---|---|---|---|
| Basic usage | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| Common use case 1 | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| Common use case 2 | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| Advanced usage | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| Error handling | [ ] Yes [ ] No | [ ] Yes [ ] No | |

### Cross-References & Related Information

- [ ] Related documentation is referenced
- [ ] "See Also" sections are present
- [ ] Links to related content are complete
- [ ] No orphaned content (no clear how to navigate to/from)
- [ ] Cross-references in other documents link back
- [ ] Related features are mentioned

**Cross-Reference Verification:**

Claimed related documents:
- [Doc 1]: [ ] Link verified [ ] Doc exists
- [Doc 2]: [ ] Link verified [ ] Doc exists
- [Doc 3]: [ ] Link verified [ ] Doc exists

---

## SECTION 3: Code Example Validation

This section details testing of code examples and technical demonstrations.

### Code Example Testing Protocol

**Test Environment Setup:**
- [ ] Ante version [X.Y.Z] installed
- [ ] Prerequisites for examples met
- [ ] Clean/consistent test environment
- [ ] No conflicting configurations

### Code Block Specifications

For all code blocks:

- [ ] Language is specified (e.g., ```bash, ```python)
- [ ] All output examples are marked as such
- [ ] Syntax highlighting is appropriate
- [ ] Long lines are properly formatted
- [ ] Comments are clear and helpful

**Code Block Format Issues Found:**

- [ ] No formatting issues
- [Issue]: [Description]

### Example Executability

- [ ] Can examples be copy-pasted and executed?
- [ ] Do examples include all necessary imports/setup?
- [ ] Are prerequisites clearly stated?
- [ ] Do examples assume correct default state?
- [ ] Are file paths relative or absolute?
- [ ] Would examples work for a new user?

### Output Verification

For examples with expected output:

- [ ] Output is accurately shown
- [ ] Output format matches actual output
- [ ] Line breaks and spacing are correct
- [ ] Optional output lines are marked
- [ ] Output varies by circumstances is noted
- [ ] Explanatory notes for output are provided

**Output Test Results:**

| Example | Expected Output | Actual Output | Match? | Notes |
|---|---|---|---|---|
| [Example 1] | [Expected] | [Actual] | [ ] Yes [ ] No | |
| [Example 2] | [Expected] | [Actual] | [ ] Yes [ ] No | |
| [Example 3] | [Expected] | [Actual] | [ ] Yes [ ] No | |

### Error Case Examples

- [ ] Error conditions are demonstrated (if applicable)
- [ ] Error messages shown are accurate
- [ ] Explanations for errors are clear
- [ ] Solutions/workarounds are provided
- [ ] Error recovery is explained

---

## SECTION 4: Link & Reference Validation

This section verifies all links and references are correct and functional.

### Link Testing

**Internal Links (relative paths):**

| Link | Target File | Exists? | Correct? | Notes |
|---|---|---|---|---|
| [Link 1] | [Target] | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| [Link 2] | [Target] | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| [Link 3] | [Target] | [ ] Yes [ ] No | [ ] Yes [ ] No | |

- [ ] All internal links use relative paths
- [ ] No absolute paths or URLs for internal content
- [ ] Links point to correct sections
- [ ] Link text is descriptive

**External Links:**

| URL | Status | Current? | Notes |
|---|---|---|---|
| [URL 1] | [ ] 200 [ ] 404 [ ] Other | [ ] Yes [ ] No | |
| [URL 2] | [ ] 200 [ ] 404 [ ] Other | [ ] Yes [ ] No | |

- [ ] All external links are accessible
- [ ] External links are appropriate and relevant
- [ ] HTTPS is used where available
- [ ] Links are from authoritative sources

**Broken/Invalid Links Found:**

- [ ] No broken links
- [Link 1]: [Issues]
- [Link 2]: [Issues]

### Reference Accuracy

- [ ] All citations are accurate
- [ ] Version numbers in references are correct
- [ ] Feature names match current naming
- [ ] Command names match current syntax
- [ ] Configuration parameters use current names
- [ ] File paths are current and accurate

### Documentation Cross-References

- [ ] Links to STANDARDS.md are appropriate
- [ ] Links to PROCESSES.md are appropriate
- [ ] Links to governance documents are accurate
- [ ] Related documentation references are complete
- [ ] Backward links in related docs are present

---

## SECTION 5: Standards Compliance

This section verifies compliance with documentation standards.

### Terminology Standards

**Reference:** governance/STANDARDS.md - Terminology section

- [ ] Terminology is consistent with standards
- [ ] Technical terms are used correctly
- [ ] Product names are capitalized correctly
- [ ] Abbreviations are spelled out on first use
- [ ] Terminology is consistent throughout document
- [ ] No invented or non-standard terminology

**Terminology Issues Found:**

- [ ] No issues
- [Term 1]: [Issue]
- [Term 2]: [Issue]

### Style & Tone

**Reference:** governance/STANDARDS.md - Style Guide

- [ ] Tone is technical and objective
- [ ] Language is clear and concise
- [ ] Sentences are appropriately structured
- [ ] Paragraphs are focused on single topics
- [ ] Active voice is preferred over passive
- [ ] No unnecessary jargon

### Markdown Formatting

- [ ] Markdown syntax is valid
- [ ] Heading hierarchy is correct (no skipped levels)
- [ ] Lists use consistent formatting
- [ ] Emphasis (bold/italic) is used appropriately
- [ ] Tables are properly formatted
- [ ] Code blocks have language specified

**Formatting Issues Found:**

- [ ] No formatting issues
- [Issue 1]: [Description]
- [Issue 2]: [Description]

### Document Structure

**Reference:** governance/STANDARDS.md - Document Structure

- [ ] Document follows expected structure
- [ ] All required sections are present
- [ ] Section order is logical
- [ ] Content flows well between sections
- [ ] Appropriate use of subsections
- [ ] No missing or incomplete sections

### Metadata Compliance

- [ ] YAML front matter is present and valid
- [ ] Required metadata fields are populated:
  - [ ] `title:`
  - [ ] `description:`
  - [ ] `audience:`
  - [ ] `version:`
  - [ ] `updated:`
  - [ ] `author:`
- [ ] Metadata values are accurate
- [ ] No placeholder metadata values

---

## SECTION 6: Consistency Assessment

This section verifies consistency with related documentation and standards.

### Consistency with Related Documentation

**Related Documents Reviewed:**

- [Related doc 1]: [ ] Consistent [ ] Inconsistent
  - Issue: [Any inconsistencies found]
- [Related doc 2]: [ ] Consistent [ ] Inconsistent
  - Issue: [Any inconsistencies found]

**Consistency Check Items:**

- [ ] Terminology matches related documentation
- [ ] Examples follow same patterns as similar docs
- [ ] Code style matches related examples
- [ ] Version information is consistent
- [ ] Feature descriptions don't contradict
- [ ] No duplicate content with other docs

### Consistency with Standards

- [ ] Document structure matches STANDARDS.md
- [ ] Terminology matches STANDARDS.md
- [ ] Code formatting matches STANDARDS.md
- [ ] Metadata format matches STANDARDS.md
- [ ] Example style matches STANDARDS.md
- [ ] Link formatting matches STANDARDS.md

### Internal Consistency

Within this document:

- [ ] Terminology is consistent throughout
- [ ] Examples follow consistent patterns
- [ ] Code style is consistent
- [ ] Formatting is consistent
- [ ] No contradictory statements
- [ ] Assumptions are consistent

---

## SECTION 7: Accessibility for LLMs

This section verifies the documentation is well-structured for LLM understanding.

### Content Structure for LLM Parsing

- [ ] Clear, descriptive headings
- [ ] Logical sectioning and hierarchy
- [ ] Self-contained explanations (minimal cross-document dependencies)
- [ ] Explicit relationships between concepts
- [ ] Clear examples with expected outputs
- [ ] Structured lists rather than prose lists

### Information Completeness for LLMs

- [ ] All prerequisites are explicitly stated
- [ ] All assumptions are stated
- [ ] Technical terms are defined or explained
- [ ] Context is provided for features
- [ ] Relationships to other features are explained
- [ ] Error conditions are explicitly listed

### Example Quality for LLMs

- [ ] Examples are self-contained
- [ ] Examples have complete command invocation
- [ ] Examples show complete output
- [ ] Input/output are clearly separated
- [ ] Variables in examples are clearly marked
- [ ] Placeholders are clearly indicated

### Potential LLM Confusion Points

**Areas that may be difficult for LLM understanding:**

- [Area 1]: [Potential confusion and how to improve]
- [Area 2]: [Potential confusion and how to improve]

**Improvements suggested:**

- [Improvement 1]: [Description and location]
- [Improvement 2]: [Description and location]

---

## Summary & Overall Assessment

### Issues Found by Severity

**Critical Issues** (Prevent publication):
- [ ] No critical issues
- [ ] [Issue 1]: [Description]
- [ ] [Issue 2]: [Description]

**High Priority Issues** (Should be fixed):
- [ ] No high priority issues
- [ ] [Issue 1]: [Description]
- [ ] [Issue 2]: [Description]

**Medium Priority Issues** (Should be considered):
- [ ] No medium priority issues
- [ ] [Issue 1]: [Description]
- [ ] [Issue 2]: [Description]

**Low Priority Issues** (Nice to have):
- [ ] No low priority issues
- [ ] [Issue 1]: [Description]

### Overall Quality Assessment

**Quality Score:** [ ] Excellent [ ] Good [ ] Acceptable [ ] Needs Revision [ ] Reject

**Strengths:**
- [Strength 1]
- [Strength 2]
- [Strength 3]

**Areas for Improvement:**
- [Area 1]
- [Area 2]

### Recommendation

- [ ] **APPROVE** - Ready for publication
- [ ] **APPROVE WITH MINOR REVISIONS** - Approve after addressing low-priority issues
- [ ] **REQUEST REVISIONS** - Address high-priority issues before approval
- [ ] **REJECT** - Critical issues prevent publication

**Required Actions Before Approval:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

---

## Reviewer Sign-Off

**I have completed a thorough technical review of this documentation and verify that:**

- [ ] I tested code examples against the stated Ante version
- [ ] I verified all links and references
- [ ] I checked consistency with related documentation
- [ ] I assessed accuracy against actual feature behavior
- [ ] I verified completeness of content
- [ ] I reviewed all required sections
- [ ] My findings are documented above

**Reviewer Name:** ________________________

**Reviewer Signature:** ________________________

**Review Date:** ________________________

**Next Reviewer (if applicable):** ________________________

---

## Review Feedback for Author

### Summary for Author

[Brief summary of findings and next steps]

### Detailed Feedback

[Detailed comments organized by section]

### Questions for Author

[Any clarifying questions or requests for more information]

### Suggested Improvements

[Specific, actionable suggestions for improvement]

---

## File Location & Management

**Document File Location:** [Path in repository]

**Review Status:** [ ] In Progress [ ] Complete [ ] Requires Revision

**Review Version:** [Version number or date]

**Next Review:** [Date if scheduled for future review]

**Archive Location:** [Where this review will be filed]


---

Copied count: 11