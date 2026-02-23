import os
import plistlib
import re


def main():
    path = "/Users/kooshapari/Downloads/Ramlord (u:PlasmusAng) - Reddit.webarchive"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "rb") as f:
        data = plistlib.load(f)

    # Recursively find WebResourceData in the plist
    def find_data(node):
        if isinstance(node, dict):
            if "WebResourceData" in node:
                return [node["WebResourceData"]]
            found = []
            for v in node.values():
                found.extend(find_data(v))
            return found
        if isinstance(node, list):
            found = []
            for item in node:
                found.extend(find_data(item))
            return found
        return []

    all_data = find_data(data)

    # Extract links from all binary data found
    reddit_links = set()
    for binary in all_data:
        try:
            # Try to decode as UTF-8
            text = binary.decode("utf-8", errors="ignore")
            # Look for /r/ comments patterns
            # Also catch the "id": "t3_..." pattern commonly used in Reddit's JSON/HTML
            links = re.findall(r"reddit\.com/r/[a-zA-Z0-9_]+/comments/[a-zA-Z0-9_]+/[a-zA-Z0-9_]+", text)
            reddit_links.update(links)
        except Exception:
            pass

    # Save the links to a file
    with open("/tmp/saved_reddit_links_v4.txt", "w") as f:
        f.writelines(f"https://www.{link}\n" for link in sorted(reddit_links))

    print(f"Extracted {len(reddit_links)} reddit links.")


if __name__ == "__main__":
    main()
