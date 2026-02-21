#!/usr/bin/env python3
"""
Git Audit Journaling Research Script
Run: python scripts/git_audit_research.py
"""
import json
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

def main():
    results = {}
    for query in SEARCHES:
        print(f"Searching: {query}")
        results[query] = ddg_search(query, max_results=8)
    
    # Save results
    with open("git_audit_research_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n=== RESULTS ===\n")
    for query, hits in results.items():
        print(f"\n## {query}")
        for h in hits:
            print(f"- {h.get('title', 'N/A')}")
            print(f"  {h.get('href', h.get('url', 'N/A'))}")
            print(f"  {h.get('body', '')[:200]}...")

if __name__ == "__main__":
    main()
