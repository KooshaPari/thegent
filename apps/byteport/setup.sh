#!/bin/bash
# BytePort Setup Script
# Installs dependencies and prepares environment for BytePort orchestration

set -e

BYTEPORT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BYTEPORT_ROOT"

echo "🎯 BytePort Setup"
echo "=================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python $(python3 --version)"

# Check Go
if ! command -v go &> /dev/null; then
    echo "❌ Go not found. Please install Go 1.19+"
    exit 1
fi

echo "✓ Go $(go version | awk '{print $3}')"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo "✓ Node.js $(node --version)"

# Check pnpm (recommended for frontend)
if ! command -v pnpm &> /dev/null; then
    echo "⚠️  pnpm not found (recommended for frontend)"
    echo "   Install with: npm install -g pnpm"
else
    echo "✓ pnpm $(pnpm --version)"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt -q

# Install pheno-sdk packages in editable mode
echo ""
echo "📦 Installing Pheno-SDK packages..."

PHENO_SDK="/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk"

# Install tui-kit
if [ -d "$PHENO_SDK/tui-kit" ]; then
    echo "  • Installing tui-kit..."
    pip3 install -e "$PHENO_SDK/tui-kit" -q
    echo "    ✓ tui-kit installed"
fi

# Install process-monitor-sdk
if [ -d "$PHENO_SDK/process-monitor-sdk" ]; then
    echo "  • Installing process-monitor-sdk..."
    pip3 install -e "$PHENO_SDK/process-monitor-sdk" -q
    echo "    ✓ process-monitor-sdk installed"
fi

# Verify KInfra is accessible
echo ""
echo "🔍 Checking KInfra..."
KINFRA_PATH="$HOME/KInfra/libraries/python"
if [ -d "$KINFRA_PATH" ]; then
    echo "  ✓ KInfra found at $KINFRA_PATH"
    # Test import
    python3 -c "import sys; sys.path.insert(0, '$KINFRA_PATH'); from kinfra.port_registry import PortRegistry; from kinfra.tunnel_sync import TunnelManager; print('  ✓ KInfra imports successful')" 2>&1 || echo "  ⚠️  KInfra import failed - tunnel support may be limited"
else
    echo "  ⚠️  KInfra not found at $KINFRA_PATH"
    echo "     Tunnel management will be limited"
fi

# Check for cloudflared
echo ""
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️  cloudflared not found (tunnel support disabled)"
    echo "   Install from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/"
else
    echo "✓ cloudflared $(cloudflared version 2>&1 | head -n1)"

    # Check if authenticated
    if [ ! -f "$HOME/.cloudflared/cert.pem" ]; then
        echo "⚠️  cloudflared not authenticated"
        echo "   Run: cloudflared tunnel login"
    else
        echo "✓ cloudflared authenticated"
    fi
fi

# Install Air for Go live reload (optional)
echo ""
if ! command -v air &> /dev/null; then
    echo "📦 Installing Air for Go live reload..."
    go install github.com/cosmtrek/air@latest
    echo "✓ Air installed"
else
    echo "✓ Air already installed"
fi

# Install backend Go dependencies
echo ""
echo "📦 Installing Go dependencies..."
cd "$BYTEPORT_ROOT/backend/api"
mkdir -p .gomodcache .gocache
if [ -d "$HOME/go/pkg/mod" ]; then
    echo "  • Syncing cached modules"
    rsync -a "$HOME/go/pkg/mod/" .gomodcache/ >/dev/null 2>&1 || true
fi
GOCACHE=$(pwd)/.gocache GOMODCACHE=$(pwd)/.gomodcache GOPROXY=off GONOSUMDB=* go build -mod=mod ./...
echo "✓ Go dependencies installed"

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd "$BYTEPORT_ROOT/frontend/web-next"
if command -v pnpm &> /dev/null; then
    pnpm install --silent
    echo "✓ Frontend dependencies installed (pnpm)"
else
    echo "⚠️  pnpm not found, using npm"
    npm install --silent
    echo "✓ Frontend dependencies installed (npm)"
fi

cd "$BYTEPORT_ROOT"

# Make scripts executable
chmod +x byteport.py 2>/dev/null || true

echo ""
echo "✅ BytePort setup complete!"
echo ""
echo "Next steps:"
echo "  Production: ./byteport.py"
echo "  Development: ./byteport.py --dev"
echo "  Status: ./byteport.py --status"
echo ""