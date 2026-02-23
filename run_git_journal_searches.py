#!/usr/bin/env python3
"""Run the specific ddgr searches requested for GitJournal research."""

import orjson as json
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from thegent.skills.research import ddg_search

SEARCHES = [
    ("git event streaming kafka changes", 5),
    ("bup git backup deduplication", 5),
    ("jj jujutsu version control features", 5),
    ("git attestation sigstore signing", 5),
    ("git sparse index performance", 5),
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
    output_file = Path(__file__).parent / "git_journal_search_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    logger.info("Results saved to %s", output_file)
