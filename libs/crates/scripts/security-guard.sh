#!/bin/bash
set -e

echo "Running security audit..."

# Check for known vulnerabilities in dependencies
if command -v cargo-audit &> /dev/null; then
    cargo audit --deny warnings
else
    echo "⚠️  cargo-audit not installed. Skipping dependency audit."
    echo "   Install with: cargo install cargo-audit"
fi

# Check for known vulnerable crates (if cargo-deny is available)
if [ -f "Cargo.deny" ] || [ -f "deny.toml" ]; then
    if command -v cargo-deny &> /dev/null; then
        cargo deny check
    else
        echo "⚠️  cargo-deny not installed. Skipping crate deny checks."
        echo "   Install with: cargo install cargo-deny"
    fi
fi

echo "✅ Security checks completed"
