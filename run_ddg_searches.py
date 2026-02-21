#!/usr/bin/env python3
"""Quick DDG search runner for git audit research."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thegent.skills.research import ddg_search

SEARCHES = [
    "git audit trail enterprise 2025 2026",
    "git refs local-only namespace best practices",
    "git journaling filesystem changes track",
    "gitoxide gix performance vs libgit2 2025",
    "content-addressable storage git objects efficient",
    "git forensics audit trail tools 2025",
    "merkle tree git commits verification",
    "git alternates object sharing multiple repos",
]

if __name__ == "__main__":
    all_results = {}
    for query in SEARCHES:
        print(f"Searching: {query}")
        results = ddg_search(query, max_results=8)
        all_results[query] = results
        print(f"  Found {len(results)} results")

    # Save results
    output_file = Path(__file__).parent / "git_audit_search_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {output_file}")
