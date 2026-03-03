#!/usr/bin/env zsh
# Build all thegent Rust extensions with clean output and error handling
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CRATES_DIR="$THEGENT_ROOT/crates"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔨 Building all thegent Rust extensions...${NC}"
echo ""

# Check prerequisites
check_prereq() {
    local cmd=$1
    local install_cmd=$2

    if ! command -v "$cmd" &>/dev/null; then
        echo -e "${YELLOW}📦 Installing $cmd...${NC}"
        eval "$install_cmd" || {
            echo -e "${RED}❌ Failed to install $cmd${NC}"
            exit 1
        }
    fi
}

check_prereq cargo "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
if command -v uv &>/dev/null; then
    check_prereq maturin "uv tool install maturin || python3 -m pip install --user maturin || cargo install maturin"
else
    check_prereq maturin "python3 -m pip install --user maturin || cargo install maturin"
fi

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$("$PYTHON" --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}🐍 Using Python: $PYTHON_VERSION${NC}"
echo ""

# Build extensions
EXTENSIONS=(
    "thegent-discovery"
    "thegent-tool-detect"
    "thegent-path-resolve"
)

BUILT=0
FAILED=0

for ext in "${EXTENSIONS[@]}"; do
    EXT_DIR="$CRATES_DIR/$ext"

    if [[ ! -d "$EXT_DIR" ]]; then
        echo -e "${YELLOW}⚠️  Skipping $ext (directory not found)${NC}"
        continue
    fi

    echo -e "${BLUE}📦 Building $ext...${NC}"
    cd "$EXT_DIR"

    # Check if it has Python bindings
    if [[ -f "pyproject.toml" ]] || grep -q "pyo3" Cargo.toml 2>/dev/null; then
        echo -e "   ${BLUE}Building Python extension...${NC}"
        if maturin develop --release --features python 2>&1 | tee "/tmp/maturin-$ext.log" | grep -E "(Compiling|Finished|error|warning)" | tail -20; then
            echo -e "   ${GREEN}✅ $ext built successfully${NC}"

            # Verify import
            if "$PYTHON" -c "import ${ext//-/_}" 2>/dev/null; then
                echo -e "   ${GREEN}✅ $ext import verified${NC}"
                ((BUILT++))
            else
                echo -e "   ${YELLOW}⚠️  $ext built but import failed (check /tmp/maturin-$ext.log)${NC}"
                ((FAILED++))
            fi
        else
            echo -e "   ${RED}❌ $ext build failed (check /tmp/maturin-$ext.log)${NC}"
            ((FAILED++))
        fi
    else
        echo -e "   ${BLUE}Building binary...${NC}"
        if cargo build --release 2>&1 | tee "/tmp/cargo-$ext.log" | grep -E "(Compiling|Finished|error|warning)" | tail -20; then
            echo -e "   ${GREEN}✅ $ext built successfully${NC}"
            ((BUILT++))
        else
            echo -e "   ${RED}❌ $ext build failed (check /tmp/cargo-$ext.log)${NC}"
            ((FAILED++))
        fi
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Build Summary:${NC}"
echo -e "  ${GREEN}✅ Built: $BUILT${NC}"
if [[ $FAILED -gt 0 ]]; then
    echo -e "  ${RED}❌ Failed: $FAILED${NC}"
else
    echo -e "  ${GREEN}❌ Failed: $FAILED${NC}"
fi
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}🎉 All extensions built successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test imports: python3 -c 'from thegent_discovery import DiscoveryInterface'"
    echo "  2. Run: bash scripts/fix-which-timeout.sh"
    echo "  3. Restart your shell"
else
    echo -e "${YELLOW}⚠️  Some builds failed. Check logs in /tmp/${NC}"
    exit 1
fi
