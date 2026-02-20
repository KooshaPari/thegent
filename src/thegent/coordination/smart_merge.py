"""Phase 7: Smart Merge implementation.
Includes Mergiraf integration, conflict prediction, and structural merge.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class SmartMerger:
    """Smart merge coordination using Mergiraf and structural aware merges."""

    def __init__(self, mergiraf_path: str = "mergiraf") -> None:
        self.mergiraf_path = mergiraf_path

    def merge_ast(self, base: Path, local: Path, remote: Path, output: Path) -> bool:
        """Perform AST-aware merge using Mergiraf."""
        try:
            cmd = [self.mergiraf_path, "merge", str(base), str(local), str(remote), "-o", str(output)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                logger.info(f"AST merge successful for {output}")
                return True
            logger.warning(f"AST merge failed for {output}: {result.stderr}")
            return False
        except FileNotFoundError:
            logger.error("Mergiraf binary not found. Falling back to standard merge.")
            return False

    def predict_conflicts(self, intents: list[dict[str, Any]]) -> list[str]:
        """Predict potential conflicts based on agent intents."""
        file_map = {}
        conflicts = []
        for intent in intents:
            for file_op in intent.get("file_ops", []):
                path = file_op["path"]
                op_type = file_op["type"]
                if path in file_map:
                    if op_type == "write" or file_map[path] == "write":
                        conflicts.append(path)
                file_map[path] = op_type
        return list(set(conflicts))

    def resolve_imports(self, content: str, lang: str = "python") -> str:
        """Automatically resolve import union conflicts."""
        if lang == "python":
            lines = content.splitlines()
            imports = set()
            others = []
            for line in lines:
                if line.startswith(("import ", "from ")):
                    imports.add(line)
                else:
                    others.append(line)
            return "\n".join(sorted(imports)) + "\n\n" + "\n".join(others)
        return content

    def merge_structural(self, base_file: Path, local_file: Path, remote_file: Path, output_file: Path) -> bool:
        """Perform structural merge for JSON/YAML files."""
        ext = output_file.suffix.lower()
        try:
            if ext == ".json":
                base = json.loads(base_file.read_text())
                local = json.loads(local_file.read_text())
                remote = json.loads(remote_file.read_text())
                merged = self._deep_merge(base, local, remote)
                output_file.write_text(json.dumps(merged, indent=2))
                return True
            if ext in (".yaml", ".yml"):
                base = yaml.safe_load(base_file.read_text())
                local = yaml.safe_load(local_file.read_text())
                remote = yaml.safe_load(remote_file.read_text())
                merged = self._deep_merge(base, local, remote)
                output_file.write_text(yaml.dump(merged, sort_keys=False))
                return True
        except Exception as e:
            logger.error(f"Structural merge failed for {output_file}: {e}")
        return False

    def _deep_merge(self, base: Any, local: Any, remote: Any) -> Any:
        """Simple recursive deep merge (ours-wins on conflict)."""
        if isinstance(local, dict) and isinstance(remote, dict):
            merged = base.copy() if isinstance(base, dict) else {}
            all_keys = set(local.keys()) | set(remote.keys())
            for k in all_keys:
                if k in local and k in remote:
                    merged[k] = self._deep_merge(base.get(k) if isinstance(base, dict) else None, local[k], remote[k])
                elif k in local:
                    merged[k] = local[k]
                else:
                    merged[k] = remote[k]
            return merged
        return local  # Ours wins
