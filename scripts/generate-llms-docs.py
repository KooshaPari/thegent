#!/usr/bin/env python3
"""
Generate LLM-friendly documentation (.llms.txt) from VitePress docs.

Part of VitePress Rich Documentation Implementation Plan - Phase 3.
"""

import re
import sys
from pathlib import Path


def extract_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract and parse frontmatter from markdown."""
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not frontmatter_match:
        return None, content

    frontmatter_text = frontmatter_match.group(1)
    body = content[frontmatter_match.end() :]

    # Simple frontmatter parser
    frontmatter = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip("\"'")

    return frontmatter, body


def clean_markdown_for_llm(content: str, include_code: bool = True) -> str:
    """Clean markdown content for LLM consumption."""
    # Remove frontmatter
    _, body = extract_frontmatter(content)

    # Remove HTML comments
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)

    # Remove Vue components (keep text content)
    body = re.sub(r"<CodePlayground[^>]*>.*?</CodePlayground>", "", body, flags=re.DOTALL)
    body = re.sub(r"<DemoGif[^>]*/>", "", body, flags=re.DOTALL)
    body = re.sub(r"<Callout[^>]*>.*?</Callout>", "", body, flags=re.DOTALL)

    # Convert code blocks to plain text if include_code is False
    if not include_code:
        body = re.sub(r"```[\s\S]*?```", "", body)
    else:
        # Keep code blocks but simplify
        body = re.sub(r"```(\w+)?\n", "```\n", body)

    # Remove excessive blank lines
    body = re.sub(r"\n{3,}", "\n\n", body)

    # Remove "See Also" sections (they're navigation, not content)
    body = re.sub(r"## See Also.*$", "", body, flags=re.DOTALL | re.MULTILINE)

    return body.strip()


def generate_llms_file(md_file: Path, output_dir: Path, include_code: bool = True) -> Path:
    """Generate .llms.txt file from markdown."""
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception:
        return None

    # Clean content
    cleaned = clean_markdown_for_llm(content, include_code)

    # Get relative path for output
    rel_path = md_file.relative_to(output_dir.parent)
    output_path = output_dir / f"{rel_path.parent}" / f"{md_file.stem}.llms.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add metadata header
    frontmatter, _ = extract_frontmatter(content)
    header = f"# {md_file.stem}\n\n"
    if frontmatter:
        if "title" in frontmatter:
            header += f"Title: {frontmatter['title']}\n"
        if "description" in frontmatter:
            header += f"Description: {frontmatter['description']}\n"
    header += f"Source: {rel_path}\n\n---\n\n"

    output_content = header + cleaned
    output_path.write_text(output_content, encoding="utf-8")

    return output_path


def generate_index_file(output_dir: Path, md_files: list[Path]) -> Path:
    """Generate index file listing all LLM-friendly docs."""
    index_path = output_dir / "index.llms.txt"

    index_content = "# LLM-Friendly Documentation Index\n\n"
    index_content += "This directory contains LLM-friendly versions of all documentation.\n\n"
    index_content += "## Files\n\n"

    for md_file in sorted(md_files):
        rel_path = md_file.relative_to(output_dir.parent.parent)
        llms_path = output_dir / f"{rel_path.parent}" / f"{md_file.stem}.llms.txt"
        if llms_path.exists():
            index_content += f"- [{md_file.stem}]({llms_path.relative_to(output_dir)})\n"

    index_path.write_text(index_content, encoding="utf-8")
    return index_path


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate LLM-friendly documentation")
    parser.add_argument("--docs-dir", type=str, default="docs", help="Documentation directory")
    parser.add_argument("--output-dir", type=str, default=".llms", help="Output directory")
    parser.add_argument("--include-code", action="store_true", default=True, help="Include code blocks in output")
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="*",
        default=["node_modules", ".vitepress", "dist", ".git"],
        help="Directories to exclude",
    )

    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all markdown files
    md_files = []
    exclude_dirs = set(args.exclude_dirs)

    for md_file in docs_dir.rglob("*.md"):
        # Check if file is in excluded directory
        if any(excluded in md_file.parts for excluded in exclude_dirs):
            continue
        md_files.append(md_file)

    print(f"Found {len(md_files)} markdown files")

    # Generate LLM-friendly files
    generated = []
    for md_file in md_files:
        try:
            output_path = generate_llms_file(md_file, output_dir, args.include_code)
            if output_path:
                generated.append(output_path)
                print(f"✅ Generated: {output_path.relative_to(Path.cwd())}")
        except Exception as e:
            print(f"Warning: Failed to process {md_file}: {e}", file=sys.stderr)

    # Generate index
    index_path = generate_index_file(output_dir, md_files)
    print(f"✅ Generated index: {index_path}")

    print(f"\n✅ Generated {len(generated)} LLM-friendly documentation files")
    print(f"   Output directory: {output_dir}")


if __name__ == "__main__":
    main()
