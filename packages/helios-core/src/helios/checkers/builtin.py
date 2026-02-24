"""Built-in checkers"""

from pathlib import Path
import re
import json

from helios.checkers.base import Checker, CheckResult, CheckType, register_checker


@register_checker(CheckType.EXIT_CODE)
class ExitCodeChecker(Checker):
    """Check that exit code matches expected"""
    
    def __init__(self, expected_code: int = 0):
        self.expected_code = expected_code
    
    @property
    def check_type(self) -> CheckType:
        return CheckType.EXIT_CODE
    
    async def check(
        self,
        task_id: str,
        output_dir: Path,
        context: dict[str, Any]
    ) -> CheckResult:
        exit_code = context.get("exit_code", 1)
        passed = exit_code == self.expected_code
        
        return CheckResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            message=f"Exit code: {exit_code} (expected: {self.expected_code})",
            details={"exit_code": exit_code, "expected": self.expected_code}
        )


@register_checker(CheckType.OUTPUT)
class OutputChecker(Checker):
    """Check that output matches expected"""
    
    def __init__(
        self,
        expected: str,
        mode: str = "exact"  # exact, contains, regex
    ):
        self.expected = expected
        self.mode = mode
    
    @property
    def check_type(self) -> CheckType:
        return CheckType.OUTPUT
    
    async def check(
        self,
        task_id: str,
        output_dir: Path,
        context: dict[str, Any]
    ) -> CheckResult:
        output = context.get("stdout", "")
        
        if self.mode == "exact":
            passed = output.strip() == self.expected.strip()
        elif self.mode == "contains":
            passed = self.expected in output
        elif self.mode == "regex":
            passed = bool(re.search(self.expected, output))
        else:
            passed = False
        
        return CheckResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            message=f"Output check ({self.mode}): {'passed' if passed else 'failed'}",
            details={"mode": self.mode, "expected": self.expected[:100]}
        )


@register_checker(CheckType.FILE_EXISTS)
class FileExistsChecker(Checker):
    """Check that a file exists"""
    
    def __init__(self, path: str):
        self.path = path
    
    @property
    def check_type(self) -> CheckType:
        return CheckType.FILE_EXISTS
    
    async def check(
        self,
        task_id: str,
        output_dir: Path,
        context: dict[str, Any]
    ) -> CheckResult:
        file_path = output_dir / self.path
        exists = file_path.exists()
        
        return CheckResult(
            passed=exists,
            score=1.0 if exists else 0.0,
            message=f"File exists: {self.path}" if exists else f"File not found: {self.path}",
            details={"path": str(file_path)}
        )


@register_checker(CheckType.REGEX)
class RegexChecker(Checker):
    """Check that output matches a regex pattern"""
    
    def __init__(self, pattern: str, group: int | None = None):
        self.pattern = pattern
        self.group = group
        self.regex = re.compile(pattern)
    
    @property
    def check_type(self) -> CheckType:
        return CheckType.REGEX
    
    async def check(
        self,
        task_id: str,
        output_dir: Path,
        context: dict[str, Any]
    ) -> CheckResult:
        output = context.get("stdout", "")
        match = self.regex.search(output)
        
        passed = match is not None
        
        if passed and self.group is not None:
            captured = match.group(self.group) if match.groups() else None
            message = f"Regex matched, group {self.group}: {captured}"
        else:
            message = f"Regex {'matched' if passed else 'did not match'}: {self.pattern}"
        
        return CheckResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            message=message,
            details={"pattern": self.pattern, "matched": passed}
        )


@register_checker(CheckType.JSON)
class JSONChecker(Checker):
    """Check that output is valid JSON and matches expected"""
    
    def __init__(self, expected: dict | None = None, key: str | None = None):
        self.expected = expected
        self.key = key
    
    @property
    def check_type(self) -> CheckType:
        return CheckType.JSON
    
    async def check(
        self,
        task_id: str,
        output_dir: Path,
        context: dict[str, Any]
    ) -> CheckResult:
        output = context.get("stdout", "")
        
        try:
            data = json.loads(output)
        except json.JSONDecodeError as e:
            return CheckResult(
                passed=False,
                score=0.0,
                message=f"Invalid JSON: {e}",
                details={"error": str(e)}
            )
        
        if self.key:
            if self.key not in data:
                return CheckResult(
                    passed=False,
                    score=0.0,
                    message=f"Key not found: {self.key}",
                    details={"available_keys": list(data.keys())}
                )
            data = data[self.key]
        
        if self.expected:
            passed = data == self.expected
            return CheckResult(
                passed=passed,
                score=1.0 if passed else 0.0,
                message=f"JSON check: {'passed' if passed else 'failed'}",
                details={"expected": self.expected, "actual": data}
            )
        
        return CheckResult(
            passed=True,
            score=1.0,
            message="Valid JSON",
            details={"keys": list(data.keys()) if isinstance(data, dict) else "array"}
        )
