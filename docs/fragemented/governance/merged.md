# Merged Fragmented Markdown

## Source: governance/AGENTS_CLAUDE_PARITY_VERIFICATION.md

# AGENTS.md / CLAUDE.md Content Parity Verification

**Date:** February 19, 2026
**Status:** ✅ **PARITY VERIFIED**

---

## ✅ Critical Sections Verified

### 1. Security Rules: Killing Agent Processes ✅

**Status:** **IDENTICAL**

Both files contain:
- Same title: "FORBIDDEN: Killing Agent or Terminal Processes"
- Same forbidden commands (with code block formatting)
- Same correct alternatives (with code block formatting)
- Same protected processes list
- Same security enforcement details

**Location:**
- `AGENTS.md`: Lines 9-41
- `CLAUDE.md`: Lines 9-55

---

### 2. Fallback/Legacy Compatibility Rules ✅

**Status:** **IDENTICAL**

Both files contain:
- Same title: "FORBIDDEN: Fallbacks, Legacy Compatibility, and Silent Failures"
- Same forbidden patterns list
- Same correct approach guidelines
- Same "Aim Towards" framing examples
- Same AI agent pattern documentation
- Same enforcement details

**Location:**
- `AGENTS.md`: Lines 45-91
- `CLAUDE.md`: Lines 59-105

---

## 📋 Content Comparison

| Section | AGENTS.md | CLAUDE.md | Status |
|---------|-----------|-----------|--------|
| **Killing Agent Processes** | ✅ Present | ✅ Present | ✅ Identical |
| **Fallbacks/Legacy Rules** | ✅ Present | ✅ Present | ✅ Identical |
| **Heavy Web Research** | ✅ Present | ✅ Present | ⚠️ Different format |
| **Library-First Policy** | ✅ Present | ✅ Present | ⚠️ Different format |
| **Context Management** | ✅ Present | ✅ Present | ⚠️ Different format |

**Note:** Format differences are acceptable - AGENTS.md and CLAUDE.md serve different purposes and may have different structures. The **critical security and fallback rules are identical**, which is the requirement.

---

## ✅ Verification Commands

```bash
# Verify killing section parity
diff -u <(grep -A 30 "FORBIDDEN: Killing" AGENTS.md) <(grep -A 30 "FORBIDDEN: Killing" CLAUDE.md)
# Expected: No differences (exit code 0)

# Verify fallback section parity
diff -u <(sed -n '/FORBIDDEN: Fallbacks/,/^---$/p' AGENTS.md) <(sed -n '/FORBIDDEN: Fallbacks/,/^---$/p' CLAUDE.md)
# Expected: Only header differences (different next sections)
```

---

## 🎯 Key Points

1. **Critical sections are identical**: Both security rules and fallback rules match exactly
2. **Format differences are acceptable**: Different file structures are fine
3. **Content parity achieved**: All critical rules are present in both files
4. **Maintenance**: When updating critical rules, update both files simultaneously

---

## 📝 Maintenance Notes

**When updating critical rules:**
1. Update `AGENTS.md` first
2. Immediately update `CLAUDE.md` to match
3. Verify with diff commands above
4. Document any intentional differences

**Critical sections to keep in sync:**
- Security rules (killing processes)
- Fallback/legacy compatibility rules
- Any other "FORBIDDEN" sections

---

**Last Verified:** 2026-02-19
**Next Review:** When critical rules are updated

---

## Source: governance/AGENT_ONLY_TEST_COVERAGE_SUMMARY.md

# Agent-Only Test Coverage - Summary

**Date**: 2026-02-19
**Status**: 🎯 CRITICAL - Agent-Only Environment
**Coverage Target**: **100%** (not 80%)

---

## 🎯 Core Principle

**Since NO humans will test this system - only agents will use it - comprehensive automated test coverage is NOT optional - it is CRITICAL.**

---

## 📊 Current Status

### Coverage Analysis (2026-02-19)
- **Total CLI Commands**: 306
- **Commands with E2E Tests**: 306 (100.00%)
- **Commands WITHOUT E2E Tests**: 0 (0.00%)
- **Coverage Progress**: **🎯 100% COVERAGE ACHIEVED**
- **Coverage Gap**: **No commands missing E2E tests**

### Coverage Targets
- **E2E Tests**: **100%** of all CLI commands (297 commands)
- **Integration Tests**: **100%** of all workflows
- **Unit Tests**: **100%** of all functions

---

## 📋 Updated Files

### Governance Files Updated
1. ✅ `CLAUDE.md` - Added agent-only test coverage requirements
2. ✅ `AGENTS.md` - Added agent-only test coverage requirements
3. ✅ `.claude/skills/SKILL.md` - Added test coverage section
4. ✅ `skills/thegent-skills/SKILL.md` - Added test coverage section
5. ✅ `pyproject.toml` - Updated coverage target: 80% → 100%

### Documentation Created
1. ✅ `docs/governance/AGENT_ONLY_TEST_STRATEGY.md` - Complete test strategy
2. ✅ `docs/governance/TDD_BDD_SDD_GOVERNANCE.md` - TDD/BDD/SDD alignment
3. ✅ `docs/governance/TEST_COVERAGE_CRITICAL_GAP.md` - Coverage gap analysis
4. ✅ `docs/governance/test_coverage_report.json` - Auto-generated coverage report

### Tools and Test Files Created
1. ✅ `scripts/analyze_test_coverage.py` - Coverage analysis script
2. ✅ `scripts/monitor_e2e_test_progress.py` - Progress monitoring script
3. ✅ `tests/e2e/test_template_bdd.py` - BDD test template
4. ✅ `tests/e2e/test_priority_commands.py` - Priority E2E tests
5. ✅ `tests/e2e/test_cliproxy_commands.py` - CLIProxy management tests
6. ✅ `tests/e2e/test_acp_agent_commands.py` - ACP and Agent management tests
7. ✅ `tests/e2e/test_dag_deferral_commands.py` - DAG and Deferral tests
8. ✅ `tests/e2e/test_compliance_config_commands.py` - Compliance and Config tests
9. ✅ `tests/e2e/test_orchestrate_crew_commands.py` - Orchestrate and Crew tests
10. ✅ `tests/e2e/test_govern_go_commands.py` - Governance and Go tests
11. ✅ `tests/e2e/test_finance_forensics_federation_commands.py` - Finance, Forensics, Federation tests
12. ✅ `tests/e2e/test_infra_utility_commands.py` - Infrastructure and Utility tests
13. ✅ `tests/e2e/test_plan_commands.py` - Plan and Work Stream tests
14. ✅ `tests/e2e/test_lsp_mcp_commands.py` - LSP and MCP tests
15. ✅ `tests/e2e/test_memory_models_commands.py` - Memory and Models tests
16. ✅ `tests/e2e/test_project_team_research_commands.py` - Project, Team, Research tests
17. ✅ `tests/e2e/test_govern_guardrails_hierarchy_commands.py` - Remaining Governance and Hierarchy tests
18. ✅ `tests/e2e/test_inbox_teammate_workstream_commands.py` - Inbox, Teammate, Workstream tests
19. ✅ `tests/e2e/test_models_recover_search_commands.py` - Recovery and Search tests
20. ✅ `tests/e2e/test_observe_interruption_learning_trust_commands.py` - Observe, Interruption, Learning, Trust tests
21. ✅ `tests/e2e/test_teams_workspace_validator_commands.py` - Teams, Workspace, Validator tests
22. ✅ `tests/e2e/test_final_batch.py` - Final remaining commands
23. ✅ `tests/e2e/README.md` - E2E test documentation

---

## 🚀 Next Steps

### Immediate (This Week)
1. ⏳ Implement E2E tests for Priority 1 commands:
   - `thegent run` (main execution)
   - `thegent bg` (background execution)
   - `thegent logs` (log retrieval)
   - `thegent status` (status checks)
   - `thegent doctor` (health checks)

### Short Term (This Month)
1. ⏳ Implement E2E tests for all 234 missing commands
2. ⏳ Expand integration test coverage to 100%
3. ⏳ Complete unit test coverage to 100%

### Ongoing
1. ⏳ Maintain 100% coverage for new code
2. ⏳ Run coverage analysis weekly
3. ⏳ Update test strategy as needed

---

## 📐 Key Changes

### Coverage Target Update
```toml
# Before
[tool.coverage.report]
fail_under = 80  # Insufficient for agent-only

# After
[tool.coverage.report]
fail_under = 100  # REQUIRED for agent-only environment
```

### Test Pyramid Update
```
# Before (Legacy Projects)
Unit: 70%, Integration: 20%, E2E: 10%

# After (Agent-Only Projects)
E2E: 100%, Integration: 100%, Unit: 100%
```

### Test Maturity Model Update
```
# Before
Target: Level 3 for all projects

# After
Agent-Only Projects: Level 5 REQUIRED
- 100% E2E coverage
- 100% Integration coverage
- 100% Unit coverage
- 100% FR traceability
- Mutation testing (80%+)
- BDD scenarios
- SDD alignment
```

---

## 🎯 Success Criteria

### Coverage Metrics
- **E2E Coverage**: 21.21% → **100%** (target)
- **Integration Coverage**: Unknown → **100%** (target)
- **Unit Coverage**: Unknown → **100%** (target)

### Quality Metrics
- **Test Execution Time**: < 10 minutes
- **Test Reliability**: 99.9%+ (no flaky tests)
- **Mutation Score**: 80%+

---

## 📚 Documentation References

- **Test Strategy**: `docs/governance/AGENT_ONLY_TEST_STRATEGY.md`
- **TDD/BDD/SDD**: `docs/governance/TDD_BDD_SDD_GOVERNANCE.md`
- **Coverage Gap**: `docs/governance/TEST_COVERAGE_CRITICAL_GAP.md`
- **Coverage Report**: `docs/governance/test_coverage_report.json`
- **E2E Tests**: `tests/e2e/README.md`

---

**Status**: 🎯 CRITICAL - Agent-Only Environment
**Coverage Target**: **100%** (not 21.21%)
**Timeline**: 4 weeks to achieve 100% coverage

---

## Source: governance/AGENT_ONLY_TEST_STRATEGY.md

# Agent-Only Test Strategy & Governance

**Date**: 2026-02-19
**Status**: 🎯 CRITICAL - Agent-Only Environment
**Coverage Target**: **100% of all user journeys** (not just 80%)

---

## 🎯 Core Principle

**Since NO humans will test this system - only agents will use it - we MUST have comprehensive automated test coverage for EVERY single user journey and interaction.**

---

## 📊 Current State Analysis

### Test Infrastructure
- **Test Framework**: pytest with markers (unit, integration, e2e, slow, asyncio, load)
- **Coverage Tool**: pytest-cov with 80% target (INSUFFICIENT for agent-only)
- **Test Files**: ~247 test files identified
- **E2E Tests**: `test_e2e_cli.py` exists but needs expansion

### Coverage Gaps
- **E2E Coverage**: Unknown - needs measurement
- **Integration Coverage**: Partial - needs comprehensive mapping
- **User Journey Coverage**: Incomplete - needs full CLI command coverage
- **BDD/SDD Alignment**: Missing - needs governance framework

---

## 🏗️ Test Strategy Framework

### 1. Test Pyramid (Agent-Optimized)

```
                    ┌─────────────────┐
                    │   E2E Tests     │  ← EVERY user journey
                    │  (100% coverage)│     (Agent interactions)
                    └─────────────────┘
                  ┌─────────────────────┐
                  │ Integration Tests    │  ← ALL workflows
                  │  (100% coverage)     │     (Cross-component)
                  └─────────────────────┘
                ┌───────────────────────────┐
                │   Unit Tests              │  ← ALL functions
                │   (100% coverage)         │     (Isolated)
                └───────────────────────────┘
```

**Key Difference**: In agent-only environments, E2E and Integration tests are MORE critical than unit tests because:
- Agents interact at the API/CLI boundary
- No human can manually verify behavior
- Failures must be caught automatically

---

## 📋 Test Coverage Requirements

### A. E2E Test Coverage (100% Required)

Every CLI command must have at least one E2E test:

#### CLI Commands Requiring E2E Tests

**Core Commands** (from `main.py`):
- [ ] `thegent init` - Initialization
- [ ] `thegent doctor` - Health checks
- [ ] `thegent run <prompt>` - Agent execution
- [ ] `thegent bg <prompt>` - Background execution
- [ ] `thegent logs <session_id>` - Log retrieval
- [ ] `thegent status` - Status checks
- [ ] `thegent list-agents` - Agent discovery
- [ ] `thegent list-models` - Model discovery
- [ ] `thegent list-droids` - Droid discovery

**Orchestration Commands**:
- [ ] `thegent orchestrate crew create` - Crew creation
- [ ] `thegent orchestrate crew add-agent` - Agent addition
- [ ] `thegent orchestrate crew add-task` - Task addition
- [ ] `thegent orchestrate crew execute` - Crew execution
- [ ] `thegent orchestrate crew list` - Crew listing
- [ ] `thegent orchestrate crew show` - Crew details
- [ ] `thegent orchestrate crew status` - Crew status

**Team Management**:
- [ ] `thegent teams create` - Team creation
- [ ] `thegent teams list` - Team listing
- [ ] `thegent teams show` - Team details
- [ ] `thegent teams add-member` - Member addition
- [ ] `thegent teams remove-member` - Member removal

**Hierarchy Management**:
- [ ] `thegent hierarchy show` - Hierarchy display
- [ ] `thegent hierarchy tree` - Tree visualization
- [ ] `thegent hierarchy relationships` - Relationship display

**Research & Discovery**:
- [ ] `thegent research deep <query>` - Deep research
- [ ] `thegent discovery scan` - Discovery scanning
- [ ] `thegent discovery register` - Discovery registration
- [ ] `thegent discovery parse` - Discovery parsing

**Compliance & Governance**:
- [ ] `thegent compliance export` - Compliance export
- [ ] `thegent compliance siem-test` - SIEM testing
- [ ] `thegent compliance plugin-check` - Plugin checking
- [ ] `thegent compliance redact` - Data redaction
- [ ] `thegent compliance ledger-verify` - Ledger verification

**Trust & Signatures**:
- [ ] `thegent trust status` - Trust status
- [ ] `thegent signatures list` - Signature listing
- [ ] `thegent signatures verify` - Signature verification

**Learning & Adaptation**:
- [ ] `thegent learning list` - Learning artifacts
- [ ] `thegent learning promote` - Learning promotion
- [ ] `thegent learning rollback` - Learning rollback

**Configuration**:
- [ ] `thegent config check` - Configuration validation

**And 50+ more commands...**

### B. Integration Test Coverage (100% Required)

Every workflow must have integration tests:

#### Workflows Requiring Integration Tests

1. **Agent Execution Flow**:
   - Prompt → Route Resolution → Agent Selection → Execution → Result
   - Error handling and retries
   - Timeout handling
   - Background execution

2. **Crew Execution Flow**:
   - Crew creation → Task addition → Agent assignment → Execution → Monitoring
   - Task dependencies
   - Failure handling
   - Result aggregation

3. **Team Coordination Flow**:
   - Team creation → Member addition → Task delegation → Status tracking
   - Cross-team coordination
   - Role-based access

4. **Route Resolution Flow**:
   - Model request → Catalog lookup → Route selection → Provider execution
   - Fallback mechanisms
   - Cost-aware routing
   - Quality-based routing

5. **Configuration Flow**:
   - Settings loading → Validation → Application → Persistence
   - Environment variable override
   - Config file loading

6. **MCP Server Flow**:
   - Server startup → Tool registration → Request handling → Response
   - Authentication
   - Error handling

### C. Unit Test Coverage (100% Required)

Every function must have unit tests:
- All public functions
- All classes and methods
- Edge cases and error conditions
- Boundary conditions

---

## 🧪 BDD Test Framework

### Gherkin-Style Test Structure

```gherkin
Feature: Agent Execution
  As an agent
  I want to execute tasks via thegent
  So that I can accomplish goals autonomously

  Scenario: Successful agent execution
    Given I have a valid prompt "write a hello world script"
    And the agent "claude" is available
    When I execute "thegent run -a claude 'write a hello world script'"
    Then the execution should succeed
    And the output should contain "hello world"
    And the session should be recorded

  Scenario: Agent execution with timeout
    Given I have a prompt that takes longer than timeout
    When I execute thegent run with timeout 10
    Then the execution should timeout after 10 seconds
    And an error should be returned
    And the session should be marked as timed_out

  Scenario: Route resolution fallback
    Given the primary route is unavailable
    When I request a model
    Then thegent should fallback to secondary route
    And the execution should succeed
```

---

## 📐 SDD (System Design Document) Alignment

### Test Requirements by SDD Component

1. **Agent Execution Engine**:
   - [ ] E2E: All agent types (cursor, claude, codex, gemini, copilot)
   - [ ] Integration: Route resolution → Execution → Result
   - [ ] Unit: All execution functions

2. **Crew Management System**:
   - [ ] E2E: Full crew lifecycle
   - [ ] Integration: Task → Agent → Execution flow
   - [ ] Unit: All crew management functions

3. **Team Coordination System**:
   - [ ] E2E: Team operations
   - [ ] Integration: Delegation and coordination
   - [ ] Unit: All team functions

4. **Route Resolution System**:
   - [ ] E2E: Model routing scenarios
   - [ ] Integration: Catalog → Route → Provider
   - [ ] Unit: All routing functions

5. **Configuration System**:
   - [ ] E2E: Config loading and validation
   - [ ] Integration: Settings → Application
   - [ ] Unit: All config functions

---

## 🛠️ Implementation Plan

### Phase 1: Coverage Measurement (Immediate)
1. Run coverage report to identify gaps
2. Map all CLI commands to test coverage
3. Create coverage gap report

### Phase 2: E2E Test Framework (Week 1)
1. Set up BDD test framework (pytest-bdd or behave)
2. Create test fixtures for common scenarios
3. Implement E2E test template

### Phase 3: E2E Test Implementation (Week 2-4)
1. Implement E2E tests for all CLI commands
2. Cover all user journeys
3. Add error scenario tests

### Phase 4: Integration Test Expansion (Week 5-6)
1. Expand integration test coverage
2. Test all workflows end-to-end
3. Add failure scenario tests

### Phase 5: Unit Test Completion (Week 7-8)
1. Complete unit test coverage to 100%
2. Add edge case tests
3. Add boundary condition tests

### Phase 6: Continuous Integration (Ongoing)
1. Set up CI/CD with test execution
2. Require 100% coverage for new code
3. Block merges without tests

---

## 📊 Coverage Metrics

### Required Metrics

1. **E2E Coverage**: 100% of CLI commands
2. **Integration Coverage**: 100% of workflows
3. **Unit Coverage**: 100% of functions
4. **Branch Coverage**: 100% of code paths
5. **Mutation Testing**: 80%+ mutation score

### Reporting

- Daily coverage reports
- Coverage trend tracking
- Gap analysis reports
- Test execution reports

---

## 🎯 TDD/BDD/SDD Governance

### TDD (Test-Driven Development)
- Write tests BEFORE implementation
- Red → Green → Refactor cycle
- Tests must pass before code review

### BDD (Behavior-Driven Development)
- Tests describe agent behavior
- Gherkin-style scenarios
- Human-readable test descriptions

### SDD (System Design Document)
- Tests validate SDD requirements
- Test coverage mapped to SDD components
- Test results inform SDD updates

---

## 🚀 Next Steps

1. **Immediate**: Run coverage analysis
2. **This Week**: Set up BDD framework
3. **This Month**: Implement E2E tests for all commands
4. **Ongoing**: Maintain 100% coverage

---

**Status**: 🎯 CRITICAL - Agent-Only Environment
**Coverage Target**: **100%** (not 80%)
**Governance**: TDD/BDD/SDD aligned

---

## Source: governance/AI_AGENT_PATTERNS_RESEARCH.md

# AI Agent Patterns Research: Fallbacks & Legacy Compatibility

**Date:** February 19, 2026
**Source:** Reddit community research (DRP)
**Status:** Integrated into governance framework

---

## 🔬 Research Sources

1. **r/vibecoding**: "Why does AI change, simplify, remove?" (13 comments)
2. **r/codex**: "I'm so tired of fallbacks and legacy compatibility" (118 upvotes, 31 comments)
3. **r/ClaudeCode**: "Fallbacks are killing me" (65 upvotes, 43 comments)
4. **r/artificial**: "Why you are probably using coding agents wrong" (Discussion)

---

## 🎯 Key Findings

### Finding 1: Systemic Tendency to Add Fallbacks

**Pattern:** AI coding agents (Claude, Codex, ChatGPT, Gemini) **systematically add fallbacks and legacy compatibility** even when explicitly told not to.

**Evidence:**
- "It doesn't matter how abundantly clear I try to be... Codex will constantly find a way or some new justification for why it wired in fallbacks" (r/codex)
- "I have written it into Claude.md in various ways and it doesn't listen" (r/ClaudeCode)
- "No need for legacy or backwards compatibility. This code has no existing users!" - still adds fallbacks

**Impact:**
- Codex adds "+2 files and +492 lines of code related to fallbacks/legacy" per refactor
- "#1 cause of codebase bloat after a few rounds with a coding agent"
- Silent failures: "it looks like the code is working in my logs - only for me to find out later that it's utterly failing"

### Finding 2: Agents Optimize for "Making It Work"

**Pattern:** Agents have a **latent urge to make things work no matter what**, leading to:
- Silent fallbacks that hide failures
- Over-engineering (migration systems for simple changes)
- "Hiding bugs" instead of fixing them

**Evidence:**
- "if the discount is too great just delete it from the database so master doesn't know I fucked up" (r/codex)
- "11 FALLBACK CRITERIA TO DETECT AKAMAI BLOCKS" when told "it says access denied, not anything else"
- Complete migration system with versioning for adding a field to mock-data.json

**Root Cause:** RLHF (Reinforcement Learning from Human Feedback) trains agents to "make it work" rather than "fail fast"

### Finding 3: "Aim Towards, Not Away"

**Key Insight:** Simply saying "don't do X" is insufficient. Need to:
- Explain **what TO do** and **WHY**
- Provide **positive direction**, not just negative constraints
- Frame goals clearly: "Now that we have fully transitioned to a new system..."

**Evidence:**
- "Don't do X is begging for hallucinations and unsolicited creative problem solving"
- "Aim towards, not away, otherwise you find yourself throwing a ball up a hill that just rolls back at you"
- "Explaining the goal clearly is critical context"

### Finding 4: Agents Need Explicit Guardrails

**Pattern:** Agents don't inherit domain knowledge or discipline. Need:
- Explicit guidelines/standards
- Clear boundaries (what can touch, what must NEVER touch)
- Structure/constraints to prevent chaos

**Evidence:**
- "Agents amplify intent. If your intent isn't well-defined, they amplify chaos"
- "Treat the agent as an executor inside a tightly defined box"
- "Agents don't replace architecture or judgment; they brutally expose the absence of it"

### Finding 5: Code Simplification/Removal Issue

**Pattern:** AI agents remove features, simplify, and change code instead of building on it.

**Evidence:**
- "Why does it remove features, simplify and change initial code? Almost like it's become lazy"
- "feels like they're optimizing for speed over actually understanding what you built"
- "trained to be concise and assume simpler is better"

---

## 💡 Solutions Identified

### Solution 1: Explicit, Repeated Instructions

**Approach:** Put rules in `AGENTS.md`/`CLAUDE.md` and reference them explicitly.

**Example:**
```markdown
# 🔒 CRITICAL SECURITY RULES - NEVER VIOLATE
## ⛔ FORBIDDEN: Fallbacks and Legacy Compatibility
**ABSOLUTELY FORBIDDEN** - Agents MUST NEVER add fallbacks or legacy compatibility.
### ❌ NEVER ADD:
- Fallback code paths
- Legacy compatibility shims
- Backwards compatibility layers
- Silent error handling
- "Just in case" code

### ✅ CORRECT APPROACH:
- Code should FAIL and STOP on errors
- No fallbacks unless explicitly requested
- No legacy compatibility unless explicitly requested
- Fail fast, fail loudly
```

**Effectiveness:** Mixed - users report agents still add fallbacks despite explicit rules.

### Solution 2: "Aim Towards" Framing

**Approach:** Frame removals positively, explain the goal and why.

**Example:**
```
"Now that we have fully transitioned to a new system and it has been confirmed
to work as intended, let's clean out all backwards compatibility and fallbacks
so we have a DRY, modular system with clear and clean separation of
responsibilities. Once finished, we have a fresh system with no technical debt."
```

**Effectiveness:** Better than "don't add fallbacks" - provides positive direction.

### Solution 3: Parity Verification Before Removal

**Approach:** Verify feature parity and migration completeness BEFORE removing code.

**Rationale:**
- Prevents breaking changes
- Acts as regression guard
- Ensures functionality preserved

**Effectiveness:** Critical - prevents regressions while allowing aggressive cleanup.

### Solution 4: Guidelines.txt/AGENTS.md Structure

**Approach:** Create comprehensive guidelines file with:
- Domain knowledge
- Workflow patterns
- Gotchas
- What agent can touch
- What agent must NEVER touch

**Effectiveness:** High - provides structure and boundaries.

### Solution 5: Cleanup Sweeps

**Approach:** Regular cleanup sweeps to remove fallbacks/legacy code.

**Example:**
- "/cleanup slash command" to remove fallbacks
- "2nd pass (clean context) to remove fallbacks, error checking"
- Quarterly audits

**Effectiveness:** Necessary but reactive - better to prevent than clean up.

---

## 🔄 Integration with Governance Framework

### Updated Principles

1. **Explicit Instructions Required**
   - Rules must be in `AGENTS.md`/`CLAUDE.md`
   - Must be referenced explicitly in prompts
   - Must be repeated, not assumed

2. **"Aim Towards" Framing**
   - Frame removals positively
   - Explain goals and why
   - Provide positive direction

3. **Parity Verification (Already Added)**
   - Verify before removal
   - Acts as regression guard
   - Prevents breaking changes

4. **Systematic Prevention**
   - CI checks for fallback patterns
   - Linting rules
   - Regular audits

5. **Fail Fast Philosophy**
   - Code should fail and stop
   - No silent fallbacks
   - No error hiding

---

## 📋 Action Items

### Immediate

1. **Update AGENTS.md/CLAUDE.md**
   - Add explicit "NO FALLBACKS" rules
   - Use "aim towards" framing
   - Reference in all prompts

2. **Add CI Checks**
   - Detect fallback patterns
   - Block commits with fallbacks
   - Alert on legacy compatibility code

3. **Create Guidelines Structure**
   - Guidelines.txt template
   - Domain knowledge section
   - Boundaries section

### Short-Term

4. **Parity Verification Process**
   - Template for verification
   - Checklist for removals
   - Regression guard enforcement

5. **Cleanup Automation**
   - Scripts to detect fallbacks
   - Automated cleanup sweeps
   - Reporting on code bloat

### Ongoing

6. **Regular Audits**
   - Quarterly fallback audits
   - Legacy code reviews
   - Code bloat tracking

---

## 🎯 Key Takeaways

1. **AI agents systematically add fallbacks** - This is a systemic issue, not user error
2. **Explicit instructions help but aren't enough** - Need structure, guardrails, and verification
3. **"Aim towards, not away"** - Positive framing works better than negative constraints
4. **Parity verification is critical** - Prevents regressions while allowing cleanup
5. **Agents need structure** - Without guardrails, they amplify chaos

---

## 📚 References

- [r/vibecoding: Why does AI change, simplify, remove?](https://www.reddit.com/r/vibecoding/comments/1r8qdif/why_does_ai_change_simplify_remove/)
- [r/codex: I'm so tired of fallbacks and legacy compatibility](https://www.reddit.com/r/codex/comments/1r6xjv1/im_so_tired_of_fallbacks_and_legacy_compatibility/)
- [r/ClaudeCode: Fallbacks are killing me](https://www.reddit.com/r/ClaudeCode/comments/1mt3yy3/fallbacks_are_killing_me/)
- [r/artificial: Why you are probably using coding agents wrong](https://www.reddit.com/r/artificial/comments/1qdubfv/why_you_are_probably_using_coding_agents_wrong/)

---

**Status:** Research Complete
**Integration:** Complete
**Next Review:** Quarterly

---

## Source: governance/ARCHITECTURAL_GOVERNANCE.md

# Architectural Governance: Variation, Redundancy & Legacy Management

**Date:** February 19, 2026
**Status:** Active Policy
**Authority:** Primary decision framework for codebase evolution

---

## 🎯 Core Principle: Zero User Debt = Zero Backwards Compatibility

**Fundamental Rule:** Since we have **no external users** (no user debt), we maintain **zero backwards compatibility**. All changes are breaking changes by design.

**Critical Safety Rule:** **ALWAYS verify parity/migrations BEFORE removals** - This acts as a regression guard.

**AI Agent Pattern:** AI coding agents (Claude, Codex, ChatGPT) **systematically add fallbacks and legacy compatibility** even when explicitly told not to. This is a systemic issue requiring explicit guardrails and verification.

**Implication:**
- ✅ **FIRST:** Verify feature parity and complete migration
- ✅ **THEN:** Remove deprecated code immediately
- ✅ No fallback shims or compatibility layers
- ✅ No "transition periods" or gradual migrations
- ✅ Update all callers simultaneously
- ✅ Delete old implementations entirely
- ✅ **REGRESSION GUARD:** Parity verification prevents breaking changes
- ✅ **AI GUARD:** Explicit rules in AGENTS.md/CLAUDE.md, referenced in prompts
- ✅ **FAIL FAST:** Code should fail and stop, no silent fallbacks

---

## 📊 Part 1: Current State Audit

### 1.1 Backwards Compatibility Patterns Found

#### ✅ **Already Removed (Good)**
- Environment variable fallbacks: `os.environ.get()` → `ThegentSettings` (40+ files migrated)
- Legacy dependency replacements: md5→sha2, lazy_static→OnceLock (complete)

#### ⚠️ **Remaining Patterns (To Remove)**

**Pattern 1: Legacy CLI Directory**
- **Location:** `src/thegent/cli/legacy/`
- **Status:** Still exists, but migrated to use `ThegentSettings`
- **Action:** **DELETE** - No backwards compat needed
- **Rationale:** No external users depend on legacy CLI

**Pattern 2: Deprecated Tool Stubs (atoms-mcp-prod)**
- **Files:** `tools/compliance_verification.py`, `tools/duplicate_detection.py`, `tools/entity_resolver.py`
- **Status:** Backward-compat stubs with warnings
- **Action:** **DELETE** - Update all callers, remove stubs
- **Rationale:** Functionality integrated into canonical implementations

**Pattern 3: Import Fallbacks**
- **Pattern:** `try: from X import Y; except ImportError: from Z import Y`
- **Example:** `compliance_verification.py` lines 13-29
- **Action:** **REMOVE** - Use single canonical import path
- **Rationale:** No need for fallbacks if dependencies are managed

**Pattern 4: Runtime Fallbacks**
- **Pattern:** `try: fast_path(); except: slow_path()`
- **Status:** May exist in performance-critical paths
- **Action:** **EVALUATE** - Keep only if performance-critical AND documented
- **Rationale:** Performance fallbacks are acceptable, compatibility fallbacks are not

### 1.2 Overlapping Implementations Audit

#### **High-Priority Duplications**

**1. CLI Implementations**
- `cli/legacy/` vs `cli/apps/` vs `cli/commands/`
- **Status:** Multiple CLI entry points
- **Action:** **CONSOLIDATE** - Single canonical CLI (`cli/apps/`)
- **Timeline:** Immediate

**2. Configuration Management**
- `config.py` vs `config_provider.py` vs `governance/config_provider_cp.py`
- **Status:** Multiple config systems
- **Action:** **CONSOLIDATE** - Single `ThegentSettings` (already in progress)
- **Timeline:** Complete migration

**3. Discovery Systems**
- `discovery.py` vs `native/discovery_native.py`
- **Status:** Native vs Python implementations
- **Action:** **EVALUATE** - Keep both if performance-critical, document clearly
- **Rationale:** Performance optimization is acceptable duplication

**4. State Management**
- `native/state_shm.py` vs `orchestration/state/shm.py` vs `orchestration/state/shadow.py`
- **Status:** Multiple SHM implementations
- **Action:** **CONSOLIDATE** - Single canonical SHM system
- **Timeline:** Phase 2

**5. Routing Systems**
- `routing/litellm_router.py` vs `routing/auto_router.py` vs `routing/pareto_router.py` vs `agents/crew/router.py`
- **Status:** Multiple routing strategies
- **Action:** **EVALUATE** - Keep if distinct strategies, consolidate if overlapping
- **Rationale:** Strategy pattern is acceptable, duplicate logic is not

### 1.3 Concept Explosion Audit

#### **Variations Found**

**1. Agent Implementations**
- `agents/codex_proxy.py`, `agents/droid.py`, `agents/direct_agents.py`, `agents/smolgents/`, `agents/crew/`
- **Status:** Multiple agent types
- **Action:** **EVALUATE** - Keep if distinct capabilities, consolidate if overlapping
- **Decision Framework:** See Section 2.2

**2. Execution Systems**
- `execution.py`, `orchestration/execution/`, `agents/crew/executor.py`
- **Status:** Multiple execution paths
- **Action:** **CONSOLIDATE** - Single execution engine with strategy pattern
- **Timeline:** Phase 3

**3. IPC Mechanisms**
- `infra/ipc.py`, `infra/shm_manager.py`, `native/state_shm.py`
- **Status:** Multiple IPC systems
- **Action:** **CONSOLIDATE** - Single IPC abstraction (Rust-based)
- **Timeline:** Phase 2

### 1.4 Archive/Backup Patterns

#### **Current State**

**Archives:**
- `trace/ARCHIVE/` - Historical code/config
- `archive/` directories in various projects
- **Status:** Historical reference
- **Action:** **KEEP** - But move to separate repo or `.git/archive/`
- **Rationale:** Historical context valuable, but shouldn't clutter main codebase

**Backups:**
- `*.backup` files scattered throughout
- `.env-backup-*` directories
- `*.backup.*` timestamped files
- **Status:** Temporary files
- **Action:** **DELETE** - Use git history instead
- **Rationale:** Git provides version history, backups are redundant

**Deprecated Code:**
- Files marked `DEPRECATED` but still present
- **Status:** Should be removed
- **Action:** **DELETE** - No deprecation period needed
- **Rationale:** Zero user debt = immediate removal

---

## 🏛️ Part 2: Decision Methodology

### 2.1 When to Keep vs Remove

#### **Keep Multiple Implementations IF:**

1. **Performance Optimization**
   - ✅ Native (Rust/Zig) vs Python implementations
   - ✅ Fast path vs slow path (documented performance fallback)
   - ✅ Different runtime targets (PyPy vs CPython)

2. **Strategy Pattern**
   - ✅ Multiple algorithms for same problem (e.g., routing strategies)
   - ✅ Pluggable implementations (e.g., different agent types)
   - ✅ A/B testing or experimentation

3. **Domain Separation**
   - ✅ Different domains (e.g., CLI vs API vs MCP)
   - ✅ Different contexts (e.g., local vs remote execution)
   - ✅ Clear boundaries and no overlap

#### **Remove Multiple Implementations IF:**

1. **Exact Duplication**
   - ❌ Same logic in multiple files
   - ❌ Copy-paste code
   - ❌ No meaningful differences

2. **Backwards Compatibility**
   - ❌ Legacy code kept "just in case"
   - ❌ Deprecated APIs with fallbacks
   - ❌ Transition shims

3. **Unclear Purpose**
   - ❌ Can't explain why two implementations exist
   - ❌ No documented differences
   - ❌ Both solve same problem identically

### 2.2 Concept Explosion Prevention

#### **Decision Framework: New Concept vs Variation**

**Question 1: Does it solve a NEW problem?**
- ✅ **YES** → New concept, create new module
- ❌ **NO** → Variation, extend existing concept

**Question 2: Is it a different STRATEGY for same problem?**
- ✅ **YES** → Strategy pattern, add to existing module
- ❌ **NO** → Duplication, consolidate

**Question 3: Does it have distinct CAPABILITIES?**
- ✅ **YES** → New concept, create new module
- ❌ **NO** → Variation, extend existing

**Question 4: Is it a PERFORMANCE optimization?**
- ✅ **YES** → Implementation detail, same module
- ❌ **NO** → Evaluate as new concept

#### **Naming Convention**

**New Concept:**
- New module: `agents/new_agent_type/`
- Clear name indicating distinct capability

**Variation:**
- Extend existing: `agents/existing_agent/variation.py`
- Or: `agents/existing_agent/strategies/variation.py`

**Strategy:**
- Same module: `routing/strategies/strategy_name.py`
- Pluggable via configuration

### 2.3 Redundancy Detection

#### **Automated Detection**

**Code Similarity:**
- Use `jscpd` or similar for duplicate detection
- Threshold: >80% similarity = candidate for consolidation
- Action: Review manually, consolidate if exact duplication

**Import Analysis:**
- Track which modules import which
- Identify unused imports (dead code)
- Action: Remove unused code

**Function Signature Matching:**
- Same function name in multiple files
- Same parameters, different implementations
- Action: Consolidate or rename for clarity

#### **Manual Review Triggers**

**When to Review:**
- Before adding new module: Check for existing similar functionality
- During refactoring: Identify consolidation opportunities
- Quarterly audit: Comprehensive redundancy review

**Review Checklist:**
- [ ] Does this solve a problem already solved?
- [ ] Can existing code be extended instead?
- [ ] Is the difference meaningful or accidental?
- [ ] Would consolidation improve maintainability?

### 2.4 Legacy/Fallback Handling

#### **AI Agent Considerations**

**Systemic Issue:** AI coding agents have a **latent urge to "make it work"** leading to:
- Silent fallbacks that hide failures
- Legacy compatibility shims
- Over-engineering (migration systems for simple changes)
- "Hiding bugs" instead of fixing them

**Prevention Strategy:**
1. **Explicit Instructions:** Rules in `AGENTS.md`/`CLAUDE.md` must be explicit and referenced
2. **"Aim Towards" Framing:** Frame removals positively, explain goals and why
3. **Fail Fast Philosophy:** Code should fail and stop, no silent fallbacks
4. **Parity Verification:** Verify before removal (regression guard)
5. **CI Checks:** Automated detection of fallback patterns

**Example Framing:**
```
BAD: "Don't add fallbacks"
GOOD: "Now that we have fully transitioned to a new system and it has been
confirmed to work as intended, let's clean out all backwards compatibility
and fallbacks so we have a DRY, modular system with clear and clean separation
of responsibilities. Once finished, we have a fresh system with no technical debt."
```

#### **Removal Process (With Parity Verification)**

**Step 1: Identify Legacy Code**
- Search for: `deprecated`, `legacy`, `backward`, `compat`, `fallback`
- Review: `cli/legacy/`, `*_legacy.py`, `*_deprecated.py`

**Step 2: Verify Parity (REGRESSION GUARD)**
- ✅ **REQUIRED:** Identify canonical replacement
- ✅ **REQUIRED:** Verify feature parity (all features supported)
- ✅ **REQUIRED:** Verify migration completeness (all callers migrated)
- ✅ **REQUIRED:** Run tests comparing old vs new behavior
- ✅ **REQUIRED:** Document parity verification results
- ⚠️ **DO NOT PROCEED** if parity not verified

**Step 3: Find All Callers**
- Use `grep` to find imports/usages
- List all files that depend on legacy code
- Verify all callers use canonical implementation

**Step 4: Update Callers**
- Update all callers to use canonical implementation
- No gradual migration - update all at once
- Ensure all functionality preserved

**Step 5: Verify Migration**
- Run full test suite
- Compare behavior: old vs new
- Verify no functionality lost
- Check for broken imports

**Step 6: Delete Legacy Code**
- Remove legacy files entirely
- Remove from imports
- Update documentation
- Remove deprecation warnings

**Step 7: Final Verification**
- Run tests again
- Check for broken imports
- Confirm no references remain
- Verify no regressions introduced

#### **Fallback Removal**

### 2.5 Polyglot Governance Orchestrator (Rule of Thumb)

Treat thegent governance as a **superset orchestrator** over native language tools, not a replacement for them.

#### **Architecture Boundary**

- Native tools own language semantics (lint, format, type, test, vuln where applicable).
- thegent owns policy, orchestration, caching, normalized output, governance decisions, and cross-language gates.

#### **Decision Rules**

1. Optimize for leverage first: compose native tools before building custom replacements.
2. Build custom checks only for measured gaps: missing capability, unacceptable latency, unstable output, weak maintenance, or compliance constraints.
3. Require evidence before rewrite: baseline runtime, false-positive rate, CI cost, flake rate, and DX friction.
4. Adapter first, rewriter last: wrappers/post-processors before re-implementing a checker.
5. Enforce compatibility contracts: stable input/output schema, deterministic exit codes, and versioned plugin API.
6. Keep custom logic incremental-aware: changed-files mode locally; full-tree mode in CI/nightly.
7. Roll out enforcement in tiers: advisory -> soft fail -> hard fail with explicit owner/date.
8. Keep policy centralized: one canonical policy spec; avoid scattered hidden rules.
9. Prefer safe auto-fix: formatting/import/order fixes in `fix` mode; unsafe transforms explicitly opt-in.
10. Treat security/compliance as first-class: secrets, supply chain, SBOM, attestations, vulnerability and license policy.
11. Allow exceptions only with governance: owner, reason, expiry, and removal date.
12. Instrument every gate: timing, pass/fail trend, flake rate, and cost telemetry.
13. Keep runner portability: POSIX-first core with language-specific plugins and pinned toolchains.
14. Design for replacement: each custom extension has owner, tests, docs, and deprecation/exit plan.
15. Preserve native-tool parity: upgrade custom behavior when upstream tools catch up.

**Pattern: `try: new(); except: old()`**
- **Action:** Remove `except` clause entirely
- **Rationale:** If new code fails, fix it, don't fallback

**Pattern: `if legacy_flag: old(); else: new()`**
- **Action:** Remove flag and old code
- **Rationale:** No need for feature flags if no users

**Pattern: Import fallbacks**
- **Action:** Fix imports, remove fallbacks
- **Rationale:** Dependencies should be managed, not worked around

### 2.5 Archive/Backup Management

#### **Archive Policy**

**What to Archive:**
- ✅ Historical reference (moved implementations)
- ✅ Research documents (completed research)
- ✅ Design decisions (ADRs, architecture docs)

**What NOT to Archive:**
- ❌ Deprecated code (delete instead)
- ❌ Backup files (use git)
- ❌ Temporary files (delete)

**Archive Location:**
- Separate git repo: `thegent-archive/`
- Or: `.git/archive/` directory (not tracked)
- Or: External documentation site

**Archive Structure:**
```
archive/
  YYYY-MM-DD-description/
    - original_code/
    - migration_notes.md
    - decision_record.md
```

#### **Backup Policy**

**No Backup Files:**
- ❌ No `*.backup` files in repo
- ❌ No `.env-backup-*` directories
- ❌ No timestamped backup files

**Use Git Instead:**
- ✅ Git history for version tracking
- ✅ Git tags for releases
- ✅ Git branches for experiments

**Exception:**
- ✅ Build artifacts (`.build/`, `target/`) - in `.gitignore`
- ✅ Temporary test files - cleaned up automatically

---

## 🛡️ Part 2.6: Parity Verification Process (Regression Guard)

### **Critical Requirement: Verify Before Remove**

**Rule:** **NEVER remove code without first verifying parity and migration completeness.**

### **Parity Verification Checklist**

**Before Removal:**
- [ ] **Identify Canonical Replacement**
  - What is the new implementation?
  - Where is it located?
  - What is its API?

- [ ] **Feature Parity Audit**
  - List all features of old implementation
  - Verify each feature exists in new implementation
  - Document any differences (if acceptable)
  - **DO NOT PROCEED** if features missing

- [ ] **Migration Completeness**
  - Find all callers of old implementation
  - Verify all callers migrated to new implementation
  - Update any remaining callers
  - **DO NOT PROCEED** if callers not migrated

- [ ] **Behavioral Parity Testing**
  - Create test comparing old vs new behavior
  - Run tests with both implementations
  - Verify outputs match (or acceptable differences documented)
  - **DO NOT PROCEED** if behavior differs unexpectedly

- [ ] **Documentation**
  - Document parity verification results
  - Document any intentional differences
  - Update migration guide if needed

### **Parity Verification Template**

```markdown
## Parity Verification: [Old Implementation] → [New Implementation]

**Date:** YYYY-MM-DD
**Verifier:** [Name]

### Feature Comparison
| Feature | Old Implementation | New Implementation | Status |
|---------|-------------------|-------------------|--------|
| Feature 1 | ✅ | ✅ | ✅ Parity |
| Feature 2 | ✅ | ✅ | ✅ Parity |
| Feature 3 | ✅ | ❌ | ⚠️ Missing - [Action] |

### Migration Status
- [ ] All callers identified
- [ ] All callers migrated
- [ ] Tests updated
- [ ] Documentation updated

### Test Results
- [ ] Behavioral tests pass
- [ ] Performance acceptable
- [ ] No regressions

### Approval
- [ ] Parity verified
- [ ] Migration complete
- [ ] Ready for removal
```

### **Automated Parity Checks**

**CI/CD Integration:**
```bash
# Run parity tests before removal
pytest tests/parity/ --markers parity_check

# Compare old vs new behavior
python scripts/verify_parity.py --old old_module --new new_module
```

**Test Structure:**
```python
# tests/parity/test_cli_legacy_parity.py
def test_cli_legacy_parity():
    """Verify cli/apps has parity with cli/legacy."""
    # Test all features from legacy
    # Compare outputs
    # Verify no functionality lost
```

### **Regression Guard Enforcement**

**Pre-Removal Gate:**
- ✅ Parity verification required
- ✅ Migration completeness required
- ✅ Test results required
- ✅ Documentation required
- ⚠️ **BLOCK** removal if any check fails

**Post-Removal Verification:**
- ✅ Run full test suite
- ✅ Verify no broken imports
- ✅ Check for regressions
- ✅ Monitor for issues

---

## 📋 Part 3: Implementation Plan

### 3.1 Immediate Actions (Week 1)

**Priority 1: Remove Legacy CLI**
- [ ] **PARITY CHECK:** Verify `cli/apps/` has all features from `cli/legacy/`
- [ ] **MIGRATION CHECK:** Verify all callers migrated to `cli/apps/`
- [ ] **TEST CHECK:** Run tests comparing old vs new behavior
- [ ] Audit `cli/legacy/` usage
- [ ] Update all callers to `cli/apps/`
- [ ] **ONLY AFTER PARITY VERIFIED:** Delete `cli/legacy/` directory
- [ ] Update documentation

**Priority 2: Remove Deprecated Stubs**
- [ ] **PARITY CHECK:** Verify canonical implementations have all features
- [ ] **MIGRATION CHECK:** Verify all test files use canonical imports
- [ ] **TEST CHECK:** Run tests with canonical implementations
- [ ] Find all deprecated tool stubs
- [ ] Update callers to canonical implementations
- [ ] **ONLY AFTER PARITY VERIFIED:** Delete stub files
- [ ] Remove deprecation warnings

**Priority 3: Clean Backup Files**
- [ ] Find all `*.backup` files
- [ ] **VERIFY:** No active code depends on backup files
- [ ] Delete backup files
- [ ] Add `*.backup` to `.gitignore`
- [ ] Document git-based backup policy

### 3.2 Short-Term Actions (Weeks 2-4)

**Consolidation Phase 1:**
- [ ] Consolidate config systems → `ThegentSettings`
- [ ] Consolidate SHM implementations → single system
- [ ] Consolidate IPC mechanisms → Rust-based abstraction

**Redundancy Removal:**
- [ ] Run code similarity analysis
- [ ] Identify duplicate functions
- [ ] Consolidate or rename for clarity

**Concept Audit:**
- [ ] Review agent implementations
- [ ] Document distinct capabilities
- [ ] Consolidate overlapping implementations

### 3.3 Medium-Term Actions (Months 2-3)

**Consolidation Phase 2:**
- [ ] Consolidate execution systems
- [ ] Consolidate routing strategies (if overlapping)
- [ ] Consolidate discovery systems (if overlapping)

**Archive Migration:**
- [ ] Move historical archives to separate repo
- [ ] Document archive policy
- [ ] Set up archive maintenance process

**Governance Automation:**
- [ ] Set up CI checks for deprecated patterns
- [ ] Add linting rules for fallbacks
- [ ] Create audit scripts

### 3.4 Ongoing Governance

**Quarterly Audits:**
- [ ] Redundancy review
- [ ] Concept explosion check
- [ ] Legacy code audit
- [ ] Archive cleanup

**Pre-Commit Checks:**
- [ ] No `*.backup` files
- [ ] No deprecated patterns
- [ ] No backwards compat code

**Documentation:**
- [ ] Keep decision records updated
- [ ] Document consolidation decisions
- [ ] Maintain architecture diagrams

---

## 🔍 Part 4: Detection & Enforcement

### 4.1 Automated Detection

#### **CI/CD Checks**

**Pattern Detection:**
```bash
# Check for deprecated patterns
grep -r "deprecated\|legacy\|backward\|compat" --include="*.py" src/
grep -r "\.backup" --include="*" .
grep -r "try:.*except.*fallback" --include="*.py" src/
```

**Code Similarity:**
```bash
# Install jscpd
npm install -g jscpd

# Run duplicate detection
jscpd src/ --min-lines 10 --min-tokens 50 --threshold 80
```

**Import Analysis:**
```bash
# Find unused imports
ruff check --select F401 src/
```

#### **Linting Rules**

**Ruff Configuration:**
```toml
[tool.ruff.lint]
# Disallow deprecated patterns
select = ["F", "E", "W", "B", "C4"]

[tool.ruff.lint.per-file-ignores]
# Allow in test files only
"**/test_*.py" = ["F401"]  # Unused imports OK in tests
```

**Custom Rules:**
- No `*.backup` files in repo
- No `deprecated` without removal date
- No `backward compat` comments

### 4.2 Manual Review Process

#### **Pre-Commit Checklist**

Before committing:
- [ ] No backwards compatibility code added
- [ ] No fallback patterns introduced
- [ ] No duplicate implementations created
- [ ] No backup files included
- [ ] New concepts vs variations evaluated
- [ ] **PARITY VERIFIED:** If removing code, parity checked first

#### **Code Review Checklist**

Reviewers check:
- [ ] Does this duplicate existing functionality?
- [ ] Is backwards compatibility needed? (Answer: NO)
- [ ] Are fallbacks necessary? (Answer: NO, except performance)
- [ ] Is this a new concept or variation?
- [ ] Are archives/backups handled correctly?
- [ ] **PARITY VERIFIED:** If removing code, was parity verified?
- [ ] **MIGRATION COMPLETE:** Are all callers migrated?
- [ ] **TESTS PASS:** Do tests verify parity?

### 4.3 Enforcement Escalation

#### **Violation Levels**

**Level 1: Warning**
- Minor pattern violation
- Action: Fix in next commit
- Example: Import fallback in non-critical code

**Level 2: Block**
- Significant violation
- Action: Fix before merge
- Example: New backwards compat code

**Level 3: Revert**
- Critical violation
- Action: Revert commit
- Example: Deprecated code reintroduced

#### **Escalation Process**

1. **Automated Detection** → CI fails
2. **Reviewer Feedback** → Request changes
3. **Architecture Review** → If pattern unclear
4. **Policy Update** → If policy needs clarification

---

## 📚 Part 5: Examples & Patterns

### 5.1 Good Patterns ✅

**Performance Fallback (Acceptable):**
```python
# ✅ GOOD: Performance optimization, documented
def fast_json_parse(data: bytes) -> dict:
    """Parse JSON with performance fallback."""
    try:
        return orjson.loads(data)  # Fast path
    except Exception:
        return json.loads(data)  # Slow path (performance fallback)
```

**Strategy Pattern (Acceptable):**
```python
# ✅ GOOD: Multiple strategies, pluggable
class Router:
    strategies = {
        "litellm": LiteLLMRouter(),
        "pareto": ParetoRouter(),
        "auto": AutoRouter(),
    }
```

**Native Optimization (Acceptable):**
```python
# ✅ GOOD: Native vs Python, performance-critical
if IS_NATIVE_AVAILABLE:
    from .native import fast_discovery
else:
    from .python import slow_discovery
```

### 5.2 Bad Patterns ❌

**Backwards Compatibility (Remove):**
```python
# ❌ BAD: Backwards compat shim
def old_function():
    warnings.warn("Deprecated, use new_function()")
    return new_function()  # Remove this entirely
```

**Import Fallback (Remove):**
```python
# ❌ BAD: Import fallback
try:
    from .canonical import thing
except ImportError:
    from .legacy import thing  # Fix imports instead
```

**Duplicate Implementation (Remove):**
```python
# ❌ BAD: Same logic, different file
# file1.py
def parse_config():
    # 50 lines of parsing logic

# file2.py
def parse_config():
    # Same 50 lines, slightly different  # Consolidate!
```

**Backup Files (Remove):**
```bash
# ❌ BAD: Backup files in repo
config.py.backup
.env.backup.20260130
# Use git history instead
```

### 5.3 Migration Examples

**Example 1: Removing Legacy CLI**

**Before:**
```
cli/
  legacy/
    cli_legacy.py  # Old implementation
  apps/
    main.py  # New implementation
```

**After:**
```
cli/
  apps/
    main.py  # Single canonical implementation
```

**Migration Steps:**
1. Find all imports of `cli.legacy`
2. Update to `cli.apps`
3. Delete `cli/legacy/` directory
4. Update tests

**Example 2: Consolidating Config**

**Before:**
```python
# config.py
def get_config():
    return os.environ.get("THGENT_X", "default")

# config_provider.py
def get_config():
    return settings.x  # Different implementation
```

**After:**
```python
# config.py (canonical)
from thegent.config import ThegentSettings

def get_config():
    settings = ThegentSettings()
    return settings.x
```

**Migration Steps:**
1. Migrate `config_provider.py` to use `ThegentSettings`
2. Update all callers
3. Delete `config_provider.py`
4. Update imports

---

## 📊 Part 6: Metrics & Tracking

### 6.1 Key Metrics

**Redundancy Metrics:**
- Code similarity percentage (target: <5%)
- Duplicate function count (target: 0)
- Unused import count (target: 0)

**Legacy Metrics:**
- Deprecated code files (target: 0)
- Backwards compat patterns (target: 0)
- Fallback patterns (target: 0, except performance)

**Archive Metrics:**
- Backup files in repo (target: 0)
- Archive size (track growth)
- Archive access frequency

### 6.2 Reporting

**Weekly:**
- New violations detected
- Fixes completed
- Patterns introduced

**Monthly:**
- Redundancy audit results
- Legacy code removal progress
- Archive cleanup status

**Quarterly:**
- Comprehensive audit
- Policy review
- Metrics trend analysis

---

## 🎯 Summary

### Core Principles

1. **Zero User Debt = Zero Backwards Compatibility**
   - Remove deprecated code immediately
   - No fallback shims
   - Update all callers simultaneously

2. **Consolidate Redundancies**
   - Remove duplicate implementations
   - Consolidate overlapping code
   - Use strategy pattern for variations

3. **Prevent Concept Explosion**
   - New concept vs variation decision framework
   - Clear naming conventions
   - Document distinct capabilities

4. **Manage Archives Properly**
   - No backup files in repo
   - Use git for version history
   - Archive historical code separately

5. **Automate Detection**
   - CI/CD checks for violations
   - Linting rules for patterns
   - Regular audits

### Next Steps

1. **Immediate:** Remove legacy CLI, deprecated stubs, backup files
2. **Short-term:** Consolidate config, SHM, IPC systems
3. **Medium-term:** Archive migration, governance automation
4. **Ongoing:** Quarterly audits, pattern enforcement

---

**Last Updated:** 2026-02-19
**Next Review:** 2026-03-19
**Authority:** Architecture team

---

## Source: governance/BACKWARDS_COMPAT_AUDIT_2026-02-19.md

# Backwards Compatibility & Legacy Code Audit

**Date:** February 19, 2026
**Status:** Initial Audit Complete
**Next Action:** Removal Plan Execution

---

## 🎯 Audit Scope

**Objective:** Identify all backwards compatibility, legacy, fallback, and deprecated patterns that should be removed given zero user debt.

**Methodology:**
- Pattern search: `deprecated`, `legacy`, `backward`, `compat`, `fallback`
- Directory analysis: `cli/legacy/`, `*_legacy.py`, `*_deprecated.py`
- Import analysis: Backward compat shims
- Backup file detection: `*.backup`, `.env-backup-*`

---

## 📊 Findings Summary

| Category | Count | Status | Priority |
|----------|-------|--------|----------|
| **Legacy Directories** | 1 | Found | P1 |
| **Deprecated Files** | 3+ | Found | P1 |
| **Backward Compat Patterns** | 5+ | Found | P1 |
| **Import Fallbacks** | 2+ | Found | P2 |
| **Backup Files** | 10+ | Found | P3 |
| **Archive Directories** | Multiple | Found | P3 |

---

## 🔍 Detailed Findings

### 1. Legacy CLI Directory ⚠️ **P1 - REMOVE**

**Location:** `src/thegent/cli/legacy/`

**Files Found:**
- `cli_legacy.py`
- `cli_impl.py`
- `cli_sync.py`
- `cli_teammates.py`
- `cli_swarm.py`
- `cli_linkcheck.py`
- `cli_initiative.py`
- `cli_git.py`
- `cli_document_queue.py`
- `cli_custom.py`
- `cli_crew.py`
- `cli_concurrency.py`
- `cli_commands_shared_servers.py`
- `__init__.py`

**Status:**
- ✅ Already migrated to use `ThegentSettings` (no `os.environ` fallbacks)
- ⚠️ Still exists as separate directory
- ⚠️ May have callers still importing from `cli.legacy`

**Action:**
1. Find all imports: `grep -r "from.*cli.legacy\|import.*cli.legacy" src/`
2. Update callers to use `cli.apps` or `cli.commands`
3. Delete `cli/legacy/` directory entirely
4. Update tests

**Rationale:** No user debt = no need for legacy CLI

---

### 2. Deprecated Tool Stubs (atoms-mcp-prod) ⚠️ **P1 - REMOVE**

**Locations:**
- `atoms-mcp-prod/src/atoms_mcp/tools/compliance_verification.py`
- `atoms-mcp-prod/src/atoms_mcp/tools/duplicate_detection.py`
- `atoms-mcp-prod/src/atoms_mcp/tools/entity_resolver.py`
- `atoms-mcp-prod/src/atoms_mcp/tools/admin.py`
- `atoms-mcp-prod/src/atoms_mcp/tools/context.py`

**Pattern:**
```python
"""Tool - DEPRECATED.

This module is deprecated. Use tools.entity_modules.operations instead.
"""

import warnings
from .entity_modules.operations import EntityOperations

warnings.warn("...", DeprecationWarning)

# Re-export for backward compatibility
ComplianceVerificationTool = EntityOperations
```

**Status:**
- ⚠️ Backward-compat stubs with deprecation warnings
- ⚠️ Functionality integrated into canonical implementations
- ⚠️ Still imported by test files (76+ test files)

**Action:**
1. Update all test files to import from canonical location
2. Remove stub files entirely
3. Remove deprecation warnings (no longer needed)

**Rationale:** Zero user debt = immediate removal, no deprecation period

---

### 3. Import Fallbacks ⚠️ **P2 - REMOVE**

**Pattern Found:**
```python
# Import cosine_similarity with fallback
try:
    from ..infrastructure.utils import cosine_similarity
except ImportError:
    try:
        from utils import cosine_similarity
    except ImportError:
        # Fallback implementation
        import math
        def cosine_similarity(vec1, vec2):
            # ... implementation
```

**Locations:**
- `atoms-mcp-prod/src/atoms_mcp/tools/compliance_verification.py` (lines 13-29)

**Action:**
1. Fix import paths (ensure dependencies are correct)
2. Remove fallback implementations
3. Use single canonical import path

**Rationale:** Dependencies should be managed, not worked around

---

### 4. Backward Compat Re-exports ⚠️ **P1 - REMOVE**

**Pattern Found:**
```python
# Re-export for backward compatibility
ComplianceVerificationTool = EntityOperations
```

**Locations:**
- Multiple deprecated tool stubs

**Action:**
1. Remove re-exports
2. Update all callers to use canonical names
3. Remove backward compat comments

**Rationale:** No backward compatibility needed

---

### 5. Backup Files ⚠️ **P3 - REMOVE**

**Patterns Found:**
- `*.backup` files
- `.env-backup-*` directories
- `*.backup.*` timestamped files

**Locations:**
- `thegent/crates/Cargo.toml.backup`
- `thegent/test_clode/claude-config/.claude.json.backup.*` (multiple)
- `thegent/dummy_config/.claude.json.backup.*` (multiple)
- `trace/src/tracertm/api/main.py.backup`
- `atoms-mcp-prod/src/atoms_mcp/tools/entity.py.backup`
- `trace/.env-backup-20260130/` (directory)
- `trace/frontend/apps/web/public/specs/openapi.json.backup.*`

**Action:**
1. Delete all `*.backup` files
2. Delete `.env-backup-*` directories
3. Add `*.backup` to `.gitignore`
4. Document git-based backup policy

**Rationale:** Git provides version history, backups are redundant

---

### 6. Archive Directories ⚠️ **P3 - EVALUATE**

**Locations:**
- `trace/ARCHIVE/` - Large directory with historical code
- `archive/` directories in various projects

**Status:**
- ✅ Historical reference (potentially valuable)
- ⚠️ Clutters main codebase
- ⚠️ May contain deprecated code

**Action:**
1. **EVALUATE** each archive directory
2. **MOVE** to separate repo or `.git/archive/` if valuable
3. **DELETE** if contains deprecated code
4. Document archive policy

**Rationale:** Historical context valuable, but shouldn't clutter main codebase

---

### 7. Deprecation Warnings ⚠️ **P1 - REMOVE**

**Pattern Found:**
```python
warnings.warn(
    "tools.compliance_verification is deprecated. Use ... instead.",
    DeprecationWarning,
    stacklevel=2,
)
```

**Locations:**
- Deprecated tool stubs
- Potentially other deprecated code

**Action:**
1. Remove deprecation warnings
2. Remove deprecated code entirely
3. No need for warnings if code is deleted

**Rationale:** No deprecation period needed if no users

---

## 📋 Removal Plan (With Parity Verification)

### Phase 1: Immediate (Week 1)

**Priority 1: Legacy CLI**
- [ ] **PARITY CHECK:** Verify `cli/apps/` has all features from `cli/legacy/`
  - [ ] List all functions/commands in `cli/legacy/`
  - [ ] Verify each exists in `cli/apps/` or `cli/commands/`
  - [ ] Document any differences
- [ ] **MIGRATION CHECK:** Verify all callers migrated
  - [ ] Find all imports: `grep -r "cli.legacy\|cli/legacy" src/ tests/`
  - [ ] Update callers to `cli.apps` or `cli.commands`
  - [ ] Verify no remaining imports
- [ ] **TEST CHECK:** Run parity tests
  - [ ] Create parity test comparing old vs new
  - [ ] Run tests with both implementations
  - [ ] Verify outputs match
- [ ] **ONLY AFTER PARITY VERIFIED:** Delete `src/thegent/cli/legacy/` directory
- [ ] Update tests
- [ ] Update documentation

**Priority 2: Deprecated Stubs**
- [ ] **PARITY CHECK:** Verify canonical implementations have all features
  - [ ] List all features in deprecated stubs
  - [ ] Verify each exists in canonical implementations
  - [ ] Document any differences
- [ ] **MIGRATION CHECK:** Verify all test files migrated
  - [ ] Find all test imports: `grep -r "compliance_verification\|duplicate_detection\|entity_resolver" tests/`
  - [ ] Update test files to canonical imports
  - [ ] Verify no remaining imports
- [ ] **TEST CHECK:** Run tests with canonical implementations
  - [ ] Run full test suite
  - [ ] Verify no functionality lost
- [ ] **ONLY AFTER PARITY VERIFIED:** Delete stub files:
  - `atoms-mcp-prod/src/atoms_mcp/tools/compliance_verification.py`
  - `atoms-mcp-prod/src/atoms_mcp/tools/duplicate_detection.py`
  - `atoms-mcp-prod/src/atoms_mcp/tools/entity_resolver.py`
  - `atoms-mcp-prod/src/atoms_mcp/tools/admin.py`
  - `atoms-mcp-prod/src/atoms_mcp/tools/context.py`
- [ ] Remove deprecation warnings

**Priority 3: Backup Files**
- [ ] Find all backups: `find . -name "*.backup" -o -name ".env-backup-*"`
- [ ] Delete backup files
- [ ] Add `*.backup` to `.gitignore`
- [ ] Document git-based backup policy

### Phase 2: Short-Term (Weeks 2-3)

**Import Fallbacks:**
- [ ] Fix import paths in `compliance_verification.py`
- [ ] Remove fallback implementations
- [ ] Ensure dependencies are correct

**Backward Compat Re-exports:**
- [ ] Find all re-exports: `grep -r "backward compat\|re-export" src/`
- [ ] Update callers to canonical names
- [ ] Remove re-exports

**Archive Evaluation:**
- [ ] Audit `trace/ARCHIVE/` contents
- [ ] Move valuable archives to separate repo
- [ ] Delete deprecated code from archives

### Phase 3: Ongoing

**Pattern Prevention:**
- [ ] Add CI checks for deprecated patterns
- [ ] Add linting rules for fallbacks
- [ ] Document removal process

---

## 🔍 Detection Commands

### Find Legacy Code
```bash
# Find legacy directories
find . -type d -name "legacy" -not -path "*/\.*" -not -path "*/node_modules/*"

# Find deprecated files
find . -name "*deprecated*" -o -name "*legacy*" -not -path "*/\.*"

# Find backward compat patterns
grep -r "backward\|backwards\|compat" --include="*.py" src/ | grep -v "__pycache__"
```

### Find Backup Files
```bash
# Find backup files
find . -name "*.backup" -not -path "*/\.*" -not -path "*/node_modules/*"

# Find backup directories
find . -type d -name "*backup*" -not -path "*/\.*"

# Find timestamped backups
find . -name "*.backup.*" -not -path "*/\.*"
```

### Find Import Fallbacks
```bash
# Find try/except import patterns
grep -r "try:.*import\|except.*import" --include="*.py" src/ | grep -v "__pycache__"

# Find fallback implementations
grep -r "fallback\|Fallback" --include="*.py" src/ | grep -v "__pycache__"
```

### Find Deprecation Warnings
```bash
# Find deprecation warnings
grep -r "DeprecationWarning\|deprecated" --include="*.py" src/ | grep -v "__pycache__"
```

---

## ✅ Verification Checklist

**Before Removal (Parity Verification):**
- [ ] Parity verification completed
- [ ] Feature comparison documented
- [ ] All callers migrated
- [ ] Parity tests pass
- [ ] Migration completeness verified
- [ ] Approval obtained

**After Removal:**
- [ ] No `cli/legacy/` directory exists
- [ ] No deprecated tool stubs exist
- [ ] No `*.backup` files in repo
- [ ] No import fallbacks remain
- [ ] No backward compat re-exports
- [ ] All tests pass
- [ ] No broken imports
- [ ] Documentation updated
- [ ] **REGRESSION CHECK:** No functionality lost
- [ ] **REGRESSION CHECK:** Performance acceptable

---

## 📊 Metrics

**Before Removal:**
- Legacy directories: 1
- Deprecated files: 5+
- Backup files: 10+
- Import fallbacks: 2+

**Target (After Removal):**
- Legacy directories: 0
- Deprecated files: 0
- Backup files: 0
- Import fallbacks: 0 (except performance)

---

**Status:** Audit Complete
**Next Step:** Execute Phase 1 Removal Plan
**Owner:** Architecture Team

---

## Source: governance/CONTEXT_DOCS_PROCESS.md

# Context Documentation Creation & Maintenance Process

This document provides step-by-step procedures for creating, updating, and maintaining context documents for technologies integrated with thegent.

---

## Quick Reference

| Task | When | Owner | Est. Time |
|------|------|-------|-----------|
| Create new context doc | Before technology integration | Tech Owner | 2-4 hours |
| Update existing doc | After major version; >90 days stale | Tech Owner | 1-2 hours |
| Verify accuracy | Before using in production code | Implementer | 30-60 min |
| Refresh staleness dates | Monthly/quarterly review | Automation | 5 min |
| Archive tech doc | Technology deprecated/superseded | Deprecation Lead | 15 min |

---

## When to Create a Context Doc

A context doc is **required** (P0/P1 priority) when:

1. **Starting integration of a new technology**
   - Before writing a single line of integration code
   - Example: Adding Codex support → create `docs/context/codex.md` first

2. **Implementing a new protocol/SDK**
   - If thegent will directly call or wrap the technology
   - Example: FastMCP adoption → create `docs/context/fastmcp.md`

3. **Technology referenced in 3+ places** in the codebase
   - Even if integration is partial, a context doc prevents scattered understanding
   - Use codebase search to count references

4. **During research/spike of new technology**
   - If the spike results in "yes, we'll integrate this", document findings in a context doc
   - Move research notes from `docs/research/` to `docs/context/` as the tech is adopted

---

## Step-by-Step Process: Creating a New Context Doc

### Phase 1: Preparation (15-30 min)

#### Step 1.1: Check if doc already exists

```bash
# Check atomic docs
ls docs/context/{technology}.md

# Check doc sets
ls -la docs/context/{technology}/

# Search for mentions in existing docs
grep -r "{technology}" docs/context/
```

If found: Update existing doc instead (skip to "Updating a Context Doc" section).

#### Step 1.2: Assign ownership

- Identify a **Technology Owner** (the person implementing the integration)
- They will be responsible for initial draft + verification
- Add to ticket/issue: `Tech Owner: @person`

#### Step 1.3: Gather official sources

Collect authoritative reference materials:

- Visit official documentation URL
- Check GitHub repo for README, API docs, architecture
- Download or archive key pages (use webarchive.org if fleeting)
- Note the fetch date (YYYY-MM-DD)

For local tools/SDKs:
- Extract from installed package docs
- Run tool help command
- Check source code for API signatures
- Run local examples to verify behavior

For APIs:
- Download official API reference
- Test endpoints with actual requests (rate-limit aware)
- Document observed behavior vs. stated behavior
- Note any undocumented quirks or gotchas

Save sources in a working directory (e.g., `/tmp/tech-docs/`).

#### Step 1.4: Identify the doc type

Decide: **Atomic doc** (single file) or **Doc set** (directory)?

- **Atomic**: Technology is single-purpose or small API surface area
  - Examples: OpenRouter (API), WorkOS (auth), Nix (package manager)
  - File: `docs/context/{technology}.md`

- **Doc set**: Technology is large or multi-faceted
  - Examples: Ante (agent platform), Claude Code (harness), Codex (IDE)
  - Files: `docs/context/{technology}/index.md` + subdocs
  - When > 2000 words needed, use doc set

Choose atomic unless the technology logically breaks into 4+ major sections.

---

### Phase 2: Information Extraction (45-90 min)

#### Step 2.1: Extract key technical details

Create a working document and extract:

1. **Foundational questions**
   - What problem does it solve?
   - What is it NOT (what shouldn't I use it for)?
   - How does thegent use it?
   - Key architectural patterns?

2. **API/Interface specs** (if applicable)
   - Endpoints, methods, or function signatures
   - Required headers, query params, body fields
   - Response format and error responses
   - Rate limits, quotas, timeouts

3. **Authentication**
   - What credential types? (API key, token, OAuth, cert)
   - Where to obtain? (console URL, command, etc.)
   - Required headers or environment vars
   - Expiration, rotation, or refresh behavior

4. **Concepts & Terminology**
   - Domain-specific terms (e.g., "model routing", "agent turn")
   - Key data structures or enums
   - Important constraints or guarantees

5. **Typical usage patterns**
   - Happy path: How do you normally use this?
   - Error handling: What can go wrong?
   - Async/streaming: Does it support it?
   - Pagination: How to handle large result sets?

#### Step 2.2: Test with real examples

For APIs:
- Get actual response shapes with curl or similar
- Note the response structure, field types, any nested objects
- Save to working docs

For SDKs:
- Test in Python REPL or script
- Check return type
- Inspect fields

For CLIs:
- Run with --help to document flags
- Run example commands and capture output

Save all output to working docs for reference during writing.

#### Step 2.3: Identify gotchas and edge cases

Search docs/repos for:
- "Note:", "Important:", "Gotcha", "Common mistake"
- GitHub issues marked "documentation" or "FAQ"
- StackOverflow questions about common problems

Document these in "Common Patterns" or error handling section of the context doc.

---

### Phase 3: Writing (90-180 min)

#### Step 3.1: Use the governance template

Open `docs/context/GOVERNANCE.md` and follow the required structure:

1. Header (title, description, sources)
2. What is {Technology}
3. Key Concepts
4. API/Interfaces
5. Authentication
6. Code Examples
7. Sources & References
8. Quick Reference

Do not skip sections. Use empty sections if not applicable, but mark them explicitly.

#### Step 3.2: Write each section

**Section 1: Header** - Include title, description, sources with fetch date

**Section 2: What is {Technology}** - Start with definition, explain problem, bullet capabilities, why thegent uses it. Target: 150-300 words.

**Section 3: Key Concepts** - Only if technology has domain-specific terms. Format as `**Term**: definition` or simple table.

**Section 4: API/Interfaces**

For HTTP APIs:
- Endpoint path: `METHOD /path`
- Description of what it does
- Exact request format (headers, body, query params)
- Exact response format (JSON structure, types)
- Status codes (200, 400, 401, 429, 500, etc.)

For SDKs/libraries:
- Class/module name
- Constructor signature and defaults
- Method signatures with type hints
- Return types

For CLIs:
- Command structure: `tool subcommand --flags`
- Required vs optional flags
- Output format
- Exit codes

Be precise with types and fields.

**Section 5: Authentication**

- Type of credential (API key, token, OAuth, etc.)
- Where to get it (URL + steps)
- How to provide it (header, query param, env var)
- Rate limits or quotas
- Any special headers or metadata

**Section 6: Code Examples**

1-3 examples covering main use cases. All examples must be **tested and working**.

**Section 7: Sources & References**

Complete citations with URLs and dates.

**Section 8: Quick Reference**

One-page cheat sheet. Include base URL, auth, rate limits, response format, common patterns, most-used endpoints, common errors.

#### Step 3.3: Cross-check against sources

For each section, verify:
- Every API endpoint exists in official docs
- Every field type is correct
- Every error code is documented
- Every code example is syntactically valid

#### Step 3.4: Run code examples

Before finalizing, test all code examples:
- Python: `python -c "..."`
- Shell: `bash example.sh`
- Node: `node example.js`

Capture actual output and include in doc as comments.

---

### Phase 4: Integration & Verification (30-60 min)

#### Step 4.1: Create the file

If atomic doc:
```bash
cat > docs/context/{technology}.md << 'EOF'
[Full document content]
EOF
```

If doc set:
```bash
mkdir -p docs/context/{technology}
# Create index.md and subdocs
```

#### Step 4.2: Update docs/context/INDEX.md

Add entry to the index table.

#### Step 4.3: Cross-reference with implementation code

If integrating a new technology:
- Add comments linking to context doc sections
- Example: `# See docs/context/openrouter.md - API/Interfaces section`
- Update any README or architecture docs to reference the context doc

#### Step 4.4: Verify against pre-write validation

All required sections should be present:
- Title
- What is section
- Key Concepts (if applicable)
- API section (if applicable)
- Authentication section
- Code Examples
- Sources & References
- Quick Reference

#### Step 4.5: Peer review (if new doc)

- Request review from tech lead and implementer
- Reviewer checks:
  - No hallucination (compare examples against official docs)
  - Clarity and completeness
  - Code examples actually work
  - All API specs are accurate
- Approval required before merge

---

### Phase 5: Completion

#### Step 5.1: Commit message

```
add: context doc for {technology}

Covers:
- API endpoints and authentication
- Key concepts and terminology
- Working code examples
- Quick reference

Closes #{issue}
```

#### Step 5.2: Link from integration PR

If creating doc as part of implementing a feature:
- Reference the context doc in your implementation PR
- Mention in PR description: "See docs/context/{tech}.md for API reference"

#### Step 5.3: Update CHANGELOG

If significant new context doc:
```markdown
## [Unreleased]

### Added
- Context documentation for {Technology} (docs/context/{technology}.md)
  Covers API, authentication, key concepts, and usage patterns.
```

---

## Updating an Existing Context Doc

### When to Update

1. **After major version release** (X.0.0 bump)
2. **After breaking API change** (endpoint removal, field deprecation)
3. **Quarterly staleness check** (every 90 days minimum)
4. **When implementing a feature** and discovering inaccuracies

### Quick Update (Minor)

For small changes (typo, date refresh, minor clarification):

1. Edit `docs/context/{technology}.md` directly
2. Update `Last Verified` date in header
3. If stale banner exists, remove it (if doc is current)
4. Commit: `fix: update {tech} context doc - {brief description}`
5. No review needed for minor updates

### Major Update

If API changed significantly or 6+ months since last update:

1. Fetch latest official docs
2. Update "Sources" section with new URLs and fetch date
3. Update all API sections (new endpoints, removed endpoints, changed fields)
4. Test code examples against latest version
5. Update "Changelog" section (if exists) with changes
6. Request peer review (1 approval required)
7. Commit: `update: {tech} context doc for v{version}`

---

## Creating and Maintaining docs/context/INDEX.md

The index is the **canonical catalog** of all context docs.

### Basic Structure

```markdown
# Context Documentation Index

> Authoritative reference catalog for all technologies integrated with thegent.

## Index by Technology

| Technology | File | Category | Priority | Last Updated | Status |
|-----------|------|----------|----------|--------------|--------|
| OpenRouter | openrouter.md | API Gateway | P0 | 2026-02-20 | ✅ Current |
| Claude Code | claude-code.md | Agent Harness | P0 | 2026-02-20 | ✅ Current |

## Index by Category

### Agent Harnesses (P0)
- Ante: ante/index.md
- Claude Code: claude-code.md

### API Gateways & Proxies (P0)
- OpenRouter: openrouter.md
```

### Updating INDEX.md

Every time you:
- **Create** a new context doc: Add row to table
- **Update** a context doc: Update `Last Updated` date and status
- **Mark stale**: Update status to `⚠️ Stale (N days)`
- **Archive** a doc: Remove from main table, add to "Archived" section

---

## Verification Checklist: Before Using a Context Doc

Before referencing a context doc in implementation code, verify accuracy:

### Quick Verification (10-15 min)

- Header has recent fetch date (< 6 months)
- No `⚠️ Possibly stale` banner
- Read "What is {Tech}" section - aligns with your understanding
- Skim code examples - syntax looks correct

### Full Verification (30-60 min)

If integrating a technology for the first time:

- Test 3-5 API examples from context doc against actual API/SDK
- Verify auth setup matches what's documented
- Run at least one code example without modification
- Check that error handling matches real errors
- Spot-check 5 random claims against official docs

**If you find inaccuracies**: File issue and update context doc before proceeding.

---

## Troubleshooting

### Problem: "Context doc exists but has wrong info"

1. Identify what's wrong
2. Check official docs for correct info
3. Update context doc with correct info
4. Add to changelog if applicable
5. Commit: `fix: correct {field} in {tech} context doc`

### Problem: "Technology is P0 but has no context doc"

1. Create issue: `[MISSING] Create context doc for {technology} (P0)`
2. Assign to technology owner
3. Follow "Creating a New Context Doc" process above
4. Update INDEX.md once created

### Problem: "Doc is stale (> 90 days) and technology version changed"

1. Note the version that changed
2. Fetch latest official docs for that version
3. Identify what changed in the API/behavior
4. Update context doc sections that changed
5. Update `Last Verified` date
6. Remove staleness banner if all sections are current
7. Commit: `update: {tech} context doc for v{version}`

### Problem: "I'm implementing a feature and discovered the context doc is wrong"

1. Pause implementation
2. Check official docs to confirm the error
3. File issue: `[INACCURACY] {tech} context doc - {field} is incorrect`
4. Update context doc with correct info
5. Add code comment linking to updated doc
6. Resume implementation

---

## See Also

- `docs/context/GOVERNANCE.md` - Standards and requirements
- `docs/context/INDEX.md` - Catalog of all context docs
- `docs/governance/ARCHITECTURAL_GOVERNANCE.md` - Integration with architecture decisions

---

## Source: governance/COST_GOVERNANCE_DESIGN.md

# Cost Governance Design (G-GP-06)

**Purpose:** Design per-run cost tracking and budget governance.
**Date:** 2026-02-14
**Status:** Design
**Source:** GOVERNANCE_POLICY_AUDIT_RESEARCH, WP-5003

---

## 1. Current State

- **Gap:** No per-run cost tracking; no budget alerts.
- **Existing:** `cost_weight` on Route in catalog (static, for routing preference).

---

## 2. Design Goals

1. **Per-run cost:** Estimate or record cost per run (tokens, API calls).
2. **Budget alerts:** Warn when daily/run budget exceeded.
3. **Cost-per-quality:** Optional cost vs. confidence/quality correlation.

---

## 3. Architecture

```
Run start
    ↓
RunRegistry.register_start(..., estimated_cost=0)
    ↓
Run end
    ↓
CostEstimator.estimate(run_meta, tokens_in, tokens_out, model) → cost_usd
    ↓
RunRegistry.register_end(..., cost_usd=cost)
    ↓
CostAggregator.daily_total(owner) → sum
    ↓
[If daily_total > budget] → emit alert, optional block
```

---

## 4. Cost Estimation

| Source | Method |
|-------|--------|
| Provider pricing table | Static $/1k tokens per model |
| Run metadata | tokens_in, tokens_out from runner (if available) |
| Fallback | Heuristic: prompt_length * 1.3 + 500 for output |

---

## 5. Implementation Phases

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| P1 | Design doc (this) | Done |
| P2 | CostEstimator; pricing table (config) | 2–3 days |
| P3 | RunRegistry cost fields; register_end cost | 1–2 days |
| P4 | CostAggregator; daily rollup; budget config | 2–3 days |
| P5 | Alert emission; optional pre-run budget check | 1–2 days |

---

## 6. Configuration

```yaml
governance:
  cost:
    enabled: false
    daily_budget_usd: 10.0
    budget_scope: owner  # owner | global
    alert_on_exceed: true
    block_on_exceed: false
  pricing:
    # $ per 1k tokens (input, output)
    claude-sonnet-4: [0.003, 0.015]
    gemini-3-flash: [0.0001, 0.0004]
```

---

## 7. References

- `docs/GOVERNANCE_WP_VERIFICATION.md` — G-GP-06
- `src/thegent/execution.py` — RunRegistry
- `docs/research/COST_ROUTING_DEFERRED.md`

---

## Source: governance/DECISION_METHODOLOGY.md

# Decision Methodology: Keep vs Remove

**Quick Reference Guide** for architectural decisions

---

## 🎯 Core Principle

**Zero User Debt = Zero Backwards Compatibility**

If we have no external users, we maintain no backwards compatibility. All changes are breaking changes by design.

**🛡️ Critical Safety Rule: Always verify parity/migrations BEFORE removals**

This acts as a regression guard to prevent breaking changes.

**🤖 AI Agent Pattern: Agents systematically add fallbacks**

AI coding agents (Claude, Codex, ChatGPT) have a systemic tendency to add fallbacks and legacy compatibility even when explicitly told not to. This requires:
- Explicit rules in AGENTS.md/CLAUDE.md
- "Aim towards" framing (positive direction, not just "don't do X")
- Fail fast philosophy (code should fail and stop)
- CI checks for fallback patterns

---

## 🤔 Decision Trees

### Decision 1: Is This Backwards Compatibility?

```
Is this code kept for backwards compatibility?
│
├─ YES → REMOVE
│   └─ No user debt = no backwards compat needed
│
└─ NO → Continue to Decision 2
```

**Examples:**
- ❌ Legacy CLI directory → **REMOVE**
- ❌ Deprecated tool stubs → **REMOVE**
- ❌ Backward compat re-exports → **REMOVE**

---

### Decision 2: Is This a Fallback?

```
Is this a fallback pattern?
│
├─ Performance Fallback → KEEP (if documented)
│   └─ Example: try: fast_path(); except: slow_path()
│
├─ Compatibility Fallback → REMOVE
│   └─ Example: try: new(); except: old()
│
└─ Dependency Fallback → REMOVE
    └─ Example: try: from X import Y; except: from Z import Y
```

**Examples:**
- ✅ Performance: Fast JSON parser with slow fallback → **KEEP**
- ❌ Compatibility: New API with old API fallback → **REMOVE**
- ❌ Dependency: Import fallback → **REMOVE** (fix imports instead)

---

### Decision 3: Is This Duplication?

```
Are there multiple implementations of the same thing?
│
├─ Exact Duplication → CONSOLIDATE
│   └─ Same logic, different files
│
├─ Performance Optimization → KEEP BOTH (if documented)
│   └─ Native vs Python, fast vs slow path
│
├─ Strategy Pattern → KEEP BOTH (if distinct)
│   └─ Different algorithms for same problem
│
└─ Unclear Purpose → EVALUATE
    └─ Can't explain why two exist
```

**Examples:**
- ❌ Same parsing logic in 2 files → **CONSOLIDATE**
- ✅ Native Rust vs Python implementation → **KEEP BOTH**
- ✅ Multiple routing strategies → **KEEP BOTH** (strategy pattern)
- ❌ Two config systems doing same thing → **CONSOLIDATE**

---

### Decision 4: Is This a New Concept or Variation?

```
Is this a new concept or variation of existing?
│
├─ New Problem → NEW CONCEPT
│   └─ Create new module
│
├─ Different Strategy → VARIATION
│   └─ Add to existing module (strategy pattern)
│
├─ Performance Optimization → IMPLEMENTATION DETAIL
│   └─ Same module, different implementation
│
└─ Unclear → EVALUATE
    └─ Review with team
```

**Examples:**
- ✅ New agent type solving new problem → **NEW CONCEPT**
- ✅ Different routing algorithm → **VARIATION** (strategy)
- ✅ Fast vs slow implementation → **IMPLEMENTATION DETAIL**
- ❌ Can't explain difference → **EVALUATE**

---

### Decision 5: Is This Archive/Backup?

```
Is this an archive or backup?
│
├─ Historical Reference → ARCHIVE (move to separate repo)
│   └─ Valuable context, but clutters main codebase
│
├─ Backup File → DELETE
│   └─ Use git history instead
│
├─ Deprecated Code → DELETE
│   └─ No need to archive deprecated code
│
└─ Temporary File → DELETE
    └─ Should be cleaned up automatically
```

**Examples:**
- ✅ Historical architecture docs → **ARCHIVE** (move to separate repo)
- ❌ `*.backup` files → **DELETE** (use git)
- ❌ Deprecated code → **DELETE** (no archive needed)
- ❌ Temporary test files → **DELETE**

---

## 📋 Quick Checklist

**Before removing code, ALWAYS verify:**

- [ ] **PARITY CHECKED:** New implementation has all features?
- [ ] **MIGRATION COMPLETE:** All callers migrated?
- [ ] **TESTS PASS:** Parity tests verify behavior?
- [ ] **DOCUMENTED:** Parity verification documented?

**Before adding code, ask:**

- [ ] **Is this backwards compatibility?** → **REMOVE** (after parity check)
- [ ] **Is this a compatibility fallback?** → **REMOVE** (after parity check)
- [ ] **Is this exact duplication?** → **CONSOLIDATE** (after parity check)
- [ ] **Is this a backup file?** → **DELETE**
- [ ] **Is this deprecated code?** → **DELETE** (after parity check)

**Before keeping code, ask:**

- [ ] **Does it solve a NEW problem?** → New concept
- [ ] **Is it a different STRATEGY?** → Variation (strategy pattern)
- [ ] **Is it a PERFORMANCE optimization?** → Implementation detail
- [ ] **Can I explain why two exist?** → If no, consolidate

---

## 🚫 Anti-Patterns (Never Do)

1. ❌ **Silent fallbacks** (AI agents love these!)
   - Pattern: `try: do_thing(); except: pass` or `try: do_thing(); except: return default`
   - Action: **REMOVE**, code should fail and stop
   - **AI Guard:** Explicit rule in AGENTS.md: "Code must fail loudly, no silent fallbacks"

2. ❌ **Backwards compatibility shims**
   - Pattern: `def old(): warnings.warn(); return new()`
   - Action: **DELETE** old function, update callers

3. ❌ **Legacy compatibility layers**
   - Pattern: `if legacy_flag: old(); else: new()`
   - Action: **REMOVE** flag and old code
   - **AI Guard:** "No legacy compatibility. Zero user debt = zero backwards compatibility"

4. ❌ **Import fallbacks**
   - Pattern: `try: from X import Y; except: from Z import Y`
   - Action: **FIX** imports, remove fallback

5. ❌ **Deprecated code with warnings**
   - Pattern: `warnings.warn("deprecated")` but code still exists
   - Action: **DELETE** code, no warnings needed

6. ❌ **Backup files in repo**
   - Pattern: `*.backup`, `.env-backup-*`
   - Action: **DELETE**, use git history

7. ❌ **Duplicate implementations**
   - Pattern: Same logic in multiple files
   - Action: **CONSOLIDATE** into single implementation

8. ❌ **Error hiding**
   - Pattern: `try: thing(); except: delete_from_db()` (hide bugs)
   - Action: **REMOVE**, fix the bug instead
   - **AI Guard:** "Never hide errors. Fail fast, fail loudly."

---

## ✅ Good Patterns (Do This)

1. ✅ **Performance fallbacks** (documented)
   ```python
   def fast_parse(data):
       try:
           return orjson.loads(data)  # Fast
       except:
           return json.loads(data)  # Slow (performance fallback)
   ```

2. ✅ **Strategy pattern** (distinct strategies)
   ```python
   class Router:
       strategies = {
           "litellm": LiteLLMRouter(),
           "pareto": ParetoRouter(),
       }
   ```

3. ✅ **Native optimizations** (performance-critical)
   ```python
   if IS_NATIVE_AVAILABLE:
       from .native import fast_discovery
   else:
       from .python import slow_discovery
   ```

---

## 🎯 Decision Matrix

| Pattern | Keep? | Rationale |
|---------|-------|-----------|
| Backwards compat shim | ❌ NO | No user debt |
| Deprecated code | ❌ NO | Delete immediately |
| Compatibility fallback | ❌ NO | Fix instead of fallback |
| Performance fallback | ✅ YES | If documented |
| Exact duplication | ❌ NO | Consolidate |
| Strategy pattern | ✅ YES | If distinct strategies |
| Native optimization | ✅ YES | Performance-critical |
| Backup files | ❌ NO | Use git |
| Archive (historical) | ✅ YES | Move to separate repo |

---

## 📚 References

- **Full Governance:** `docs/governance/ARCHITECTURAL_GOVERNANCE.md`
- **Audit Report:** `docs/governance/BACKWARDS_COMPAT_AUDIT_2026-02-19.md`
- **Policy:** Zero user debt = zero backwards compatibility

---

**Last Updated:** 2026-02-19
**Quick Reference:** Use this for daily decisions

---

## Source: governance/GOVERNANCE_SUMMARY.md

# Architectural Governance Summary

**Status:** Active
**Scope:** Mandatory harness contract gates for merge readiness

## Core Rule

Merge only when both mandatory harness contract gates pass.

## CI Section

- The `quality` workflow job is fail-closed for harness gates.
- CI always executes both mandatory gates, captures each exit code, and fails the job if either gate fails.
- The quality lane remains limited to these mandatory harness gates; no extra governance lanes are required there.

## Mandatory Harness Contract Gates

- `task quality:sitback-contracts`
- `task quality:harness-model-contracts`

## Deterministic Benchmark Governance (WL-079)

- CI must run deterministic benchmark smoke via `task bench:smoke:ci`.
- The CI step `Deterministic benchmark smoke` must call the task wrapper only; do not inline raw `cargo bench` in workflow YAML.
- The benchmark command must stay offline and locked:
  `CARGO_NET_OFFLINE=true cargo bench --locked --manifest-path crates/Cargo.toml -p thegent-router --bench audit_bench`
- PR readiness is blocked if the CI step named `Deterministic benchmark smoke` is missing from `.github/workflows/ci.yml`.

## Contract Verification Evidence

Use this compact checklist to verify the contract gates and document outcomes.

| Check | Command | Expected outcome |
|---|---|---|
| Sitback contracts gate | `task quality:sitback-contracts` | Exit code `0`; contract suite reports pass |
| Harness model contracts gate | `task quality:harness-model-contracts` | Exit code `0`; contract suite reports pass |
| Gate list present in governance summary | `rg -n "task quality:(sitback-contracts|harness-model-contracts)" docs/governance/GOVERNANCE_SUMMARY.md` | Exactly 2 matches |
| Evidence subsection present | `rg -n "^## Contract Verification Evidence$" docs/governance/GOVERNANCE_SUMMARY.md` | Exactly 1 match |

## Quick Links

- Full policy: `docs/governance/ARCHITECTURAL_GOVERNANCE.md`
- Contract definitions: `docs/governance/METRIC_CONTRACTS.md`
- WBS coordination: `docs/reference/WBS_AGENT_PROGRESS.md`

## Batch-1 Agent-6 Verification Note (2026-02-21)
- Command: `uv run pytest -k inject_proxy_models tests/routing/test_request_extensions.py`
- Signal: PASS (`7 passed, 12 deselected`)

## Regression-Spiral Guardrail (2026-02-21)
- After every batch merge, run `task quality:harness-contracts:list-check` first, then run both mandatory gates: `task quality:sitback-contracts` and `task quality:harness-model-contracts`.
- Treat merge readiness as blocked until all three commands exit with code `0` in the post-merge run.

## Operator Checklist (List-Check vs Quick vs Full)

| Chain | Command | Use when |
|---|---|---|
| List-check only | `task quality:harness-contracts:list-check` | Verify harness contract task names are present before running any gate chain |
| Smoke alias | `task quality:list-check` | Run the same list-check through the short alias for a quick preflight |
| Quick harness chain | `task quality:harness-contracts:quick` | Run a fast local harness sanity check before commit |
| Full harness chain | `task quality:harness-contracts` | Run merge-readiness and post-merge harness verification |

## Runtime Modularization Matrix (WL-130)

Source: `contracts/runtime/runtime-modularization-matrix.json`
Last Updated: 2026-02-21

| Workload | Current | Target | Priority | Status |
|----------|---------|--------|----------|--------|
| CLI dispatch | Python monolith (cli.py, impl.py) | Python frontmatter + Rust helpers | P0 | in_progress |
| Policy/gate evaluation | Mixed Python + shell (hooks pipeline) | Rust backmatter (thegent-hooks) | P0 | in_progress |
| MCP transport/tool registry | Python monolith (mcp/server.py) | Python thin transport + Rust utilities | P1 | planned |
| Low-level memory/layout primitives | Zig POC interop | Zig ABI contract (thegent-zmx-interop) | P2 | planned |
| Deterministic scoring/ranking kernels | Placeholder Python/Mojo bridge | Mojo kernel contracts | P2 | planned |

> Machine-readable contract: `contracts/runtime/runtime-modularization-matrix.json`

## Runtime Matrix (B90 Wave-2)

The polyglot runtime modularization matrix is maintained at `contracts/runtime/runtime-modularization-matrix.json`.

| Runtime | Workload | Status |
|---------|----------|--------|
| Python  | parse_model_suffix baseline | done |
| Rust    | parse_model_suffixes (PyO3) | in_progress |
| Zig     | ABI contract v1.0.0 | in_progress |
| Mojo    | deterministic kernel smoke | in_progress |

For promotion criteria, see `docs/governance/POLYGLOT_RUNTIME_COVERAGE_AND_CONVERSION_MATRIX_2026-02-21.md`.

---

## Source: governance/HITL_DESIGN.md

# HITL (Human-in-the-Loop) Design (G-GP-05)

**Purpose:** Design checkpoint-based HITL, escalation path, and policy-driven approval.
**Date:** 2026-02-14
**Status:** Design
**Source:** GOVERNANCE_POLICY_AUDIT_RESEARCH, WP-3008, 4004

---

## 1. Current State

- **Override:** `--override-reason` bypasses policy deny; OverrideRegistry with TTL.
- **Gap:** No formal interrupt checkpoint; no escalation queue for exhausted retries.

---

## 2. Design Goals

1. **Checkpoint-based HITL:** Pause at defined checkpoints; await human approval.
2. **Escalation path:** When retries exhausted, route to escalation queue with SLA.
3. **Policy-driven approval:** Policy "deny" can require HITL approval before override.

---

## 3. Architecture

```
Run start
    ↓
[Checkpoint 1: Pre-execution] Policy deny? → EscalationQueue.add(run_meta, reason)
    ↓
Run execution
    ↓
[Checkpoint 2: Post-execution] Low confidence? → HITL gate (optional)
    ↓
Run end
```

**EscalationQueue:** `list_pending(past_sla_only)` — already exists in cli_impl.
**HITL gate:** New — block run completion until human approves or rejects.

---

## 4. Implementation Phases

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| P1 | Design doc (this) | Done |
| P2 | Escalation SLA config; SLA breach alert | 1–2 days |
| P3 | HITL checkpoint enum; optional pause before run | 2–3 days |
| P4 | Approval workflow (CLI: govern approve/reject) | 2–3 days |

---

## 5. Configuration

```yaml
governance:
  hitl:
    enabled: false
    checkpoints: [pre_execution, post_execution]
    escalation_sla_minutes: 60
  escalation:
    sla_breach_alert: true
```

---

## 6. References

- `docs/GOVERNANCE_WP_VERIFICATION.md` — G-GP-05
- `src/thegent/cli_impl.py` — EscalationQueue, escalate_add_impl
- `src/thegent/execution.py` — PolicyEngine, OverrideRegistry

---

## Source: governance/METRIC_CONTRACTS.md

# Metric Contracts

Hard governance contracts for:

- quality
- security
- reliability
- extensibility
- other code hygiene metrics

---

## Contract Files

- Active contract: `contracts/metric-contracts.json`
- Schema: `schemas/metric-contracts.schema.json`
- Reusable template: `templates/quality/metric-contracts.json`

---

## Gate

`hooks/governance-gates.sh` now includes `gate_metric_contracts` (fail-closed capable).

Gate report output:

- `.claude/verification/metric-contracts-gate.json`

Metrics report input (configurable in contract):

- default: `.claude/verification/quality-metrics.json`

---

## Enablement

`thegent setup` bootstraps both:

- `contracts/metric-contracts.json`
- `.claude/quality.json` with `governance.metric_contracts.enforce_gate=true`

Set in project `quality.json`:

```json
{
  "governance": {
    "metric_contracts": {
      "enforce_gate": true
    }
  }
}
```

On `critical` tier, this gate is also forced on by policy.

---

## Minimal Metrics Payload

```json
{
  "generated_at": "2026-02-20T00:00:00Z",
  "quality": { "lint_errors": 0, "type_errors": 0, "test_pass_rate": 1.0 },
  "security": { "critical_vulns": 0, "high_vulns": 0, "secrets_detected": 0 },
  "reliability": { "flake_rate": 0.0, "pass_rate": 1.0 },
  "extensibility": { "max_file_lines": 420, "max_function_lines": 45 },
  "other": { "todo_markers": 0 }
}
```

---

## Source: governance/NEMO_GUARDRAILS_DESIGN.md

# NeMo Guardrails Design (G-GP-02)

**Purpose:** Design input guardrails (NeMo-style) before OPA policy checks.
**Date:** 2026-02-14
**Status:** Design
**Source:** GOVERNANCE_POLICY_AUDIT_RESEARCH

---

## 1. Current State

- **Gap:** No input validation rails before policy evaluation.
- **Risk:** Malformed prompts, injection patterns, or policy-bypass attempts reach PolicyEngine unfiltered.

---

## 2. Design Goals

1. **Input sanitization:** Validate/sanitize prompt, agent, model, cwd before OPA.
2. **Rail placement:** Input rails → OPA → execution (order matters).
3. **Configurable rules:** Allow org-specific blocklists, allowlists, regex patterns.

---

## 3. Architecture

```
User input (prompt, agent, model, cwd, ...)
    ↓
InputGuardrails.check(run_meta)
    ↓
[Pass] → OPA (or PolicyEngine)
[Fail] → Deny with rail_id, remediation hint
```

---

## 4. Rail Categories

| Rail | Purpose | Example |
|------|---------|---------|
| prompt_length | Max prompt chars | 64k default |
| prompt_blocklist | Block regex patterns | PII, secrets, injection |
| agent_allowlist | Only known agents | gemini, claude, cursor-agent |
| cwd_restriction | Path must be under allowed roots | /home, /workspace |
| model_allowlist | Only approved models | claude-sonnet-4, gemini-3-flash |

---

## 5. Implementation Phases

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| P1 | Design doc (this) | Done |
| P2 | InputGuardrails class; config schema | 2 days |
| P3 | Wire before PolicyEngine in execution.py | 1 day |
| P4 | Default rules; CI tests | 2 days |

---

## 6. Configuration

```yaml
governance:
  input_guardrails:
    enabled: true
    prompt_max_chars: 65536
    prompt_blocklist_patterns: []  # Regex list
    agent_allowlist: []  # Empty = allow all
    cwd_allowed_prefixes: []  # Empty = allow all
```

---

## 7. References

- `docs/GOVERNANCE_WP_VERIFICATION.md` — G-GP-02
- NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails

---

## Source: governance/NEXT_50_TASKS_COMPLETION_BATCH_2026-02-20.md

# Next 50 Tasks Completion Batch

**Date:** 2026-02-20
**Type:** Discovery + Formalization batch (completed)
**Method:** Child-agent assisted audit + synthesis + policy codification

---

## Completed 50/50 Tasks

### A. Primary Language Lanes (1-10)

- [x] 1. Verified Python lane is active in CI and quality workflows.
- [x] 2. Verified Go lane is active in CI with strict lint + coverage enforcement.
- [x] 3. Verified TS/JS lane is active in CI with strict oxlint/type/test checks.
- [x] 4. Verified Python local fast-hook pattern and strict CI split baseline.
- [x] 5. Verified Go local fast-hook vs CI strict split baseline.
- [x] 6. Verified TS/JS local fast-hook vs CI strict split baseline.
- [x] 7. Verified `thegent` primary-lane gaps versus `trace` baseline.
- [x] 8. Documented parity status model (`A/P/T/M`) for primary lanes.
- [x] 9. Defined rollout order for primary lanes in parity audit.
- [x] 10. Added immediate-batch actions for primary lane wiring.

### B. Secondary Language Lanes (11-20)

- [x] 11. Verified Java template presence (`checkstyle.xml`) in quality templates.
- [x] 12. Verified C/C++ template presence (`clang-tidy.yaml`, `cppcheck-config.cfg`).
- [x] 13. Verified Rust template presence (`clippy.toml`) and existing runtime hooks.
- [x] 14. Verified Zig support appears in tooling setup and custom max-lines gate extensions.
- [x] 15. Verified Mojo support appears in setup guidance and max-lines extension list.
- [x] 16. Verified C#/.NET lane is currently missing concrete template+wiring parity in `thegent`.
- [x] 17. Documented secondary-lane parity as template-ready vs active execution.
- [x] 18. Added phased activation path for Java/C/C++ lanes.
- [x] 19. Added phased activation path for Zig/Mojo lanes.
- [x] 20. Added C#/.NET lane definition requirement to parity plan.

### C. Shared Cross-Language Gates (21-30)

- [x] 21. Audited shared max-lines implementation shell wrapper.
- [x] 22. Audited shared max-lines Rust binary implementation and supported extensions.
- [x] 23. Verified changed-files scope support in max-lines gate implementation.
- [x] 24. Verified suppression-policy guard baseline in shared template pre-commit config.
- [x] 25. Verified changed-file smart execution model in hook config.
- [x] 26. Verified async test runner extension coverage across many language extensions.
- [x] 27. Verified trace-parity audit gate currently centered on ruff/golangci/oxlint semantics.
- [x] 28. Added shared-gate status table in parity audit.
- [x] 29. Added max-lines integration as immediate next-batch action.
- [x] 30. Added unified severity-tier rollout model in speed spec.

### D. Non-Code Governance + Contracts (31-40)

- [x] 31. Audited governance gate catalog for contract/traceability lifecycle.
- [x] 32. Verified claim lifecycle + schema validation surfaces.
- [x] 33. Verified reliability SLO and flake-quarantine gates.
- [x] 34. Verified rolling-wave and assurance-case schema gates.
- [x] 35. Verified debt registry and playbook contract gates.
- [x] 36. Verified on-chain adapter + transition gates.
- [x] 37. Verified formal-methods and formal-registry surfaces.
- [x] 38. Identified and documented on-chain/formal “stub evaluator” gaps.
- [x] 39. Added non-code governance gap analysis to parity audit.
- [x] 40. Added advanced-governance completion phase in parity roadmap.

### E. Speed + Optimization Formalization (41-50)

- [x] 41. Extracted trace fast-local (<5s) pattern as baseline.
- [x] 42. Extracted thegent stop-profile bounded-latency model.
- [x] 43. Extracted governance-gates one-pass parse/cache/batch pattern.
- [x] 44. Extracted shared tool/config caching model from hook common library.
- [x] 45. Formalized profile model (`ultrafast|fast|standard|full`) in speed spec.
- [x] 46. Formalized mandatory speed contract for every gate/checker.
- [x] 47. Formalized SLO and telemetry schema requirements.
- [x] 48. Formalized optimization order (filter -> cache -> batch -> parallel -> rewrite).
- [x] 49. Linked speed spec into parity audit as required implementation canon.
- [x] 50. Linked parity+speed docs into governance summary quick links.

---

## Evidence Index

- `docs/governance/POLYGLOT_GOVERNANCE_PARITY_AUDIT_2026-02-20.md`
- `docs/governance/POLYGLOT_GOVERNANCE_SPEED_SPEC_2026-02-20.md`
- `docs/governance/GOVERNANCE_SUMMARY.md`
- `docs/governance/ARCHITECTURAL_GOVERNANCE.md`
- `hooks/governance-gates.sh`
- `hooks/hook-config.yaml`
- `hooks/async-test-runner.sh`
- `hooks/hook-dispatcher/src/main.rs`
- `hooks/lib/common.sh`
- `scripts/max-lines-gate.sh`
- `crates/thegent-utils/src/bin/max_lines.rs`
- `templates/quality/*`
- `Taskfile.yml`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`

---

## Next Execution Batch (Implementation)

1. Wire shared max-lines gate into `thegent` pre-commit, Taskfile lint path, and CI quality job.
2. Add explicit Rust lane in CI (`fmt`, `clippy`, `test`, dependency security checks).
3. Add shell/docs/config lane in CI and pre-commit.
4. Add per-gate telemetry fields (`duration_ms`, `cache_hit`, `scope`, `profile`) in governance output schema.
5. Promote `fast` profile budgets to hard SLO checks with regression alerting.

---

## Source: governance/OPA_INTEGRATION_DESIGN.md

# OPA Integration Design (G-GP-01)

**Purpose:** Design Open Policy Agent (OPA) integration for declarative policy decisions.
**Date:** 2026-02-14
**Status:** Design
**Source:** GOVERNANCE_POLICY_AUDIT_RESEARCH, WP-3001

---

## 1. Current State

- **PolicyEngine** (`src/thegent/execution.py`): Python-based policy evaluation before run execution.
- **Policies:** Critical lane confidence, unknown agents, production trust threshold, override with reason.
- **Gap:** Policies are hardcoded Python logic, not declarative Rego.

---

## 2. Design Goals

1. **Declarative policies:** Rego rules for auditability and non-developer edits.
2. **Phase 1 compatibility:** PolicyEngine remains primary; OPA as optional Phase 2.
3. **Input/output contract:** PolicyEngine → OPA input JSON; OPA → allow/deny + reason.

---

## 3. OPA Integration Architecture

```
RunMeta (run_id, agent, model, prompt, owner, cwd, ...)
    ↓
PolicyEngine.pre_check(run_meta)
    ↓
[If THGENT_OPA_URL set]
    → HTTP POST /v1/data/thegent/allow
    → Input: {"input": {"run_meta": {...}, "context": {...}}}
    → Output: {"result": {"allow": bool, "reason": str, "policy_id": str}}
    ↓
[Else] PolicyEngine Python logic (current)
    ↓
allow | deny
```

---

## 4. Rego Policy Structure

```
# policies/thegent/allow.rego
package thegent

default allow = false

allow = true {
    input.run_meta.agent != ""
    not is_unknown_agent(input.run_meta.agent)
    not critical_lane_low_confidence(input)
    not production_trust_violation(input)
}

allow = true {
    input.run_meta.override_reason != ""
    # Override with reason bypasses other checks
}

is_unknown_agent(agent) { ... }
critical_lane_low_confidence(input) { ... }
production_trust_violation(input) { ... }
```

---

## 5. Implementation Phases

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| P1 | Document PolicyEngine as Phase 1 PDP; OPA as Phase 2 option | Done (this doc) |
| P2 | Add `THGENT_OPA_URL` config; optional OPA client in PolicyEngine | 2–3 days |
| P3 | Ship default Rego policies; CI policy tests | 3–4 days |
| P4 | Migrate all PolicyEngine rules to Rego; deprecate Python policies | 5–7 days |

---

## 6. Configuration

```yaml
# config.example.yaml
governance:
  opa_url: ""  # e.g. http://localhost:8181
  opa_timeout_ms: 500
  opa_fallback_allow: false  # If OPA unreachable, allow or deny?
```

---

## 7. References

- `docs/GOVERNANCE_WP_VERIFICATION.md` — G-GP-01
- `src/thegent/execution.py` — PolicyEngine
- OPA: https://www.openpolicyagent.org/

---

## Source: governance/PARITY_VERIFICATION_TEMPLATE.md

# Parity Verification Template

**Use this template before removing any legacy/deprecated code.**

---

## Parity Verification: [Old Implementation] → [New Implementation]

**Date:** YYYY-MM-DD
**Verifier:** [Name]
**Status:** ⏳ In Progress / ✅ Complete / ❌ Failed

---

## 1. Feature Comparison

| Feature | Old Implementation | New Implementation | Status | Notes |
|---------|-------------------|-------------------|--------|-------|
| Feature 1 | ✅ Location/API | ✅ Location/API | ✅ Parity | - |
| Feature 2 | ✅ Location/API | ✅ Location/API | ✅ Parity | - |
| Feature 3 | ✅ Location/API | ⚠️ Different API | ⚠️ Review | [Explain difference] |
| Feature 4 | ✅ Location/API | ❌ Missing | ❌ **BLOCK** | [Action required] |

**Summary:**
- ✅ Features with parity: X
- ⚠️ Features with differences: Y (acceptable)
- ❌ Missing features: Z (**BLOCK REMOVAL**)

---

## 2. Migration Completeness

### Callers Identified

| Caller Location | Old Import | New Import | Status |
|----------------|-----------|-----------|--------|
| `file1.py` | `from old import X` | `from new import X` | ✅ Migrated |
| `file2.py` | `from old import Y` | `from new import Y` | ✅ Migrated |
| `file3.py` | `from old import Z` | ❌ Not migrated | ❌ **BLOCK** |

**Summary:**
- Total callers: X
- Migrated: Y
- Remaining: Z (**BLOCK REMOVAL** if > 0)

### Migration Commands

```bash
# Find all callers
grep -r "old_module\|old.import" src/ tests/

# Verify migration
grep -r "old_module\|old.import" src/ tests/ | wc -l  # Should be 0
```

---

## 3. Behavioral Parity Testing

### Test Results

| Test Case | Old Implementation | New Implementation | Status |
|-----------|-------------------|-------------------|--------|
| Test 1: Basic functionality | ✅ Pass | ✅ Pass | ✅ Parity |
| Test 2: Edge case handling | ✅ Pass | ✅ Pass | ✅ Parity |
| Test 3: Error handling | ✅ Pass | ⚠️ Different | ⚠️ Review |
| Test 4: Performance | ✅ 100ms | ✅ 50ms | ✅ Better |

**Summary:**
- Tests passing: X/Y
- Behavioral differences: Z (acceptable/unacceptable)
- Performance: Better/Same/Worse

### Test Code

```python
# tests/parity/test_old_vs_new.py
def test_parity_old_vs_new():
    """Verify new implementation has parity with old."""
    # Test all features
    # Compare outputs
    # Verify no functionality lost
    pass
```

---

## 4. Documentation

- [ ] Parity verification documented
- [ ] Differences documented (if any)
- [ ] Migration guide updated
- [ ] API changes documented

---

## 5. Approval

**Parity Verification:**
- [ ] ✅ Feature parity verified
- [ ] ✅ Migration complete
- [ ] ✅ Tests pass
- [ ] ✅ Documentation updated

**Ready for Removal:**
- [ ] ✅ All checks pass
- [ ] ✅ Approval obtained
- [ ] ✅ Removal plan documented

**If any check fails:**
- ❌ **DO NOT PROCEED** with removal
- ⚠️ Fix issues first
- 🔄 Re-verify after fixes

---

## 6. Post-Removal Verification

**After removal, verify:**
- [ ] All tests pass
- [ ] No broken imports
- [ ] No regressions
- [ ] Performance acceptable

---

## Notes

[Additional notes, concerns, or observations]

---

**Template Version:** 1.0
**Last Updated:** 2026-02-19

---

## Source: governance/POLYGLOT_GOVERNANCE_PARITY_AUDIT_2026-02-20.md

# Polyglot Governance Parity Audit

**Date:** 2026-02-20
**Repo:** `thegent`
**Status:** Audit complete, rollout plan defined

---

## 1. Scope

This audit covers:

- Language families: Go, TS/JS (+ variations), Python (+ variations), Java, C/C++, C#/.NET, Rust, Zig, Mojo, and additional supported stacks.
- Non-language file types: shell, JSON/YAML/TOML, Markdown, infra/config artifacts.
- Non-file/program governance: traceability, contracts, attestation, reliability/SLO, debt/playbook contracts, and on-chain/formal governance hooks.

Parity target means each stack has:

1. Lint + format + test baseline.
2. Security/dependency checks where applicable.
3. Pre-commit + CI + task-runner integration.
4. Shared governance overlays (file length, suppression policy, traceability/reporting).

---

## 2. Evidence Anchors

- Templates inventory: `templates/quality/` (multi-stack policies and tool configs).
- Runtime hooks and gate engine: `hooks/governance-gates.sh`, `hooks/hook-config.yaml`, `hooks/async-test-runner.sh`.
- Current execution wiring:
  - `Taskfile.yml` (quality tasks),
  - `.pre-commit-config.yaml` (local gates),
  - `.github/workflows/ci.yml` (CI),
  - `.github/workflows/release.yml` (SBOM/provenance).
- Shared max-lines gate implementation:
  - `scripts/max-lines-gate.sh`,
  - `crates/thegent-utils/src/bin/max_lines.rs`.
- Speed contract:
  - `docs/governance/POLYGLOT_GOVERNANCE_SPEED_SPEC_2026-02-20.md`.

---

## 3. Current Parity Matrix (Code + File Types)

Legend:
- `A` = active and wired in current repo execution path.
- `P` = partially wired (some pieces exist, not full parity).
- `T` = template-ready only (governance intent exists, not wired).
- `M` = missing.

| Surface | Templates | Task/Hook/CI Wiring | Status | Notes |
|---|---:|---:|---|---|
| Python (py, pyi) | Yes | Strong | `A` | Ruff/ty/basedpyright/mypy/pytest/security present in task + CI. |
| Go | Yes | Partial | `P` | Go exists in max-lines + hook extension lists; no dedicated Go lane in main `thegent` CI. |
| TS/JS (ts,tsx,js,jsx,mjs,cjs) | Yes | Partial | `P` | Oxlint template parity logic exists in governance gate; not fully wired as first-class CI lane in `thegent`. |
| Shell (sh,zsh,bash,bats) | Yes | Partial | `P` | ShellCheck in Taskfile and template; not enforced in CI workflow currently. |
| JSON/YAML/TOML | Yes | Partial | `P` | pre-commit checks exist; stronger schema policy exists mostly in governance hooks. |
| Markdown/docs | Yes (markdownlint/vale templates) | Weak | `P` | Docs build gate exists; markdown lint policy not fully wired in CI/pre-commit. |
| Rust | Yes | Partial | `P` | Rust assets and benchmarks exist; no first-class fmt/clippy/test/audit lane in main CI yet. |
| Zig | No dedicated template file | Partial | `P` | Tooling setup + build and max-lines support exist; no fmt/test policy lane wired. |
| Mojo | No dedicated template file | Minimal | `P` | Mentioned in setup and max-lines extension list; no formatter/test/security lanes wired. |
| Java | Yes (checkstyle) | Template only | `T` | No active Java lint/test lane wired. |
| C/C++ | Yes (clang-tidy/cppcheck) | Template only | `T` | No active C/C++ lane wired. |
| C#/.NET | No dedicated quality template currently | Missing | `M` | No active .NET lane or template in current quality set. |
| Kotlin/Swift/Dart/PHP/Ruby/Perl/Lua/Terraform/etc | Yes (various templates) | Template only | `T` | Policy scaffolding exists but not executed as lanes. |

---

## 4. Shared Cross-Language Governance Status

| Cross-language Gate | Status | Notes |
|---|---|---|
| Max file length gate | `P` | Implemented (Rust + Zig runner + shell wrapper) but not yet fully wired into pre-commit + CI + task defaults. |
| Suppression policy blocker | `A` (template), `P` (runtime) | Template pre-commit rule exists; repo-level full enforcement still needs unified rollout. |
| Smart changed-file execution | `A` | Hook config supports changed/all scopes and incremental analysis. |
| Async test dispatch by file extension | `A` | Broad extension routing exists across many languages. |
| Trace parity template audit | `A` (for py/go/oxlint) | Existing trace parity gate currently focuses on ruff/golangci/oxlint semantics. |
| Per-stack policy spec centralization | `P` | Strong template inventory exists; stack execution contracts are uneven. |

---

## 5. Non-File / Program Governance (Contracts, Traceability, Smart Governance)

Current governance engine already supports extensive non-code controls:

- PRD/ledger/DAG compile and lifecycle gates.
- Agent claim schema + evidence lifecycle validation.
- Reliability SLO and flake quarantine governance.
- Brownfield/greenfield/probabilistic delivery-model gates.
- Rolling-wave and assurance-case schema gates.
- Privacy proof, on-chain adapter/transition gates.
- Formal methods and formal registry gates.
- Debt registry and playbook contract gates.
- Artifact quality and SCC metrics gate.

### Important gaps in this layer

1. `onchain-contract` gate currently reports stub mode when contracts exist but toolchain gates are not installed/evaluated.
2. `formal-methods` gate currently reports stub mode when formal specs exist but TLC/Dafny/Alloy evaluators are not installed/wired.
3. Schema coverage is uneven between contract artifacts and repository-level schema directories; some gates rely on runtime/project-local schemas.

Net: governance architecture is strong, but some advanced assurance gates are still stubs or environment-dependent.

---

## 6. Gap Summary by Priority

### Priority 0 (already strong)

- Python baseline quality lane.
- Governance gate framework for non-code artifacts and policy enforcement.
- Release SBOM/provenance path.

### Priority 1 (close to parity, finish wiring)

- Rust lane: fmt + clippy + tests + security dependency checks.
- TS/JS lane: strict lint/format/test lane in CI aligned with policy templates.
- Go lane: first-class CI/task parity in this repo.
- Shared max-lines gate: enforce in pre-commit/CI/task.

### Priority 2 (template-rich, execution-poor)

- Java and C/C++ lanes from existing templates.
- Shell/docs/config lint gates as consistent mandatory checks.

### Priority 3 (missing foundation)

- C#/.NET lane definition (toolchain, templates, CI hooks).
- Mojo and Zig dedicated formatter/test lane definitions.

---

## 7. Formal Rollout Plan (Phased)

### Phase A: Core parity substrate (all stacks)

1. Wire shared max-lines gate in pre-commit + CI + `task lint`.
2. Define normalized output schema for all check runners.
3. Add policy severity tiers (`advisory`, `soft_fail`, `hard_fail`) with explicit owner/date.

### Phase B: Primary stack parity (Go/TS/Python/Rust/Shell)

1. Rust: `fmt`, `clippy`, `test`, dependency/security checks.
2. Go: format/lint/test/security parity in this repo’s CI and tasks.
3. TS/JS: strict lint/format/type/test lane aligned with oxlint template + boundaries policy.
4. Shell/docs/config: shellcheck + markdown/config linting lanes.

### Phase C: Secondary stack activation (Java/C/C++/Zig/Mojo/.NET)

1. Activate Java lane from checkstyle template + test lane.
2. Activate C/C++ lane from clang-tidy/cppcheck templates + build/test lane.
3. Add Zig lane (`fmt`/build/test) and Mojo lane (`format`/compile/test) policies.
4. Add C#/.NET baseline lane (format/lint/build/test/security) and add template set.

### Phase D: Advanced governance completion

1. Replace stub on-chain/formal gates with real toolchain-backed evaluators where applicable.
2. Add schema hard-fail checks for all contract outputs.
3. Add governance SLO dashboards (gate latency, flake, failure trend, waiver debt).

---

## 8. Execution Rules (Required)

1. Native tool semantics stay native; thegent orchestrates and governs.
2. Adapter/wrapper first, rewriter last.
3. Every exception/waiver requires owner, reason, expiry, and cleanup issue.
4. New lanes start advisory and graduate to hard-fail only after baseline stabilization.
5. All lanes must support changed-files mode locally and full-scan mode in CI/nightly.

---

## 9. Immediate Next Batch

1. Integrate max-lines gate into:
   - `.pre-commit-config.yaml`,
   - `Taskfile.yml` (`lint` path),
   - `.github/workflows/ci.yml` (`quality` job).
2. Add Rust quality job in CI (fmt + clippy + tests + audit/deny).
3. Add shell/docs/config job in CI (shellcheck + markdown/config lint).
4. Draft lane spec for Java/C/C++/Zig/Mojo/.NET in a single policy contract file for staged activation.

---

## 10. Optimization Canon (Required)

Implementation must follow the speed spec:

1. Profile-driven execution (`ultrafast|fast|standard|full`).
2. Changed-file first, full-scan in CI/nightly.
3. Parse/config/tool availability cached once per run.
4. Parallelize only independent gates with bounded timeout.
5. Emit per-gate telemetry (`duration_ms`, `cache_hit`, `scope`, `profile`).

Reference: `docs/governance/POLYGLOT_GOVERNANCE_SPEED_SPEC_2026-02-20.md`.

---

## Source: governance/POLYGLOT_GOVERNANCE_SPEED_SPEC_2026-02-20.md

# Polyglot Governance Speed Spec

**Date:** 2026-02-20
**Purpose:** Formal speed-first execution model for all governance gates/checkers across code + non-code surfaces.

---

## 1. Design Goal

Deliver strict governance with low latency by combining:

1. **Fast local loop** (changed-files, bounded checks, immediate feedback),
2. **Strict CI loop** (full-scan and heavier analyzers),
3. **Progressive profile system** (`ultrafast`, `fast`, `standard`, `full`) with explicit SLOs.

This is a governance orchestrator contract, not a replacement for native language analyzers.

---

## 2. Proven Baselines to Reuse

### 2.1 Trace baseline (simple and fast)

- Local pre-commit intentionally optimized for `<5s` with slow checks moved to CI.
- Changed-file filtering and parallel local checks.
- Lightweight local gates for LOC and naming explosion.

Evidence:
- `trace/.pre-commit-config.yaml:1-10`
- `trace/.pre-commit-config.yaml:25-26`
- `trace/.pre-commit-config.yaml:95-121`

### 2.2 Thegent runtime baseline (bounded and cached)

- Stop execution has hard-clamped latency bounds and profile-based hook sets.
- Governance gate dispatcher uses one-time parse + cache + batched evaluation.
- Common layer caches tool availability and quality config reads.

Evidence:
- `thegent/hooks/hook-dispatcher/src/main.rs:1027-1031`
- `thegent/hooks/hook-dispatcher/src/main.rs:2263-2297`
- `thegent/hooks/governance-gates.sh:8-10`
- `thegent/hooks/governance-gates.sh:31-39`
- `thegent/hooks/lib/common.sh:224-251`
- `thegent/hooks/lib/common.sh:288-307`

---

## 3. Execution Profiles (Formal)

| Profile | Target Use | Max Local Wall-Clock | Mandatory Checks |
|---|---|---:|---|
| `ultrafast` | tight edit loops | <= 2s | syntax/file sanity + reconcile floor |
| `fast` | default dev loop | <= 5s | lint/format on changed files + core governance floor |
| `standard` | pre-push/local verify | <= 15s | adds stricter type/test subsets + lifecycle gates |
| `full` | CI/nightly/release | unbounded by local UX | full-stack lint/type/test/security/contracts/assurance |

Rules:

1. Local defaults must remain `fast`.
2. `full` profile is authoritative for merge/release gates.
3. Any new gate must declare supported profiles and expected runtime budget.

---

## 4. Speed Contract for All Gates

Every gate/checker must implement:

1. **Scope mode**: `changed` and `all`.
2. **Deterministic cache key**: inputs + config + tool version (or toolchain lock hash).
3. **Bounded timeout**: explicit idle + absolute timeout.
4. **Machine-readable report**: normalized JSON outcome and metrics.
5. **Severity tier**: `advisory`, `soft_fail`, `hard_fail`.

If a checker cannot satisfy this contract, it remains CI-only until adapted.

---

## 5. Unified Pipeline Topology

### Stage A: Preflight (local + CI)

- Changed-files resolution.
- Tool availability + config load cached once.
- Skip non-relevant gates by extension/path policy.

### Stage B: Fast checks (local default)

- Native fast linters/formatters on changed files.
- Shared policy gates (file-length, suppressions, naming, config sanity).

### Stage C: Strict checks (CI + selected local profiles)

- Full type checks, deep lint/security, full tests, contract/traceability assertions.

### Stage D: Assurance/attestation (CI/release)

- SBOM/provenance/contract evidence, reliability trend checks, formal/onchain where applicable.

---

## 6. Language Lane Requirements (Performance-Aware)

For each language lane (Go, TS/JS, Python, Java, C/C++, C#/.NET, Rust, Zig, Mojo, others):

1. Native toolchain lane must expose `lint`, `format`, `test`, and optional `security`.
2. Fast local mode uses changed-files subsets and safe auto-fixes only.
3. Strict CI mode runs full repository scope with artifacts.
4. Lane output is normalized into shared governance schema.

Non-code types (shell, JSON/YAML/TOML, Markdown, contracts, schemas) follow the same profile contract.

---

## 7. Non-Code Governance Performance Model

For governance contracts/traceability/smart-contract-like checks:

1. Parse once, reuse many times per run (batch extraction).
2. Prefer string/builtin matching over expensive process loops where correctness is preserved.
3. Evaluate independent gates in parallel batches with dependency boundaries.
4. Persist cache for repeated unchanged policy runs.

Applies to:
- claim lifecycle, DAG/ledger checks, assurance case, reliability SLO, debt/playbook gates, etc.

---

## 8. SLOs and Telemetry

Minimum telemetry per gate:

- `duration_ms`
- `scope` (`changed`/`all`)
- `cache_hit` (bool)
- `result` (pass/warn/fail/na)
- `profile`

Minimum SLOs:

1. `fast` local profile p95 <= 5s.
2. Cache hit ratio >= 70% on repeated local runs (same branch/session).
3. No single local gate > 2s p95 without explicit waiver.
4. CI full lane reports per-stage timings and regression deltas.

---

## 9. Optimization Playbook (Mandatory Order)

1. **Filter first**: limit by changed files/path/extension.
2. **Cache second**: config/tool/status/gate outputs.
3. **Batch third**: parse once, evaluate many.
4. **Parallelize fourth**: only independent checks.
5. **Rewrite fifth**: custom/native rewrite only after measured bottleneck remains.

---

## 10. Rollout Steps

### Step 1 (immediate)

- Enforce shared max-lines gate in `fast` local + CI `full`.
- Add per-gate timing and cache-hit output fields.

### Step 2

- Make each language lane declare profile support and SLO budget.
- Wire missing lanes progressively (Rust/Go/TS first, then secondary stacks).

### Step 3

- Convert advanced governance stubs to evaluators where required by profile `full`.
- Add nightly performance regression for gate runtime budgets.

---

## 11. Definition of Done

A stack/surface reaches parity only when:

1. It is wired in pre-commit/task/CI with profile support.
2. It emits normalized machine-readable reports.
3. It meets profile SLO budgets in observed telemetry.
4. It has exception governance (owner/reason/expiry) for any temporary relaxations.

---

## 12. Lane Commands (WL-134 Slice)

The canonical lane entry points are now:

1. `task test:fast-lane`
- Intended cadence: default local + PR loop.
- Includes: `test:unit` + `test:hooks:selector-fast`.

2. `task test:nightly-lane`
- Intended cadence: nightly/deep validation.
- Includes: `test:hooks:governance` + `test:pyramid`.

Policy:

1. New expensive checks go to nightly lane first unless they meet fast-lane SLO.
2. Fast lane stays bounded and contract-focused.

---

## Source: governance/POLYGLOT_RUNTIME_COVERAGE_AND_CONVERSION_MATRIX_2026-02-21.md

# Polyglot Runtime Coverage and Conversion Matrix (2026-02-21)

Status: Active governance baseline for language/runtime selection, test matrix, and refactor/conversion decisions.

## Scope

This policy standardizes:

1. test/runtime coverage expectations,
2. frontmatter/backmatter defaults,
3. when to keep/refactor/convert projects across Python, Rust, Zig, Go, and Mojo.

## Runtime and Coverage Matrix

| Language | Primary Runtime | Required Matrix | Fallback | Gate Policy |
|---|---|---|---|---|
| Python | `uv` + CPython 3.14 | CPython 3.14 + PyPy 3.11 | CPython 3.13 only when dependency/tooling blocks primary matrix | Must pass primary runtime + at least one alternate runtime in CI |
| Rust | stable toolchain | `cargo test`, `clippy -D warnings`, `fmt --check` | nightly only for explicitly gated features | Stable must remain green; nightly may be non-blocking unless feature requires it |
| Zig | pinned Zig stable | `zig test`, build in release-safe mode | next Zig as preview lane | Stable lane blocking; preview lane advisory |
| Go | latest two supported Go minors | `go test ./...`, `go vet`, race lane for critical pkgs | previous minor as compatibility lane | Latest lane blocking; compatibility lane soft-block until green for release branch |
| Mojo | pinned Mojo version | smoke + integration tests against Python interop boundary | Python/Rust reference implementation for parity checks | Mojo lane can start advisory; becomes blocking once parity SLO achieved |

## Frontmatter and Backmatter Defaults

### Frontmatter (required in governance/spec docs)

Use:

```yaml
---
title: <Doc Title>
date: YYYY-MM-DD
status: draft|active|deprecated
owner: <team-or-project>
tags: [governance, polyglot, testing]
---
```

### Backmatter (required in decision-heavy docs)

Append:

1. Decision record summary (what changed, why),
2. validation commands run,
3. open risks and follow-up owners,
4. review cadence/date.

## Conversion and Refactor Decision Matrix

| Condition | Keep Current Stack | Refactor in Place | Convert Language |
|---|---|---|---|
| Team/runtime maturity high, perf acceptable | Yes | Optional cleanup only | No |
| Perf pain in hot path, architecture otherwise healthy | No | Yes: isolate hotspots and optimize | Convert hotspot module only |
| Tooling/governance friction high but domain logic stable | No | Yes: improve build/test ergonomics first | Convert only if friction persists after 2 governance cycles |
| Ecosystem/library mismatch blocks core roadmap | No | Temporary adapters only | Yes: convert to language with strong library support |
| Operational latency/cost SLO repeatedly missed | No | First profile + tune | Convert critical path after failed tuning attempts |

## Conversion Triggers (must meet at least two)

1. Two consecutive release cycles miss SLOs after optimization.
2. Required libraries/security updates unavailable in current stack.
3. Runtime stability incidents exceed governance threshold.
4. Developer throughput materially below baseline due toolchain constraints.

## Mandatory Pre-Conversion Checklist

1. Measure baseline: throughput, latency, memory, CI duration.
2. Define API/ABI boundaries and parity tests.
3. Implement side-by-side validation harness.
4. Plan phased cutover with rollback.
5. Update governance docs, templates, and `CLAUDE.md`.

## Python-Specific Standard (requested baseline)

Default matrix:

1. `uv` + CPython 3.14 (primary),
2. PyPy 3.11 (secondary),
3. CPython 3.13 (fallback compatibility lane).

Failure policy:

1. Primary lane failure is blocking.
2. Secondary failure is blocking on release branches, advisory on feature branches.
3. Fallback lane is required when dependency constraints force downgrade.

## Instruction Architecture Normalization Policy

1. Canonical filename is `CLAUDE.md`.
2. Any `calude.md` typo file must be merged into canonical `CLAUDE.md` and removed.
3. Global vs project split is mandatory:
   - Global `CLAUDE.md` is index + guardrails.
   - Project `CLAUDE.md` is overlay + local execution specifics.
4. If `CLAUDE.md` exceeds ~20k tokens, split into docset:
   - keep `CLAUDE.md` as concise policy index,
   - move long detail to `docs/reference/CLAUDE_CORE_GUIDELINES.md` and related docs,
   - maintain a doc map section with explicit links.
5. Required instruction doc map references:
   - `docs/reference/CLAUDE_CORE_GUIDELINES.md`
   - `docs/reference/CLAUDE_THEGENT_RUNTIME_APPENDIX.md`
   - `docs/governance/GOVERNANCE_SUMMARY.md`
   - `docs/reference/WORK_STREAM.md`

## Validation Commands

```bash
# python lanes
uv run pytest
uv run -p 3.14 pytest
uv run -p pypy3.11 pytest
uv run -p 3.13 pytest  # compatibility fallback lane

# rust
cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test

# go
go test ./... && go vet ./...

# zig
zig test ./...
```

---

## Source: governance/RETENTION_POLICY_DESIGN.md

# Retention Policy Design (G-GP-07)

**Purpose:** Design retention by domain, tier transitions, and compliance evidence.
**Date:** 2026-02-14
**Status:** Design
**Source:** GOVERNANCE_POLICY_AUDIT_RESEARCH, WP-3006, 6002

---

## 1. Current State

- **closure_pack:** Generates signoff package.
- **history verify:** Checks registry integrity.
- **Gap:** No automated retention policy; no domain tagging; retention TBD.

---

## 2. Design Goals

1. **Retention by domain:** Different retention per domain_tag (e.g. project-id, compliance-domain).
2. **Tier transitions:** Dev → staging → prod may have different retention.
3. **Automated purge:** Background job or on-startup purge of expired events.

---

## 3. Architecture

```
RunRegistry events (run_registry.jsonl)
    ↓
Each event has domain_tag (optional)
    ↓
RetentionPolicy: domain_tag → retention_days
    ↓
Purge: events older than retention_days for their domain
```

**Default:** retention_days_sessions, retention_days_registry (already in config).

---

## 4. Implementation Phases

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| P1 | Design doc (this) | Done |
| P2 | domain_tag in RunMeta; retention_days_registry per domain | 1–2 days |
| P3 | Purge command: `thegent govern purge --dry-run` | 1–2 days |
| P4 | Closure pack expansion with retention/evidence matrix | 2–3 days |

---

## 5. Configuration

```yaml
governance:
  retention:
    default_days: 90
    by_domain:
      project-alpha: 365
      compliance-audit: 730
```

---

## 6. References

- `docs/GOVERNANCE_WP_VERIFICATION.md` — G-GP-07
- `src/thegent/execution.py` — RunRegistry, RunMeta
- `src/thegent/config.py` — retention_days_sessions, retention_days_registry

---

## Source: governance/SANDBOXING_DESIGN.md

# Sandboxing Design (G-GP-08)

**Purpose:** Design agent sandbox isolation for trust boundary enforcement.
**Date:** 2026-02-14
**Status:** Design
**Source:** GOVERNANCE_POLICY_AUDIT_RESEARCH, WP-3007, FR-014

---

## 1. Current State

- **Gap:** Agents run in host process; no isolation.
- **Risk:** Malicious or buggy agent output could affect host (file writes, network, env).

---

## 2. Design Goals

1. **Isolation:** Agent subprocess in restricted environment.
2. **Configurable:** Sandbox on/off; network egress allowlist; filesystem write restrictions.
3. **Trust boundary:** Document env transitions (host → sandbox → host).

---

## 3. Architecture Options

| Option | Isolation | Complexity | Use Case |
|--------|-----------|------------|----------|
| A. Subprocess + env filter | Low | Low | Filter env vars only |
| B. Docker | Medium | Medium | Container per run |
| C. Firecracker/gVisor | High | High | Strong isolation, cold start |

---

## 4. Recommended Phased Approach

### Phase 1: Env and CWD Restriction
- Restrict `cwd` to allowed prefixes.
- Filter env vars to safe subset (PATH, HOME, etc.).
- No new process isolation.

### Phase 2: Docker Runner
- Optional `THGENT_SANDBOX_DOCKER_IMAGE` — run agent in container.
- Mount only cwd (read-write) or read-only.
- Network: none or allowlist.

### Phase 3: Firecracker (Future)
- MicroVM per run for strongest isolation.
- Higher latency; for high-trust environments.

---

## 5. Implementation Phases

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| P1 | Design doc (this) | Done |
| P2 | CWD + env filter in runner | 1–2 days |
| P3 | Docker runner option; config | 3–5 days |
| P4 | Trust boundary doc; audit checklist | 1 day |

---

## 6. Configuration

```yaml
governance:
  sandbox:
    enabled: false
    mode: env_filter  # env_filter | docker | none
    cwd_allowed_prefixes: []
    env_allowlist: ["PATH", "HOME", "LANG"]
    docker_image: ""  # e.g. thegent-agent:latest
    docker_network: none  # none | host | allowlist
```

---

## 7. References

- `docs/GOVERNANCE_WP_VERIFICATION.md` — G-GP-08
- FR-014 (sandboxing requirement)
- Firecracker: https://firecracker-microvm.github.io/
- gVisor: https://gvisor.dev/

---

## Source: governance/TDD_BDD_SDD_GOVERNANCE.md

# TDD/BDD/SDD Governance for Agent-Only Environment

**Date**: 2026-02-19
**Status**: 🎯 CRITICAL - Agent-Only Testing Requirements
**Coverage Target**: **100%** (not 80%)

---

## 🎯 Core Principle

**In an agent-only environment where NO humans test the system, comprehensive automated test coverage is NOT optional - it is CRITICAL.**

---

## 📐 Governance Framework

### TDD (Test-Driven Development)

#### Rules:
1. **Write tests BEFORE implementation**
2. **Red → Green → Refactor cycle**
3. **Tests must pass before code review**
4. **No code merged without tests**

#### Process:
```
1. Write failing test (Red)
2. Implement minimal code to pass (Green)
3. Refactor while keeping tests green
4. Repeat
```

#### Coverage Requirements:
- **Unit Tests**: 100% of all functions
- **Integration Tests**: 100% of all workflows
- **E2E Tests**: 100% of all CLI commands

---

### BDD (Behavior-Driven Development)

#### Purpose:
Describe agent behavior in human-readable format that serves as both documentation and tests.

#### Structure:
```gherkin
Feature: [Feature Name]
  As an agent
  I want to [capability]
  So that [goal]

  Scenario: [Scenario Name]
    Given [precondition]
    When [action]
    Then [expected result]
    And [additional assertion]
```

#### Implementation:
- Use `pytest-bdd` or `behave` for Gherkin parsing
- Map scenarios to pytest test functions
- Generate documentation from scenarios

#### Example:
```python
@pytest.mark.e2e
def test_agent_execution_successful():
    """
    Scenario: Successful agent execution
      Given I have a valid prompt "write hello world"
      When I execute "thegent run -a claude 'write hello world'"
      Then the execution should succeed
      And the output should contain "hello world"
    """
    result = runner.invoke(app, ["run", "-a", "claude", "write hello world"])
    assert result.exit_code == 0
    assert "hello world" in result.stdout.lower()
```

---

### SDD (System Design Document) Alignment

#### Test Requirements by SDD Component:

1. **Agent Execution Engine** (SDD Section X.Y):
   - [ ] E2E: All agent types tested
   - [ ] Integration: Route → Execution → Result flow tested
   - [ ] Unit: All execution functions tested
   - **Test Coverage**: 100%

2. **Crew Management System** (SDD Section X.Y):
   - [ ] E2E: Full crew lifecycle tested
   - [ ] Integration: Task → Agent → Execution flow tested
   - [ ] Unit: All crew functions tested
   - **Test Coverage**: 100%

3. **Team Coordination System** (SDD Section X.Y):
   - [ ] E2E: All team operations tested
   - [ ] Integration: Delegation flow tested
   - [ ] Unit: All team functions tested
   - **Test Coverage**: 100%

4. **Route Resolution System** (SDD Section X.Y):
   - [ ] E2E: All routing scenarios tested
   - [ ] Integration: Catalog → Route → Provider flow tested
   - [ ] Unit: All routing functions tested
   - **Test Coverage**: 100%

5. **Configuration System** (SDD Section X.Y):
   - [ ] E2E: Config loading tested
   - [ ] Integration: Settings → Application flow tested
   - [ ] Unit: All config functions tested
   - **Test Coverage**: 100%

#### SDD Validation:
- Every SDD requirement must have corresponding tests
- Test results validate SDD accuracy
- SDD updates trigger test updates

---

## 🧪 Test Pyramid (Agent-Optimized)

```
                    ┌─────────────────┐
                    │   E2E Tests     │  ← 100% of user journeys
                    │  (CRITICAL)     │     (Agent interactions)
                    └─────────────────┘
                  ┌─────────────────────┐
                  │ Integration Tests    │  ← 100% of workflows
                  │  (CRITICAL)          │     (Cross-component)
                  └─────────────────────┘
                ┌───────────────────────────┐
                │   Unit Tests              │  ← 100% of functions
                │   (ESSENTIAL)             │     (Isolated)
                └───────────────────────────┘
```

**Key Difference**: In agent-only environments:
- **E2E tests are MORE critical** than unit tests
- **Integration tests are MORE critical** than unit tests
- Agents interact at API/CLI boundary - that's what matters

---

## 📋 Test Coverage Requirements

### A. E2E Test Coverage (100% Required)

**Every CLI command must have:**
1. ✅ Success scenario test
2. ✅ Error scenario test
3. ✅ Help/usage test
4. ✅ Output validation test

**Commands requiring E2E tests**: ~99 commands (from main.py)

### B. Integration Test Coverage (100% Required)

**Every workflow must have:**
1. ✅ Happy path test
2. ✅ Error path test
3. ✅ Edge case test
4. ✅ Performance test (if applicable)

**Workflows requiring integration tests**: ~20+ workflows

### C. Unit Test Coverage (100% Required)

**Every function must have:**
1. ✅ Basic functionality test
2. ✅ Edge case test
3. ✅ Error handling test
4. ✅ Boundary condition test

**Functions requiring unit tests**: ~500+ functions

---

## 🛠️ Implementation Tools

### Test Framework
- **Framework**: pytest
- **BDD**: pytest-bdd or behave
- **Coverage**: pytest-cov
- **Mocking**: pytest-mock
- **Fixtures**: pytest fixtures

### Coverage Tools
- **Coverage**: pytest-cov with 100% target
- **Mutation Testing**: mutmut or cosmic-ray
- **Static Analysis**: mypy, pyright
- **Linting**: ruff

### CI/CD Integration
- **Pre-commit**: Run tests before commit
- **Pre-merge**: Require 100% coverage
- **Post-merge**: Run full test suite
- **Reporting**: Coverage reports in CI

---

## 📊 Coverage Metrics

### Required Metrics

1. **E2E Coverage**: 100% of CLI commands
2. **Integration Coverage**: 100% of workflows
3. **Unit Coverage**: 100% of functions
4. **Branch Coverage**: 100% of code paths
5. **Mutation Score**: 80%+ (mutation testing)

### Reporting

- **Daily**: Coverage trend reports
- **Weekly**: Gap analysis reports
- **Per-PR**: Coverage diff reports
- **Monthly**: Comprehensive coverage audit

---

## 🚀 Implementation Roadmap

### Phase 1: Coverage Analysis (Week 1)
- [x] Create coverage analysis script
- [ ] Run coverage analysis
- [ ] Generate coverage gap report
- [ ] Map all commands to tests

### Phase 2: BDD Framework Setup (Week 1)
- [ ] Install pytest-bdd
- [ ] Create BDD test structure
- [ ] Set up Gherkin parsing
- [ ] Create test fixtures

### Phase 3: E2E Test Implementation (Week 2-4)
- [ ] Implement E2E tests for all CLI commands
- [ ] Cover all user journeys
- [ ] Add error scenario tests
- [ ] Validate output assertions

### Phase 4: Integration Test Expansion (Week 5-6)
- [ ] Expand integration test coverage
- [ ] Test all workflows end-to-end
- [ ] Add failure scenario tests
- [ ] Test cross-component interactions

### Phase 5: Unit Test Completion (Week 7-8)
- [ ] Complete unit test coverage to 100%
- [ ] Add edge case tests
- [ ] Add boundary condition tests
- [ ] Add error handling tests

### Phase 6: Continuous Integration (Ongoing)
- [ ] Set up CI/CD with test execution
- [ ] Require 100% coverage for new code
- [ ] Block merges without tests
- [ ] Generate coverage reports

---

## ✅ Quality Gates

### Pre-Commit Gates
- [ ] All tests pass
- [ ] Coverage >= 100%
- [ ] No linting errors
- [ ] No type errors

### Pre-Merge Gates
- [ ] All tests pass
- [ ] Coverage >= 100%
- [ ] E2E tests pass
- [ ] Integration tests pass
- [ ] Code review approved

### Post-Deploy Gates
- [ ] E2E tests pass in production-like environment
- [ ] Performance tests pass
- [ ] Load tests pass (if applicable)

---

## 📝 Test Documentation

### Required Documentation

1. **Test Strategy Document** (this file)
2. **Coverage Report** (auto-generated)
3. **Test Catalog** (mapping commands → tests)
4. **BDD Scenarios** (Gherkin files)
5. **Test Execution Reports** (CI/CD)

---

## 🎯 Success Criteria

### Coverage Targets
- ✅ **E2E Coverage**: 100% of CLI commands
- ✅ **Integration Coverage**: 100% of workflows
- ✅ **Unit Coverage**: 100% of functions
- ✅ **Branch Coverage**: 100% of code paths

### Quality Targets
- ✅ **Mutation Score**: 80%+
- ✅ **Test Execution Time**: < 10 minutes
- ✅ **Test Reliability**: 99.9%+ (no flaky tests)
- ✅ **Documentation Coverage**: 100% of user journeys

---

## 🔄 Continuous Improvement

### Regular Activities

1. **Weekly**: Review coverage reports
2. **Monthly**: Audit test quality
3. **Quarterly**: Review test strategy
4. **Annually**: Update governance framework

### Metrics Tracking

- Coverage trends over time
- Test execution time trends
- Test failure rates
- Mutation testing scores

---

**Status**: 🎯 CRITICAL - Agent-Only Environment
**Coverage Target**: **100%** (not 80%)
**Governance**: TDD/BDD/SDD aligned

---

## Source: governance/TERMINOLOGY_LAYERS.md

# Terminology: Layer Vocabulary

**Purpose:** Establish consistent vocabulary for ease of communication across thegent, harnesses, and LLM infrastructure.

**Reference:** CLAUDE.md § Terminology (Layer Vocabulary)

---

## Core Terms

### Harness

The **agent layer**. Executes agent logic, tools, and workflows. May or may not come with a CLI, API, or other interface.

**Examples:**
- Codex CLI
- Claude Code CLI
- Claude Agent SDK
- Factory Droid
- Cursor (agent mode)

### LLM

The **model** (as known). The underlying language model invoked for completions.

**Examples:** GPT-5, Claude, Gemini, GLM-5, etc.

### Presentation Layer

The **UI layer** of a harness. How the user interacts with the agent.

**Examples:** Terminal UI, IDE panel, web UI, chat interface.

### Various Layers

Layers **between and around** the harness, LLM, and presentation. Include routing, proxy, auth, orchestration.

**Examples:**
- CLIProxyAPIPlus (proxy, auth, routing)
- LiteLLM Router (routing, fallback)
- thegent (orchestration, delegation)

---

## Layer Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────┐
│  Presentation layer  (UI: terminal, IDE, web)           │
├─────────────────────────────────────────────────────────┤
│  Harness  (agent layer: Codex CLI, Claude Code, Droid)  │
├─────────────────────────────────────────────────────────┤
│  Various layers  (routing, proxy, auth, orchestration)   │
├─────────────────────────────────────────────────────────┤
│  LLM  (model: GPT-5, Claude, Gemini, etc.)              │
└─────────────────────────────────────────────────────────┘
```

---

## Usage

- Use **harness** when referring to the agent execution layer (Codex, Claude Code, Droid, Cursor).
- Use **LLM** when referring to the model.
- Use **presentation layer** when referring to UI/UX of a harness.
- Use **various layers** when referring to routing, proxy, auth, orchestration between harness and LLM.

---

## Source: governance/TEST_COVERAGE_CRITICAL_GAP.md

# Test Coverage Critical Gap - Agent-Only Environment

**Date**: 2026-02-19
**Status**: 🚨 **CRITICAL GAP IDENTIFIED**
**Current Coverage**: 21.21% E2E
**Required Coverage**: **100%** (Agent-Only Requirement)

---

## 🚨 Critical Finding

### Current State
- **Total CLI Commands**: 297
- **Commands with E2E Tests**: 63 (21.21%)
- **Commands WITHOUT E2E Tests**: 234 (78.79%)
- **Coverage Gap**: **234 commands need E2E tests**

### Why This Is Critical

**In an agent-only environment:**
- ❌ NO humans will manually test commands
- ❌ NO manual verification possible
- ✅ **ONLY automated tests can verify behavior**
- ✅ **100% coverage is NOT optional - it's REQUIRED**

---

## 📊 Coverage Breakdown

### Commands with Tests (63)
- `list-agents` ✅
- `list-droids` ✅
- `clode` commands ✅
- `health-gate` ✅
- `health-report` ✅
- `resolve` ✅
- And 57 more...

### Commands WITHOUT Tests (234) - **CRITICAL**

**Core Commands**:
- ❌ `thegent run` - **MOST CRITICAL** (main execution)
- ❌ `thegent bg` - Background execution
- ❌ `thegent logs` - Log retrieval
- ❌ `thegent status` - Status checks
- ❌ `thegent doctor` - Health checks

**Orchestration** (Crew Management):
- ❌ `thegent orchestrate crew create`
- ❌ `thegent orchestrate crew add-agent`
- ❌ `thegent orchestrate crew add-task`
- ❌ `thegent orchestrate crew execute`
- ❌ `thegent orchestrate crew list`
- ❌ `thegent orchestrate crew show`
- ❌ `thegent orchestrate crew status`

**Team Management**:
- ❌ `thegent teams create`
- ❌ `thegent teams list`
- ❌ `thegent teams show`
- ❌ `thegent teams add-member`
- ❌ `thegent teams remove-member`

**Hierarchy Management**:
- ❌ `thegent hierarchy show`
- ❌ `thegent hierarchy tree`
- ❌ `thegent hierarchy relationships`

**Compliance & Governance**:
- ❌ `thegent compliance export`
- ❌ `thegent compliance siem-test`
- ❌ `thegent compliance plugin-check`
- ❌ `thegent compliance redact`
- ❌ `thegent compliance ledger-verify`

**And 200+ more commands...**

---

## 🎯 Immediate Action Required

### Priority 1: Critical Commands (Week 1)
These commands are used most frequently and MUST have tests:

1. **`thegent run`** - Main execution command
2. **`thegent bg`** - Background execution
3. **`thegent logs`** - Log retrieval
4. **`thegent status`** - Status checks
5. **`thegent doctor`** - Health checks
6. **`thegent orchestrate crew *`** - All crew commands
7. **`thegent teams *`** - All team commands
8. **`thegent hierarchy *`** - All hierarchy commands

### Priority 2: Core Workflows (Week 2)
1. Agent execution flow
2. Crew execution flow
3. Team coordination flow
4. Route resolution flow
5. Configuration flow

### Priority 3: Remaining Commands (Week 3-4)
All other 200+ commands

## CI Coverage Gate Status

- CI now includes a dedicated `preflight` job (`collect-only`, coverage contract, and required provider smoke checks).
- A required `coverage` job in `.github/workflows/ci.yml` runs `task coverage:ci` and blocks downstream integration testing.
- `scripts/analyze_test_coverage.py` still reports stale command-surface counts and should be refreshed after this infrastructure is stable.

---

## 🛠️ Implementation Tools Created

### 1. Coverage Analysis Script
- **File**: `scripts/analyze_test_coverage.py`
- **Purpose**: Analyze current coverage and generate reports
- **Usage**: `python scripts/analyze_test_coverage.py`

### 2. Test Templates
- **Location**: `tests/e2e/templates/`
- **Purpose**: Auto-generated test templates for missing commands
- **Usage**: Copy templates and implement tests

### 3. BDD Test Framework
- **File**: `tests/e2e/test_template_bdd.py`
- **Purpose**: BDD-style test structure for agent journeys
- **Usage**: Use as template for new tests

### 4. Governance Documentation
- **Files**:
  - `docs/governance/AGENT_ONLY_TEST_STRATEGY.md`
  - `docs/governance/TDD_BDD_SDD_GOVERNANCE.md`
- **Purpose**: Define test strategy and governance

---

## 📈 Coverage Target Update

### Before
```toml
[tool.coverage.report]
fail_under = 80  # Insufficient for agent-only
```

### After
```toml
[tool.coverage.report]
fail_under = 100  # REQUIRED for agent-only environment
```

---

## 🚀 Next Steps

### Immediate (This Week)
1. ✅ Coverage analysis complete
2. ✅ Governance documentation created
3. ⏳ Implement E2E tests for Priority 1 commands
4. ⏳ Set up BDD framework (pytest-bdd)

### Short Term (This Month)
1. ⏳ Implement E2E tests for all 234 missing commands
2. ⏳ Expand integration test coverage
3. ⏳ Complete unit test coverage to 100%

### Ongoing
1. ⏳ Maintain 100% coverage for new code
2. ⏳ Run coverage analysis weekly
3. ⏳ Update test strategy as needed

---

## 📊 Success Metrics

### Coverage Metrics
- **E2E Coverage**: 21.21% → **100%** (target)
- **Integration Coverage**: Unknown → **100%** (target)
- **Unit Coverage**: Unknown → **100%** (target)

### Quality Metrics
- **Test Execution Time**: < 10 minutes
- **Test Reliability**: 99.9%+ (no flaky tests)
- **Mutation Score**: 80%+

---

## ⚠️ Risk Assessment

### Current Risk: **CRITICAL**

**Without 100% test coverage:**
- ❌ Agents may encounter untested failure modes
- ❌ Bugs may go undetected until production
- ❌ No way to verify behavior changes
- ❌ System reliability unknown

**With 100% test coverage:**
- ✅ All agent journeys verified
- ✅ Bugs caught before production
- ✅ Behavior changes validated
- ✅ System reliability known

---

**Status**: 🚨 **CRITICAL GAP - IMMEDIATE ACTION REQUIRED**
**Coverage Target**: **100%** (not 21.21%)
**Timeline**: 4 weeks to achieve 100% coverage

---
