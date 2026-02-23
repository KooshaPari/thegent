#!/usr/bin/env python3
"""Reusable helpers for agent workflows (ax-improve-reusable-helpers)."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


def normalize_path(path: str) -> Path:
    """Normalize path to absolute, resolving home and project root."""
    p = Path(path).expanduser()
    if not p.is_absolute():
        # Assume relative to project root
        project_root = Path.cwd()
        while project_root.parent != project_root:
            if (project_root / ".git").exists():
                break
            project_root = project_root.parent
        p = (project_root / p).resolve()
    return p


def read_file_optimized(path: Path, offset: int = 0, limit: Optional[int] = None) -> str:
    """Read a file with offset and limit to reduce tool call size."""
    if not path.exists():
        return ""
    
    with open(path, "r", errors="replace") as f:
        if offset > 0:
            for _ in range(offset):
                next(f, None)
        
        if limit is not None:
            lines = []
            for _ in range(limit):
                line = next(f, None)
                if line is None:
                    break
                lines.append(line)
            return "".join(lines)
        else:
            return f.read()


def batch_read_files(paths: List[Path]) -> Dict[str, str]:
    """Read multiple files in one batch."""
    results = {}
    for p in paths:
        results[str(p)] = read_file_optimized(p)
    return results


def run_command(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a shell command safely."""
    try:
        return subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
    except subprocess.TimeoutExpired as e:
        # Return a simulated result for timeout
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=124,
            stdout=e.stdout.decode() if e.stdout else "",
            stderr=e.stderr.decode() if e.stderr else "Command timed out"
        )


def log_friction(task_id: str, category: str, friction_type: str, description: str, solution: str):
    """Log a friction point to docs/research/FRICTION_LOG.md."""
    log_path = Path("thegent/docs/research/FRICTION_LOG.md")
    if not log_path.exists():
        return
    
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    
    entry = f"""
### {task_id}-{timestamp[:10]}

- **Category**: {category.upper()}
- **Type**: {friction_type.title()}
- **Location**: Agent auto-logged
- **Description**: {description}
- **Solution**: {solution}
- **Priority**: P2
- **Timestamp**: {timestamp}
"""
    with open(log_path, "a") as f:
        f.write(entry)


if __name__ == "__main__":
    # Example usage
    print(f"Project root normalized path: {normalize_path('.')}")
