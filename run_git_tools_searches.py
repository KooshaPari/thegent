#!/usr/bin/env python3
"""Run additional ddgr searches for git tools 2026 research."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from thegent.skills.research import ddg_search

SEARCHES = [
    ("git event streaming kafka changes 2025", 8),
    ("git diff delta efficient storage deduplication", 8),
    ("bup git backup deduplication efficient", 8),
    ("jj jujutsu version control 2025 features", 8),
    ("git attestation sigstore signing 2025", 8),
    ("git sparse index performance 2025", 8),
]

if __name__ == "__main__":
    all_results = {}
    for query, max_results in SEARCHES:
        print(f"\n=== Searching: {query} ===")
        results = ddg_search(query, max_results=max_results)
        all_results[query] = results
        print(f"Found {len(results)} results")
        for i, r in enumerate(results[:5], 1):
            print(f"  {i}. {r.get('title', 'N/A')}")
            print(f"     {r.get('href', 'N/A')}")
            body = r.get('body', 'N/A')
            print(f"     {body[:300]}...")

    # Save results
    output_file = Path(__file__).parent / "git_tools_2026_search_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n\nResults saved to {output_file}")
