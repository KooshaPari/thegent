#!/usr/bin/env python3
"""
Auto-generate VitePress sidebar from directory structure.

Part of VitePress Rich Documentation Implementation Plan - Phase 3.
"""

import orjson as json
import re
import sys
from pathlib import Path


def extract_title_from_markdown(md_file: Path) -> str | None:
    """Extract title from markdown file (frontmatter or first H1)."""
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception:
        return None

    # Check frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        title_match = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip().strip("\"'")

    # Check first H1
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    # Fallback to filename
    return md_file.stem.replace("_", " ").replace("-", " ").title()


def build_sidebar_structure(docs_dir: Path, base_path: str = "/") -> list[dict]:
    """Build sidebar structure from directory tree."""
    sidebar_items = []

    # Get all markdown files and directories
    items = []
    for item in sorted(docs_dir.iterdir()):
        if item.name.startswith(".") or item.name in ["node_modules", "dist", ".vitepress"]:
            continue

        if item.is_dir():
            items.append(("dir", item))
        elif item.is_file() and item.suffix == ".md":
            items.append(("file", item))

    # Process directories first
    for item_type, item in items:
        if item_type == "dir":
            # Recursively build sidebar for subdirectory
            sub_items = build_sidebar_structure(item, f"{base_path}{item.name}/")
            if sub_items:
                sidebar_items.append(
                    {
                        "text": item.name.replace("_", " ").replace("-", " ").title(),
                        "collapsed": False,
                        "items": sub_items,
                    }
                )

    # Process files
    for item_type, item in items:
        if item_type == "file":
            title = extract_title_from_markdown(item)
            if not title:
                continue

            # Calculate link path
            rel_path = item.relative_to(docs_dir.parent)
            link = f"/{rel_path.as_posix()}"

            sidebar_items.append({"text": title, "link": link})

    return sidebar_items


def generate_sidebar_config(docs_dir: Path, output_file: Path | None = None) -> dict:
    """Generate VitePress sidebar configuration."""
    sidebar_config = {}

    # Build sidebar for root
    root_items = build_sidebar_structure(docs_dir, "/")
    if root_items:
        sidebar_config["/"] = root_items

    # Build sidebars for subdirectories
    for subdir in docs_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("."):
            sub_items = build_sidebar_structure(subdir, f"/{subdir.name}/")
            if sub_items:
                sidebar_config[f"/{subdir.name}/"] = sub_items

    return sidebar_config


def generate_typescript_config(sidebar_config: dict, output_file: Path) -> str:
    """Generate TypeScript config code for sidebar."""
    config_str = "export const sidebar = "
    config_str += json.dumps(sidebar_config, indent=2, ensure_ascii=False).decode("utf-8")
    config_str += "\n"
    return config_str


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate VitePress sidebar from directory structure")
    parser.add_argument("--docs-dir", type=str, default="docs", help="Documentation directory")
    parser.add_argument("--output", type=str, default="docs/.vitepress/sidebar.ts", help="Output TypeScript file")
    parser.add_argument("--format", choices=["ts", "json"], default="ts", help="Output format")

    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"Error: Documentation directory not found: {docs_dir}", file=sys.stderr)
        sys.exit(1)

    sidebar_config = generate_sidebar_config(docs_dir)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "ts":
        config_code = generate_typescript_config(sidebar_config, output_path)
        output_path.write_text(config_code, encoding="utf-8")
    else:
        json_str = json.dumps(sidebar_config, indent=2, ensure_ascii=False).decode("utf-8")
        output_path.write_text(json_str, encoding="utf-8")

    print(f"✅ Generated sidebar config: {output_path}")
    print(f"   Found {len(sidebar_config)} sidebar sections")


if __name__ == "__main__":
    main()
