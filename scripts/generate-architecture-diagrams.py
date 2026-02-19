#!/usr/bin/env python3
"""
Generate Mermaid architecture diagrams from code structure.

Reduces verbosity: single command to generate all architecture diagrams.
"""

import ast
from collections import defaultdict
from pathlib import Path


def analyze_module_dependencies(module_path: Path) -> dict[str, set[str]]:
    """Analyze module dependencies from AST.

    Args:
        module_path: Path to Python module

    Returns:
        Dict mapping module name -> set of imported modules
    """
    try:
        with open(module_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(module_path))
    except Exception as e:
        print(f"⚠️  Error parsing {module_path}: {e}")
        return {}

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])

    module_name = module_path.stem
    return {module_name: imports}


def analyze_package_structure(package_path: Path) -> dict[str, list[str]]:
    """Analyze package structure (modules and subpackages).

    Args:
        package_path: Path to package directory

    Returns:
        Dict mapping package -> list of modules/subpackages
    """
    structure = defaultdict(list)

    for item in package_path.rglob("*.py"):
        if item.name.startswith("__"):
            continue

        rel_path = item.relative_to(package_path)
        parts = rel_path.parts[:-1]  # Exclude filename

        if parts:
            parent = ".".join(parts)
            structure[parent].append(item.stem)
        else:
            structure["."].append(item.stem)

    return dict(structure)


def generate_mermaid_dependency_graph(deps: dict[str, set[str]], title: str = "Module Dependencies") -> str:
    """Generate Mermaid dependency graph.

    Args:
        deps: Dict mapping module -> set of dependencies
        title: Graph title

    Returns:
        Mermaid diagram code
    """
    mermaid = "```mermaid\ngraph TD\n"
    mermaid += f"  %% {title}\n"

    # Collect all nodes
    all_nodes = set(deps.keys())
    for imports in deps.values():
        all_nodes.update(imports)

    # Filter to thegent modules only
    thegent_nodes = {n for n in all_nodes if n.startswith("thegent") or "." in n}

    # Add nodes
    for node in sorted(thegent_nodes):
        node_id = node.replace(".", "_").replace("-", "_")
        label = node.split(".")[-1]
        mermaid += f'  {node_id}["{label}"]\n'

    # Add edges
    for module, imports in deps.items():
        module_id = module.replace(".", "_").replace("-", "_")
        for imp in imports:
            if imp.startswith("thegent") or "." in imp:
                imp_id = imp.replace(".", "_").replace("-", "_")
                mermaid += f"  {module_id} --> {imp_id}\n"

    mermaid += "```\n"
    return mermaid


def generate_mermaid_package_structure(structure: dict[str, list[str]], title: str = "Package Structure") -> str:
    """Generate Mermaid package structure diagram.

    Args:
        structure: Dict mapping package -> list of modules
        title: Diagram title

    Returns:
        Mermaid diagram code
    """
    mermaid = "```mermaid\ngraph TD\n"
    mermaid += f"  %% {title}\n"

    # Root package
    mermaid += '  root["thegent"]\n'

    # Add packages and modules
    for package, modules in sorted(structure.items()):
        if package == ".":
            package_id = "root"
        else:
            package_id = package.replace(".", "_").replace("-", "_")
            parent_id = "root" if "." not in package else package.rsplit(".", 1)[0].replace(".", "_")
            mermaid += f'  {package_id}["{package or "root"}"]\n'
            mermaid += f"  {parent_id} --> {package_id}\n"

        for module in modules:
            module_id = f"{package_id}_{module}".replace(".", "_").replace("-", "_")
            mermaid += f'  {module_id}["{module}"]\n'
            mermaid += f"  {package_id} --> {module_id}\n"

    mermaid += "```\n"
    return mermaid


def generate_architecture_diagrams(
    source_dir: Path = Path("src/thegent"), output_dir: Path = Path("docs/architecture/diagrams")
) -> dict[str, str]:
    """Generate all architecture diagrams.

    Args:
        source_dir: Source directory to analyze
        output_dir: Output directory for diagrams

    Returns:
        Dict mapping diagram name -> file path
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # Analyze dependencies
    print("📊 Analyzing module dependencies...")
    all_deps = {}
    for py_file in source_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
        deps = analyze_module_dependencies(py_file)
        all_deps.update(deps)

    # Generate dependency graph
    dep_graph = generate_mermaid_dependency_graph(all_deps, title="Thegent Module Dependencies")
    dep_file = output_dir / "module-dependencies.md"
    dep_file.write_text(dep_graph, encoding="utf-8")
    results["dependencies"] = str(dep_file)
    print(f"  ✅ Generated: {dep_file}")

    # Analyze package structure
    print("📦 Analyzing package structure...")
    structure = analyze_package_structure(source_dir)

    # Generate structure diagram
    struct_diagram = generate_mermaid_package_structure(structure, title="Thegent Package Structure")
    struct_file = output_dir / "package-structure.md"
    struct_file.write_text(struct_diagram, encoding="utf-8")
    results["structure"] = str(struct_file)
    print(f"  ✅ Generated: {struct_file}")

    return results


if __name__ == "__main__":
    import sys

    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src/thegent")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("docs/architecture/diagrams")

    print("🏗️  Generating architecture diagrams...")
    results = generate_architecture_diagrams(source_dir, output_dir)

    print(f"\n✅ Generated {len(results)} diagrams:")
    for name, path in results.items():
        print(f"  - {name}: {path}")
