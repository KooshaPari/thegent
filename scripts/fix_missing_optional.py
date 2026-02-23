from pathlib import Path
import os
import re


def fix_missing_optional(root_dir):
    print(f"Fixing missing Optional in {root_dir}")

    for root, _dirs, files in os.walk(root_dir):
        if ".git" in root or ".venv" in root:
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file
            try:
                with file_path.open(encoding="utf-8") as f:
                    content = f.read()

                if "Optional[" in content and "Optional" not in content.split("import")[0]:
                    # Check if it's already imported
                    if re.search(r"from typing import .*Optional", content) or re.search(r"import typing", content):
                        continue

                    # Add import
                    if "from typing import" in content:
                        new_content = re.sub(
                            r"from typing import ([^\n]+)", r"from typing import \1, Optional", content
                        )
                        # Clean up if it adds duplicate
                        new_content = new_content.replace(", Optional, Optional", ", Optional")
                    else:
                        new_content = "from typing import Optional\n" + content

                    file_path.write_text(new_content, encoding="utf-8")
                    print(f"Fixed missing Optional in {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    fix_missing_optional(".")
