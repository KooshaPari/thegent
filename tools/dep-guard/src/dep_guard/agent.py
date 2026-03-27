import os
from typing import List, Dict, Any, Optional
import json
import subprocess
from rich.console import Console

console = Console()

class AgenticAnalyzer:
    """Agentic LLM analyzer using forge -p (minimax) or githubcopilot (gpt-5-mini)."""

    def __init__(self, provider: str = "minimax-m2.7-highspeed"):
        self.provider = provider

    def analyze_suspicious_code(self, code_snippet: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send suspicious code to the LLM agent for deep semantic analysis."""
        prompt = f"""
Analyze the following Python code for malicious behavior, focusing on software supply chain attacks (credential theft, backdoors, exfiltration, obfuscation).

Context:
- Package: {context.get('package_name')}
- Version: {context.get('version')}
- Findings from static triage: {context.get('triage_findings')}

Code Snippet:
```python
{code_snippet}
```

Identify if the code is malicious, suspicious, or benign. Explain your reasoning.
Provide a confidence score (0-1) and a recommended action.
Return JSON format: {{"status": "malicious|suspicious|benign", "reasoning": "...", "confidence": 0.9, "action": "..."}}
"""
        # Call forge -p or similar agent tool
        # This is a mock implementation of the CLI call
        try:
            # Command: forge -p "minimax-m2.7-highspeed" -m "prompt..."
            # For now, we simulate the agentic loop
            console.print(f"[cyan]Invoking Agent ({self.provider}) for deep analysis...[/cyan]")
            
            # Placeholder for actual subprocess call to forge
            # result = subprocess.run(["forge", "-p", self.provider, "-m", prompt], capture_output=True, text=True)
            # return json.loads(result.stdout)

            # Simulated Response
            return {
                "status": "suspicious",
                "reasoning": "Detected potential credential exfiltration via unexpected network call in setup.py.",
                "confidence": 0.85,
                "action": "Manual review required; quarantine package."
            }
        except Exception as e:
            console.print(f"[red]Agent analysis failed:[/red] {e}")
            return {"status": "error", "error": str(e)}

    def analyze_dependency(self, dep_name: str, triage_results: List[Dict[str, Any]], dep_path: str) -> Dict[str, Any]:
        """Perform agentic deep dive on a dependency based on triage results."""
        if not triage_results:
            return {"status": "benign"}

        # Extract code snippets for the most severe findings
        high_severity = [f for f in triage_results if f['severity'] == 'high']
        snippet = ""
        if high_severity:
            target_file = high_severity[0]['file']
            try:
                with open(target_file, "r") as f:
                    snippet = f.read()[:2000] # Limit snippet size
            except:
                snippet = "Could not read file content."

        context = {
            "package_name": dep_name,
            "version": "unknown", # To be extracted from metadata
            "triage_findings": triage_results
        }

        return self.analyze_suspicious_code(snippet, context)
