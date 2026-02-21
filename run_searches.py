#!/usr/bin/env python3
"""Run the 6 specific ddgr searches requested."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from thegent.skills.research import ddg_search

SEARCHES = [
    ("git audit trail enterprise 2025 2026", 5),
    ("git refs local-only namespace best practices", 5),
    ("git journaling filesystem changes track", 5),
    ("gitoxide gix performance 2025", 5),
    ("content-addressable storage git objects efficient", 5),
    ("git forensics audit trail tools 2025", 5),
]

if __name__ == "__main__":
    all_results = {}
    for query, max_results in SEARCHES:
        print(f"\n=== Searching: {query} ===")
        results = ddg_search(query, max_results=max_results)
        all_results[query] = results
        print(f"Found {len(results)} results")
        for i, r in enumerate(results[:3], 1):
            print(f"  {i}. {r.get('title', 'N/A')}")
            print(f"     {r.get('href', 'N/A')}")
            print(f"     {r.get('body', 'N/A')[:200]}...")
    
    # Save results
    output_file = Path(__file__).parent / "search_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n\nResults saved to {output_file}")
