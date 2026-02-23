"""Tests for WL-177: Edge Case Parser Unit Tests.

@pytest.mark.requirement("WL-177")
"""

from __future__ import annotations

import pytest

from thegent.integrations.parser_edge_cases import EdgeCaseParser, ParseResult


class TestParseResult:
    """Test the ParseResult dataclass."""

    @pytest.mark.requirement("WL-177")
    def test_parse_result_creation_success(self) -> None:
        """Test creating a ParseResult for successful parsing."""
        result = ParseResult(raw='{"key": "value"}', parsed={"key": "value"})
        assert result.raw == '{"key": "value"}'
        assert result.parsed == {"key": "value"}
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_result_creation_failure(self) -> None:
        """Test creating a ParseResult for failed parsing."""
        result = ParseResult(
            raw="invalid json",
            parsed=None,
            error="Expecting value: line 1 column 1",
        )
        assert result.raw == "invalid json"
        assert result.parsed is None
        assert result.error == "Expecting value: line 1 column 1"

    @pytest.mark.requirement("WL-177")
    def test_parse_result_default_error_none(self) -> None:
        """Test that error defaults to None."""
        result = ParseResult(raw='{"a": 1}', parsed={"a": 1})
        assert result.error is None


class TestEdgeCaseParser:
    """Test the EdgeCaseParser."""

    @pytest.mark.requirement("WL-177")
    def test_parser_initialization(self) -> None:
        """Test parser initialization."""
        parser = EdgeCaseParser()
        assert parser is not None

    @pytest.mark.requirement("WL-177")
    def test_parse_valid_json(self) -> None:
        """Test parsing valid JSON."""
        parser = EdgeCaseParser()
        result = parser.parse('{"key": "value"}')
        assert result.parsed == {"key": "value"}
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_valid_json_complex(self) -> None:
        """Test parsing complex valid JSON."""
        parser = EdgeCaseParser()
        json_str = '{"items": [1, 2, 3], "name": "test", "nested": {"a": "b"}}'
        result = parser.parse(json_str)
        assert result.parsed == {
            "items": [1, 2, 3],
            "name": "test",
            "nested": {"a": "b"},
        }
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_invalid_json_missing_quote(self) -> None:
        """Test parsing invalid JSON with missing quote."""
        parser = EdgeCaseParser()
        result = parser.parse('{"key: "value"}')
        assert result.parsed is None
        assert result.error is not None

    @pytest.mark.requirement("WL-177")
    def test_parse_invalid_json_trailing_comma(self) -> None:
        """Test parsing invalid JSON with trailing comma."""
        parser = EdgeCaseParser()
        result = parser.parse('{"key": "value",}')
        assert result.parsed is None
        assert result.error is not None

    @pytest.mark.requirement("WL-177")
    def test_parse_empty_string(self) -> None:
        """Test parsing empty string."""
        parser = EdgeCaseParser()
        result = parser.parse("")
        assert result.parsed is None
        assert result.error is not None

    @pytest.mark.requirement("WL-177")
    def test_parse_whitespace_only(self) -> None:
        """Test parsing whitespace-only string."""
        parser = EdgeCaseParser()
        result = parser.parse("   \n  \t  ")
        assert result.parsed is None
        assert result.error is not None

    @pytest.mark.requirement("WL-177")
    def test_parse_null_value(self) -> None:
        """Test parsing JSON null value."""
        parser = EdgeCaseParser()
        result = parser.parse("null")
        assert result.parsed is None
        assert result.error is None  # null is valid JSON

    @pytest.mark.requirement("WL-177")
    def test_parse_boolean_value(self) -> None:
        """Test parsing JSON boolean value."""
        parser = EdgeCaseParser()
        result = parser.parse("true")
        assert result.parsed is True
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_number_value(self) -> None:
        """Test parsing JSON number value."""
        parser = EdgeCaseParser()
        result = parser.parse("42")
        assert result.parsed == 42
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_string_value(self) -> None:
        """Test parsing JSON string value."""
        parser = EdgeCaseParser()
        result = parser.parse('"hello"')
        assert result.parsed == "hello"
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_array_value(self) -> None:
        """Test parsing JSON array value."""
        parser = EdgeCaseParser()
        result = parser.parse("[1, 2, 3]")
        assert result.parsed == [1, 2, 3]
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_preserves_raw_input(self) -> None:
        """Test that raw input is preserved."""
        parser = EdgeCaseParser()
        raw = '{"key": "value"}'
        result = parser.parse(raw)
        assert result.raw == raw

    @pytest.mark.requirement("WL-177")
    def test_parse_many_all_valid(self) -> None:
        """Test parse_many with all valid inputs."""
        parser = EdgeCaseParser()
        inputs = ['{"a": 1}', '{"b": 2}', '{"c": 3}']
        results = parser.parse_many(inputs)
        assert len(results) == 3
        assert all(r.error is None for r in results)
        assert [r.parsed for r in results] == [{"a": 1}, {"b": 2}, {"c": 3}]

    @pytest.mark.requirement("WL-177")
    def test_parse_many_with_failures(self) -> None:
        """Test parse_many with some invalid inputs."""
        parser = EdgeCaseParser()
        inputs = ['{"a": 1}', "invalid", '{"c": 3}']
        results = parser.parse_many(inputs)
        assert len(results) == 3
        assert results[0].error is None
        assert results[1].error is not None
        assert results[2].error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_many_empty_list(self) -> None:
        """Test parse_many with empty list."""
        parser = EdgeCaseParser()
        results = parser.parse_many([])
        assert len(results) == 0

    @pytest.mark.requirement("WL-177")
    def test_failures_filters_correctly(self) -> None:
        """Test failures method filters out successful parses."""
        parser = EdgeCaseParser()
        inputs = ['{"a": 1}', "invalid", '{"c": 3}', "bad json"]
        results = parser.parse_many(inputs)
        failures = EdgeCaseParser.failures(results)
        assert len(failures) == 2
        assert all(r.parsed is None for r in failures)

    @pytest.mark.requirement("WL-177")
    def test_failures_all_valid(self) -> None:
        """Test failures returns empty list when all valid."""
        parser = EdgeCaseParser()
        inputs = ['{"a": 1}', '{"b": 2}', '{"c": 3}']
        results = parser.parse_many(inputs)
        failures = EdgeCaseParser.failures(results)
        assert len(failures) == 0

    @pytest.mark.requirement("WL-177")
    def test_failures_all_invalid(self) -> None:
        """Test failures returns all when all invalid."""
        parser = EdgeCaseParser()
        inputs = ["bad1", "bad2", "bad3"]
        results = parser.parse_many(inputs)
        failures = EdgeCaseParser.failures(results)
        assert len(failures) == 3

    @pytest.mark.requirement("WL-177")
    def test_failures_empty_list(self) -> None:
        """Test failures with empty list."""
        failures = EdgeCaseParser.failures([])
        assert len(failures) == 0

    @pytest.mark.requirement("WL-177")
    def test_parse_special_characters_in_string(self) -> None:
        """Test parsing JSON with special characters."""
        parser = EdgeCaseParser()
        result = parser.parse('{"key": "hello\\nworld"}')
        assert result.parsed == {"key": "hello\nworld"}
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_unicode_characters(self) -> None:
        """Test parsing JSON with unicode characters."""
        parser = EdgeCaseParser()
        result = parser.parse('{"emoji": "\\u263A"}')
        assert result.error is None

    @pytest.mark.requirement("WL-177")
    def test_parse_deeply_nested(self) -> None:
        """Test parsing deeply nested JSON."""
        parser = EdgeCaseParser()
        json_str = '{"a": {"b": {"c": {"d": {"e": "value"}}}}}'
        result = parser.parse(json_str)
        assert result.parsed is not None
        assert result.error is None
