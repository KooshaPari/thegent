#!/bin/bash
set -e

# Cloudflare Tunnel Setup Script for thegent Offload Worker
# Usage: ./setup-offload-tunnel.sh <tunnel-name> <domain>

TUNNEL_NAME=${1:-"thegent-worker"}
DOMAIN=${2:-"worker.kooshapari.com"}

if ! command -v cloudflared &> /dev/null; then
    echo "Error: cloudflared not found. Please install it first (e.g., 'brew install cloudflared')."
    exit 1
fi

echo "--- 1. Logging into Cloudflare ---"
cloudflared tunnel login

echo "--- 2. Creating Tunnel: $TUNNEL_NAME ---"
cloudflared tunnel create "$TUNNEL_NAME"

TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
echo "Created Tunnel ID: $TUNNEL_ID"

echo "--- 3. Mapping Tunnel to Domain: $DOMAIN ---"
cloudflared tunnel route dns "$TUNNEL_NAME" "$DOMAIN"

# Generate basic config
CONFIG_FILE="$HOME/.cloudflared/thegent-offload.yml"
echo "--- 4. Generating Configuration: $CONFIG_FILE ---"

cat <<EOF > "$CONFIG_FILE"
tunnel: $TUNNEL_ID
credentials-file: $HOME/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: $DOMAIN
    service: http://localhost:9000
  - service: http_status:404
EOF

echo "--- Setup Complete! ---"
echo "To run the tunnel, execute:"
echo "cloudflared tunnel --config $CONFIG_FILE run"
echo ""
echo "Then, start the offload executor:"
echo "thegent-offload serve --port 9000 --token \"your-secret-token-here\""
echo ""
echo "IMPORTANT: Configure Cloudflare Access at https://one.dash.cloudflare.com/"
echo "to protect $DOMAIN with a Service Token for the Laptop client."
