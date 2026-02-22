#!/usr/bin/env python3
"""
Update Go dependencies to latest versions
"""

import re
from pathlib import Path


def update_go_mod(file_path):
    """Update go.mod to use latest versions"""
    try:
        with open(file_path) as f:
            content = f.read()

        original_content = content
        updated = False

        # Update redis/go-redis to latest stable (already done, but ensure it's latest)
        # Check for any beta/pre-release versions and update to stable

        # Pattern: github.com/redis/go-redis/v9 v9.18.0-beta.2 -> v9.18.0
        pattern1 = r"(github\.com/redis/go-redis/v9\s+v)([\d.]+)(-.*)"

        def repl1(m):
            return f"{m.group(1)}{m.group(2)}"

        new_content = re.sub(pattern1, repl1, content)
        if new_content != content:
            content = new_content
            updated = True

        if updated:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"✓ Updated {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False


def main():
    base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush")

    # Find all go.mod files (excluding venv)
    go_mod_files = [f for f in base_path.rglob("go.mod") if ".venv" not in str(f) and "venv" not in str(f)]

    print(f"Found {len(go_mod_files)} go.mod files")
    print("Updating Go dependencies...")

    updated_count = 0
    for go_mod_file in go_mod_files:
        if update_go_mod(go_mod_file):
            updated_count += 1

    print(f"\nUpdated {updated_count} files")
    print("\nNext steps:")
    print("1. Run 'go get -u ./...' in each Go module")
    print("2. Run 'go mod tidy' to clean up")


if __name__ == "__main__":
    main()
