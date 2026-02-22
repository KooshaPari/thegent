import os
import re


def main():
    path = "/Users/kooshapari/Downloads/Ramlord (u:PlasmusAng) - Reddit.webarchive"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    # Using strings-like extraction in Python for better control
    with open(path, "rb") as f:
        data = f.read()

    # Look for t3_ post IDs
    # Reddit post IDs are t3_ followed by 6-7 alphanumeric characters
    t3_ids = re.findall(rb"t3_([a-z0-9]{5,8})", data)

    unique_ids = set()
    for tid in t3_ids:
        unique_ids.add(tid.decode("utf-8"))

    print(f"Extracted {len(unique_ids)} unique Reddit post IDs from webarchive.")

    with open("data/research/webarchive_ids.txt", "w") as f:
        for tid in sorted(unique_ids):
            f.write(f"{tid}\n")


if __name__ == "__main__":
    main()
