import plistlib
import os

def main():
    path = "/Users/kooshapari/Downloads/Ramlord (u:PlasmusAng) - Reddit.webarchive"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, 'rb') as f:
        plist = plistlib.load(f)

    resources = []
    main_res = plist.get('WebMainResource')
    if main_res:
        resources.append((main_res.get('WebResourceURL'), len(main_res.get('WebResourceData', b''))))

    sub_res = plist.get('WebSubresources', [])
    for res in sub_res:
        resources.append((res.get('WebResourceURL'), len(res.get('WebResourceData', b''))))

    # Sort by size descending
    resources.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Size (bytes)':<15} {'URL'}")
    print("-" * 80)
    for url, size in resources[:50]:
        print(f"{size:<15} {url}")

if __name__ == "__main__":
    main()
