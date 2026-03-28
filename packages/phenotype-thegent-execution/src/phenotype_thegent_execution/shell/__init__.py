"""
Shell Execution Module

Configurable shell command execution with:
- Configurable timeouts (default 300s)
- Exponential backoff retry
- Detailed error messages
"""

from .executor import ShellExecutor
from .config import ShellConfig

__all__ = ["ShellExecutor", "ShellConfig"]
