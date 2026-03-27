import ast
import os
import re
from typing import List, Dict, Any
from rich.console import Console

console = Console()

class TriageEngine:
    """Static and heuristic triage engine for suspicious patterns."""

    SUSPICIOUS_KEYWORDS = [
        "eval", "exec", "base64.b64decode", "requests.post", "urllib.request.urlopen",
        "socket.connect", "subprocess.Popen", "os.system", "shutil.rmtree"
    ]

    def __init__(self):
        pass

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file for suspicious patterns using AST and heuristics."""
        findings = []
        if not os.path.exists(file_path):
            return findings

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 1. Simple Keyword Heuristics
            for keyword in self.SUSPICIOUS_KEYWORDS:
                if keyword in content:
                    findings.append({
                        "type": "heuristic",
                        "pattern": keyword,
                        "file": file_path,
                        "severity": "medium"
                    })

            # 2. AST Analysis
            tree = ast.parse(content)
            for node in ast.walk(tree):
                # Detect dynamic execution
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec"]:
                        findings.append({
                            "type": "ast",
                            "pattern": f"dynamic_{node.func.id}",
                            "file": file_path,
                            "severity": "high"
                        })
                # Detect obfuscated imports (e.g., __import__('base64'.decode('rot13')))
                # This is a simplified check
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__":
                    findings.append({
                        "type": "ast",
                        "pattern": "dynamic_import",
                        "file": file_path,
                        "severity": "high"
                    })

        except Exception as e:
            console.print(f"[red]Error scanning {file_path}:[/red] {e}")

        return findings

    def triage_dependency(self, dep_path: str) -> List[Dict[str, Any]]:
        """Triage an entire dependency directory."""
        all_findings = []
        # Target sensitive files like .pth, setup.py, and core logic
        target_extensions = [".py", ".pth", ".sh"]
        target_filenames = ["setup.py", "install.py", "preinstall.js", "postinstall.js"]

        for root, _, files in os.walk(dep_path):
            for file in files:
                if file.endswith(tuple(target_extensions)) or file in target_filenames:
                    file_path = os.path.join(root, file)
                    all_findings.extend(self.scan_file(file_path))

        return all_findings
