import re
import sys
import urllib.parse


def main():
    content = sys.stdin.read()
    # Find all uddg=... sequences
    matches = re.findall(r'uddg=([^&"]+)', content)
    for m in matches:
        url = urllib.parse.unquote(m)
        if url.startswith('http'):
            print(url)

if __name__ == "__main__":
    main()
