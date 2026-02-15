"""CI architecture guardrails (G-KD-05): boundary checks, contract conformance."""

import subprocess
import sys
from pathlib import Path


def test_check_boundaries_passes() -> None:
    """Run scripts/check_boundaries.py; must exit 0."""
    script = Path(__file__).resolve().parent.parent / "scripts" / "check_boundaries.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=script.parent.parent)
    assert result.returncode == 0, f"Boundary check failed:\n{result.stdout}\n{result.stderr}"
