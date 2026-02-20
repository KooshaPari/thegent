import json
import os
import re
import subprocess
import time
from io import BytesIO
from typing import Any, Dict, List

import httpx
import pytesseract
from PIL import Image

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
LINKS_FILE = "data/research/reddit_backlog_3mo.txt"
OUTPUT_FILE = "data/research/all_processed_reddit.json"
DISCOVERED_LINKS_FILE = "data/research/discovered_links.txt"
BATCH_SIZE = 2000
MAX_SUCCESSES = 2000
SLEEP_TIME = 4.0
COMMENT_LIMIT = 15

def extract_links(text: str) -> list[str]:
    """Extract all URLs from text."""
    return re.findall(r'https?://[^\s<>"\'\)]+', text)

def is_image_url(url: str) -> bool:
    """Check if a URL points to an image."""
    return any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp'])

def perform_ocr_from_url(url: str) -> str:
    """Download image and perform OCR."""
    try:
        resp = httpx.get(url, headers={"User-Agent": DEFAULT_USER_AGENT}, follow_redirects=True, timeout=10)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content))
            text = pytesseract.image_to_string(img)
            return text.strip()
    except Exception:
        pass
    return ""

def fetch_reddit_post(url: str) -> dict:
    priority_subreddits = ["ClaudeAI", "ClaudeCode", "AI_Agents", "mcp", "LocalLLaMA", "golang", "Python", "zsh", "Supabase", "cursor", "nextjs", "LangChain", "vibecoding"]
    skip_subreddits = ["ASU", "ASUOnline", "ApplyingToCollege", "AskSF", "AskLosAngeles", "ArsenalFC", "Apartmentliving", "BeyondWonderlandPNW", "BoJackHorseman", "CRedit", "CitiesSkylines", "worldnews", "CVS", "theydidthemath", "tmobile", "threejs", "thinkpad", "trashy", "traderjoes", "torrents"]

    if any(f"/r/{s}/" in url for s in skip_subreddits):
        return {"error": "Skipping non-technical/noisy subreddit"}

    if "reddit.com" not in url:
        return {"error": "Not a reddit.com link"}

    clean_url = url.rstrip("/") + ".json" if not url.endswith(".json") else url
    if "/r/" not in clean_url or "/comments/" not in clean_url:
        return {"error": "Not a direct reddit post link"}

    try:
        result = subprocess.run(
            ["curl", "-L", "-A", DEFAULT_USER_AGENT, "-s", clean_url],
            capture_output=True,
            text=True,
            timeout=20
        )
        if result.returncode != 0:
            return {"error": f"Curl error: {result.stderr}"}

        if not result.stdout.strip():
            return {"error": "Empty response from reddit"}

        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            post_info = data[0]["data"]["children"][0]["data"]
            selftext = post_info.get("selftext", "")

            # Extract links and OCR images in selftext
            all_discovered_links = extract_links(selftext)
            ocr_results = []
            for link in all_discovered_links:
                if is_image_url(link):
                    ocr_text = perform_ocr_from_url(link)
                    if ocr_text:
                        ocr_results.append({"url": link, "text": ocr_text})

            comments = []
            if len(data) > 1:
                for child in data[1]["data"]["children"][:COMMENT_LIMIT]:
                    if child.get("kind") == "t1":
                        body = child["data"].get("body", "")
                        comment_links = extract_links(body)
                        all_discovered_links.extend(comment_links)

                        # OCR images in comments
                        for clink in comment_links:
                            if is_image_url(clink):
                                ocr_text = perform_ocr_from_url(clink)
                                if ocr_text:
                                    ocr_results.append({"url": clink, "text": ocr_text})

                        comments.append({
                            "author": child["data"].get("author"),
                            "body": body[:1000]
                        })

            return {
                "title": post_info.get("title"),
                "subreddit": post_info.get("subreddit"),
                "selftext": selftext,
                "url": url,
                "comments": comments,
                "discovered_links": list(set(all_discovered_links)),
                "ocr_images": ocr_results
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
    remaining_links_initial = [l for l in all_links if l not in processed_urls]
    remaining_links_initial.reverse()

    priority_links = []
    other_links = []
    priority_subreddits_for_sorting = ["ClaudeAI", "ClaudeCode", "AI_Agents", "mcp", "LocalLLaMA", "cursor", "LangChain", "vibecoding"]

    for l in remaining_links_initial:
        if any(f"/r/{s}/" in l for s in priority_subreddits_for_sorting):
            priority_links.append(l)
        else:
            other_links.append(l)

    to_process = priority_links + other_links
    to_process = to_process[:BATCH_SIZE]

    print(f"Found {len(all_links)} total links. Already processed: {len(processed_urls)}.")
    print("Processing batch with Enhanced Mode (Deep Comments + Image OCR + Link Extraction)...")

    success_count = 0
    consecutive_json_errors = 0
    discovered_links_total = set()

    for i, link in enumerate(to_process):
        if success_count >= MAX_SUCCESSES:
            break

        print(f"[{i+1}/{len(to_process)}] Fetching: {link}")
        result = fetch_reddit_post(link)

        if "error" in result:
            print(f"  Error: {result['error']}")
            if "JSON decode error" in result["error"]:
                consecutive_json_errors += 1
                time.sleep(10)
            else:
                processed_data.append({"url": link, "error": result["error"]})
                consecutive_json_errors = 0

            if consecutive_json_errors > 15:
                 print("Too many consecutive JSON errors. Likely hard rate limited. Stopping.")
                 break
        else:
            processed_data.append(result)
            if "discovered_links" in result:
                discovered_links_total.update(result["discovered_links"])
            success_count += 1
            consecutive_json_errors = 0

        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(processed_data, f, indent=2)
            # Append discovered links
            with open(DISCOVERED_LINKS_FILE, "a") as f:
                f.writelines(f"{dlink}\n" for dlink in discovered_links_total)
            discovered_links_total.clear()

        time.sleep(SLEEP_TIME)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(processed_data, f, indent=2)

    print(f"Batch complete. Success: {success_count}.")

if __name__ == "__main__":
    main()
