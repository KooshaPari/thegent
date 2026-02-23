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
