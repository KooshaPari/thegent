# 2026-02-22 Pytest Optimization and Atoms Cross-Repo Research

## Scope
- Consolidate findings and plan for pytest performance in `thegent`.
- Add FR/user-story traceability + DAG execution strategy.
- Document cross-repo findings for `atoms.tech` clean/deploy in:
  - `../atoms-mcp-prod`
  - `../agentapi/atomsAgent`

## Part A: thegent Pytest Performance Audit

### Measured Baseline
- Test files discovered under `tests/`: `733`.
- Additional template test files in `tests/e2e/templates`: `47`.
- Collection timing (`python -m pytest --collect-only -q`): about `11.4s-12.0s`.
- Collected nodes before interruption: `13464` with `3` collection errors.
- Marker distribution (source scan):
  - `e2e=263`
  - `integration=21`
  - `slow=5`
  - `load=3`
  - `deep=4`
  - `fast=7`
- Lane selectivity (collect-only):
  - `-m fast`: `48` nodes
  - `-m "not slow and not integration and not e2e and not load"`: `12545` nodes
  - `-m "slow or integration or e2e or load"`: `1003` nodes

### Config/CI Surfaces
- `pyproject.toml` keeps broad discovery and marker config:
  - `pyproject.toml:114`
  - `pyproject.toml:116`
  - `pyproject.toml:140`
- Task lanes exist but current fast lane still selects most suite:
  - `Taskfile.yml:248`
  - `pytest-fast.ini:6`
- CI still runs broad test commands:
  - `.github/workflows/ci.yml:42`
  - `.github/workflows/test.yml:37`

### Key Bottlenecks
- High fixed collection cost due suite size and broad discovery.
- Marker imbalance means fast lane remains too large.
- Collection errors block reliable timing regressions and optimization loops.
- `xdist` exists in `uv` environment, but blanket usage is not a guaranteed win.

## Part B: thegent Optimization Plan

### P0 (Stability First)
1. Make collection clean (fix/guard failing native collection modules).
2. Add CI check that `--collect-only` has zero errors.

### P1 (Biggest Runtime Reduction)
1. Tighten discovery scope:
   - Exclude non-runtime template trees from default collection.
   - Reassess `testpaths = ["tests", "src"]` and keep default lane focused.
2. Rebalance marker taxonomy:
   - Move heavy tests to `integration/slow/e2e/load` consistently.
   - Target a much smaller PR fast lane and push heavier coverage to nightly.
3. Split CI lanes:
   - PR: `test:fast-lane` + targeted contract checks.
   - Scheduled/nightly: `nightly-lane` + leak/native/deep lanes.

### P2 (Measured Advanced Tuning)
1. Apply `xdist` selectively where measured gains exist.
2. Add duration telemetry per lane and rebalance periodically.
3. Pilot impact-based selection and CI sharding (see Part C).

## Part C: FR/User-Story Linking + DAG Strategy

### Current State in thegent
- Requirement marker is declared: `pyproject.toml:126`.
- Real usage exists across tests (for example `tests/test_project_tenancy.py:49`).
- `@trace` comments also exist and can be mined as secondary evidence.

### Recommended Traceability Contract
1. Canonical key: `@pytest.mark.requirement("FR-...")`.
2. Build extractor artifact each run:
   - `requirement -> [test nodeids]`
   - `test nodeid -> [requirements]`
   - uncovered requirements report
3. Enforce in CI:
   - Changed tests must map to FR/WL unless exempted.
   - Nightly full graph consistency check.

### DAG Execution Strategy
- Preferred: requirement-layer DAG (topological order by FR dependencies).
- Secondary: test-level dependency DAG only for small critical chains.
- Keep dependency DAG narrow to avoid broad parallelism penalties.

### Additional Optimization Candidates
- Impact-based local/PR runs (`pytest-testmon`).
- Duration-balanced shard splitting (`pytest-split` + CI matrix).
- Local developer speedups (`--lf`, `--ff`).
- Stricter plugin/marker governance (`strict_markers`, `required_plugins`).

### Web Research References
- Pytest markers and strict markers:
  - https://docs.pytest.org/en/stable/how-to/mark.html
- Pytest hooks (`pytest_ignore_collect`, collection control):
  - https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html
- Pytest cache (`--lf`, `--ff`):
  - https://docs.pytest.org/en/stable/how-to/cache.html
- Pytest reference (config options incl. strict markers/required_plugins):
  - https://docs.pytest.org/en/stable/reference/reference.html
- pytest-xdist docs and limitations:
  - https://pytest-xdist.readthedocs.io/
  - https://pytest-xdist.readthedocs.io/en/stable/known-limitations.html
- pytest-dependency (dependency graphing caveats apply):
  - https://pytest-dependency.readthedocs.io/en/stable/configuration.html
- pytest-testmon:
  - https://testmon.org/
  - https://pypi.org/project/pytest-testmon/
- pytest-split:
  - https://pypi.org/project/pytest-split/
- GitHub Actions matrix (for shard fan-out):
  - https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
- Allure pytest links (optional external traceability linkage):
  - https://allurereport.org/docs/pytest-reference/

## Part D: atoms.tech Clean/Deploy Research

### D1. `../atoms-mcp-prod`

#### Clean Operations
- Task cleanup command present: `Taskfile.yml:50`.
- CLI cleanup command present: `cli.py:1163` (`atoms clean`).

#### Deploy Operations
- Vercel is explicitly configured and documented:
  - Runtime/build/routes in `vercel.json:1`.
  - Vercel deploy docs in `docs/guides/deployment.md:94` and `docs/guides/deployment.md:112`.
  - Base URL env points to prod domain in `docs/DEPLOYMENT_GUIDE.md:162`.
- App behavior switches docs/wiki links by environment:
  - `app.py:839` to `app.py:842` maps dev/prod wiki domains.
- Cloud Run deploy script also exists:
  - `scripts/deploy_gcp.sh:97`.

### D2. `../agentapi/atomsAgent`

#### clean/deploy/atoms.tech Linkage (explicit)
- `scripts/generate_supabase_models.py` directly searches for env files in sibling workspace paths including:
  - `clean/deploy/atoms.tech/.env.local`
  - `clean/deploy/atoms.tech/.env`
- Evidence:
  - `scripts/generate_supabase_models.py:41`
  - `scripts/generate_supabase_models.py:42`

#### Deploy Operations
- Cloud Run deploy CLI command is implemented:
  - `src/atomsAgent/cli/commands/cloud_run.py:90`.
- Cloud Run usage is documented for default flow:
  - `docs/guides/deployment.md:22`.
- Infra docs/scripts show SST Cloud Run deployment path:
  - `package.json:8`
  - `infrastructure/README.md:20`
- Pulumi deploy command still exists in CLI:
  - `src/atomsAgent/cli/commands/deploy.py:17`.

#### Domain/Endpoint Wiring
- Environment-specific Atoms MCP endpoint registration:
  - `migrations/register_atoms_mcp_prod.sql:31`
  - `migrations/register_atoms_mcp_prod.sql:32`
- DNS automation for custom domain:
  - `scripts/deployment/configure-dns.sh:12` (`ai.atoms.tech`).

### D3. Cleanup Work in atomsAgent Docs
- Historical documentation cleanup report exists:
  - `docs/CLEANUP_SUMMARY.md:1`
  - Includes root markdown consolidation and standards.

### Task 81–85 Execution Addendum

- Task-81: cross-repo KB now created at `docs/contracts/ATOMS_CLEAN_DEPLOY_KNOWLEDGE_BASE.md`.
- Task-82: canonical clean/deploy guidance for `atoms-mcp-prod` and `atomsAgent` documented there.
- Task-83: env discovery contract normalized in the KB with precedence and hard-fail expectations.
- Task-84: pytest health aggregation command and contract now documented in `docs/contracts/TEST_HEALTH_DASHBOARD.md`.
- Task-85: CI alert surface + dedicated health artifact upload added to `.github/workflows/ci.yml` and `.github/workflows/test.yml`.

## Observed Cross-Repo Pattern
- `atoms-mcp-prod` appears Vercel-first with optional Cloud Run tooling.
- `atomsAgent` appears Cloud Run-first but contains multiple deploy surfaces (Cloud Run CLI + Pulumi command + SST scripts/docs).
- `atomsAgent` includes active coupling to the `clean/deploy/atoms.tech` workspace for env discovery during model generation.

## Suggested Consolidation Follow-up
1. Declare one canonical deploy path per repo and mark others as legacy/deprecated.
2. Keep `clean/deploy/atoms.tech` env dependency explicit in onboarding docs if intentional.
3. Add a lightweight consistency check so endpoint/domain assumptions remain aligned across repos.


## Addendum: User Confirmed "Yes to All" (2026-02-22)

Status: Accepted. Proceed with all recommendations below.

### A. FR/User-story Linking Strategy (Accepted)

Context confirmed in `thegent`:
- Requirement marker is registered in `thegent/pyproject.toml:126`.
- Existing usage of `@pytest.mark.requirement(...)` is substantial (for example `tests/test_project_tenancy.py:49`).
- `@trace ...` comments are present and can be mined into the same graph.

Accepted strategy:
1. Normalize to one canonical ID schema and one source of truth.
2. Keep `@pytest.mark.requirement("FR-...")` as canonical test metadata.
3. Add a lightweight extractor (AST/regex) that outputs:
   - `requirement -> [test nodeids]`
   - `test nodeid -> [requirements]`
   - coverage gaps (requirements with 0 tests)
4. Emit machine-readable artifacts each CI run (JSON + CSV + markdown summary).
5. Enforce governance:
   - PR lane: changed tests must include requirement mapping unless explicitly exempt.
   - Nightly lane: full matrix consistency check.

Reference alignment (confirmed):
- https://docs.pytest.org/en/stable/how-to/mark.html
- https://docs.pytest.org/en/stable/reference/reference.html
- Optional external test-management linkage (Allure):
  - https://allurereport.org/docs/pytest-reference/

### B. DAG-ing Tests (Accepted)

Two-model approach accepted:

1. Requirement DAG (primary, recommended)
- Nodes: FR/user stories.
- Edges: requirement dependencies from backlog/spec graph.
- Run order: topological sort of FRs, then run tests mapped to each FR layer.
- Benefit: architecture-aware and product-facing.

2. Test dependency DAG (limited/sparing use)
- Nodes: specific tests.
- Edges: explicit test dependencies.
- `pytest-dependency` can model this, but it has xdist-parallelization limitations.
- Best for small critical chains; not for broad suite scaling.

References:
- https://pytest-dependency.readthedocs.io/en/stable/configuration.html
- https://pytest-dependency.readthedocs.io/en/0.6.0/usage.html
- https://pytest-xdist.readthedocs.io/en/stable/known-limitations.html

### C. Other Relevant Optimization Strategies (Accepted)

1. Impact-based local/PR runs
- Pilot `pytest-testmon` for changed-code selective runs.
- https://testmon.org/
- https://pypi.org/project/pytest-testmon/

2. Duration-balanced CI sharding
- Use `pytest-split` + GitHub matrix to reduce wall-clock.
- Recompute duration data regularly.
- https://pypi.org/project/pytest-split/
- https://docs.github.com/en/actions/

3. Use xdist where it helps
- Keep `-n auto` optional by lane/subtree, not blanket-enabled.

4. Tighten selection/governance
- Enable strict marker/config modes to prevent taxonomy drift.
- Use `required_plugins` to fail fast when perf-critical plugins are missing.
- https://docs.pytest.org/en/stable/reference/reference.html

5. Developer loop acceleration
- Standardize `--lf` / `--ff` local workflows.
- https://docs.pytest.org/en/stable/how-to/cache.html

6. Collection-time pruning
- Use `pytest_ignore_collect` (or config exclusions) to skip non-runtime template trees by default.
- https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html

### D. Concrete Rollout for thegent (Accepted)

1. Build traceability graph artifact + CI report first (no behavior change).
2. Introduce FR-layered lane (topologically ordered requirement groups).
3. Add impact lane (`testmon`) for PRs as non-blocking pilot.
4. Add duration-sharded nightly lane (`pytest-split` + matrix).
5. Promote stable lanes to required checks once flake/error budget is acceptable.

### E. Audit Summary (Accepted)

- Baseline size is large: `733` test files under `tests/`, plus `47` additional `test_*.py` files under `tests/e2e/templates` (currently in discovery).
- Collection overhead is high/fixed: `python -m pytest --collect-only -q` at about `11.4s-12.0s`, with `13464 tests collected, 3 errors`.
- Current blockers to clear first:
  - `tests/native/test_discovery_native.py`
  - `tests/native/test_git_native.py`
  - `tests/native/test_jsonl_parser.py`
- Marker distribution imbalance:
  - `e2e=263, integration=21, slow=5, load=3, deep=4, fast=7`
- Lane selectivity:
  - `-m fast` collects `48` nodes.
  - fast-lane expression collects `12545` nodes.
  - nightly expression collects `1003` nodes.
- `xdist` is available in `uv` env, but CI default jobs do not use it; measured gain on `tests/routing` was marginal (`18.13s` serial vs `17.51s` with `-n auto`).

Primary causes accepted:
- Discovery scope is broad (`testpaths = ["tests", "src"]`) and includes template-heavy e2e surface.
- Fast lane is expression-based while heavy tests are under-marked.
- CI default runs broad `pytest tests/ -v` instead of true PR fast lane.
- Collection errors block reliable optimization baselines.

### F. Prioritized Actions (Accepted)

P0:
1. Stabilize collection first.
2. Fix/skip native tests for missing optional binaries and broken mocks so `--collect-only` is clean.
3. Add CI gate: fail when collection has errors.

P1:
4. Prune default collection scope.
5. Revisit `testpaths` so `src` is not scanned in default lane unless required.
6. Make fast lane real via marker normalization and lane boundary enforcement.

### G. Config Surfaces to Change (Accepted)

- `pyproject.toml:114` (pytest discovery + markers)
- `pytest-fast.ini:6` (lane behavior)
- `Taskfile.yml:248` (fast/nightly tasks)

### H. Research Note (Accepted)

- Continue grounding implementation choices in official pytest docs and maintained plugins.
- Targeted research source set includes marker governance, config enforcement, hooks, cache behavior, xdist limitations, and maintained selection/sharding plugins.


## Part I: 100-Item Execution Plan (6 Agents + Owner)

### Tasks 1-15 (Owner: agent-1 / strategy + baseline)

1. Build a shared execution charter with scope, priority, lane policy, and rollback rules. | Owner: agent-1 | Acceptance: single markdown doc links each task to an objective and failure policy.
2. Confirm all task owners and handoff format; lock PR/owner matrix in the plan. | Owner: agent-1 | Acceptance: no unowned tasks in plan ranges 1-100.
3. Capture a reproducible suite baseline snapshot (`collect-only`, full/fast/nightly selections, wall time) and save it to artifacts. | Owner: agent-1 | Acceptance: baseline file includes timestamp, counts, command hash, runner metadata.
4. Export raw suite topology (`test file`, `nodeid`, marker, path) from current tree for migration planning. | Owner: agent-1 | Acceptance: topology export succeeds on clean checkout without custom env.
5. Define target success metrics for collection, PR fast lane, and nightly lane with explicit thresholds. | Owner: agent-1 | Acceptance: thresholds added to docs and used as CI checks.
6. Define canonical requirement schema and ID normalization rules in one place. | Owner: agent-1 | Acceptance: source of truth file contains FR and story ID regex, examples, and migration examples.
7. Define a 100-task execution contract and milestone cadence (P0/P1/P2 gates). | Owner: agent-1 | Acceptance: contract is accepted in report with named milestones.
8. Baseline and record current CI runtime, queue, and failure-mode profile for one representative run. | Owner: agent-1 | Acceptance: baseline file includes fail classes and per-lane timing.
9. Inventory all non-runtime / template-heavy discovery paths and classify required vs optional. | Owner: agent-1 | Acceptance: generated classification list includes owners and pruning policy per path.
10. Design change-risk matrix for each proposed config/lane adjustment. | Owner: agent-1 | Acceptance: each change includes rollback owner and expected risk score.
11. Define artifact retention policy for all new CI artifacts. | Owner: agent-1 | Acceptance: retention windows, naming pattern, and cleanup policy committed.
12. Standardize lane command templates and parameter placeholders in Taskfile and docs. | Owner: agent-1 | Acceptance: one command source can run PR fast, nightly, and deep lanes from same template.
13. Draft runbook for “collection fails / fast lane too big / artifact missing” incidents. | Owner: agent-1 | Acceptance: runbook covers triage steps and required owner escalation.
14. Set acceptance gate order: collection → traceability → schedule → optimization experiments → rollout. | Owner: agent-1 | Acceptance: CI checks reflect this order without race conditions.
15. Publish the final planning packet and freeze task numbering against report. | Owner: agent-1 | Acceptance: final plan section references all tasks 1-100.

### Tasks 16-30 (Owner: agent-2 / stabilization + gates)

16. P0 Collection Error Quarantine | Owner: agent-2 | Owner: agent-2 | Success criteria: Native collection entry points in `tests/native/` are fixed or deterministically skipped and `python -m pytest --collect-only -q` reports 0 errors locally and in CI.
17. P0 Optional Dependency Guards for Collection | Owner: agent-2 | Success criteria: optional binaries/plugins missing do not fail collection; tests are skip-guarded with explicit reasons.
18. P0 “collect-only” Error Gate in CI | Owner: agent-2 | Success criteria: CI runs `--collect-only` and fails on any collection error with log artifact.
19. P0 Collection Baseline Freeze | Owner: agent-2 | Success criteria: node-count and file-level error baseline is compared each run, >15% regression blocks reliability lane.
20. P0 Marker Registration Completeness | Owner: agent-2 | Success criteria: strict marker and required plugin checks fail unknown/invalid markers.
21. P0 Template-Tree Pruning Rule | Owner: agent-2 | Success criteria: default lane skips template-heavy trees and non-template collection shrinks by at least 70%.
22. P0 Lane Topology Enforcement | Owner: agent-2 | Success criteria: PR and nightly collection selectors are truly separate with no template bleed in fast lane.
23. P0 Fast-Lane Correctness Gate | Owner: agent-2 | Success criteria: fast-lane collection remains below 10% of full suite and is stable for two consecutive runs.
24. P0 Marker Taxonomy Correction | Owner: agent-2 | Success criteria: heavy tests are fully reclassified into runtime categories and validator confirms no misclassified leftovers.
25. P0 Collection Reliability Telemetry | Owner: agent-2 | Success criteria: collection timing + error telemetry is emitted and trend alerts on >10% regression.
26. P0 CI Gate for Collection Exit Codes | Owner: agent-2 | Success criteria: collection exit codes are mandatory checks and no soft-fail paths in PR lane.
27. P0 xdist Scope Control | Owner: agent-2 | Success criteria: xdist is only used on eligible workloads and rejected by gate when undocumented.
28. P0 Collection Skiplist Contract | Owner: agent-2 | Success criteria: stable skiplist file exists and CI validates format with drift error.
29. P0 Collection Timeout Controls | Owner: agent-2 | Success criteria: collection timeout guard fails fast and returns stack/context artifact.
30. P0 CI Orchestration for PR vs Nightly Gates | Owner: agent-2 | Success criteria: PR and nightly reliability gates run with branch-aware policy and clear failure reasons.

### Tasks 31-44 (Owner: agent-3 / FR linkage)

31. Add `@pytest.mark.requirement` and FR alias markers to suites missing traceability metadata. | Owner: agent-3 | Success criteria: target perf-related suites have mandatory requirement/story marker coverage.
32. Map user-story IDs to FR IDs in test decorators. | Owner: agent-3 | Success criteria: deterministic mapping from story marker to FR IDs with no orphan story markers.
33. Add auto-discovery of FR/user-story markers in extractor CLI. | Owner: agent-3 | Success criteria: extractor produces complete FR-story pair list for collected tests.
34. Normalize marker parsing across test types for extractor consistency. | Owner: agent-3 | Success criteria: parser handles `pytest` markers, `conftest`, and inline markers consistently.
35. Generate enriched `traceability_links.json` artifacts. | Owner: agent-3 | Success criteria: output includes source, type, FR/story IDs, file path, node id and relation.
36. Generate human-readable `LINK_INDEX.md`. | Owner: agent-3 | Success criteria: FR-to-test matrix with counts is generated each run.
37. Generate FR-level coverage report for pytest. | Owner: agent-3 | Success criteria: mapped vs unmapped FR list is emitted with gap highlighting.
38. Add validation for extractor schema and broken references. | Owner: agent-3 | Success criteria: CI fails on invalid references or schema.
39. Add extractor output diffing and changelog artifact. | Owner: agent-3 | Success criteria: added/removed links are diffed and included in CI summary.
40. Establish FR coverage floor for pytest optimization domain. | Owner: agent-3 | Success criteria: minimum 70% baseline, 85% target FR traceability coverage.
41. Link performance tests to optimization FRs/stories. | Owner: agent-3 | Success criteria: all new perf tests carry FR/story markers and appear in artifacts.
42. Link test-only artifacts to FRs. | Owner: agent-3 | Success criteria: slow/integration markers include FR linkage.
43. Add extractor command in CI/CD. | Owner: agent-3 | Success criteria: extractor runs in CI and publishes artifacts.
44. Document maintenance workflow for marker and artifact refresh. | Owner: agent-3 | Success criteria: clear PR flow exists from marker add → regenerate → validate → merge.

### Tasks 45-58 (Owner: agent-4 / DAG + scheduler)

45. Pytest Graph Contract v1 | Owner: agent-4 | Success criteria: deterministic graph schema defined and validated.
46. Dependency Annotation Extraction | Owner: agent-4 | Success criteria: dependency markers and known dependencies are extracted into graph edges.
47. Fixture-Scoped Dependency Resolver | Owner: agent-4 | Success criteria: fixture-derived edges are deterministic and validated.
48. DAG Validation and Cycle Guardrail | Owner: agent-4 | Success criteria: cyclic graphs and orphan edges fail clearly with cycle path.
49. Topological Batch Planner | Owner: agent-4 | Success criteria: stable batches are produced and reproduce the same order under same input.
50. Dependency-Aware Readiness Engine | Owner: agent-4 | Success criteria: nodes run only when predecessor constraints are satisfied.
51. Lane Model Specification | Owner: agent-4 | Success criteria: typed lane contracts exist with priority and policy controls.
52. Lane Scheduler Core | Owner: agent-4 | Success criteria: scheduler maps ready nodes to lanes honoring caps.
53. Capacity + Backpressure Controller | Owner: agent-4 | Success criteria: concurrency caps and backpressure behavior prevent saturation.
54. Anti-Starvation Fairness Policy | Owner: agent-4 | Success criteria: non-critical tasks make progress under continuous critical load.
55. Retry and Skip Propagation Policy | Owner: agent-4 | Success criteria: dependency behavior for fail/skip/retry is explicit and deterministic.
56. DAG Execution Engine with Checkpointing | Owner: agent-4 | Success criteria: reruns resume from last committed wave safely.
57. Telemetry and Lane Analytics | Owner: agent-4 | Success criteria: wave wait time, utilization, and dependency-wait metrics are exported.
58. 100-Item Optimization Validation | Owner: agent-4 | Success criteria: benchmark runbook demonstrates correctness and improved wall-clock for the DAG flow.

### Tasks 59-72 (Owner: agent-5 / perf controls + sharding)

59. Centralized marker registry and ownership model. | Owner: agent-5 | Success criteria: allowed markers are codified with owners and migration notes.
60. Marker consistency CI enforcement. | Owner: agent-5 | Success criteria: CI blocks unregistered markers.
61. Deprecate duplicate/legacy markers. | Owner: agent-5 | Success criteria: deprecated marker usage reduced by >90% with compatibility notes.
62. Standardize marker naming and semantics policy. | Owner: agent-5 | Success criteria: naming policy published and adopted by new tests.
63. Build baseline xdist performance baseline. | Owner: agent-5 | Success criteria: baseline runtime/utilization metrics captured before policy changes.
64. Define and publish xdist policy matrix. | Owner: agent-5 | Success criteria: documented decision matrix for suite class and worker profile.
65. Implement adaptive xdist worker routing. | Owner: agent-5 | Success criteria: CPU-bound tests parallelized, stateful tests serialized.
66. Add xdist failure-mode safeguards. | Owner: agent-5 | Success criteria: worker crash/retry policy and artifacts are deterministic.
67. Launch testmon pilot scope and success gate. | Owner: agent-5 | Success criteria: targeted pilot with measured hit-rate and false-negative watch.
68. Provision testmon cache infra and storage policy. | Owner: agent-5 | Success criteria: versioned, documented cache and retention.
69. Evaluate testmon selection quality and fallback behavior. | Owner: agent-5 | Success criteria: comparison report versus full suite with clear miss-rate risk.
70. Design sharding strategy and API contract. | Owner: agent-5 | Success criteria: shard contract includes shard count formula and assignment schema.
71. Implement deterministic time-aware shard assignment. | Owner: agent-5 | Success criteria: stable mapping with <2% runtime variance across reruns.
72. Unify cache flows across xdist/testmon/sharding. | Owner: agent-5 | Success criteria: single orchestrated cache flow with invalidation strategy.

### Tasks 73-86 (Owner: agent-6 / cross-repo + observability)

73. Refine Pytest Collection Baseline | Owner: agent-6 | Success criteria: collect-only runs report 0 errors and baseline telemetry emitted.
74. Tighten Default Discovery Scope | Owner: agent-6 | Success criteria: template and non-runtime trees are excluded by default and fast node count reduced by ≥20%.
75. Introduce Collection Guardrails Hook | Owner: agent-6 | Success criteria: deterministic skip behavior with low cross-run variance.
76. Rebalance Marker Taxonomy and Strictness | Owner: agent-6 | Success criteria: strict marker mode enforced and fast lane consistently under 1000 nodes.
77. Implement PR/CI Lane Split Strategy | Owner: agent-6 | Success criteria: separate lanes with budgets and failure triage are documented.
78. Emit Core Pytest Performance Metrics | Owner: agent-6 | Success criteria: JSON and markdown summaries emitted every run.
79. Add FR/Requirement Traceability Extractor | Owner: agent-6 | Success criteria: artifacts include requirement->tests and uncovered requirements.
80. Enforce Requirement Mapping Gate on PR Changes | Owner: agent-6 | Success criteria: PRs fail when test changes miss required markers with explicit exceptions syntax.
81. Create Cross-Repo Atoms Clean/Deploy Knowledge Base | Owner: agent-6 | Success criteria: knowledge base summarizes Vercel/Cloud Run path differences and env coupling.
82. Document Canonical Clean/Deploy Path in thegent | Owner: agent-6 | Success criteria: one canonical path doc with deprecated paths flagged.
83. Institutionalize Env-Discovery Contract | Owner: agent-6 | Success criteria: explicit contract for clean/deploy env requirements with hard-fail checks.
84. Stand Up Pytest Observability Plumbing | Owner: agent-6 | Success criteria: metrics export supports local verification and CI artifact output.
85. Add CI Dashboard/Alert Surface for Test Health | Owner: agent-6 | Success criteria: alert thresholds and breach runbook exist for collection/misfire/lane regressions.
86. Publish 14-Day Optimization Feedback Loop | Owner: agent-6 | Success criteria: recurring feedback task updates owners/priority and closes completed milestones.

### Tasks 87-100 (Owner: Codex / execution sequencing + hardening)

87. Build a PR-only targeted run profile and wire to local helper task alias. | Owner: Codex | Success criteria: PR contributors can run the same gate locally with documented command.
88. Add changelist-aware selector to run only touched/related suites in PR mode. | Owner: Codex | Success criteria: changed files map to test selection with safe fallback to fast lane.
89. Add anti-flake run profile (`--reruns` + `--maxfail`) with explicit opt-in lane. | Owner: Codex | Success criteria: dedicated flake lane has deterministic thresholds and failure visibility.
90. Publish a minimal “how to reduce suite impact” guide for developers. | Owner: Codex | Success criteria: guide includes marker best practices and cost-aware test writing.
91. Add `trace` comment harvesting in extractor as secondary evidence source. | Owner: Codex | Success criteria: optional source emits `@trace` to FR mapping warnings and confidence score.
92. Add migration helper script to list untagged heavy tests over threshold. | Owner: Codex | Success criteria: script reports tests exceeding configured duration and missing FR markers.
93. Add PR template updates to require artifact links and FR mapping evidence. | Owner: Codex | Success criteria: PR lint check validates template fields for test-only touch points.
94. Add explicit benchmark jobs for `tests/routing` and one heavy e2e module with/without xdist. | Owner: Codex | Success criteria: job history stores comparable baseline with confidence intervals.
95. Add nightly job to run collect-only on template path separately. | Owner: Codex | Success criteria: template regressions are detected without slowing PR lanes.
96. Add contract test for requirement extractor CLI schema stability. | Owner: Codex | Success criteria: schema contract test fails on breaking change.
97. Define promotion criteria for making optional lanes required. | Owner: Codex | Success criteria: criteria includes stability threshold, max flake ratio, and acceptable fail budget.
98. Build a one-page dependency DAG/FR mapping diagram from extractor output. | Owner: Codex | Success criteria: generated diagram is committed and updated in each nightly.
99. Set quarterly cleanup routine to remove deprecated markers and stale traceability debt. | Owner: Codex | Success criteria: scheduled cleanup issue created when stale debt window breaches threshold.
100. Produce final “go-live” handoff brief and handoff checklist. | Owner: Codex | Success criteria: checklist includes config gates, rollback steps, and on-call ownership.

### Task 96-100 Execution Evidence

- 96: added contract stability test coverage for `requirements-map` payload keys in `tests/test_wl137_pr_mode_and_flake_lane.py`.
- 97: added promotion criteria assertions for stability threshold, flake ratio, fail budget, and optional-lane readiness in `tests/test_wl137_pr_mode_and_flake_lane.py`.
- 98: added FR map truncation test and diagram command coverage plus Taskfile/guide updates for diagram refresh in `tests/test_wl137_pr_mode_and_flake_lane.py` and `Taskfile.yml`.
- 99: added quarterly traceability cleanup task and issue contract test coverage in `Taskfile.yml` and `tests/test_wl137_pr_mode_and_flake_lane.py`.
- 100: added go-live handoff report at `docs/reports/2026-02-22-pytest-go-live-handoff.md` and contract/guide updates for rollout checks.

See operational Wave-1 execution tracker in `thegent/docs/reports/2026-02-22-pytest-wave-1-runbook.md`.

Wave-1 execution tracker: `thegent/docs/reports/2026-02-22-pytest-wave-1-progress.md`.
