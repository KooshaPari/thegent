import plistlib
import os


def main():
    path = "/Users/kooshapari/Downloads/Ramlord (u:PlasmusAng) - Reddit.webarchive"
    target_url = "https://www.reddit.com/user/PlasmusAng/saved/"

    with open(path, "rb") as f:
        plist = plistlib.load(f)

    main_resource = plist.get("WebMainResource")
    if main_resource and main_resource.get("WebResourceURL") == target_url:
        print("Found main resource matching target URL.")
        data = main_resource.get("WebResourceData")
        if data:
            with open("data/research/saved_posts_main.html", "wb") as f:
                f.write(data)
            print("Wrote main resource data to data/research/saved_posts_main.html")
            return

    # If not main, check subresources
    subresources = plist.get("WebSubresources", [])
    for res in subresources:
        if res.get("WebResourceURL") == target_url:
            print("Found subresource matching target URL.")
            data = res.get("WebResourceData")
            if data:
                with open("data/research/saved_posts_sub.html", "wb") as f:
                    f.write(data)
                print("Wrote subresource data to data/research/saved_posts_sub.html")
                return

    print("Target URL not found in WebMainResource or WebSubresources.")


if __name__ == "__main__":
    main()
