"""
Shared CLI Utilities

Provides reusable CLI patterns across the Phenotype ecosystem.
"""
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class CLICommand:
    """Represents a CLI command."""
    name: str
    description: str
    aliases: List[str]


class CLIFormatter:
    """Formats CLI output consistently."""
    
    @staticmethod
    def success(message: str) -> str:
        return f"✓ {message}"
    
    @staticmethod
    def error(message: str) -> str:
        return f"✗ {message}"
    
    @staticmethod
    def warning(message: str) -> str:
        return f"⚠ {message}"
    
    @staticmethod
    def info(message: str) -> str:
        return f"ℹ {message}"
