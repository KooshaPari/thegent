# Phase 1 Binary Implementation Handoff

## Scope: Phase 1.2 - 1.3 (Quality-Gate & Security-Pipeline Binaries)

### Tasks
- **1.2.1** — Create quality-gate Binary Skeleton (2h)
- **1.2.2** — Implement quality-gate Logic (4h)
- **1.2.3** — Write Integration Tests (3h)
- **1.2.4** — Benchmark & Compare (3h)
- **1.3.1** — SecurityScanner (already in lib) (0h)
- **1.3.2** — Create security-pipeline Binary (2h)
- **1.3.3** — Cross-Platform Testing (2h)

**Total Effort**: ~16 hours

### Resources Available

#### Governance Library (Ready to Use)
Location: `crates/thegent-hooks/src/`

**Available Components**:
- `PolicyEngine`: `policy.rs` (~200 LOC)
  - `PolicyEngine::new(rules: Vec<PolicyRule>)`
  - `PolicyEngine::evaluate(context: HashMap<String, Value>) -> Result<Vec<PolicyOutcome>>`
  - Rules support Cost, Quality, Security, Spec types
  - Built-in caching via DashMap

- `QualityEvaluator`: `quality.rs` (~130 LOC)
  - `QualityEvaluator::parse_ruff_json(json_str) -> Result<Vec<LintIssue>>`
  - `QualityEvaluator::parse_oxlint_json(json_str) -> Result<Vec<LintIssue>>`
  - `QualityEvaluator::extract_coverage_percent(json_str) -> Result<f64>`
  - `QualityEvaluator::aggregate_metrics(issues, coverage) -> QualityMetrics`

- `SecurityScanner`: `security.rs` (~100 LOC)
  - `SecurityScanner::new()` → pre-loaded with 8+ secret patterns
  - `SecurityScanner::scan_text(content) -> Vec<SecurityFinding>`
  - `SecurityScanner::parse_semgrep_json(json_str) -> Result<Vec<SecurityFinding>>`

- `CostCalculator`: `cost.rs` (~120 LOC)
  - `CostCalculator::calculate(model, input_tokens, output_tokens) -> Result<CostEstimate>`
  - Hardcoded pricing for 6+ models

#### Type Definitions
All types in `crates/thegent-hooks/src/types.rs`:
- `PolicyRule`, `PolicyOutcome`, `RuleType`, `Severity`
- `QualityMetrics`, `LintIssue`
- `SecurityFinding`, `Severity`
- `CostEstimate`
- `HookError` (custom error type)

### Binary Design

#### Option 1: Unified Binary (Recommended)
**Approach**: Single `quality-gate` binary that wraps PolicyEngine + QualityEvaluator
```bash
# Input: JSON stdin
{ "project_dir": "/path", "changed_files": [...], "coverage_pct": 85.5, ... }

# Execution: 
# 1. Load governance rules from .thegent/governance.yaml
# 2. Parse stdin → EvaluationContext
# 3. engine.evaluate(context) → Vec<PolicyOutcome>
# 4. Print violations to stderr
# 5. Exit 0 (pass) or 1 (fail)
```

**Separate Binaries**: Similar pattern for `security-pipeline`

#### Option 2: Subcommand Binary (Alternative)
```bash
thegent-hooks quality-gate < input.json
thegent-hooks security-pipeline < input.json
```

### Implementation Checklist

#### Binary Scaffold (1.2.1)
- [ ] Create `quality-gate` binary entry point
- [ ] Accept JSON on stdin, parse to context
- [ ] Print to stderr on failure
- [ ] Exit code handling (0 pass, 1 fail, 124 timeout)

#### Quality-Gate Logic (1.2.2)
- [ ] Load governance.yaml rules
- [ ] Extract metrics from project files (coverage, lint, etc.)
- [ ] Evaluate rules via PolicyEngine
- [ ] Report violations to stderr
- [ ] Return exit code
- [ ] **Target**: ~150 LoC main logic

#### Tests (1.2.3)
- [ ] Test 1: Pass case (high coverage, no lint issues)
- [ ] Test 2: Fail case (low coverage < threshold)
- [ ] Test 3: Fail case (lint errors > threshold)
- [ ] Test 4: Fail case (lint suppressions without justification)
- [ ] Test 5: Edge case (empty project)
- [ ] Test 6: Cross-platform (macOS, Linux, WSL)
- [ ] **Target**: 10+ tests, <100ms each

#### Benchmarks (1.2.4)
- [ ] Run quality-gate 10× on test project
- [ ] Compare Rust vs Bash latency
- [ ] Collect: mean, stddev, min, max
- [ ] **Target**: ≥50% faster than Bash equivalent

#### Security-Pipeline (1.3.2)
- [ ] Similar scaffold to quality-gate
- [ ] Use SecurityScanner for secret/SAST detection
- [ ] Report findings to stderr
- [ ] Exit code (0 pass, 1 fail)
- [ ] **Target**: ~120 LoC main logic

#### Cross-Platform Tests (1.3.3)
- [ ] Run all tests on macOS 13+
- [ ] Run all tests on Ubuntu 22.04 (CI container)
- [ ] Run all tests on WSL2
- [ ] Document platform-specific findings

### File Structure (Target)
```
crates/thegent-hooks/
├── Cargo.toml                         # Add [[bin]] targets
├── src/
│   ├── lib.rs                        # (No changes)
│   ├── main.rs                       # (Existing utility)
│   ├── bin/
│   │   ├── quality-gate.rs           # NEW
│   │   └── security-pipeline.rs      # NEW
│   └── [other modules]
└── tests/
    ├── quality_gate_integration_tests.rs    # NEW
    └── security_pipeline_integration_tests.rs # NEW
```

### Configuration Files

#### Governance Rules (governance.yaml)
```yaml
policies:
  - id: coverage-threshold
    type: quality
    condition: "coverage >= 80"
    severity: error
    enabled: true
    
  - id: lint-errors
    type: quality
    condition: "lint_errors == 0"
    severity: error
    enabled: true
```

#### Input JSON Format
```json
{
  "project_dir": "/path/to/project",
  "cwd": "/path/to/project",
  "session_id": "abc-123",
  "head_sha": "abc1234",
  "changed_files": ["src/main.rs", "tests/test.rs"],
  "coverage_pct": 85.5,
  "lint_errors": 3,
  "lint_warnings": 12,
  "lint_suppressions": ["E501 -- long line is URL"]
}
```

#### Output Format
**Stderr** (on failure):
```
HOOK quality-gate: evaluating governance policy
HOOK quality-gate: loaded 3 rules from governance.yaml
HOOK quality-gate: VIOLATION - coverage 65% < threshold 80%
HOOK quality-gate: VIOLATION - 2 new lint suppressions without justification
```

**Exit Code**:
- 0: All checks pass
- 1: Violations found
- 124: Timeout

### Build & Test Commands
```bash
# Build
cd crates/thegent-hooks
cargo build --release --bin quality-gate
cargo build --release --bin security-pipeline

# Test
cargo test --bin quality-gate
cargo test --bin security-pipeline
cargo test --test '*_integration'

# Benchmark
time ./target/release/quality-gate < tests/fixtures/input.json

# Coverage (optional)
cargo tarpaulin --bin quality-gate --out Html
```

### Key Dependencies
- `serde_json` (for JSON parsing)
- `serde_yaml` (for governance.yaml loading)
- `thegent-hooks` (the library we created)
- `lazy_static` (for regex patterns)
- `dashmap` (for caching)

### Success Criteria

#### Phase 1.2 (Quality-Gate)
- [ ] Binary compiles without warnings
- [ ] Accepts JSON on stdin, parses correctly
- [ ] Evaluates policies and reports violations
- [ ] Exit codes match spec (0/1/124)
- [ ] 10+ integration tests pass
- [ ] Cross-platform tests pass (macOS, Linux, WSL)
- [ ] Rust version 50% faster than Bash

#### Phase 1.3 (Security-Pipeline)
- [ ] Binary compiles without warnings
- [ ] Detects 8+ secret patterns accurately
- [ ] Parses semgrep JSON output
- [ ] Reports findings with severity levels
- [ ] Cross-platform tests pass

#### Code Quality
- [ ] Test coverage ≥85%
- [ ] No lint errors (ruff/clippy)
- [ ] Type-safe (no unsafe code)
- [ ] Documented main functions

### Risk Mitigation
- **Risk**: Async complexity → **Mitigation**: Phase 1 is sync-only
- **Risk**: Dependency version conflicts → **Mitigation**: Use pinned versions from workspace
- **Risk**: Cross-platform issues → **Mitigation**: Early testing on all platforms
- **Risk**: Performance regression → **Mitigation**: Benchmark from day 1

---

## Recommended Approach

**Use `thegent free --do-next`** to execute:

```
Task: Implement Phase 1.2-1.3 quality-gate and security-pipeline binaries

Phase 1.2 Quality-Gate PoC:
1. Create binary crate scaffold (stdin/stdout/exit code interface)
2. Implement core logic (~150 LoC) using PolicyEngine + QualityEvaluator
3. Write 10+ integration tests (pass/fail scenarios)
4. Benchmark vs Bash: target 50% latency improvement

Phase 1.3 Security-Pipeline PoC:
1. Create binary scaffold (similar to quality-gate)
2. Implement core logic (~120 LoC) using SecurityScanner
3. Write cross-platform tests (macOS, Linux, WSL)

Deliverables:
- Compiled binaries: quality-gate, security-pipeline
- Integration tests (all passing on CI)
- Benchmark report (latency, memory, CPU)
- Test fixtures and config samples
```

---

**Owner**: Rust Engineer  
**Duration**: ~16h (2-day sprint)  
**Blockers**: None (library ready)
