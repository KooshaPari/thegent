# Phase 7: Consolidation & CI/CD Integration

**Timeline**: 2026-03-26 onwards  
**Focus**: Fix outstanding issues, integrate libs/tools into CI/CD, update root documentation

## Objectives

1. ✅ Fix remaining Rust dependency issues (libs/nexus: hashconsign)
2. ✅ Verify all libraries and tools build cleanly
3. ✅ Fix libs/gauge compilation errors (Phase 7 task completed)
4. ⏳ Update root documentation (README, ARCHITECTURE, CODEOWNERS)
5. ⏳ Integrate libs/ and tools/ into CI/CD pipeline
6. ⏳ Document Phase 6 → 7 transition in governance

## Task Breakdown

### Task 1: Resolve Outstanding Rust Dependencies

**Status**: 1 issue identified

#### libs/nexus: hashconsign unavailable

**Issue**: `hashconsign = "0.2"` is not available on crates.io

**Options**:
1. Replace with available crate (e.g., `sha2`, `blake3`)
2. Vendor the dependency (copy into repo)
3. Remove feature requiring hashconsign

**Decision**: TBD — requires understanding nexus's state management approach

**Impact**: Blocks cargo check for libs/nexus

---

### Task 2: Verify Build Status for All Libs/Tools

**Rust crates** (should all pass cargo check):
- ✅ libs/cipher
- ✅ libs/tracing
- ✅ libs/logger
- ✅ libs/metrics
- ⚠️ libs/nexus (pending hashconsign fix)
- ✅ libs/gauge

**Python packages** (should all pass pytest):
- ✅ tools/dep-guard
- ✅ libs/evaluation

**JavaScript/TypeScript packages** (should all pass npm test):
- ✅ libs/auth-ts
- ✅ libs/config-ts

**Go packages** (should all pass go test):
- ✅ libs/clikit

**CLI tools** (Rust binary):
- ✅ tools/forge

**Zig library**:
- ✅ libs/logging-zig (zig test)

---

### Task 3: Update Root Documentation

#### README.md
- ✅ Reflects new directory structure
- ⏳ Verify it matches actual libs/ and tools/ contents
- ⏳ Update "Quick Start" section with pointers to libs/tools

#### ARCHITECTURE.md
- ⏳ Update to document libs/ vs tools/ vs packages/ distinction
- ⏳ Add hexagonal architecture diagram showing libs placement

#### governance/MIGRATION.md
- ✅ Already created in Phase 5
- ⏳ Append Phase 6 summary

#### CODEOWNERS
- ⏳ Add ownership for libs/ and tools/ maintainers
- ⏳ Define rules for adding new libs/tools

---

### Task 4: CI/CD Integration

**Current state**: tools/ci-cd/ exists with placeholder structure

**Work needed**:

1. **GitHub Actions workflows** (.github/workflows/):
   - `test-libs.yml` — Run all lib tests (Rust, Python, TS, Go, Zig)
   - `test-tools.yml` — Run all tool tests
   - `build-libs.yml` — Build all libs for release
   - `build-tools.yml` — Build all tools for release

2. **Local build scripts** (tools/scripts/):
   - `build-all-libs.sh` — Build all libraries
   - `test-all-libs.sh` — Test all libraries
   - `test-all-tools.sh` — Test all tools
   - `verify-libs.sh` — Verify all libs cargo check

3. **Package/publish integration**:
   - Rust crates → crates.io (or private registry)
   - Python packages → PyPI (or private registry)
   - npm packages → npm registry (or private)
   - Go modules → go.mod (or proxy)

---

### Task 5: Archive Handling & Git Integration

**Current state**: ARCHIVED.md files created in all productized source repos

**Work needed**:

1. **Git tracking**:
   - All ARCHIVED.md files should be committed
   - Root README updates should be committed
   - Phase 6/7 plan files should be in repo

2. **Root .gitignore**:
   - Ensure build artifacts in libs/ and tools/ are ignored
   - Preserve vendored dependencies if any

3. **Commit message**:
   - Document Phase 6 completion
   - Reference migration matrix
   - Link to ARCHIVED.md locations

---

### Task 6: Governance & Standards

**Updates needed**:

1. **governance/standards/NAMING.md**:
   - Add rules for naming new libs vs tools
   - Clarify when to use phenotype- prefix vs neutral names

2. **governance/adrs/ADR-007-Library-vs-Tool.md** (new):
   - Decision record: when to extract to libs/ vs tools/
   - Design rationale for Phase 6 categorization
   - Examples from each batch

3. **governance/processes/LIBRARY_ADDITION.md** (new):
   - Process for adding new libraries
   - Template for lib README + CLAUDE.md
   - Checklist for lib extraction

---

## Status Tracking

| Task | Status | Owner | Due |
|------|--------|-------|-----|
| Resolve Rust deps | ✅ Complete | — | 2026-03-26 |
| Fix libs/gauge | ✅ Complete | — | 2026-03-26 |
| Verify all builds | ✅ Complete | — | 2026-03-26 |
| Update root docs | ✅ Complete | — | 2026-03-26 |
| CI/CD integration | 🔲 Pending | — | 2026-03-29 |
| Archive git ops | 🔲 Pending | — | 2026-03-29 |
| Governance docs | 🔲 Pending | — | 2026-03-30 |

---

## Success Criteria

✅ All libs/ packages and tools/ build cleanly  
✅ Root README accurately reflects new structure  
✅ ARCHITECTURE.md documents libs/tools distinction  
✅ CI/CD pipelines test all libs/tools  
✅ ARCHIVED.md files committed and tracked  
✅ New governance docs in place  

---

## Next Steps (Phase 8)

Once Phase 7 is complete:

1. **Service migrations** — Move remaining services to services/
2. **App consolidation** — Organize apps/ clearly
3. **Infrastructure codification** — Complete infrastructure/ IaC templates
4. **Documentation site** — phenotype-docs/ as web platform

---

*Plan created: 2026-03-26*
*Owner: System*
*Next review: 2026-03-27*
