# Dependency Migration Guide

## Updated Libraries (Phase 2)

The following libraries have been moved from `phenotype-*` repos to `libs/`:

| Library | Old Name | New Name | New Cargo.toml | New Package.json |
|---------|----------|----------|----------------|------------------|
| hexagonal-rs | `phenotype_hexagonal` | `hexagonal_rs` | ✅ Updated | N/A |
| hexagonal-ts | `@phenotype/ts-hexagonal` | `@phenotype/libs-hexagonal-ts` | N/A | ✅ Updated |
| hexagonal-py | `phenotype-hexagonal` | `hexagonal-py` | ✅ Updated | N/A |
| hexagonal-go | `kooshapari/phenotype-go-hexagonal` | `phenotype/libs/hexagonal-go` | ✅ Updated | N/A |
| xdd-lib-rs | `phenotype-xdd-lib` | `xdd-lib-rs` | ✅ Updated | N/A |

## Updating Dependencies

### Rust Projects

```toml
# OLD
phenotype_hexagonal = { path = "../phenotype-hexagonal" }
phenotype_xdd_lib = { path = "../phenotype-xdd-lib" }

# NEW
hexagonal_rs = { git = "https://github.com/phenotype/libs", package = "hexagonal_rs" }
xdd_lib_rs = { git = "https://github.com/phenotype/libs", package = "xdd_lib_rs" }
```

### TypeScript Projects

```json
// OLD
"@phenotype/ts-hexagonal": "file:../phenotype-ts-hexagonal"

// NEW
"@phenotype/libs-hexagonal-ts": "https://github.com/phenotype/libs"
```

### Python Projects

```toml
# OLD
phenotype-hexagonal = { path = "../phenotype-py-hexagonal" }

# NEW
hexagonal-py = { git = "https://github.com/phenotype/libs", package = "hexagonal-py" }
```

### Go Projects

```go
// OLD
import "github.com/kooshapari/phenotype-go-hexagonal"

// NEW
import "github.com/phenotype/libs/hexagonal-go"
```

## Known Consumers

None currently. These libraries were placeholders/extracted but not yet integrated into other Phenotype projects.

## Verification

After updating dependencies, verify:

```bash
# Rust
cargo update
cargo build

# TypeScript
npm update
npm run build

# Python
pip install -e .
python -c "import hexagonal_py"

# Go
go mod tidy
go build
```
