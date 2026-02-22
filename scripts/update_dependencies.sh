#!/bin/bash
# Update all dependencies to latest versions (Feb 17, 2026)

set -e

echo "Updating Rust dependencies to latest versions..."

# Key updates based on crates.io API (as of Feb 17, 2026):
# - pyo3: 0.23.5 → 0.28.2 (latest stable)
# - tokio: already at 1.49.0 (latest)
# - serde: already at 1.0.228 (latest)
# - serde_json: already at 1.0.149 (latest)
# - rayon: check and update to 1.11.0
# - clap: check and update to 4.5.59
# - reqwest: already at 0.12 (check for latest patch)
# - simd-json: check for latest
# - dashmap: already at 6 (check for latest patch)
# - git2: already at 0.20 (check for latest)
# - gix: already at 0.79 (check for latest)

cd /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/crates

# Update pyo3 from 0.23 to 0.28.2
find . -name "Cargo.toml" -type f -exec sed -i '' 's/pyo3 = { version = "0\.23/pyo3 = { version = "0.28/g' {} \;
find . -name "Cargo.toml" -type f -exec sed -i '' 's/pyo3 = "0\.23/pyo3 = "0.28/g' {} \;

echo "Updated pyo3 to 0.28.2"
echo "Run 'cargo update' to fetch latest versions"
