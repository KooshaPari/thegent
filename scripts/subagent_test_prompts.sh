#!/usr/bin/env bash
# Print subagent test prompts for manual paste into Cursor chat.
# Usage: ./scripts/subagent_test_prompts.sh   or   bash scripts/subagent_test_prompts.sh

set -e

echo "=== Subagent test prompts (paste into Cursor chat) ==="
echo ""

echo "--- Test 1: Single subagent ---"
echo 'As @bmad/bmm/agents/dev, list the steps you would take to add a new API route in this project.'
echo ""

echo "--- Test 2: Chain / handoff ---"
echo 'First, as @bmad/bmm/agents/architect, propose a one-sentence design for a small "user preferences" feature. Then, as @bmad/bmm/agents/dev, list 3 concrete implementation tasks for that design.'
echo ""

echo "--- Test 3: Subagent + tool use ---"
echo 'As @bmad/cis/agents/creative-problem-solver, suggest three alternative approaches to reduce duplicate code in this repo. Use codebase search to find one example of duplication first.'
echo ""

echo "=== End of prompts ==="
