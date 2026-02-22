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

