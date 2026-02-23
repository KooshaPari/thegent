import contextlib
import orjson as json
import os
import subprocess
import time
from typing import Any, Dict, List

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch_reddit_post(url: str) -> dict[str, Any]:
    clean_url = url.rstrip("/") + ".json" if not url.endswith(".json") else url

    try:
        result = subprocess.run(
            ["curl", "-L", "-H", f"User-Agent: {DEFAULT_USER_AGENT}", "-s", clean_url],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return {"error": f"Curl error: {result.stderr}"}

        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            post_info = data[0]["data"]["children"][0]["data"]
            comments = []
            if len(data) > 1:
                for child in data[1]["data"]["children"][:5]:
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


def run_batch(links_file: str, output_file: str, start_index: int, batch_size: int = 200):
    with open(links_file) as f:
        all_links = [line.strip() for line in f if line.strip()]

    to_process = all_links[start_index : start_index + batch_size]

    # Load existing if any
    all_data = []
    if os.path.exists(output_file):
        with open(output_file) as f:
            with contextlib.suppress(BaseException):
                all_data = json.load(f)

    processed_urls = {item["url"] for item in all_data if "url" in item}
    remaining = [l for l in to_process if l not in processed_urls]

    print(f"Starting Batch. Total to process: {len(remaining)} (start_index: {start_index})")

    for i, link in enumerate(remaining):
        print(f"[{i + 1}/{len(remaining)}] Processing: {link}")
        post_data = fetch_reddit_post(link)
        if "error" not in post_data:
            all_data.append(post_data)
        else:
            print(f"  Error: {post_data['error']}")

        time.sleep(1.2)

        if (i + 1) % 5 == 0:
            with open(output_file, "w") as out:
                json.dump(all_data, out, indent=2)

    with open(output_file, "w") as out:
        json.dump(all_data, out, indent=2)
    print("Batch finished.")


if __name__ == "__main__":
    run_batch(
        "data/research/reddit_backlog_3mo.txt", "data/research/backlog_batch2.json", start_index=200, batch_size=200
    )
