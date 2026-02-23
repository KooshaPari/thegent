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
