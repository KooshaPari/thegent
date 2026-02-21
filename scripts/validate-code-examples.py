#!/usr/bin/env python3
"""WP-8.2: Validate code examples in markdown documentation."""

import ast
import json
import re
import sys
from pathlib import Path


def validate_python_examples(md_file: Path) -> list[str]:
    """Extract and validate Python code blocks in a markdown file."""
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Failed to read file: {e}"]

    # Matches ```python ... ``` blocks
    code_blocks = re.findall(r"```python\n(.*?)```", content, re.DOTALL)

    errors = []
    for i, code in enumerate(code_blocks):
        try:
            ast.parse(code)
        except SyntaxError as e:
            # Try wrapping in a function to see if it's a signature
            try:
                # Remove trailing newlines and use single-line for signature check
                clean_code = code.strip().replace("\n", " ")
                ast.parse(f"def dummy_func({clean_code}): pass")
                continue # It's a valid signature/parameter list
            except SyntaxError:
                pass

            try:
                # Try wrapping in a def and see if it works
                # This handles 'func(a: int)' by making it 'def func(a: int): pass'
                clean_code = code.strip()
                if not clean_code.endswith(":"):
                    ast.parse(f"def {clean_code}: pass")
                else:
                    ast.parse(f"def {clean_code} pass")
                continue # It's a valid function/method signature
            except SyntaxError:
                pass

            # Try wrapping in a class if it looks like class content
            try:
                ast.parse(f"class Dummy:\n    {code}")
                continue
            except SyntaxError:
                pass

            # Try adding 'def ' if it looks like a function name with params but no 'def'
            try:
                ast.parse(f"def {code}\n    pass")
                continue
            except SyntaxError:
                pass

            # If all attempts fail, report the original error
            line_no = e.lineno or 0
            errors.append(f"Python block {i+1} syntax error at line {line_no}: {e.msg}")

    return errors


def validate_json_examples(md_file: Path) -> list[str]:
    """Extract and validate JSON code blocks in a markdown file."""
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception:
        return []

    # Matches ```json ... ``` blocks
    code_blocks = re.findall(r"```json\n(.*?)```", content, re.DOTALL)

    errors = []
    for i, code in enumerate(code_blocks):
        # Strip comments if any (common in some JSON examples but not strictly valid JSON)
        # But for strict validation we might want to keep it strict.
        # Let's try strict first.
        try:
            json.loads(code)
        except json.JSONDecodeError as e:
            errors.append(f"JSON block {i+1} error: {e}")

    return errors


def main():
    workspace_root = Path.cwd()
    docs_dir = workspace_root / "thegent" / "docs"
    if not docs_dir.exists():
        # Fallback to current dir if we are already in thegent
        docs_dir = workspace_root / "docs"
        if not docs_dir.exists():
            print("Error: Documentation directory not found.")
            sys.exit(1)

    all_errors = {}

    # Check all markdown files in docs
    md_files = list(docs_dir.glob("**/*.md"))
    print(f"Validating {len(md_files)} markdown files...")

    for md_file in md_files:
        # Skip node_modules or other unrelated dirs if any
        if "node_modules" in str(md_file) or ".vitepress" in str(md_file):
            continue

        py_errors = validate_python_examples(md_file)
        json_errors = validate_json_examples(md_file)

        errors = py_errors + json_errors
        if errors:
            all_errors[str(md_file.relative_to(workspace_root))] = errors

    if all_errors:
        print("\n❌ Code Example Validation Failed:")
        for file, errs in all_errors.items():
            print(f"\nFile: {file}")
            for err in errs:
                print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n✅ All code examples (Python/JSON) are valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
