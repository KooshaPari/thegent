import orjson as json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def extract_safari_history(file_path: str, days: int = 2) -> list[dict[str, Any]]:
    """Extract and categorize Safari history from the last N days."""
    if not Path(file_path).exists():
        return {}

    # Current time in usec (Safari uses usec since 1970)
    # Actually, Safari history often uses usec since 2001-01-01 00:00:00 UTC
    # But based on our latest timestamp check, 1771485327628223 is Feb 19, 2026.

    # Let's use the latest timestamp in the file as "now" for consistency
    with open(file_path) as f:
        data = json.load(f)
        history = data.get("history", [])

    if not history:
        return {}

    latest_usec = max(e.get("time_usec", 0) for e in history)
    cutoff_usec = latest_usec - (days * 24 * 60 * 60 * 1000000)

    relevant_history = []
    for entry in history:
        time_usec = entry.get("time_usec", 0)
        if time_usec > cutoff_usec:
            relevant_history.append(entry)

    # Sort by time descending
    relevant_history.sort(key=lambda x: x.get("time_usec", 0), reverse=True)

    # Group by "Linkset" (clusters of activity within a 30-minute window)
    linksets = []
    current_linkset = []
    last_time = 0

    for entry in relevant_history:
        time_usec = entry.get("time_usec", 0)
        if last_time == 0 or (last_time - time_usec) < (30 * 60 * 1000000):
            current_linkset.append(entry)
        else:
            if current_linkset:
                linksets.append(current_linkset)
            current_linkset = [entry]
        last_time = time_usec

    if current_linkset:
        linksets.append(current_linkset)

    return linksets


def generate_recent_report(linksets: list[list[dict[str, Any]]], output_path: str):
    """Generate a detailed report for recent linksets."""
    with open(output_path, "w") as f:
        f.write("# Safari Recent Activity: Last 48 Hours\n\n")
        f.write(f"Analyzed {len(linksets)} distinct activity sessions.\n\n")

        for i, linkset in enumerate(linksets):
            start_time = datetime.fromtimestamp(linkset[-1]["time_usec"] / 1000000, tz=timezone.utc)
            end_time = datetime.fromtimestamp(linkset[0]["time_usec"] / 1000000, tz=timezone.utc)

            f.write(
                f"## Session {len(linksets) - i}: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')}\n"
            )
            f.write(f"Total entries: {len(linkset)}\n\n")

            # Show unique links in this set
            seen_urls = set()
            for entry in linkset:
                url = entry.get("url", "")
                title = entry.get("title", entry.get("url", "No Title"))
                if url not in seen_urls:
                    f.write(f"- [{title}]({url})\n")
                    seen_urls.add(url)
            f.write("\n---\n\n")


if __name__ == "__main__":
    history_file = "/tmp/safari_history/Safari Export 2026-02-19/History.json"
    linksets = extract_safari_history(history_file, days=2)
    generate_recent_report(linksets, "docs/research/SAFARI_RECENT_48H.md")
    print("Report generated: docs/research/SAFARI_RECENT_48H.md")
