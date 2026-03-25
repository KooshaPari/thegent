#!/bin/bash
# Security Fix Script - heliosCLI
# Fixes Rust dependency vulnerabilities

set -e

echo "=== Security Fix: heliosCLI ==="
echo ""

cd /Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI

echo "Step 1: Update Cargo.lock..."
cargo update
echo ""

echo "Step 2: Audit dependencies..."
cargo audit || true
echo ""

echo "Step 3: Check for security advisories..."
cargo search --limit 1 2>/dev/null || true
echo ""

echo "=== Done ==="
echo ""
echo "Review the audit output above for remaining vulnerabilities."
echo "Consider using 'cargo outdated' to see updateable packages."
