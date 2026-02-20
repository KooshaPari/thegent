#!/usr/bin/env zsh
# Diagnosis script for rg/grep error
# Issue: rg reports "error parsing flag -E: grep config error: unknown encoding"

echo "=== Diagnosis for rg/grep error ==="
echo ""

echo "1. Checking shell aliases for rg and grep..."
type rg 2>/dev/null || echo "  - rg: no alias found"
type grep 2>/dev/null || echo "  - grep: no alias found"
echo ""

echo "2. Checking shell functions..."
declare -f rg 2>/dev/null && echo "  - rg: function found (possible culprit)"
declare -f grep 2>/dev/null && echo "  - grep: function found (possible culprit)"
echo ""

echo "3. Checking environment variables..."
env | grep -i "GREP\|RG" || echo "  - No GREP/RG environment vars found"
echo ""

echo "4. Testing rg directly..."
echo "   Testing: rg --version"
rg --version 2>&1 | head -1
echo ""

echo "5. Testing grep directly..."
echo "   Testing: grep --version"
grep --version 2>&1 | head -1
echo ""

echo "6. Testing problematic pattern..."
echo "   Testing: echo test | rg -E 'test'"
echo "test" | rg -E 'test' 2>&1 || echo "  - Failed (check above error)"
echo ""

echo "7. Checking for config files..."
for config in ~/.ripgreprc ~/.config/ripgrep/config ~/.grep ~/.greprc; do
  if [ -f "$config" ]; then
    echo "  - Found config: $config"
    head -3 "$config"
  fi
done
echo ""

echo "=== End of diagnosis ==="
echo ""
echo "Recommendations:"
echo "1. If rg or grep is aliased/functioned, run 'unalias rg' or 'unset -f rg'"
echo "2. Remove any config files that might have malformed patterns"
echo "3. Check .zshrc/.bashrc for custom grep/rg wrappers"
