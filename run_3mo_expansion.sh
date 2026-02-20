#!/bin/bash
export PYTHONPATH=src
QUERIES=(
    "zsh performance optimization after:2025-11-19"
    "ghostty terminal benchmarks after:2025-11-19"
    "mcp protocol implementation agents after:2025-11-19"
    "autonomous agent swarm framework after:2025-11-19"
    "rust cli library comparison after:2025-11-19"
    "pydantic v2 agent performance after:2025-11-19"
    "hierarchical ai memory knowledge graph after:2025-11-19"
    "agent sandbox container microvm after:2025-11-19"
    "best terminal for macos 2026 after:2025-11-19"
    "zsh vs fish vs nushell 2026 after:2025-11-19"
    "stars:>50 pushed:>2025-11-19 topic:zsh"
    "stars:>50 pushed:>2025-11-19 topic:mcp"
    "stars:>50 pushed:>2025-11-19 topic:ai-agents"
    "stars:>50 pushed:>2025-11-19 topic:rust-cli"
    "stars:>50 pushed:>2025-11-19 topic:terminal"
    "github.com/mcp-server/ pushed:>2025-11-19"
    "github.com/anthropics/claude-code pushed:>2025-11-19"
    "github.com/OpenManus/OpenManus pushed:>2025-11-19"
)

INDEX=200
for QUERY in "${QUERIES[@]}"; do
    echo "Running DRP for: $QUERY"
    python3 src/thegent/main.py research deep "$QUERY" --output "drp_results_${INDEX}.json"
    INDEX=$((INDEX + 1))
done
