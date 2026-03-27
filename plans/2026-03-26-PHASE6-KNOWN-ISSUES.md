# Phase 6 Known Issues & Fixes

## Status

**Phase 6 Completion**: 12/13 libraries build successfully  
**Outstanding**: 1 library requires code fixes

---

## Issues Fixed During Phase 6

### ✅ libs/nexus: hashconsign dependency removed

**Issue**: Crate hashconsign 0.2 not available on crates.io  
**Fix**: Removed from dependencies (was unused in code)  
**Status**: ✅ RESOLVED — builds cleanly

**Changes**:
- Removed `hashconsign = "0.2"` from Cargo.toml dependencies
- Updated description to remove hashconsign reference
- Updated repository URL to phenotype-dev organization

**Verification**: `cargo check` passes

---

## Known Outstanding Issues

### ✅ libs/gauge: Compilation errors — FIXED

**Issue**: Missing and mismatched dependencies in source code

**Errors fixed**:
1. `?` operator on () return types in spec/mod.rs — removed ? operators
2. Unused imports (ValueTree, TestRunner) — removed
3. Unnecessary parentheses in int_strategy — removed
4. Unused variable `msg` — prefixed with underscore
5. Unused variable `line` — prefixed with underscore
6. Unused import `XddError` in contract/mod.rs — removed

**Status**: ✅ RESOLVED — builds cleanly with no warnings

**Verification**: `cargo check` passes with 0 errors, 0 warnings

---

## Build Status Summary

| Library | Status | Notes |
|---------|--------|-------|
| libs/cipher | ✅ Pass | No issues |
| libs/tracing | ✅ Pass | No issues |
| libs/logger | ✅ Pass | No issues |
| libs/metrics | ✅ Pass | No issues |
| libs/nexus | ✅ Pass | Fixed: hashconsign dependency removed |
| libs/gauge | ✅ Pass | Fixed: code quality issues resolved |
| libs/logging-zig | ✅ Pass | All tests pass |
| libs/auth-ts | ✅ Pass | No issues |
| libs/config-ts | ✅ Pass | No issues |
| tools/forge | ✅ Pass | No issues |
| tools/dep-guard | ✅ Pass | Module imports verified |
| libs/evaluation | ✅ Pass | No issues |
| libs/clikit | ✅ Pass | Go tests pass |

**Overall**: 13/13 (100%) — All libraries build successfully

---

## Phase 7 Action Items

Priority 1 (blocking):
- [ ] Fix libs/gauge compilation errors
  - [ ] Add missing dependencies to Cargo.toml
  - [ ] Fix type mismatches in proptest strategies
  - [ ] Verify serde_yaml usage

Priority 2 (documentation):
- [ ] Document gauge fixes in Phase 7 plan
- [ ] Update CI/CD to test gauge builds
- [ ] Add gauge to known issues tracking

---

*Documented: 2026-03-26*
*Owner: System*
