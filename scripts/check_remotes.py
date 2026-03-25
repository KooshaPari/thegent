import subprocess
from pathlib import Path

base_path = Path("/Users/kooshapari/temp-PRODVERCEL/485/")
for entry in base_path.iterdir():
    entry_path = base_path / entry
    if entry_path.is_dir():
        git_path = entry_path / ".git"
        if git_path.is_dir():
            try:
                output = subprocess.check_output(
                    ["git", "-C", str(entry_path), "remote", "-v"], stderr=subprocess.STDOUT, text=True
                )
                if "agslag" in output:
                    print(f"FOUND agslag in {entry_path}")
                    print(output)
            except Exception:
                pass
