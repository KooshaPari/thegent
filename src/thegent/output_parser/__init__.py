"""Output parsing utilities for thegent agents and workflows.

This module provides structured output parsing from LLM responses,
including JSON extraction, code block parsing, and validation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, TypeVar, Generic, Protocol, runtime_checkable

T = TypeVar("T")


class ParseError(Exception):
    """Raised when output parsing fails."""
    
    def __init__(self, message: str, raw_output: str | None = None, cause: Exception | None = None):
        super().__init__(message)
        self.raw_output = raw_output
        self.cause = cause


class OutputFormat(Enum):
    """Supported output formats."""
    JSON = auto()
    MARKDOWN = auto()
    CODE_BLOCK = auto()
    PLAIN_TEXT = auto()
    YAML = auto()
    XML = auto()


@dataclass
class ParsedOutput(Generic[T]):
    """Container for parsed output with metadata."""
    content: T
    format: OutputFormat
    raw: str
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class OutputParser(Protocol[T]):
    """Protocol for output parsers."""
    
    def parse(self, output: str) -> ParsedOutput[T]:
        """Parse the given output string."""
        ...
    
    def validate(self, output: T) -> bool:
        """Validate the parsed output."""
        ...


class JSONOutputParser:
    """Parser for JSON output from LLM responses."""
    
    def __init__(self, schema: dict[str, Any] | None = None, strict: bool = False):
        self.schema = schema
        self.strict = strict
    
    def parse(self, output: str) -> ParsedOutput[dict[str, Any]]:
        """Extract and parse JSON from LLM output."""
        # Try to extract JSON from code blocks
        json_str = self._extract_json(output)
        
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON: {e}", raw_output=output, cause=e)
        
        # Validate against schema if provided
        if self.schema and self.strict:
            self._validate_schema(parsed, self.schema)
        
        return ParsedOutput(
            content=parsed,
            format=OutputFormat.JSON,
            raw=output,
            confidence=1.0 if self.schema else 0.9
        )
    
    def validate(self, output: dict[str, Any]) -> bool:
        """Validate parsed JSON output."""
        if self.schema:
            return self._validate_schema(output, self.schema, raise_on_error=False)
        return True
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text, handling code blocks."""
        # Try JSON code blocks first
        patterns = [
            r'```json\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
            r'\{.*\}',
            r'\[.*\]',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                # Return the longest match (most likely complete JSON)
                return max(matches, key=len).strip()
        
        # Return stripped text as fallback
        return text.strip()
    
    def _validate_schema(
        self, 
        data: dict[str, Any], 
        schema: dict[str, Any], 
        raise_on_error: bool = True
    ) -> bool:
        """Validate data against schema."""
        # Basic schema validation
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        for key in required:
            if key not in data:
                error = f"Required field '{key}' missing"
                if raise_on_error:
                    raise ParseError(error)
                return False
        
        return True


class CodeBlockParser:
    """Parser for code blocks in markdown output."""
    
    def __init__(self, language: str | None = None):
        self.language = language
    
    def parse(self, output: str) -> ParsedOutput[list[dict[str, str]]]:
        """Extract code blocks from markdown."""
        pattern = r'```(\w+)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, output, re.DOTALL)
        
        blocks = []
        for lang, code in matches:
            if self.language is None or lang.lower() == self.language.lower():
                blocks.append({
                    "language": lang or "text",
                    "code": code.strip()
                })
        
        return ParsedOutput(
            content=blocks,
            format=OutputFormat.CODE_BLOCK,
            raw=output,
            confidence=0.95 if blocks else 0.5
        )
    
    def validate(self, output: list[dict[str, str]]) -> bool:
        """Validate code blocks."""
        return all("language" in block and "code" in block for block in output)


class MarkdownParser:
    """Parser for structured markdown output."""
    
    def parse(self, output: str) -> ParsedOutput[dict[str, list[str]]]:
        """Parse markdown into sections."""
        sections: dict[str, list[str]] = {"headers": [], "paragraphs": [], "lists": []}
        
        current_section = "paragraphs"
        for line in output.split('\n'):
            if line.startswith('#'):
                sections["headers"].append(line.lstrip('#').strip())
            elif line.strip().startswith(('- ', '* ', '1. ')):
                sections["lists"].append(line.strip())
            elif line.strip():
                sections[current_section].append(line)
        
        return ParsedOutput(
            content=sections,
            format=OutputFormat.MARKDOWN,
            raw=output,
            confidence=0.9
        )
    
    def validate(self, output: dict[str, list[str]]) -> bool:
        """Validate markdown structure."""
        required_keys = {"headers", "paragraphs", "lists"}
        return all(key in output for key in required_keys)


# Convenience functions

def parse_json(output: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Parse JSON from LLM output."""
    parser = JSONOutputParser(schema=schema)
    result = parser.parse(output)
    return result.content


def extract_code_blocks(output: str, language: str | None = None) -> list[dict[str, str]]:
    """Extract code blocks from markdown."""
    parser = CodeBlockParser(language=language)
    result = parser.parse(output)
    return result.content


def parse_markdown_sections(output: str) -> dict[str, list[str]]:
    """Parse markdown into sections."""
    parser = MarkdownParser()
    result = parser.parse(output)
    return result.content


def parse_yaml(output: str) -> dict[str, Any]:
    """Parse YAML output."""
    try:
        import yaml
        return yaml.safe_load(output)
    except ImportError:
        raise ParseError("PyYAML not installed")
    except yaml.YAMLError as e:
        raise ParseError(f"Invalid YAML: {e}", raw_output=output, cause=e)


# Export symbols
__all__ = [
    "ParseError",
    "OutputFormat",
    "ParsedOutput",
    "OutputParser",
    "JSONOutputParser",
    "CodeBlockParser",
    "MarkdownParser",
    "parse_json",
    "extract_code_blocks",
    "parse_markdown_sections",
    "parse_yaml",
]
