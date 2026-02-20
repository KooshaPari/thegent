#!/usr/bin/env python3
"""
Generate API docs from Python docstrings for VitePress documentation.

Enhanced version with mkdocstrings-like functionality:
- Support for Google, NumPy, and reStructuredText docstring styles
- Type hint extraction from annotations
- Inheritance documentation with method resolution order
- Cross-references and better markdown output

Part of VitePress Rich Documentation Implementation Plan - Phase 2.
"""

import ast
import inspect
import sys
from pathlib import Path
from typing import Any

try:
    import docstring_parser
except ImportError:
    docstring_parser = None
    print("Warning: docstring_parser not available. Install with: pip install docstring-parser", file=sys.stderr)


def parse_docstring(docstring: str | None) -> dict[str, Any]:
    """Parse docstring using docstring_parser (supports Google, NumPy, reStructuredText)."""
    if not docstring or not docstring_parser:
        return {"description": docstring or "", "params": {}, "returns": None, "raises": {}, "examples": []}

    try:
        parsed = docstring_parser.parse(docstring)
        return {
            "description": parsed.short_description or "",
            "long_description": parsed.long_description or "",
            "params": {
                p.arg_name: {"type": p.type_name or "", "description": p.description or ""} for p in parsed.params
            },
            "returns": {
                "type": parsed.returns.type_name if parsed.returns else None,
                "description": parsed.returns.description if parsed.returns else None,
            },
            "raises": {r.type_name: r.description for r in parsed.raises} if parsed.raises else {},
            "examples": [ex.description for ex in parsed.examples] if parsed.examples else [],
        }
    except Exception:
        # Fallback to raw docstring
        return {"description": docstring, "params": {}, "returns": None, "raises": {}, "examples": []}


def extract_type_hint(annotation: ast.expr | None) -> str:
    """Extract type hint string from AST annotation."""
    if annotation is None:
        return "Any"

    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant):
        return str(annotation.value)
    if isinstance(annotation, ast.Subscript):
        # Handle generics like List[str], Dict[str, int]
        slice_str = extract_type_hint(annotation.slice) if hasattr(annotation, "slice") else ""
        value_str = extract_type_hint(annotation.value)
        return f"{value_str}[{slice_str}]"
    if isinstance(annotation, ast.Attribute):
        return f"{extract_type_hint(annotation.value)}.{annotation.attr}"
    if isinstance(annotation, ast.Tuple):
        return f"({', '.join(extract_type_hint(el) for el in annotation.elts)})"
    return "Any"


def get_method_resolution_order(class_node: ast.ClassDef, all_classes: dict[str, ast.ClassDef]) -> list[str]:
    """Calculate method resolution order (MRO) for a class."""
    mro = [class_node.name]
    for base in class_node.bases:
        if isinstance(base, ast.Name) and base.id in all_classes:
            mro.extend(get_method_resolution_order(all_classes[base.id], all_classes))
    return list(dict.fromkeys(mro))  # Remove duplicates while preserving order


def extract_docstrings(module_path: Path) -> dict[str, dict[str, Any]]:
    """Extract docstrings, type hints, and inheritance info from Python module."""
    docs = {}

    try:
        with open(module_path, encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=str(module_path))
    except Exception as e:
        print(f"Warning: Could not parse {module_path}: {e}", file=sys.stderr)
        return docs

    # Build class map for MRO calculation
    class_map = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    # Extract module-level docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        parsed_doc = parse_docstring(module_doc)
        docs["__module__"] = {
            "docstring": parsed_doc["description"],
            "long_description": parsed_doc.get("long_description", ""),
            "signature": None,
            "type": "module",
        }

    # Extract classes and functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            parsed_doc = parse_docstring(docstring)

            # Extract type hints from annotations
            args_with_types = []
            for arg in node.args.args:
                arg_type = extract_type_hint(arg.annotation) if arg.annotation else "Any"
                args_with_types.append({"name": arg.arg, "type": arg_type})

            return_type = extract_type_hint(node.returns) if node.returns else None

            docs[node.name] = {
                "docstring": parsed_doc["description"],
                "long_description": parsed_doc.get("long_description", ""),
                "params": parsed_doc["params"],
                "returns": parsed_doc["returns"]
                or ({"type": return_type, "description": None} if return_type else None),
                "raises": parsed_doc["raises"],
                "examples": parsed_doc["examples"],
                "signature": None,
                "type": "function",
                "args": args_with_types,
                "decorators": [d.id if isinstance(d, ast.Name) else None for d in node.decorator_list],
            }

        elif isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            parsed_doc = parse_docstring(docstring)

            # Extract methods with enhanced info
            methods = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_doc = parse_docstring(ast.get_docstring(item))
                    method_args = []
                    for arg in item.args.args:
                        arg_type = extract_type_hint(arg.annotation) if arg.annotation else "Any"
                        method_args.append({"name": arg.arg, "type": arg_type})

                    methods[item.name] = {
                        "docstring": method_doc["description"],
                        "long_description": method_doc.get("long_description", ""),
                        "params": method_doc["params"],
                        "returns": method_doc["returns"],
                        "args": method_args,
                    }

            # Calculate MRO
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(f"{extract_type_hint(base.value)}.{base.attr}")

            mro = get_method_resolution_order(node, class_map)

            docs[node.name] = {
                "docstring": parsed_doc["description"],
                "long_description": parsed_doc.get("long_description", ""),
                "signature": None,
                "type": "class",
                "methods": methods,
                "bases": bases,
                "mro": mro,
            }

    return docs


def format_signature(args: list[dict[str, str]], return_type: dict[str, Any] | None = None) -> str:
    """Format function signature with type hints."""
    args_str = ", ".join(f"{arg['name']}: {arg['type']}" for arg in args)
    if return_type and return_type.get("type"):
        return f"({args_str}) -> {return_type['type']}"
    return f"({args_str})"


def generate_markdown(docs: dict[str, dict[str, Any]], module_name: str, module_path: Path | None = None) -> str:
    """Generate enhanced Markdown API docs from extracted docstrings."""
    md = f"# {module_name} API Reference\n\n"

    if module_path:
        md += f"> **Source**: `{module_path.relative_to(Path.cwd()) if module_path.is_relative_to(Path.cwd()) else module_path}`\n\n"

    # Module docstring
    if "__module__" in docs:
        md += f"{docs['__module__']['docstring']}\n\n"
        if docs["__module__"].get("long_description"):
            md += f"{docs['__module__']['long_description']}\n\n"
        md += "---\n\n"

    # Classes first
    classes = {k: v for k, v in docs.items() if v.get("type") == "class" and k != "__module__"}
    functions = {k: v for k, v in docs.items() if v.get("type") == "function" and k != "__module__"}

    for name, info in sorted(classes.items()):
        md += f"## {name}\n\n"
        if info.get("docstring"):
            md += f"{info['docstring']}\n\n"
        if info.get("long_description"):
            md += f"{info['long_description']}\n\n"

        # Inheritance info
        if info.get("bases"):
            bases = [b for b in info["bases"] if b]
            if bases:
                md += f"**Inherits from**: `{', '.join(bases)}`\n\n"

        # Method Resolution Order
        if info.get("mro") and len(info["mro"]) > 1:
            md += f"**Method Resolution Order**: `{' -> '.join(info['mro'])}`\n\n"

        # Methods
        if info.get("methods"):
            md += "### Methods\n\n"
            for method_name, method_info in sorted(info["methods"].items()):
                if method_name.startswith("_") and method_name != "__init__":
                    continue
                md += f"#### {name}.{method_name}\n\n"

                # Signature with type hints
                if method_info.get("args"):
                    sig = format_signature(method_info["args"], method_info.get("returns"))
                    md += f"```python\n{method_name}{sig}\n```\n\n"

                # Description
                if method_info.get("docstring"):
                    md += f"{method_info['docstring']}\n\n"
                if method_info.get("long_description"):
                    md += f"{method_info['long_description']}\n\n"

                # Parameters
                if method_info.get("params"):
                    md += "**Parameters**:\n\n"
                    for param_name, param_info in method_info["params"].items():
                        param_type = param_info.get("type", "")
                        param_desc = param_info.get("description", "")
                        if param_type:
                            md += f"- `{param_name}` ({param_type}): {param_desc}\n"
                        else:
                            md += f"- `{param_name}`: {param_desc}\n"
                    md += "\n"

                # Returns
                if method_info.get("returns") and method_info["returns"].get("description"):
                    return_info = method_info["returns"]
                    return_type = return_info.get("type", "")
                    return_desc = return_info.get("description", "")
                    if return_type:
                        md += f"**Returns** (`{return_type}`): {return_desc}\n\n"
                    else:
                        md += f"**Returns**: {return_desc}\n\n"

                # Raises
                if method_info.get("raises"):
                    md += "**Raises**:\n\n"
                    for exc_type, exc_desc in method_info["raises"].items():
                        md += f"- `{exc_type}`: {exc_desc}\n"
                    md += "\n"

                # Examples
                if method_info.get("examples"):
                    md += "**Examples**:\n\n"
                    for example in method_info["examples"]:
                        md += f"```python\n{example}\n```\n\n"

                md += "---\n\n"

        md += "---\n\n"

    # Functions
    for name, info in sorted(functions.items()):
        if name.startswith("_"):
            continue
        md += f"## {name}\n\n"

        # Signature with type hints
        if info.get("args"):
            sig = format_signature(info["args"], info.get("returns"))
            md += f"```python\n{name}{sig}\n```\n\n"

        # Description
        if info.get("docstring"):
            md += f"{info['docstring']}\n\n"
        if info.get("long_description"):
            md += f"{info['long_description']}\n\n"

        # Parameters
        if info.get("params"):
            md += "**Parameters**:\n\n"
            for param_name, param_info in info["params"].items():
                param_type = param_info.get("type", "")
                param_desc = param_info.get("description", "")
                if param_type:
                    md += f"- `{param_name}` ({param_type}): {param_desc}\n"
                else:
                    md += f"- `{param_name}`: {param_desc}\n"
            md += "\n"

        # Returns
        if info.get("returns") and info["returns"].get("description"):
            return_info = info["returns"]
            return_type = return_info.get("type", "")
            return_desc = return_info.get("description", "")
            if return_type:
                md += f"**Returns** (`{return_type}`): {return_desc}\n\n"
            else:
                md += f"**Returns**: {return_desc}\n\n"

        # Raises
        if info.get("raises"):
            md += "**Raises**:\n\n"
            for exc_type, exc_desc in info["raises"].items():
                md += f"- `{exc_type}`: {exc_desc}\n"
            md += "\n"

        # Examples
        if info.get("examples"):
            md += "**Examples**:\n\n"
            for example in info["examples"]:
                md += f"```python\n{example}\n```\n\n"

        md += "---\n\n"

    return md


def process_module(module_path: Path, output_dir: Path) -> None:
    """Process a single module and generate API docs."""
    docs = extract_docstrings(module_path)
    if not docs:
        return

    module_name = module_path.stem
    if module_name == "__init__":
        module_name = module_path.parent.name

    md_content = generate_markdown(docs, module_name, module_path)

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

    parser = argparse.ArgumentParser(description="Generate enhanced API docs from Python docstrings")
    parser.add_argument("--source", type=str, default="src/thegent", help="Source directory")
    parser.add_argument("--output", type=str, default="docs/reference/api", help="Output directory")
    parser.add_argument("--module", type=str, help="Process single module (relative to source)")

    args = parser.parse_args()

    source_dir = Path(args.source)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.module:
        # Process single module
        module_path = source_dir / args.module
        if module_path.is_file():
            process_module(module_path, output_dir)
        else:
            print(f"Error: Module not found: {module_path}", file=sys.stderr)
            sys.exit(1)
    else:
        # Process all Python files
        python_files = list(source_dir.rglob("*.py"))
        print(f"Found {len(python_files)} Python files")

        for py_file in python_files:
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            try:
                process_module(py_file, output_dir)
            except Exception as e:
                print(f"Warning: Failed to process {py_file}: {e}", file=sys.stderr)

        print(f"\n✅ Enhanced API docs generated in {output_dir}")


if __name__ == "__main__":
    main()
