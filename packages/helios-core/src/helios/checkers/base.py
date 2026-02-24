"""Checker system - Verification and validation"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any
from pathlib import Path


class CheckType(Enum):
    """Types of checks supported"""
    EXIT_CODE = "exit_code"
    OUTPUT = "output"
    FILE_EXISTS = "file_exists"
    FILE_CONTENT = "file_content"
    REGEX = "regex"
    JSON = "json"
    BASH = "bash"
    PYTEST = "pytest"
    LLM_JUDGE = "llm_judge"
    CUSTOM = "custom"


@dataclass
class CheckResult:
    """Result from a checker"""
    passed: bool
    score: float  # 0.0 - 1.0
    message: str
    details: dict[str, Any] | None = None


class Checker(ABC):
    """Abstract base class for checkers"""
    
    @property
    @abstractmethod
    def check_type(self) -> CheckType:
        """Return the type of check this checker performs"""
        ...
    
    @abstractmethod
    async def check(
        self,
        task_id: str,
        output_dir: Path,
        context: dict[str, Any]
    ) -> CheckResult:
        """Run the check"""
        ...


class CheckerRegistry:
    """Registry of all available checkers"""
    
    _checkers: dict[CheckType, type[Checker]] = {}
    
    @classmethod
    def register(cls, check_type: CheckType, checker_class: type[Checker]):
        """Register a checker class"""
        cls._checkers[check_type] = checker_class
    
    @classmethod
    def get(cls, check_type: CheckType) -> type[Checker]:
        """Get a checker class by type"""
        if check_type not in cls._checkers:
            raise KeyError(f"Checker for '{check_type.value}' not found")
        return cls._checkers[check_type]
    
    @classmethod
    def list(cls) -> list[CheckType]:
        """List all registered checker types"""
        return list(cls._checkers.keys())


def register_checker(check_type: CheckType):
    """Decorator to register a checker class"""
    def decorator(checker_class: type[Checker]):
        CheckerRegistry.register(check_type, checker_class)
        return checker_class
    return decorator
