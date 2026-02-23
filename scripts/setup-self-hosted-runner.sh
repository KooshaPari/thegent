#!/bin/bash
# Self-hosted runner registration script for thegent

set -e

REPO="KooshaPari/thegent"
RUNNER_DIR="${HOME}/actions-runner"

echo "=== thegent Self-Hosted Runner Setup ==="

# Check if already configured
if [ -d "$RUNNER_DIR" ]; then
    echo "Runner already exists at $RUNNER_DIR"
    cd "$RUNNER_DIR"
    ./svc.sh status || true
    exit 0
fi

# Get token (user needs to generate from GitHub)
echo "1. Go to: https://github.com/${REPO}/settings/actions/runners/new"
echo "2. Copy the token"
read -p "Enter token: " TOKEN

# Create runner
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Download
if [ "$(uname)" = "Darwin" ]; then
    curl -o runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.320.0/actions-runner-osx-x64-2.320.0.tar.gz
else
    curl -o runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.320.0/actions-runner-linux-x64-2.320.0.tar.gz
fi

tar xzf runner.tar.gz
rm runner.tar.gz

# Configure
./config.sh --url "https://github.com/${REPO}" --token "$TOKEN" --labels self-hosted

# Install service
if [ "$(uname)" = "Darwin" ]; then
    ./svc.sh install
    ./svc.sh start
else
    sudo ./svc.sh install
    sudo ./svc.sh start
fi

echo "=== Runner configured and started ==="
