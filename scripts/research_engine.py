import json
import os
import subprocess
import time
from typing import Any, Dict, List

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LINKS_FILE = "data/research/reddit_backlog_3mo.txt"
OUTPUT_FILE = "data/research/all_processed_reddit.json"
BATCH_SIZE = 500
MAX_SUCCESSES = 400

def fetch_reddit_post(url: str) -> dict:
    # Skip noise/irrelevant subreddits
    skip_subreddits = ["ASU", "ASUOnline", "ApplyingToCollege", "AskSF", "AskLosAngeles", "ArsenalFC", "Apartmentliving", "BeyondWonderlandPNW", "BoJackHorseman", "CRedit", "CitiesSkylines", "worldnews", "CVS"]
    if any(f"/r/{s}/" in url for s in skip_subreddits):
        return {"error": "Skipping non-technical/noisy subreddit"}

    if "reddit.com" not in url:
        return {"error": "Not a reddit.com link"}

    clean_url = url.rstrip("/") + ".json" if not url.endswith(".json") else url
    # Handle links like /r/subreddit/comments/id/title/
    if "/r/" in clean_url and "/comments/" in clean_url:
        pass
    else:
        return {"error": "Not a direct reddit post link"}

    try:
        result = subprocess.run(
            ["curl", "-L", "-A", DEFAULT_USER_AGENT, "-s", clean_url],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode != 0:
            return {"error": f"Curl error: {result.stderr}"}

        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            post_info = data[0]["data"]["children"][0]["data"]
            comments = []
            if len(data) > 1:
                for child in data[1]["data"]["children"][:5]:
                    if child.get("kind") == "t1":
                        comments.append({
                            "author": child["data"].get("author"),
                            "body": child["data"].get("body", "")[:500]
                        })

            return {
                "title": post_info.get("title"),
                "subreddit": post_info.get("subreddit"),
                "selftext": post_info.get("selftext", ""),
                "url": url,
                "comments": comments
            }
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
            print("Warning: corrupted JSON output file, starting fresh.")
            processed_data = []

    processed_urls = {item["url"] for item in processed_data if "url" in item}
    remaining_links = [l for l in all_links if l not in processed_urls]
    
    # Prioritize the most recent links (end of file)
    remaining_links.reverse()

    print(f"Found {len(all_links)} total links. Already processed: {len(processed_urls)}.")
    print(f"Remaining: {len(remaining_links)}.")

    to_process = remaining_links[:BATCH_SIZE]
    print(f"Processing next batch of up to {BATCH_SIZE} links...")

    success_count = 0
    error_count = 0

    for i, link in enumerate(to_process):
        if success_count >= MAX_SUCCESSES:
            print(f"Reached MAX_SUCCESSES ({MAX_SUCCESSES}). Batch stopping.")
            break
            
        print(f"[{i+1}/{len(to_process)}] Fetching: {link}")
        result = fetch_reddit_post(link)
        
        if "error" in result:
            print(f"  Error: {result['error']}")
            # Don't save placeholders for JSON decoding errors (likely rate limit)
            if "Expecting value" not in result["error"]:
                processed_data.append({"url": link, "error": result["error"]})
            error_count += 1
            
            # If we hit multiple JSON errors in a row, maybe stop the batch
            if error_count > 10 and "Expecting value" in result["error"]:
                 print("Too many consecutive JSON errors. Stopping early.")
                 break
        else:
            processed_data.append(result)
            success_count += 1
        
        # Save every 5 successes
        if (i + 1) % 5 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(processed_data, f, indent=2)
        
        time.sleep(2.0) # Increased sleep to avoid rate limits

    # Final save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(processed_data, f, indent=2)

    print(f"Batch complete. Success: {success_count}, Errors: {error_count}.")
    print(f"Total processed so far: {len(processed_data)}.")

if __name__ == "__main__":
    main()
