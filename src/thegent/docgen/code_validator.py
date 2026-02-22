"""Implement code example validation for documentation."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CodeExampleValidator:
    """Validate code examples in documentation."""

    def __init__(self, check_syntax: bool = True, run_tests: bool = False) -> None:
        self.check_syntax = check_syntax
        self.run_tests = run_tests

    def validate_code_snippet(self, code: str, language: str = "python") -> tuple[bool, str | None]:
        """Validate a code snippet for syntax errors.

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Tuple of (is_valid, error_message)
        """
        import ast

        if language.lower() == "python":
            try:
                ast.parse(code)
                return True, None
            except SyntaxError as e:
                return False, f"Syntax error in code snippet: {e}"
        else:
            # Add support for other languages later if needed
            return True, None

    def validate_doc_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Validate all code snippets in a documentation file.

        Args:
            file_path: Documentation file path

        Returns:
            List of errors found
        """
        import re

        content = file_path.read_text()
        # Simple regex for markdown code blocks
        pattern = re.compile(r"```(?P<lang>\w+)\n(?P<code>.+?)\n```", re.DOTALL)
        errors = []
        for match in pattern.finditer(content):
            lang = match.group("lang")
            code = match.group("code")
            is_valid, error_message = self.validate_code_snippet(code, lang)
            if not is_valid:
                errors.append(
                    {
                        "file": str(file_path),
                        "lang": lang,
                        "error": error_message,
                        "code_snippet": code[:100] + "..." if len(code) > 100 else code,
                    }
                )
        return errors
