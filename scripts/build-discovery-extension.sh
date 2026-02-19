#!/usr/bin/env bash
# Build script for thegent_discovery Rust Python extension
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CRATES_DIR="$THEGENT_ROOT/crates"
DISCOVERY_CRATE="$CRATES_DIR/thegent-discovery"

echo "🔨 Building thegent_discovery Rust extension..."

# Check for required tools
if ! command -v cargo &>/dev/null; then
    echo "❌ Error: cargo not found. Install Rust: https://rustup.rs/"
    exit 1
fi

if ! command -v maturin &>/dev/null; then
    echo "📦 Installing maturin (Python-Rust bridge)..."
    cargo install maturin || {
        echo "❌ Failed to install maturin. Try: pip install maturin"
        exit 1
    }
fi

# Check Python version
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

PYTHON_VERSION=$("$PYTHON" --version 2>&1 | awk '{print $2}')
echo "🐍 Using Python: $PYTHON_VERSION"

# Build the extension with maturin
cd "$DISCOVERY_CRATE"
echo "📦 Building Python extension (this may take a few minutes)..."
maturin develop --release --features python || {
    echo "❌ Build failed. Trying without release mode..."
    maturin develop --features python
}

# Verify installation
echo "✅ Verifying installation..."
"$PYTHON" -c "from thegent_discovery import DiscoveryInterface; print('✅ thegent_discovery imported successfully')" || {
    echo "❌ Import test failed"
    exit 1
}

echo "✅ Build complete! thegent_discovery extension is ready."
