#!/bin/bash
set -e

echo "Validating governance policies..."

# Check for unresolved TODOs and FIXMEs in source code
echo "Checking for unresolved TODOs/FIXMEs..."
TODOS=$(grep -r "TODO\|FIXME" --include="*.rs" src/ || true)
if [ -n "$TODOS" ]; then
    # Filter out intentional comments in tests or documentation
    REAL_TODOS=$(echo "$TODOS" | grep -v "^[[:space:]]*//" || true)
    if [ -n "$REAL_TODOS" ]; then
        echo "⚠️  Found unresolved TODOs/FIXMEs:"
        echo "$REAL_TODOS"
        # Note: We warn but don't fail on TODOs
    fi
fi

# Check that version is set
if grep -q "^version = " Cargo.toml; then
    VERSION=$(grep "^version = " Cargo.toml | head -1 | cut -d'"' -f2)
    echo "✅ Version specified: $VERSION"
else
    echo "❌ No version found in root Cargo.toml"
    exit 1
fi

# Check that workspace members are defined
if grep -q "members = " Cargo.toml; then
    echo "✅ Workspace members defined"
else
    echo "❌ No workspace members found in Cargo.toml"
    exit 1
fi

echo "✅ Governance checks passed"
