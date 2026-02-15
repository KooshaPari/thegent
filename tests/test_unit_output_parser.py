"""Unit tests for output parser (extract_condensed)."""

from thegent.output_parser import (
    OUTPUT_PARSER_SCHEMA_VERSION,
    PARSE_EMPTY,
    PARSE_OK,
    PARSE_TRUNCATED,
    ParseResult,
    extract_condensed,
    extract_condensed_structured,
    extract_condensed_validated,
)


class TestExtractCondensedEmpty:
    """Empty or whitespace input."""

    def test_empty_string_returns_empty(self) -> None:
        assert extract_condensed("") == ""

    def test_whitespace_only_returns_empty(self) -> None:
        assert extract_condensed("   \n\t  ") == ""


class TestExtractCondensedJsonl:
    """JSONL stream extraction."""

    def test_message_role_assistant_extracts_content(self) -> None:
        stdout = '{"type":"message","role":"assistant","content":"Hello world"}'
        assert extract_condensed(stdout) == "Hello world"

    def test_data_prefix_sse_line_parsed(self) -> None:
        stdout = 'data: {"type":"message","role":"assistant","content":"SSE content"}'
        assert extract_condensed(stdout) == "SSE content"

    def test_completion_final_text_precedence(self) -> None:
        stdout = (
            '{"type":"message","role":"assistant","content":"intermediate"}\n'
            '{"type":"completion","finalText":"Final answer"}'
        )
        assert extract_condensed(stdout) == "Final answer"

    def test_item_content_envelope(self) -> None:
        stdout = '{"type":"x","item":{"type":"message","content":"From item"}}'
        assert extract_condensed(stdout) == "From item"

    def test_top_level_text_field(self) -> None:
        stdout = '{"type":"x","text":"Direct text"}'
        assert extract_condensed(stdout) == "Direct text"


class TestExtractCondensedPlainText:
    """Plain text fallback."""

    def test_plain_text_passthrough(self) -> None:
        stdout = "Simple plain output"
        assert extract_condensed(stdout) == "Simple plain output"

    def test_trailing_noise_stripped(self) -> None:
        stdout = "Actual content\n\nTotal usage est: 100 tokens"
        assert "Actual content" in extract_condensed(stdout)
        assert "Total usage" not in extract_condensed(stdout)

    def test_leading_noise_stripped(self) -> None:
        stdout = "[TIME CONSTRAINT: 60s]\n\nReal output here"
        result = extract_condensed(stdout)
        assert "Real output" in result
        assert "[TIME CONSTRAINT" not in result


class TestExtractCondensedThinkBlocks:
    """Think block stripping."""

    def test_think_block_removed(self) -> None:
        stdout = "Before <think>internal reasoning</think> After"
        result = extract_condensed(stdout)
        assert "Before" in result
        assert "After" in result
        assert "<think>" not in result
        assert "internal reasoning" not in result


class TestExtractCondensedWorkerReport:
    """Worker status report preference."""

    def test_worker_report_preferred(self) -> None:
        stdout = "Preamble\n\n**Summary**\nTask completed successfully.\n\n**Items Done**\n- item 1"
        result = extract_condensed(stdout)
        assert "Task completed" in result or "successfully" in result

    def test_unescape_literal_newlines(self) -> None:
        stdout = '{"type":"message","role":"assistant","content":"Line1\\nLine2"}'
        result = extract_condensed(stdout)
        assert "Line1" in result
        assert "Line2" in result


class TestExtractCondensedStructured:
    """Schema-aware extraction (Chunk 173 follow-up)."""

    def test_returns_text_and_schema_version(self) -> None:
        stdout = "Hello"
        result = extract_condensed_structured(stdout)
        assert result["text"] == "Hello"
        assert result["schema_version"] == OUTPUT_PARSER_SCHEMA_VERSION

    def test_schema_version_constant(self) -> None:
        assert OUTPUT_PARSER_SCHEMA_VERSION == "output-parser-v1"


class TestExtractCondensedValidated:
    """Structural validation with ParseResult and error_class."""

    def test_empty_returns_parse_empty(self) -> None:
        res = extract_condensed_validated("")
        assert res.success is False
        assert res.error_class == PARSE_EMPTY
        assert res.text == ""

    def test_whitespace_returns_parse_empty(self) -> None:
        res = extract_condensed_validated("   \n\t  ")
        assert res.success is False
        assert res.error_class == PARSE_EMPTY

    def test_success_returns_parse_ok(self) -> None:
        res = extract_condensed_validated("Hello world")
        assert res.success is True
        assert res.error_class == PARSE_OK
        assert res.text == "Hello world"
        assert res.schema_version == OUTPUT_PARSER_SCHEMA_VERSION

    def test_jsonl_success_returns_parse_ok(self) -> None:
        stdout = '{"type":"message","role":"assistant","content":"Done"}'
        res = extract_condensed_validated(stdout)
        assert res.success is True
        assert res.error_class == PARSE_OK
        assert res.text == "Done"

    def test_truncated_xml_returns_parse_truncated(self) -> None:
        stdout = "Preamble\n<SUMMARY>In progress"
        res = extract_condensed_validated(stdout)
        assert res.success is False
        assert res.error_class == PARSE_TRUNCATED
        assert res.partial_state is not None
        assert res.partial_state.get("open_tag") == "SUMMARY"
        assert "In progress" in (res.partial_state.get("partial_content") or "")
