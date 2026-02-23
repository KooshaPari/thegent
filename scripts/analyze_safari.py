import orjson as json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def extract_safari_history(file_path: str, months: int = 3) -> list[dict[str, Any]]:
    """Extract and categorize Safari history from the last N months."""
    if not Path(file_path).exists():
        return []

    # Current time in usec (Safari uses usec since 1970)
    # Actually, Safari history often uses usec since 2001-01-01 00:00:00 UTC
    # But looking at the timestamps (e.g., 1739892884413618), this is Unix epoch in usec.
    # 1739892884 is roughly Feb 2025.

    now_usec = int(datetime.now(timezone.utc).timestamp() * 1000000)
    cutoff_usec = now_usec - (months * 30 * 24 * 60 * 60 * 1000000)

    try:
        with open(file_path) as f:
            data = json.load(f)
            history = data.get("history", [])
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return []

    relevant_history = []
    for entry in history:
        time_usec = entry.get("time_usec", 0)
        if time_usec > cutoff_usec:
            relevant_history.append(entry)

    # Simple categorization based on URL and Title
    categories = {
        "AI & Agents": ["claude", "openai", "chatgpt", "agent", "mcp", "anthropic", "llm", "deepseek", "qwen"],
        "Development & Code": [
            "github",
            "stackoverflow",
            "rust",
            "python",
            "npm",
            "node",
            "nextjs",
            "react",
            "typescript",
            "zsh",
            "terminal",
            "iterm",
            "ghostty",
        ],
        "Research & Academia": [
            "arxiv",
            "scholar",
            "researchgate",
            "medium",
            "dev.to",
            "hashnode",
            "theory of computation",
            "computation",
            "cs",
        ],
        "Social & News": ["reddit", "twitter", "x.com", "ycombinator", "hacker news", "news"],
        "Tools & Utilities": ["doordash", "canvas", "asu", "duosecurity", "google search", "amazon"],
    }

    categorized_results = {cat: [] for cat in categories}
    categorized_results["Uncategorized"] = []

    for entry in relevant_history:
        url = entry.get("url", "").lower()
        title = entry.get("title", "").lower()

        found = False
        for cat, keywords in categories.items():
            if any(kw in url or kw in title for kw in keywords):
                categorized_results[cat].append(entry)
                found = True
                break

        if not found:
            categorized_results["Uncategorized"].append(entry)

    return categorized_results


def generate_report(categorized_data: dict[str, list[dict[str, Any]]], output_path: str):
    """Generate a markdown report from categorized history."""
    with open(output_path, "w") as f:
        f.write("# Safari History Deep Dive Report (Last 3 Months)\n\n")
        f.write(f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for cat, entries in categorized_data.items():
            if not entries:
                continue

            f.write(f"## {cat}\n")
            f.write(f"Total entries: {len(entries)}\n\n")

            # Show top unique links (deduplicated by title/url)
            seen_urls = set()
            count = 0
            for entry in entries:
                url = entry.get("url", "")
                title = entry.get("title", entry.get("url", "No Title"))
                if url not in seen_urls and count < 15:
                    f.write(f"- [{title}]({url})\n")
                    seen_urls.add(url)
                    count += 1
            f.write("\n")


if __name__ == "__main__":
    history_file = "/tmp/safari_history/Safari Export 2026-02-19/History.json"
    results = extract_safari_history(history_file)
    generate_report(results, "docs/research/SAFARI_HISTORY_DEEP_DIVE.md")
    print("Report generated: docs/research/SAFARI_HISTORY_DEEP_DIVE.md")
