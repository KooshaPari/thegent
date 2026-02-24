# Comprehensive Library Audit Plan

## 1. TypeScript/JS Libraries

### Current Usage (Many duplicates across projects)

| Library | Purpose | Recommendation |
|---------|---------|----------------|
| vue | UI framework | Keep |
| vitepress | Docs | Keep |
| shiki | Syntax highlighting | Keep |
| algolia | Search | Keep if needed |
| @vue/* | Vue ecosystem | Consolidate |
| preact | React alternative | Evaluate need |
| vite | Build tool | Keep |
| rollup | Bundler | Keep |
| postcss | CSS processing | Keep |
| typescript | Language | Keep |
| @types/* | TypeScript types | Keep |

### Issues Found
- 500+ .ts stub files in ts-stubs - **REMOVE** (generate at runtime)
- Duplicate configs across clones - **CONSOLIDATE**
- node_modules duplicated - **NORMAL** (expected)

### Action Items
- [ ] Remove ts-stubs (generated)
- [ ] Consolidate configs
- [ ] Use pnpm workspaces

---

## 2. Rust Libraries (Cargo.toml)

### Current Usage

| Crate | Purpose | Status |
|-------|---------|--------|
| tokio | Async runtime | KEEP |
| serde | Serialization | KEEP |
| tracing | Logging | KEEP |
| thiserror | Errors | KEEP |
| moka | Cache | KEEP |
| pyo3 | Python FFI | KEEP |
| reqwest | HTTP | KEEP |
| async-trait | Async traits | KEEP |

### Potential Upgrades
- [ ] Update tokio to latest stable
- [ ] Add `rustsec` audit to CI
- [ ] Enable more serde features if needed

---

## 3. Python Libraries

### In heliosHarness
- pydantic → Keep
- pyyaml → Keep  
- asyncio → Keep

### Recommendations
- [ ] Remove unused imports
- [ ] Add type hints
- [ ] Use __slots__ for memory optimization

---

## 4. Zig/Mojo

### Zig Status
- Current: Limited usage (POC)
- Recommendation: Keep for C interop only

### Mojo Status  
- Current: math.mojo, matrix.mojo
- Recommendation: Keep for numerical compute

---

## 5. Optimization Targets

### Remove/Replace
1. ~~ts-stubs~~ → Generate at runtime
2. ~~Duplicate configs~~ → Single source
3. ~~Unused deps~~ → cargo-bloat analysis

### Consolidate
1. GitHub Actions workflows
2. rust-toolchain.toml versions
3. clippy.toml configs

---

## Implementation

### Phase 1: TypeScript Cleanup
```bash
# Find duplicate configs
fd '\.github' | head -20

# Find ts-stubs to remove
find . -path '*/ts-stubs/*' -name '*.ts' | wc -l
```

### Phase 2: Rust Audit
```bash
# Find outdated
cargo outdated

# Security audit
cargo audit
```

### Phase 3: Python Optimization
```bash
# Find unused imports
ruff check --select=F401

# Find dead code
vulture analyze
```

---

## Success Metrics

| Metric | Current | Target |
|--------|----------|---------|
| TypeScript files | 500+ stubs | 0 stubs |
| Config files | Duplicated | Consolidated |
| Rust deps audit | Missing | Automated |
| Python type hints | Partial | 100% |
