#!/bin/bash
# BytePort Quick Fix - Reset to clean state
# Stops all services and clears state for fresh start

set -e

BYTEPORT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BYTEPORT_ROOT"

echo "🧹 BytePort Quick Fix"
echo "===================="
echo ""

echo "Stopping all BytePort processes..."
./byteport.py --stop 2>/dev/null || true
pkill -9 -f cloudflared 2>/dev/null || true
pkill -9 -f "go run" 2>/dev/null || true
pkill -9 -f "next-server" 2>/dev/null || true
pkill -9 -f "pnpm.*dev" 2>/dev/null || true
sleep 2

echo "✓ Processes stopped"
echo ""

echo "Clearing state files..."
rm -f ~/.kinfra/port_registry.json
rm -f .byteport_state.json
rm -f ~/.cloudflared/config-backend.yml
rm -f ~/.cloudflared/config-frontend.yml
rm -f ~/.cloudflared/config-api.yml

echo "✓ State cleared"
echo ""

echo "Clearing Go build caches (backend/api)..."
rm -rf backend/api/.gocache/* 2>/dev/null || true
rm -rf backend/api/.gomodcache/* 2>/dev/null || true
echo "✓ Build caches cleared"
echo ""

echo "✅ Clean state ready!"
echo ""
echo "Next steps:"
echo "  Development: ./byteport.py --dev"
echo "  Production:  ./byteport.py"
echo "  Local mode:  ./byteport.py --local"
echo "  Status:      ./byteport.py --status"
echo ""
