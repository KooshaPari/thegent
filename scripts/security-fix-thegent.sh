#!/bin/bash
# Security Fix Script - thegent
# Fixes Bun/Node dependency vulnerabilities

set -e

echo "=== Security Fix: thegent ==="
echo ""

cd /Users/kooshapari/CodeProjects/Phenotype/repos/thegent

echo "Step 1: Update lock file..."
bun pm update
echo ""

echo "Step 2: Audit dependencies..."
bun pm audit 2>/dev/null || bun pm scan 2>/dev/null || true
echo ""

echo "Step 3: Check for known vulnerabilities..."
npm audit --audit-level=high 2>/dev/null || true
echo ""

echo "=== Done ==="
echo ""
echo "Review the audit output above for remaining vulnerabilities."
