# Sprint Backlog - 2026 Q2 Week 1

## Sprint Goal
Fix all critical security vulnerabilities and establish baseline documentation.

---

## P0: Security Vulnerabilities (Must Complete)

### heliosCLI: Fix 28 Vulnerabilities

- [ ] Run `cargo update` for latest patches
- [ ] Review each Dependabot alert
- [ ] Update vulnerable dependencies
- [ ] Verify with `cargo audit`
- [ ] Commit and push fixes

**Owner**: Automated (Dependabot) + Manual review
**Time**: 2-4 hours

### thegent: Fix 8 Vulnerabilities

- [ ] Run `bun pm audit`
- [ ] Review each vulnerability
- [ ] Update vulnerable packages
- [ ] Verify with `npm audit`
- [ ] Commit and push fixes

**Owner**: Automated + Manual review
**Time**: 1-2 hours

---

## P1: Documentation (Should Complete)

### Update API Documentation

- [ ] Document heliosCLI commands
- [ ] Document thegent API endpoints
- [ ] Add code examples
- [ ] Publish to docs site

**Owner**: Documentation
**Time**: 4-8 hours

### Create Architecture Decision Records (ADRs)

- [ ] ADR-001: Hexagonal Architecture adoption
- [ ] ADR-002: xDD methodology selection
- [ ] ADR-003: Plugin architecture
- [ ] ADR-004: Library extraction strategy

**Owner**: Architecture
**Time**: 2-4 hours

---

## P2: Test Coverage (If Time Permits)

### Increase heliosApp Test Coverage

- [ ] Add integration tests for ModelSelector
- [ ] Add E2E tests for ShareModal
- [ ] Add unit tests for lane actions

**Owner**: QA
**Time**: 4-6 hours

---

## Definition of Done

1. All P0 items complete
2. No new security warnings
3. Documentation reviewed
4. All changes committed and pushed

---

## Notes

- Focus on P0 security fixes first
- P1 documentation is secondary
- P2 is nice-to-have if sprint goes well
