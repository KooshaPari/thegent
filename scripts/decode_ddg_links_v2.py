import sys
import urllib.parse
import re

def main():
    content = sys.stdin.read()
    # Find all uddg=... sequences which are the actual result links in DDG HTML
    # Example: //duckduckgo.com/l/?uddg=https%3A%2F%2Fgithub.com%2Fsst%2Fopentui&rut=...
    matches = re.findall(r'uddg=([^&"\'>\s]+)', content)
    found = set()
    for m in matches:
        url = urllib.parse.unquote(m)
        if url.startswith('http') and "duckduckgo.com" not in url:
            if url not in found:
                print(url)
                found.add(url)
    
    # Also find any raw links that look like GitHub or Dev.to
    raw_links = re.findall(r'https?://(?:github\.com|dev\.to|medium\.com|hashnode\.com|arxiv\.org)/[^\s"\'<>]+', content)
    for url in raw_links:
        if url not in found:
            print(url)
            found.add(url)

if __name__ == "__main__":
    main()
