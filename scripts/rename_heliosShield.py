import os
import stat
from pathlib import Path


def rename_and_replace(root_dir, old_name, new_name):
    print(f"Renaming and replacing '{old_name}' with '{new_name}' in {root_dir}")

    files_to_process = []
    names_to_rename = []

    # 1. Collect all files and directories
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Skip noisy dirs
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                ".git",
                ".venv",
                "coverage",
                "coverage-cache",
                "cache",
                "__pycache__",
                "crytic-export",
                ".git-cache",
                "coverage-unit",
                "var",
                "target",
                "node_modules",
                "dist",
                "artifacts",
            )
        ]

        for file in files:
            file_path = Path(root) / file
            # Check if it's a regular file (not a socket, pipe, etc.)
            try:
                mode = os.lstat(str(file_path)).st_mode
                if stat.S_ISREG(mode):
                    files_to_process.append(file_path)
            except OSError:
                pass

        for dir_name in dirs:
            names_to_rename.append(str(Path(root) / dir_name))

        for file_name in files:
            names_to_rename.append(str(Path(root) / file_name))

    # 2. Replace content in files
    for file_path in files_to_process:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if old_name in content or old_name.capitalize() in content or old_name.upper() in content:
                new_content = content.replace(old_name, new_name)
                new_content = new_content.replace(old_name.capitalize(), new_name.capitalize())
                new_content = new_content.replace(old_name.upper(), new_name.upper())

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated content in {file_path}")
        except UnicodeDecodeError, PermissionError:
            pass

    # 3. Rename files and directories (bottom-up)
    names_to_rename.sort(key=len, reverse=True)
    for path in names_to_rename:
        if not os.path.exists(path):
            continue
        base_name = os.path.basename(path)
        if old_name in base_name:
            new_base_name = base_name.replace(old_name, new_name)
            new_path = str(Path(path).with_name(new_base_name))
            try:
                os.rename(path, new_path)
                print(f"Renamed {path} to {new_path}")
            except OSError as e:
                print(f"Failed to rename {path}: {e}")


if __name__ == "__main__":
    # Rename in heliosShield
    rename_and_replace("../heliosShield", "heliosShield", "heliosShield")
    # Rename in thegent (current dir)
    rename_and_replace(".", "heliosShield", "heliosShield")
