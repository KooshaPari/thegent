import orjson as json
import os
import re
import subprocess
import time
from typing import Any, Dict, List

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch_reddit_post(url: str) -> dict[str, Any]:
    """Fetch a reddit post using its .json endpoint."""
    if not url.endswith(".json"):
        # Strip trailing slash if any and add .json
        clean_url = url.rstrip("/") + ".json"
    else:
        clean_url = url

    try:
        # Use curl with browser UA to bypass blocks
        result = subprocess.run(
            ["curl", "-L", "-H", f"User-Agent: {DEFAULT_USER_AGENT}", "-s", clean_url],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return {"error": f"Curl error: {result.stderr}"}

        data = json.loads(result.stdout)
        # Reddit returns a list: [post_data, comments_data]
        if isinstance(data, list) and len(data) > 0:
            post_info = data[0]["data"]["children"][0]["data"]
            comments = []
            if len(data) > 1:
                for child in data[1]["data"]["children"][:5]:  # Get top 5 comments
                    if child["kind"] == "t1":
                        comments.append(
                            {"author": child["data"].get("author"), "body": child["data"].get("body", "")[:500]}
                        )

            return {
                "title": post_info.get("title"),
                "subreddit": post_info.get("subreddit"),
                "selftext": post_info.get("selftext", ""),
                "url": url,
                "comments": comments,
            }
    except Exception as e:
        return {"error": str(e)}

    return {"error": "Unknown error"}


def process_links(links_file: str, output_path: str):
    with open(links_file) as f:
        links = [line.strip() for line in f if line.strip()]

    all_data = []
    print(f"Starting to process {len(links)} links...")

    for i, link in enumerate(links):
        print(f"[{i + 1}/{len(links)}] Processing: {link}")
        post_data = fetch_reddit_post(link)
        if "error" not in post_data:
            all_data.append(post_data)
        else:
            print(f"  Error: {post_data['error']}")

        # Rate limiting safety
        time.sleep(1)

        # Save progress every 10 links
        if (i + 1) % 10 == 0:
            with open(output_path, "w") as out:
                json.dump(all_data, out, indent=2)

    with open(output_path, "w") as out:
        json.dump(all_data, out, indent=2)
    print(f"Finished. Data saved to {output_path}")


if __name__ == "__main__":
    process_links("/tmp/recent_reddit_links.txt", "/tmp/recent_reddit_content.json")
