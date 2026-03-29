#!/bin/bash
# Tailscale setup script for Phenotype mesh
# Run: chmod +x ~/CodeProjects/Phenotype/repos/thegent/scripts/shell/setup-tailscale.sh && ./setup-tailscale.sh

set -euo pipefail

TAILNET_NAME="${TAILNET_NAME:-phenotype-mesh}"
TAILSCALE_BIN="/usr/local/bin/tailscale"

echo "=== Tailscale Mesh Setup ==="
echo "Target tailnet: $TAILNET_NAME"

# Check if Tailscale is installed
if [[ ! -x "$TAILSCALE_BIN" ]]; then
  echo "ERROR: Tailscale not found at $TAILSCALE_BIN"
  echo "Install with: brew install --cask tailscale"
  exit 1
fi

# Check current status
STATUS=$("$TAILSCALE_BIN" status 2>&1 || true)
if [[ "$STATUS" == *"Logged out"* ]]; then
  echo ""
  echo "Tailscale is logged out."
  echo "Open the Tailscale app (System Preferences > Tailscale)"
  echo "OR run: $TAILSCALE_BIN login"
  echo ""
  echo "After logging in, run this script again to verify."
  exit 0
fi

if [[ "$STATUS" == *"Running"* ]] || [[ "$STATUS" == *" tailscale"* ]]; then
  echo "Tailscale is already running."
  echo ""
  echo "Current status:"
  "$TAILSCALE_BIN" status | head -20
  echo ""
  echo "Your tailnet IP:"
  "$TAILSCALE_BIN" ip -4 | head -1 || true
  echo ""
  echo "To enable SSH over Tailscale:"
  echo "  $TAILSCALE_BIN" set --ssh
  echo ""
  echo "To connect from another device:"
  echo "  tailscale login --hostname <hostname>"
  echo ""
  echo "Tailscale serve status:"
  "$TAILSCALE_BIN" serve status 2>&1 || echo "Not serving anything yet"
fi

# Suggest enabling SSH
echo ""
echo "=== Next Steps ==="
read -p "Enable Tailscale SSH? (recommended for keyless SSH) [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Enabling Tailscale SSH..."
  sudo "$TAILSCALE_BIN" set --ssh
  echo "Done. You can now SSH to other tailnet hosts without keys:"
  echo "  ssh user@hostname"  # Tailscale resolves hostname automatically
fi

echo ""
echo "=== Cross-device setup ==="
echo "On your other devices (Win11, other Mac, etc.):"
echo "1. Install Tailscale from https://tailscale.com/download"
echo "2. Login with the same account"
echo "3. Devices will automatically appear on the tailnet"
echo ""
echo "To route traffic through your LA desktop (GPU passthrough):"
echo "  sudo tailscale up --exit-node=desktop-hostname"
