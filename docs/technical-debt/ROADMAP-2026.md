# Technical Roadmap - 2026

## Q2 2026: Foundation

```
April                    May                     June
┌───────────────────────┬───────────────────────┬───────────────────────┐
│ Security Hardening    │ Library Extraction     │ Hexagonal Rollout     │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ Week 1-2:            │ Week 5-6:             │ Week 9-10:            │
│ - Fix 28 vulns        │ - Domain models       │ - Apply hexagonal     │
│ - Fix 8 vulns        │ - Value objects       │ - to heliosCLI       │
│ - Enable Dependabot   │ - Shared types        │ - Migrate plugins     │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ Week 3-4:            │ Week 7-8:             │ Week 11-12:          │
│ - Update docs         │ - Infra patterns      │ - Test coverage       │
│ - Create ADRs         │ - Adapters            │ - Integration tests  │
│ - API docs            │ - Extraction scripts  │ - CI improvements     │
└───────────────────────┴───────────────────────┴───────────────────────┘

Legend: ████ = Sprint week (4 sprints in quarter)
```

## Q3 2026: Acceleration

```
July                    August                  September
┌───────────────────────┬───────────────────────┬───────────────────────┐
│ Plugin Architecture   │ CI/CD Excellence      │ Performance           │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ Week 13-14:           │ Week 17-18:           │ Week 21-22:          │
│ - Plugin core prod    │ - Security in CI       │ - Profile hot paths   │
│ - Plugin SDK docs     │ - Auto quality gates   │ - Optimize queries   │
│ - Migrate thegent    │ - Benchmarking CI      │ - Add caching        │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ Week 15-16:           │ Week 19-20:           │ Week 23-24:          │
│ - Plugin registry     │ - Dependency mgmt     │ - Memory profiling   │
│ - Plugin testing      │ - Coverage reports    │ - Reduce allocs      │
│ - Plugin marketplace  │ - Lint enforcement    │ - Performance tests   │
└───────────────────────┴───────────────────────┴───────────────────────┘
```

## Q4 2026: Polish

```
October                 November                December
┌───────────────────────┬───────────────────────┬───────────────────────┐
│ Observability          │ Cross-Cutting          │ 2026 Review           │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
│ ████ ████ ████ ████  │ ████ ████ ████ ████  │ ████ ████ ████ ████  │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ Week 25-26:           │ Week 29-30:           │ Week 33-34:          │
│ - Distributed tracing │ - Error handling std   │ - Review metrics     │
│ - Logging format      │ - Naming conventions  │ - Document learnings  │
│ - Metrics collection  │ - Code style guide    │ - Plan 2027          │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ Week 27-28:           │ Week 31-32:           │ Week 35-36:          │
│ - Alerting dashboards│ - Migration guides    │ - Publish annual     │
│ - Runbooks            │ - Breaking change log │ - Retro             │
│ - Incident response   │ - Deprecation notices  │ - Celebrate!         │
└───────────────────────┴───────────────────────┴───────────────────────┘
```

## Milestones

| Quarter | Milestone | Success Criteria |
|---------|-----------|------------------|
| Q2 Week 2 | Security Baseline | 0 critical vulnerabilities |
| Q2 Week 8 | Library Extraction | phenotype-shared has 10+ crates |
| Q2 Week 12 | Hexagonal 60% | heliosCLI, phenotype-go-kit hexagonal |
| Q3 Week 16 | Plugin Core | Production-ready plugin framework |
| Q3 Week 20 | CI Excellence | All quality gates automated |
| Q3 Week 24 | Performance 20% | 20% latency reduction achieved |
| Q4 Week 28 | Full Observability | Distributed tracing complete |
| Q4 Week 36 | 2026 Complete | All targets met, 2027 planned |

## Key Deliverables by Quarter

### Q2 Deliverables
1. ✓ Security vulnerabilities resolved
2. ✓ API documentation 80% complete
3. ✓ Shared library extraction Phase 1
4. ✓ Hexagonal architecture 60% adopted

### Q3 Deliverables
1. ✓ Plugin architecture production-ready
2. ✓ CI/CD with automated quality gates
3. ✓ Performance benchmarks in CI
4. ✓ 20% latency reduction

### Q4 Deliverables
1. ✓ Full distributed tracing
2. ✓ Standardized error handling
3. ✓ Migration guides for all major changes
4. ✓ 2027 roadmap complete

---

Last updated: 2026-03-25
