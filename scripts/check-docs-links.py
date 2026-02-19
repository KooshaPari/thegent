#!/usr/bin/env python3
"""Automated link checker for documentation.

Scans markdown files for broken links and reports results.
"""

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

try:
    import httpx
except ImportError:
    print("httpx not installed. Install with: pip install httpx")
    sys.exit(1)


def find_markdown_links(content: str) -> list[tuple[str, str]]:
    """Find all markdown links [text](url) in content."""
    # Match [text](url) patterns - handle nested parens in URLs
    pattern = r"\[([^\]]+)\]\(((?:[^()]|\([^()]*\))*)\)"
    matches = re.findall(pattern, content)
    return matches


def is_internal_link(url: str) -> bool:
    """Check if link is an internal link (relative or docs reference)."""
    parsed = urlparse(url)
    return not parsed.scheme or parsed.scheme == "" or parsed.netloc == ""


def is_skipable_link(url: str) -> bool:
    """Check if link should be skipped (anchors, mailto, tel, etc.)."""
    parsed = urlparse(url)
    fragment = parsed.fragment
    path = parsed.path

    # Skip empty anchors
    if not path and fragment:
        return True
    # Skip mailto
    if url.startswith("mailto:"):
        return True
    # Skip tel
    if url.startswith("tel:"):
        return True
    # Skip javascript links
    if url.startswith("javascript:"):
        return True
    # Skip file:// links
    if url.startswith("file://"):
        return True
    # Skip .md file links (internal documentation references)
    if path.endswith((".md", ".MD")):
        return True
    return False


def check_link(url: str, timeout: float = 10.0) -> tuple[str, bool, int | None]:
    """Check if a URL is accessible using HEAD request."""
    try:
        client = httpx.Client(timeout=timeout, follow_redirects=True)
        response = client.head(url, headers={"User-Agent": "thegent-link-checker/1.0"})
        is_valid = response.status_code < 400
        return (url, is_valid, response.status_code)
    except httpx.TimeoutException:
        return (url, False, None)
    except httpx.RequestError as e:
        return (url, False, None)
    except Exception:
        return (url, False, None)


def check_file_link(path: str, base_dir: Path) -> tuple[str, bool]:
    """Check if a file reference exists."""
    file_path = base_dir / path if not path.startswith("/") else Path(path)
    exists = file_path.exists()
    return (path, exists)


def scan_directory(directory: Path, max_workers: int = 10) -> dict:
    """Scan directory recursively for markdown files and check all links."""
    results = {
        "total_files": 0,
        "total_links": 0,
        "broken_links": [],
        "broken_files": [],
        "skipped_links": 0,
        "valid_links": 0,
    }

    # Collect all markdown files
    md_files = list(directory.rglob("*.md"))
    results["total_files"] = len(md_files)

    # Collect all links
    all_links = []  # (file_path, link_text, url)
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            links = find_markdown_links(content)
            for text, url in links:
                all_links.append((str(md_file), text, url))
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"Warning: Could not read {md_file}: {e}")
            continue

    results["total_links"] = len(all_links)

    # Process links
    skipped = []
    file_links = []
    http_links = []

    for file_path, text, url in all_links:
        # Skip anchors and special links
        if url.startswith(("#", "mailto:", "tel:")):
            skipped.append((file_path, text, url, "anchor/special"))
            continue

        # Skip relative file references
        if not url.startswith("http"):
            if is_skipable_link(url):
                skipped.append((file_path, text, url, "skipable"))
                continue
            # Treat as file reference
            file_links.append((file_path, text, url))
            continue

        http_links.append((file_path, text, url))

    results["skipped_links"] = len(skipped)

    # Check file links
    for file_path, text, url in file_links:
        exists = check_file_link(url, directory)
        if not exists[1]:
            results["broken_files"].append(
                {
                    "file": file_path,
                    "link_text": text,
                    "url": url,
                    "error": "file_not_found",
                }
            )

    # Check HTTP links in parallel
    valid_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_link, url): (file_path, text, url) for file_path, text, url in http_links}

        for future in as_completed(futures):
            file_path, text, url = futures[future]
            try:
                _url_result, is_valid, status_code = future.result()
                if is_valid:
                    valid_count += 1
                else:
                    results["broken_links"].append(
                        {
                            "file": file_path,
                            "link_text": text,
                            "url": url,
                            "status_code": status_code,
                        }
                    )
            except Exception as e:
                results["broken_links"].append(
                    {
                        "file": file_path,
                        "link_text": text,
                        "url": url,
                        "error": str(e),
                    }
                )

    results["valid_links"] = valid_count

    return results


def print_report(results: dict) -> None:
    """Print a formatted report of link checking results."""
    print("\n" + "=" * 60)
    print("DOCUMENTATION LINK CHECK REPORT")
    print("=" * 60)

    print("\nSummary:")
    print(f"  Files scanned: {results['total_files']}")
    print(f"  Total links found: {results['total_links']}")
    print(f"  Valid HTTP links: {results['valid_links']}")
    print(f"  Skipped links: {results['skipped_links']}")
    print(f"  Broken HTTP links: {len(results['broken_links'])}")
    print(f"  Broken file references: {len(results['broken_files'])}")

    if results["broken_links"]:
        print("\n" + "-" * 60)
        print("BROKEN HTTP LINKS:")
        print("-" * 60)
        for link in results["broken_links"]:
            print(f"\n  File: {link['file']}")
            print(f"  Link text: {link['link_text']}")
            print(f"  URL: {link['url']}")
            if link.get("status_code"):
                print(f"  Status: {link['status_code']}")
            if link.get("error"):
                print(f"  Error: {link['error']}")

    if results["broken_files"]:
        print("\n" + "-" * 60)
        print("BROKEN FILE REFERENCES:")
        print("-" * 60)
        for link in results["broken_files"]:
            print(f"\n  File: {link['file']}")
            print(f"  Link text: {link['link_text']}")
            print(f"  Path: {link['url']}")

    # Exit with error if broken links found
    if results["broken_links"] or results["broken_files"]:
        print("\n" + "=" * 60)
        print("FAILED: Broken links found!")
        print("=" * 60)
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("SUCCESS: All links are valid!")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Check links in markdown documentation files.")
    parser.add_argument(
        "path", nargs="?", default="docs/", help="Path to directory containing markdown files (default: docs/)"
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="Timeout for HTTP requests in seconds (default: 10)"
    )
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers (default: 10)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    directory = Path(args.path)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        sys.exit(1)

    print(f"Scanning {directory} for broken links...")
    results = scan_directory(directory, max_workers=args.workers)

    if args.json:
        import json

        print(json.dumps(results, indent=2))
    else:
        print_report(results)


if __name__ == "__main__":
    main()
