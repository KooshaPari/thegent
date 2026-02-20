import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .deep_research import perform_deep_research, reddit_json_search

logger = logging.getLogger(__name__)


def extract_subreddits_from_links(links: list[str]) -> list[str]:
    """Extract subreddit names from a list of Reddit links."""
    subreddits = set()
    for link in links:
        match = re.search(r"reddit\.com/r/([^/]+)/", link)
        if match:
            subreddits.add(match.group(1))
    return sorted(subreddits)


def suggest_related_subreddits(subreddits: list[str]) -> list[str]:
    """Suggest related subreddits based on initial list."""
    # This is a static mapping for now, but could be dynamic later
    related_map = {
        "zsh": ["bash", "commandline", "terminal", "linux", "macos"],
        "neovim": ["vim", "emacs", "coding", "softwaredevelopment"],
        "macapps": ["macos", "apple", "productivity"],
        "LocalLLaMA": ["AI_Agents", "ArtificialIntelligence", "MachineLearning"],
        "ClaudeAI": ["OpenAI", "ChatGPT", "LLM"],
        "rust": ["golang", "cpp", "programming"],
        "commandline": ["shell", "terminal", "linux", "unix"],
    }

    suggested = set()
    for sub in subreddits:
        if sub in related_map:
            suggested.update(related_map[sub])

    # Filter out subreddits already in the initial list
    return sorted(suggested - set(subreddits))


def process_reddit_swathe(links: list[str], additional_subreddits: list[str] | None = None) -> dict[str, Any]:
    """Process a swathe of Reddit links and perform deep research."""
    initial_subs = extract_subreddits_from_links(links)
    if additional_subreddits:
        initial_subs = sorted(set(initial_subs) | set(additional_subreddits))

    suggested_subs = suggest_related_subreddits(initial_subs)

    results = {
        "initial_links_count": len(links),
        "initial_subreddits": initial_subs,
        "suggested_subreddits": suggested_subs,
        "deep_research": {},
    }

    # Perform deep research on a selection of subreddits and queries
    # For now, let's just do a broad search across the subreddits
    query = "AI agents terminal zsh optimization"
    results["deep_research"] = perform_deep_research(query, subreddits=initial_subs[:5])

    return results


def save_swathe_results(results: dict[str, Any], output_path: Path):
    """Save the results of the reddit swathe processing."""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    return output_path
