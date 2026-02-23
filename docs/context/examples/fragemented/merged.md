# Merged Fragmented Markdown

## Source: docs/context/examples

## Source: governance-adoption-guide.md

# Governance Adoption Guide

## Phase 1: Understanding (Days 1-3)

### Day 1: Governance Framework Overview
- [ ] Review `docs/context/governance/README.md`
- [ ] Understand three pillars: Documentation, Approval, Operations
- [ ] Read governance policy document
- [ ] Review decision matrix for approval flows

**Checklist**:
- [ ] All team leads understand framework
- [ ] Key stakeholders identified
- [ ] Approval authority levels clarified

**Time**: 2-4 hours per person

---

### Day 2: Process and Workflow
- [ ] Study approval workflows in governance docs
- [ ] Review existing documentation standards
- [ ] Understand role definitions (author, reviewer, approver)
- [ ] Map current team to governance roles

**Checklist**:
- [ ] Roles and responsibilities documented
- [ ] Workflow diagram reviewed
- [ ] Questions logged for clarification

**Time**: 2-3 hours per person

---

### Day 3: Tools and Systems
- [ ] Explore governance tools (wiki, llms.txt, templates)
- [ ] Review template library
- [ ] Understand tracking mechanisms
- [ ] Set up team communication channel

**Checklist**:
- [ ] Tools access verified
- [ ] Templates reviewed
- [ ] Communication channel established
- [ ] Initial readiness assessment

**Time**: 1-2 hours per person

---

## Phase 2: Implementation (Days 4-10)

### Days 4-5: Onboarding

**Setup**:
- [ ] Create governance team repository/workspace
- [ ] Set up approval workflow tracking system
- [ ] Configure notification system
- [ ] Create team wiki space (if applicable)

**Training**:
- [ ] Conduct workflow walkthrough
- [ ] Demonstrate approval process
- [ ] Practice with sample documentation
- [ ] Address team questions

**Checklist**:
- [ ] All systems configured
- [ ] Team trained on workflows
- [ ] Support channel established

**Time**: 4-6 hours setup + 2 hours training

---

### Days 6-7: Process Refinement

**Review Current State**:
- [ ] Audit existing documentation
- [ ] Identify documentation gaps
- [ ] Map current approval flows
- [ ] Document exceptions and special cases

**Define Standards**:
- [ ] Document naming conventions
- [ ] Create style guide for docs
- [ ] Define approval criteria checklist
- [ ] Set timeline expectations

**Checklist**:
- [ ] Standards documented
- [ ] Style guide approved
- [ ] Checklist templates created
- [ ] Team consensus on standards

**Time**: 3-4 hours per day

---

### Days 8-10: Pilot Program

**Select Pilot Use Cases**:
- [ ] Choose 2-3 representative documentation requests
- [ ] Assign pilot team members
- [ ] Establish success metrics

**Run Pilots**:
- [ ] Execute full governance workflow
- [ ] Document issues and learnings
- [ ] Collect team feedback
- [ ] Measure timeline vs. expectations

**Checklist**:
- [ ] 2-3 successful pilot runs completed
- [ ] Issues documented
- [ ] Feedback collected
- [ ] Adjustments planned

**Time**: 2-3 hours daily

---

## Phase 3: Operationalization (Weeks 2-4)

### Week 2: Full Rollout

**Day 1-2: Final Adjustments**
- [ ] Incorporate pilot learnings
- [ ] Update procedures and templates
- [ ] Brief team on changes
- [ ] Establish escalation process

**Day 3-4: Soft Launch**
- [ ] Begin processing requests through governance
- [ ] Monitor for issues
- [ ] Support team members
- [ ] Track metrics

**Day 5: Formal Launch**
- [ ] Announce full governance adoption
- [ ] Communicate timelines
- [ ] Establish support office hours

**Checklist**:
- [ ] All adjustments completed
- [ ] Team trained on final process
- [ ] Metrics tracking started
- [ ] Communication sent

---

### Weeks 3-4: Steady State

**Operational Tasks**:
- [ ] Process documentation requests daily
- [ ] Review approval metrics weekly
- [ ] Conduct team sync (weekly or bi-weekly)
- [ ] Monitor compliance and quality
- [ ] Support team members

**Quality Gates**:
- [ ] All documentation reviewed
- [ ] All documentation approved before release
- [ ] Style guide compliance > 95%
- [ ] Average approval time within target

**Checklist**:
- [ ] Daily request processing
- [ ] Weekly metrics review
- [ ] Team support ongoing
- [ ] Quality standards met

---

## Phase 4: Optimization (Ongoing)

### Monthly Reviews
- [ ] Analyze approval time trends
- [ ] Review documentation quality
- [ ] Assess team satisfaction
- [ ] Identify automation opportunities

**Metrics to Track**:
- [ ] Approval cycle time (target: < 2 business days)
- [ ] Documentation quality score
- [ ] Team adoption rate
- [ ] Issue/escalation frequency
- [ ] Rework/revision rate

**Optimization Tasks**:
- [ ] Streamline bottleneck processes
- [ ] Enhance templates based on learnings
- [ ] Automate routine checks
- [ ] Update governance docs

---

## Team Role Assignments

### Phase 1 (Understanding)
- **Governance Lead**: Facilitate learning, answer questions
- **All Team Members**: Attend sessions, ask questions
- **Manager**: Ensure attendance, clear calendars

### Phase 2 (Implementation)
- **Governance Lead**: Coordinate setup, deliver training
- **Process Owner**: Define standards, create templates
- **Tool Administrator**: Configure systems, manage access
- **Team Members**: Attend training, participate in pilots

### Phase 3 (Operationalization)
- **Governance Lead**: Oversee rollout, manage escalations
- **Daily Processor**: Handle incoming requests
- **Approver(s)**: Review and approve documentation
- **Quality Reviewer**: Monitor compliance
- **Team Members**: Submit requests through process

### Phase 4 (Optimization)
- **Governance Lead**: Drive improvements, analyze metrics
- **Process Owner**: Update procedures
- **Tool Administrator**: Implement automation
- **Team Members**: Provide feedback

---

## Success Metrics

### Understanding Phase
- [ ] 100% team understanding (quiz/evaluation)
- [ ] All questions answered
- [ ] No confusion on roles

### Implementation Phase
- [ ] Systems fully operational
- [ ] Team trained (100% attendance)
- [ ] Pilot completion: 3/3 successful
- [ ] Feedback incorporated

### Operationalization Phase
- [ ] Approval cycle < 2 business days
- [ ] Quality score > 85%
- [ ] Team adoption > 90%
- [ ] Zero escalations due to unclear process

### Optimization Phase
- [ ] Approval cycle < 1 business day (Month 2+)
- [ ] Quality score > 95% (Month 3+)
- [ ] Automation > 50% of routine checks
- [ ] Team satisfaction > 4/5

---

## Common Issues and Solutions

| Issue | Solution | When |
|-------|----------|------|
| Slow approvals | Add parallel approval track | Week 2 |
| Unclear criteria | Refine checklist | Week 2 |
| Tool issues | Implement workaround or alternate tool | ASAP |
| Team resistance | Show pilot successes, adjust as needed | Week 2 |
| Quality problems | Add review step or training | Week 3 |
| Bottlenecks | Identify and parallelize | Week 4 |

---

## Support Resources

- **Documentation**: See `docs/context/governance/`
- **Templates**: `docs/context/governance/templates/`
- **Workflows**: `docs/context/governance/workflows/`
- **Escalation**: Contact governance-lead@[organization]
- **Questions**: Post to #governance-questions Slack channel

---

## Sign-Off

- [ ] Governance Lead: _________________ Date: _______
- [ ] Team Manager: _________________ Date: _______
- [ ] Process Owner: _________________ Date: _______

Adoption Target: Complete by end of Week 4


---

## Source: llms-txt-integration-examples.md

# llms.txt Integration Examples

## Example 1: Claude System Prompt

```python
import anthropic
with open("docs/context/llms.txt") as f:
    context = f.read()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=f"You are an Ante expert.\n\n{context}",
    messages=[{"role": "user", "content": "How do I create a skill?"}]
)
print(response.content[0].text)
```

## Example 2: LangChain RAG

```python
from langchain.chat_models import ChatAnthropic
from langchain.schema import SystemMessage, HumanMessage

with open("docs/context/llms.txt") as f:
    docs = f.read()

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
messages = [
    SystemMessage(content=f"Ante expert using docs:\n{docs}"),
    HumanMessage(content="What tools are available?")
]
print(llm(messages).content)
```

## Example 3: Fine-tuning Training Data

```python
def generate_training_examples(llms_txt):
    examples = []
    for section in parse_sections(llms_txt):
        examples.append({
            "messages": [
                {"role": "system", "content": "Ante expert"},
                {"role": "user", "content": f"Explain {section['title']}"},
                {"role": "assistant", "content": section['content']}
            ]
        })
    return examples

# Save as JSONL for fine-tuning
with open("docs/context/llms.txt") as f:
    examples = generate_training_examples(f.read())
# Upload to OpenAI for fine-tuning
```

## Example 4: Multi-turn Conversation

```python
class AnteAssistant:
    def __init__(self, llms_txt_path):
        with open(llms_txt_path) as f:
            self.docs = f.read()
        self.history = []
    
    def chat(self, msg):
        self.history.append({"role": "user", "content": msg})
        response = anthropic.Anthropic().messages.create(
            model="claude-3-5-sonnet-20241022",
            system=f"Ante expert:\n{self.docs}",
            messages=self.history
        )
        ans = response.content[0].text
        self.history.append({"role": "assistant", "content": ans})
        return ans

assistant = AnteAssistant("docs/context/llms.txt")
print(assistant.chat("What is Ante?"))
print(assistant.chat("How do I install it?"))
```

## Example 5: Vector RAG System

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatAnthropic
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load and embed
with open("docs/context/llms.txt") as f:
    docs = [{"page_content": f.read(), "metadata": {}}]

splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = splitter.split_documents(docs)

vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())

qa = RetrievalQA.from_chain_type(
    llm=ChatAnthropic(model="claude-3-5-sonnet-20241022"),
    retriever=vectorstore.as_retriever()
)

print(qa.run("How do I create a custom skill?"))
```

## Quick Comparison

| Approach | Token Cost | Latency | Best For |
|----------|-----------|---------|----------|
| System Prompt | Higher | Lower | Small docs |
| RAG | Lower | Higher | Large docs |
| Fine-tuning | Lowest | Lowest | Frequent queries |


---

## Source: team-workflow-example.md

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


---

## Source: wiki-navigation-examples.md

# Wiki Navigation Examples

## Example 1: How do I set up Ante?

**Search Path**: Start at `/docs/context/wiki/`

1. **Initial exploration**: Check `README.md` for overview
2. **Setup guide**: Look in `guides/installation.md` or `getting-started.md`
3. **Configuration**: Reference `reference/configuration.md`
4. **Quick start**: See `guides/quickstart.md` for first steps

**Real search flow**:
```bash
# Browse wiki structure
ls docs/context/wiki/guides/

# Read the installation guide
cat docs/context/wiki/guides/installation.md

# Reference config options
grep -A5 "ANTE_" docs/context/wiki/reference/configuration.md
```

**Answer**: Setup typically involves:
- Installing with `ante install`
- Running `ante init` in your project
- Configuring `ante.config.yaml`
- Creating your first skill

See: `wiki/guides/installation.md`, `wiki/guides/quickstart.md`

---

## Example 2: What tools are available?

**Search**: `wiki/reference/tools-api.md`

**Quick Answer**:
- CLI Tools: Bash, Read, Write, Edit, Glob, Grep
- Integration Tools: WebFetch, TodoWrite
- Custom Tools: Can be added via skill system

See: `wiki/reference/tools-api.md` for full API documentation

**Finding details**:
```bash
# List all available tools
ls docs/context/wiki/reference/

# Search for specific tool documentation
grep -r "Tool.*Description" docs/context/wiki/
```

---

## Example 3: How do I create a custom skill?

**Search Path**:
1. Start: `wiki/guides/custom-skills.md` (main guide)
2. Templates: `wiki/reference/skill-templates/`
3. Examples: `wiki/examples/` (if available)

**Key sections to find**:
- Skill structure and anatomy
- Interface implementation
- Registration process
- Testing custom skills

**Implementation reference**:
```bash
# Look at skill template
cat docs/context/wiki/reference/skill-templates/basic-skill.py

# Check integration examples
grep -r "custom.*skill" docs/context/wiki/

# Review API documentation
cat docs/context/wiki/reference/skill-api.md
```

**Answer path**: 
1. Read `wiki/guides/custom-skills.md` for overview
2. Use template from `wiki/reference/skill-templates/`
3. Follow examples in `docs/examples/`
4. Test using `ante test`

---

## Example 4: How do I integrate with a new model provider?

**Search**: `wiki/guides/integration.md` or `wiki/guides/provider-integration.md`

**Navigation**:
1. Provider integration architecture: `wiki/guides/integration.md`
2. Specific provider examples: `wiki/guides/providers/`
3. API reference: `wiki/reference/provider-api.md`
4. Authentication: `wiki/reference/authentication.md`

**Key steps to find**:
```bash
# Find provider documentation
ls docs/context/wiki/guides/providers/

# Check specific provider (e.g., OpenAI)
cat docs/context/wiki/guides/providers/openai.md

# Find auth requirements
grep -r "authentication\|api.*key" docs/context/wiki/guides/providers/
```

**Answer navigation**:
1. Understand provider interface in `integration.md`
2. Review authentication requirements
3. Implement provider class
4. Register in configuration
5. Test integration

---

## Example 5: What are the best practices for performance?

**Search**: `wiki/guides/performance.md` or `wiki/reference/performance-tuning.md`

**Related documentation**:
- Optimization: `wiki/guides/optimization.md`
- Caching: `wiki/reference/caching.md`
- Benchmarking: `wiki/guides/benchmarking.md`

**Key areas**:
```bash
# Search for performance guidance
grep -r "performance\|optimization\|benchmark" docs/context/wiki/guides/ | head -20

# Find caching documentation
cat docs/context/wiki/reference/caching.md

# Check monitoring guide
cat docs/context/wiki/guides/monitoring.md
```

**Best practices include**:
- Tool reuse patterns (Example 5 in llms-txt-integration-examples.md)
- Caching strategies
- Batch operations
- Resource pooling
- Monitoring and metrics

---

## Wiki Structure Quick Reference

```
docs/context/wiki/
├── guides/              # How-to guides
│   ├── quickstart.md
│   ├── installation.md
│   ├── custom-skills.md
│   ├── integration.md
│   ├── performance.md
│   └── providers/       # Provider-specific guides
├── reference/           # Technical reference
│   ├── tools-api.md
│   ├── skill-api.md
│   ├── configuration.md
│   ├── caching.md
│   └── skill-templates/
├── examples/            # Code examples
├── architecture/        # Architecture docs
└── README.md           # Wiki overview
```

---

## Search Tips

1. **Use grep for quick searches**:
   ```bash
   grep -r "your-topic" docs/context/wiki/ --include="*.md"
   ```

2. **Browse by category**: Start with `guides/` for how-tos, `reference/` for technical details

3. **Check README files**: Each directory has a README explaining contents

4. **Look for examples**: Many guides include code examples

5. **Cross-reference**: Use links in documents to navigate related content

---

## Common Navigation Patterns

| Question | Start Here | Then See |
|----------|-----------|----------|
| "How do I...?" | `guides/` | `reference/` for details |
| "What is...?" | `README.md` | `architecture/` for details |
| "What are the options for...?" | `reference/` | `guides/` for examples |
| "How do I configure...?" | `reference/configuration.md` | Provider-specific guides |
| "Show me an example" | `examples/` | Related guide |


---

Copied count: 4