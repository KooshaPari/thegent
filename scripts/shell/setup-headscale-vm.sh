#!/bin/bash
# Headscale VM provisioning via OrbStack
# Run: chmod +x ~/CodeProjects/Phenotype/repos/thegent/scripts/shell/setup-headscale-vm.sh && ./setup-headscale-vm.sh

set -euo pipefail

VM_NAME="${HEADSCALE_VM_NAME:-headscale}"
VM_DISTRO="${HEADSCALE_VM_DISTRO:-ubuntu:24.04}"
CLOUD_INIT="${HOME}/.config/phenotype/mesh/orbstack-headscale-cloud-init.yaml"

echo "=== Headscale VM via OrbStack ==="
echo "VM name: $VM_NAME"
echo "Distro:  $VM_DISTRO"
echo ""

# Check prerequisites
if ! command -v orbctl >/dev/null 2>&1; then
  echo "ERROR: orbctl not found."
  echo "Install OrbStack from: https://orbstack.dev"
  exit 1
fi

ORB_STATUS=$(orbctl status 2>&1 || true)
if [[ "$ORB_STATUS" != *"Running"* ]]; then
  echo "ERROR: OrbStack is not running."
  echo "Start it from: /Applications/OrbStack.app"
  exit 1
fi

# Check if VM already exists
if orbctl list 2>/dev/null | grep -q "$VM_NAME"; then
  echo "VM '$VM_NAME' already exists."
  echo ""
  echo "To SSH in:"
  echo "  orb ssh $VM_NAME"
  echo ""
  echo "To re-provision (destroys data):"
  echo "  orbctl delete $VM_NAME"
  echo "  $0"
  exit 0
fi

# Verify cloud-init exists
if [[ ! -f "$CLOUD_INIT" ]]; then
  echo "ERROR: Cloud-init not found at $CLOUD_INIT"
  echo "Run setup-tailscale.sh first to generate this file."
  exit 1
fi

echo "Creating OrbStack VM: $VM_NAME ($VM_DISTRO)..."
orbctl create \
  --arch arm64 \
  --user-data "$CLOUD_INIT" \
  "$VM_DISTRO" \
  "$VM_NAME"

echo ""
echo "Waiting for VM to boot and provision (30s)..."
sleep 30

echo ""
echo "Checking VM status..."
orbctl info "$VM_NAME" 2>/dev/null || echo "VM may still be booting..."

echo ""
echo "=== VM Ready ==="
echo ""
echo "To SSH into the VM:"
echo "  orb ssh $VM_NAME"
echo ""
echo "Once inside the VM, initialize Headscale:"
echo "  sudo -u headscale /usr/local/bin/headscale nodes create"
echo ""
echo "To get the node key (for registering macOS/other clients):"
echo "  orb ssh $VM_NAME -- sudo -u headscale /usr/local/bin/headscale nodes list"
echo ""
echo "To stop the VM:"
echo "  orbctl stop $VM_NAME"
echo ""
echo "To start it again:"
echo "  orbctl start $VM_NAME"
