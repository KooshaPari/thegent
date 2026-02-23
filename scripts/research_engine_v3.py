import json
import os
import subprocess
import time
from typing import Any, Dict, List

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LINKS_FILE = "data/research/reddit_backlog_3mo.txt"
OUTPUT_FILE = "data/research/all_processed_reddit.json"
BATCH_SIZE = 2000
MAX_SUCCESSES = 2000
SLEEP_TIME = 4.0


def fetch_reddit_post(url: str) -> dict:
    priority_subreddits = [
        "ClaudeAI",
        "ClaudeCode",
        "AI_Agents",
        "mcp",
        "LocalLLaMA",
        "golang",
        "Python",
        "zsh",
        "Supabase",
        "cursor",
        "nextjs",
        "LangChain",
        "vibecoding",
    ]
    skip_subreddits = [
        "ASU",
        "ASUOnline",
        "ApplyingToCollege",
        "AskSF",
        "AskLosAngeles",
        "ArsenalFC",
        "Apartmentliving",
        "BeyondWonderlandPNW",
        "BoJackHorseman",
        "CRedit",
        "CitiesSkylines",
        "worldnews",
        "CVS",
        "theydidthemath",
        "tmobile",
        "threejs",
        "thinkpad",
        "trashy",
        "traderjoes",
        "torrents",
    ]

    if any(f"/r/{s}/" in url for s in skip_subreddits):
        return {"error": "Skipping non-technical/noisy subreddit"}

    if "reddit.com" not in url:
        return {"error": "Not a reddit.com link"}

    clean_url = url.rstrip("/") + ".json" if not url.endswith(".json") else url
    if "/r/" not in clean_url or "/comments/" not in clean_url:
        return {"error": "Not a direct reddit post link"}

    try:
        result = subprocess.run(
            ["curl", "-L", "-A", DEFAULT_USER_AGENT, "-s", clean_url], capture_output=True, text=True, timeout=20
        )
        if result.returncode != 0:
            return {"error": f"Curl error: {result.stderr}"}

        if not result.stdout.strip():
            return {"error": "Empty response from reddit"}

        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            post_info = data[0]["data"]["children"][0]["data"]
            comments = []
            if len(data) > 1:
                for child in data[1]["data"]["children"][:5]:
                    if child.get("kind") == "t1":
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
    except json.JSONDecodeError:
        return {"error": "JSON decode error (possibly rate limited or HTML response)"}
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Unknown error or unparseable JSON"}


def main():
    if not os.path.exists(LINKS_FILE):
        print(f"Links file {LINKS_FILE} not found.")
        return

    with open(LINKS_FILE) as f:
        all_links = [line.strip() for line in f if line.strip()]

    processed_data = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE) as f:
                processed_data = json.load(f)
        except json.JSONDecodeError:
            processed_data = []

    processed_urls = {item["url"] for item in processed_data if "url" in item}
    print("Deduplicating...")
    remaining_links_initial = [l for l in all_links if l not in processed_urls]

    # Prioritize subreddits and recency
    print("Reversing...")
    remaining_links_initial.reverse()  # Recent first

    priority_links = []
    other_links = []
    priority_subreddits_for_sorting = [
        "ClaudeAI",
        "ClaudeCode",
        "AI_Agents",
        "mcp",
        "LocalLLaMA",
        "cursor",
        "LangChain",
        "vibecoding",
    ]

    print("Sorting...")
    for l in remaining_links_initial:
        if any(f"/r/{s}/" in l for s in priority_subreddits_for_sorting):
            priority_links.append(l)
        else:
            other_links.append(l)

    to_process = priority_links + other_links
    to_process = to_process[:BATCH_SIZE]

    print(f"Found {len(all_links)} total links. Already processed: {len(processed_urls)}.")
    print(f"Priority links remaining: {len(priority_links)}.")
    print(f"Processing next batch of up to {BATCH_SIZE} links...")

    success_count = 0
    consecutive_json_errors = 0

    for i, link in enumerate(to_process):
        if success_count >= MAX_SUCCESSES:
            print(f"Reached MAX_SUCCESSES ({MAX_SUCCESSES}). Batch stopping.")
            break

        print(f"[{i + 1}/{len(to_process)}] Fetching: {link}")
        result = fetch_reddit_post(link)

        if "error" in result:
            print(f"  Error: {result['error']}")
            if "JSON decode error" in result["error"]:
                consecutive_json_errors += 1
                # If we get a JSON error, we might be blocked. Wait longer.
                time.sleep(10)
            else:
                processed_data.append({"url": link, "error": result["error"]})
                consecutive_json_errors = 0

            if consecutive_json_errors > 15:
                print("Too many consecutive JSON errors. Likely hard rate limited. Stopping.")
                break
        else:
            processed_data.append(result)
            success_count += 1
            consecutive_json_errors = 0

        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(processed_data, f, indent=2)

        time.sleep(SLEEP_TIME)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(processed_data, f, indent=2)

    print(f"Batch complete. Success: {success_count}.")


if __name__ == "__main__":
    main()
