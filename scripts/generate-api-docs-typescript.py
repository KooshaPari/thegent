#!/usr/bin/env python3
"""
Generate API docs from TypeScript/JavaScript JSDoc comments for VitePress documentation.

Part of VitePress Rich Documentation Implementation Plan - Phase 4.
Extracts JSDoc comments and generates API documentation.
"""

import re
import sys
from pathlib import Path
from typing import Any


def extract_jsdoc(file_path: Path) -> dict[str, dict[str, Any]]:
    """Extract JSDoc comments from TypeScript/JavaScript file."""
    docs = {}

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return docs

    # Pattern to match JSDoc comments
    jsdoc_pattern = r"/\*\*\s*\n((?:\s*\*[^\n]*\n)+)\s*\*/"

    # Find all JSDoc comments
    for match in re.finditer(jsdoc_pattern, content, re.MULTILINE):
        jsdoc_text = match.group(1)
        # Remove leading * and spaces
        jsdoc_lines = [line.strip().lstrip("*").strip() for line in jsdoc_text.split("\n")]
        jsdoc_content = "\n".join(jsdoc_lines).strip()

        # Find the next function/class/interface/type after this JSDoc
        # Look ahead for function, class, interface, type, const, let, var declarations
        remaining_content = content[match.end() :]

        # Try to find function/class/etc after JSDoc
        func_match = re.search(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", remaining_content[:500])
        class_match = re.search(r"(?:export\s+)?class\s+(\w+)", remaining_content[:500])
        interface_match = re.search(r"(?:export\s+)?interface\s+(\w+)", remaining_content[:500])
        type_match = re.search(r"(?:export\s+)?type\s+(\w+)", remaining_content[:500])
        const_match = re.search(r"(?:export\s+)?const\s+(\w+)\s*[:=]", remaining_content[:500])

        # Determine what this JSDoc documents
        name = None
        doc_type = None

        if func_match:
            name = func_match.group(1)
            doc_type = "function"
        elif class_match:
            name = class_match.group(1)
            doc_type = "class"
        elif interface_match:
            name = interface_match.group(1)
            doc_type = "interface"
        elif type_match:
            name = type_match.group(1)
            doc_type = "type"
        elif const_match:
            name = const_match.group(1)
            doc_type = "constant"

        if name:
            # Parse JSDoc tags
            parsed = parse_jsdoc(jsdoc_content)
            docs[name] = {
                "docstring": parsed.get("description", ""),
                "type": doc_type,
                "params": parsed.get("params", []),
                "returns": parsed.get("returns", {}),
                "throws": parsed.get("throws", []),
                "example": parsed.get("example", ""),
                "since": parsed.get("since", ""),
                "deprecated": parsed.get("deprecated", False),
            }

    return docs


def parse_jsdoc(jsdoc_content: str) -> dict[str, Any]:
    """Parse JSDoc content into structured data."""
    parsed = {
        "description": "",
        "params": [],
        "returns": {},
        "throws": [],
        "example": "",
        "since": "",
        "deprecated": False,
    }

    lines = jsdoc_content.split("\n")
    current_section = "description"
    description_lines = []

    for line in lines:
        line = line.strip()

        # @param tag
        if line.startswith("@param"):
            param_match = re.match(r"@param\s+\{([^}]+)\}\s+(\w+)\s*(.*)", line)
            if param_match:
                param_type = param_match.group(1)
                param_name = param_match.group(2)
                param_desc = param_match.group(3).strip()
                parsed["params"].append({"name": param_name, "type": param_type, "description": param_desc})
            continue

        # @returns/@return tag
        if line.startswith(("@returns", "@return")):
            return_match = re.match(r"@returns?\s+\{([^}]+)\}\s*(.*)", line)
            if return_match:
                parsed["returns"] = {"type": return_match.group(1), "description": return_match.group(2).strip()}
            continue

        # @throws/@throws tag
        if line.startswith(("@throws", "@throws")):
            throws_match = re.match(r"@throws?\s+\{([^}]+)\}\s*(.*)", line)
            if throws_match:
                parsed["throws"].append({"type": throws_match.group(1), "description": throws_match.group(2).strip()})
            continue

        # @example tag
        if line.startswith("@example"):
            example_text = line.replace("@example", "").strip()
            parsed["example"] = example_text
            continue

        # @since tag
        if line.startswith("@since"):
            parsed["since"] = line.replace("@since", "").strip()
            continue

        # @deprecated tag
        if line.startswith("@deprecated"):
            parsed["deprecated"] = True
            deprecated_text = line.replace("@deprecated", "").strip()
            if deprecated_text:
                parsed["deprecated_message"] = deprecated_text
            continue

        # Regular description line
        if not line.startswith("@"):
            description_lines.append(line)

    parsed["description"] = "\n".join(description_lines).strip()
    return parsed


def generate_markdown(docs: dict[str, dict[str, Any]], module_name: str, module_path: Path | None = None) -> str:
    """Generate Markdown API docs from extracted JSDoc."""
    md = f"# {module_name} API Reference\n\n"

    if module_path:
        try:
            rel_path = module_path.relative_to(Path.cwd())
            md += f"> **Source**: `{rel_path}`\n\n"
        except ValueError:
            md += f"> **Source**: `{module_path}`\n\n"

    if not docs:
        md += "*No API documentation found.*\n"
        return md

    # Group by type
    classes = {k: v for k, v in docs.items() if v.get("type") == "class"}
    interfaces = {k: v for k, v in docs.items() if v.get("type") == "interface"}
    types = {k: v for k, v in docs.items() if v.get("type") == "type"}
    functions = {k: v for k, v in docs.items() if v.get("type") == "function"}
    constants = {k: v for k, v in docs.items() if v.get("type") == "constant"}

    # Classes
    if classes:
        md += "## Classes\n\n"
        for name, info in sorted(classes.items()):
            md += generate_item_markdown(name, info)

    # Interfaces
    if interfaces:
        md += "## Interfaces\n\n"
        for name, info in sorted(interfaces.items()):
            md += generate_item_markdown(name, info)

    # Types
    if types:
        md += "## Types\n\n"
        for name, info in sorted(types.items()):
            md += generate_item_markdown(name, info)

    # Functions
    if functions:
        md += "## Functions\n\n"
        for name, info in sorted(functions.items()):
            md += generate_item_markdown(name, info)

    # Constants
    if constants:
        md += "## Constants\n\n"
        for name, info in sorted(constants.items()):
            md += generate_item_markdown(name, info)

    return md


def generate_item_markdown(name: str, info: dict[str, Any]) -> str:
    """Generate markdown for a single API item."""
    md = f"### {name}\n\n"

    if info.get("deprecated"):
        deprecated_msg = info.get("deprecated_message", "This API is deprecated.")
        md += f"::: warning Deprecated\n{deprecated_msg}\n:::\n\n"

    if info.get("docstring"):
        md += f"{info['docstring']}\n\n"

    # Parameters
    if info.get("params"):
        md += "**Parameters:**\n\n"
        for param in info["params"]:
            param_type = param.get("type", "any")
            param_name = param.get("name", "")
            param_desc = param.get("description", "")
            md += f"- `{param_name}` (`{param_type}`) - {param_desc}\n"
        md += "\n"

    # Returns
    if info.get("returns"):
        returns = info["returns"]
        return_type = returns.get("type", "any")
        return_desc = returns.get("description", "")
        md += f"**Returns:** `{return_type}`"
        if return_desc:
            md += f" - {return_desc}"
        md += "\n\n"

    # Throws
    if info.get("throws"):
        md += "**Throws:**\n\n"
        for throw in info["throws"]:
            throw_type = throw.get("type", "Error")
            throw_desc = throw.get("description", "")
            md += f"- `{throw_type}` - {throw_desc}\n"
        md += "\n"

    # Example
    if info.get("example"):
        md += "**Example:**\n\n"
        md += f"```typescript\n{info['example']}\n```\n\n"

    # Since
    if info.get("since"):
        md += f"**Since:** {info['since']}\n\n"

    md += "---\n\n"
    return md


def process_file(file_path: Path, output_dir: Path) -> None:
    """Process a single TypeScript/JavaScript file."""
    docs = extract_jsdoc(file_path)

    if not docs:
        return

    module_name = file_path.stem
    if module_name == "index":
        module_name = file_path.parent.name

    md_content = generate_markdown(docs, module_name, file_path)

    # Create output path
    output_path = output_dir / f"{module_name}_api.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(md_content, encoding="utf-8")
    try:
        rel_path = output_path.relative_to(Path.cwd())
    except ValueError:
        rel_path = output_path
    print(f"✅ Generated: {rel_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate API docs from TypeScript/JavaScript JSDoc comments")
    parser.add_argument("--source", type=str, default=".", help="Source directory (default: current directory)")
    parser.add_argument(
        "--output", type=str, default="docs/reference/api", help="Output directory (default: docs/reference/api)"
    )
    parser.add_argument("--file", type=str, help="Process single file")
    parser.add_argument(
        "--extensions",
        type=str,
        nargs="+",
        default=[".ts", ".tsx", ".js", ".jsx"],
        help="File extensions to process (default: .ts .tsx .js .jsx)",
    )

    args = parser.parse_args()

    source_dir = Path(args.source)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.file:
        # Process single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        process_file(file_path, output_dir)
    else:
        # Process all matching files
        filtered_files = []
        source_subdirs = [source_dir / sub for sub in ["src", "apps", "packages", "modules", "extensions", "web", "trace"]]
        source_subdirs = [sub for sub in source_subdirs if sub.exists()]

        if not source_subdirs:
            source_subdirs = [source_dir]

        for subdir in source_subdirs:
            for ext in args.extensions:
                filtered_files.extend(list(subdir.rglob(f"*{ext}")))

        # Filter out node_modules, dist, and .vitepress directories
        filtered_files = [
            f for f in filtered_files if "node_modules" not in str(f) and "dist" not in str(f) and ".vitepress" not in str(f)
        ]

        print(f"Found {len(filtered_files)} TypeScript/JavaScript files")


        for file_path in filtered_files:
            try:
                process_file(file_path, output_dir)
            except Exception as e:
                print(f"Warning: Failed to process {file_path}: {e}", file=sys.stderr)

        print(f"\n✅ API docs generated in {output_dir}")


if __name__ == "__main__":
    main()
