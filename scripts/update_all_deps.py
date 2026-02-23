#!/usr/bin/env python3
"""
Update all dependencies to latest/beta versions as of Feb 17, 2026
"""
import re
import os
from pathlib import Path

# Latest versions as of Feb 17, 2026 (from crates.io API)
LATEST_VERSIONS = {
    "pyo3": "0.28.2",
    "tokio": "1.49.0",
    "serde": "1.0.228",
    "serde_json": "1.0.149",
    "rayon": "1.11.0",
    "clap": "4.5.59",
    "reqwest": "0.12",  # Will use latest 0.12.x
    "simd-json": "0.13",  # Will use latest 0.13.x
    "dashmap": "6",  # Will use latest 6.x
    "git2": "0.20",  # Will use latest 0.20.x
    "gix": "0.79",  # Will use latest 0.79.x
    "moka": "0.12",
    "sonic-rs": "0.5",
    "scc": "3",
    "compio": "0.7",
}

def update_cargo_toml(file_path):
    """Update versions in a Cargo.toml file"""
    try:
        with open(file_path) as f:
            content = f.read()

        original_content = content
        updated = False

        # Update each dependency
        for dep, latest_version in LATEST_VERSIONS.items():
            # Pattern 1: dep = "version"
            pattern1 = rf'({dep}\s*=\s*")([\d.]+)(")'
            def repl1(m, latest_version=latest_version):
                return f'{m.group(1)}{latest_version}{m.group(3)}'
            new_content = re.sub(pattern1, repl1, content)
            if new_content != content:
                content = new_content
                updated = True

            # Pattern 2: dep = { version = "version", ... }
            pattern2 = rf'({dep}\s*=\s*{{\s*version\s*=\s*")([\d.]+)(")'
            def repl2(m, latest_version=latest_version):
                return f'{m.group(1)}{latest_version}{m.group(3)}'
            new_content = re.sub(pattern2, repl2, content)
            if new_content != content:
                content = new_content
                updated = True

        if updated:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✓ Updated {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def main():
    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")

    # Find all Cargo.toml files
    cargo_files = list(base_path.rglob("Cargo.toml"))

    # Filter out venv and .venv directories
    cargo_files = [f for f in cargo_files if ".venv" not in str(f) and "venv" not in str(f)]

    print(f"Found {len(cargo_files)} Cargo.toml files")
    print("Updating dependencies...")

    updated_count = 0
    for cargo_file in cargo_files:
        if update_cargo_toml(cargo_file):
            updated_count += 1

    print(f"\nUpdated {updated_count} files")
    print("\nNext steps:")
    print("1. Run 'cargo update' in each workspace")
    print("2. Run 'cargo check' to verify compatibility")
    print("3. Update Go and Python dependencies separately")

if __name__ == "__main__":
    main()
