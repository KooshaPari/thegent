#!/usr/bin/env python3
"""Run additional ddgr searches for git tools 2026 research."""

import json
import sys
import logging
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
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    all_results = {}
    for query, max_results in SEARCHES:
        logger.info("=== Searching: %s ===", query)
        results = ddg_search(query, max_results=max_results)
        all_results[query] = results
        logger.info("Found %s results", len(results))
        for i, r in enumerate(results[:5], 1):
            logger.info("  %s. %s", i, r.get("title", "N/A"))
            logger.info("     %s", r.get("href", "N/A"))
            body = r.get("body", "N/A")
            logger.info("     %s...", body[:300])

    # Save results
    output_file = Path(__file__).parent / "git_tools_2026_search_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    logger.info("Results saved to %s", output_file)
