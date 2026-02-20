"""Input sanitization and validation for security."""

import html
import re
from typing import Any, Dict, List, Optional


class InputSanitizer:
    """Sanitizes and validates user inputs."""

    # Maximum input lengths
    MAX_INPUT_LENGTH = 100000  # 100KB
    MAX_FILENAME_LENGTH = 255
    MAX_URL_LENGTH = 2048

    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bOR\b|\bAND\b).*=.*",
        r"(\bUNION\b|\bSELECT\b).*FROM",
        r"(\bDROP\b|\bDELETE\b|\bINSERT\b).*TABLE",
        r"--.*$",  # SQL comment
        r";.*--",  # SQL injection
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onload\s*=",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`].*\$\(.*\)",  # Command chaining
        r"\$\{.*\}.*",  # Variable expansion
        r"`.*`",  # Backtick execution
    ]

    @staticmethod
    def sanitize_string(value: str, max_length: int | None = None) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            return str(value)

        max_len = max_length or InputSanitizer.MAX_INPUT_LENGTH
        if len(value) > max_len:
            value = value[:max_len]

        # Remove null bytes
        value = value.replace("\x00", "")

        # HTML escape
        value = html.escape(value)

        return value

    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, str | None]:
        """Validate filename safety.

        Returns:
            (is_valid, error_message)
        """
        if len(filename) > InputSanitizer.MAX_FILENAME_LENGTH:
            return False, f"Filename too long (max {InputSanitizer.MAX_FILENAME_LENGTH})"

        # Prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return False, "Filename contains dangerous characters"

        # Prevent null bytes
        if "\x00" in filename:
            return False, "Filename contains null byte"

        return True, None

    @staticmethod
    def detect_sql_injection(value: str) -> bool:
        """Detect SQL injection attempts."""
        value_upper = value.upper()
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_xss(value: str) -> bool:
        """Detect XSS attempts."""
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_command_injection(value: str) -> bool:
        """Detect command injection attempts."""
        for pattern in InputSanitizer.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                return True
        return False

    @staticmethod
    def sanitize_input(value: Any, input_type: str = "string") -> tuple[Any, str | None]:
        """Sanitize input based on type.

        Returns:
            (sanitized_value, error_message)
        """
        if input_type == "string":
            if InputSanitizer.detect_sql_injection(str(value)):
                return None, "SQL injection attempt detected"
            if InputSanitizer.detect_xss(str(value)):
                return None, "XSS attempt detected"
            if InputSanitizer.detect_command_injection(str(value)):
                return None, "Command injection attempt detected"
            return InputSanitizer.sanitize_string(str(value)), None

        if input_type == "filename":
            is_valid, error = InputSanitizer.validate_filename(str(value))
            if not is_valid:
                return None, error
            return str(value), None

        return value, None
