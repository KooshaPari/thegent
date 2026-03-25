# Technical Debt Remediation Plan - 2026 Q2-Q4

## Executive Summary

Comprehensive plan to address technical debt, security vulnerabilities, and architectural improvements across the Phenotype ecosystem.

## Priority Matrix

| Priority | Impact | Effort | Items |
|----------|--------|--------|-------|
| P0-Critical | High | High | Security vulnerabilities, data loss risks |
| P1-High | High | Low | Quick wins, documentation, tooling |
| P2-Medium | Medium | Medium | Architectural improvements |
| P3-Low | Low | Low | Nice-to-have polish |

---

## P0-Critical: Security Vulnerabilities

### heliosCLI (28 vulnerabilities)

**Timeline**: Week 1-2

**Actions**:
1. Run `cargo update` to get latest patched dependencies
2. Review GitHub Dependabot alerts
3. Enable automated security updates
4. Pin critical dependencies to exact versions

**Verification**:
```bash
cd heliosCLI && cargo audit
```

### thegent (8 vulnerabilities)

**Timeline**: Week 1-2

**Actions**:
1. Run `bun pm audit` or `npm audit`
2. Update transitive dependencies
3. Enable Dependabot for Bun/npm
4. Review and fix critical CVEs

**Verification**:
```bash
cd thegent && bun pm audit
```

---

## P1-High: Quick Wins

### 1. Documentation Gaps

**Timeline**: Week 2-3

**Items**:
- [ ] API documentation for heliosCLI
- [ ] README improvements for all 75+ repos
- [ ] Architecture decision records (ADRs)
- [ ] Migration guides for major changes

### 2. Test Coverage

**Timeline**: Week 2-4

**Items**:
- [ ] Increase heliosApp test coverage to 80%
- [ ] Add integration tests for thegent
- [ ] Add property-based tests to heliosCLI
- [ ] Set up coverage reporting in CI

### 3. CI/CD Improvements

**Timeline**: Week 3-4

**Items**:
- [ ] Add automated security scanning
- [ ] Add performance benchmarks to CI
- [ ] Add code quality gates (lint, format)
- [ ] Add dependency freshness checks

---

## P2-Medium: Architectural Improvements

### 1. Library Extraction (per rolling hand rules)

**Timeline**: Q2 2026

**Phases**:

#### Phase 1: Extract Shared Domain Models
- Move domain entities from thegent to phenotype-shared
- Move value objects from heliosApp to phenotype-shared
- Create shared type definitions

#### Phase 2: Extract Shared Infrastructure
- Extract caching patterns
- Extract logging/metrics infrastructure
- Extract configuration management

#### Phase 3: Extract Shared Adapters
- HTTP client patterns
- Database adapter patterns
- Cache adapter patterns

### 2. Hexagonal Architecture Rollout

**Timeline**: Q2-Q3 2026

**Targets**:
- [ ] Apply hexagonal to heliosCLI (60% complete)
- [ ] Apply hexagonal to phenotype-go-kit
- [ ] Apply hexagonal to phenotype-shared (80% complete)

### 3. Plugin Architecture Standardization

**Timeline**: Q3 2026

**Actions**:
- [ ] Complete phenotype-plugin-core
- [ ] Migrate thegent plugins to plugin-core
- [ ] Create plugin SDK documentation
- [ ] Set up plugin registry

---

## P3-Low: Polish

### 1. Code Quality

**Timeline**: Ongoing

**Items**:
- [ ] Reduce cyclomatic complexity in legacy code
- [ ] Remove dead code
- [ ] Standardize error handling
- [ ] Improve naming consistency

### 2. Performance

**Timeline**: Q3-Q4 2026

**Items**:
- [ ] Profile and optimize hot paths
- [ ] Add caching where appropriate
- [ ] Optimize database queries
- [ ] Reduce memory allocations

### 3. Observability

**Timeline**: Q4 2026

**Items**:
- [ ] Standardize logging format
- [ ] Add distributed tracing
- [ ] Create runbooks for common issues
- [ ] Set up alerting dashboards

---

## Resource Allocation

### Q2 2026 (April-June)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1-2 | Security fixes | Vulnerabilities resolved |
| 3-4 | Documentation | API docs, README updates |
| 5-8 | Test coverage | +20% coverage heliosApp |
| 9-12 | Library extraction | Shared domain models |

### Q3 2026 (July-September)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 13-16 | Hexagonal rollout | heliosCLI hexagonal complete |
| 17-20 | Plugin architecture | Plugin core production-ready |
| 21-24 | CI/CD improvements | Automated quality gates |

### Q4 2026 (October-December)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 25-28 | Performance | 20% latency reduction |
| 29-32 | Observability | Full distributed tracing |
| 33-36 | Polish | Documentation complete |

---

## Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Security vulnerabilities | 36 | 0 | Q2 2026 |
| Test coverage (heliosApp) | ~60% | 80% | Q2 2026 |
| Test coverage (thegent) | ~50% | 70% | Q3 2026 |
| Hexagonal adoption | 40% | 80% | Q4 2026 |
| Documentation completeness | 60% | 90% | Q4 2026 |
| API docs coverage | 40% | 80% | Q2 2026 |

---

## Dependencies

1. Security fixes must complete before library extraction
2. Documentation must complete before plugin architecture
3. Hexagonal rollout enables plugin standardization

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Resource constraints | High | Prioritize P0-P1 |
| Breaking changes | Medium | Extensive testing, migration guides |
| Dependency conflicts | Medium | Pin versions, test thoroughly |
| Scope creep | Medium | Strict priority matrix |

---

## Sign-off

Created per rolling hand rules governance.
Last updated: 2026-03-25
