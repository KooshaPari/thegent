"""Unit tests for WP-7003/7004: StreamingXMLParser with checkpoint and recovery."""

import pytest

from thegent.contracts.parser import ParserState, StreamingXMLParser


@pytest.mark.unit
class TestStreamingXMLParser:
    """Tests for StreamingXMLParser state machine and recovery."""

    def test_state_transitions_idle_to_tag(self) -> None:
        parser = StreamingXMLParser()
        assert parser.state == ParserState.IDLE

        parser.feed("some text <")
        assert parser.state == ParserState.IN_TAG

        parser.feed("STAT")
        assert parser.state == ParserState.IN_TAG

        parser.feed("US>")
        assert parser.state == ParserState.IN_CONTENT

        parser.feed("completed")
        assert parser.state == ParserState.IN_CONTENT

        parser.feed("</STATUS>")
        assert parser.state == ParserState.IDLE

    def test_feed_returns_delta(self) -> None:
        parser = StreamingXMLParser()
        delta = parser.feed("<STATUS>running</STATUS>")
        assert delta == {"STATUS": "running"}

        # Second feed with same tag doesn't produce delta if unchanged (though parse() overwrites)
        delta = parser.feed("<STATUS>running</STATUS>")
        assert delta == {}

        # New tag produces delta
        delta = parser.feed("<SUMMARY>Working</SUMMARY>")
        assert delta == {"SUMMARY": "Working"}

    def test_checkpoint_and_rollback(self) -> None:
        parser = StreamingXMLParser()
        parser.feed("<STATUS>initial</STATUS>")
        assert parser._committed_tags == {"STATUS": "initial"}

        # Create checkpoint
        cid = parser.commit_checkpoint()
        assert cid is not None

        # Change state
        parser.feed("<STATUS>updated</STATUS>")
        assert parser._committed_tags == {"STATUS": "updated"}

        # Rollback
        ok = parser.rollback()
        assert ok is True
        assert parser._committed_tags == {"STATUS": "initial"}
        assert parser._buffer == ""  # Buffer is cleared on rollback per current impl
        assert parser.state == ParserState.IDLE

    def test_rollback_empty_stack(self) -> None:
        parser = StreamingXMLParser()
        ok = parser.rollback()
        assert ok is False

    def test_partial_tag_no_delta(self) -> None:
        parser = StreamingXMLParser()
        delta = parser.feed("<STATUS>pend")
        assert delta == {}
        assert parser.state == ParserState.IN_CONTENT

        delta = parser.feed("ing</STATUS>")
        assert delta == {"STATUS": "pending"}
        assert parser.state == ParserState.IDLE

    def test_state_listener(self) -> None:
        states = []

        def listener(s):
            states.append(s)

        parser = StreamingXMLParser()
        parser.add_state_listener(listener)

        parser.feed("<")
        assert states == [ParserState.IN_TAG]

        parser.feed("STATUS>")
        assert states == [ParserState.IN_TAG, ParserState.IN_CONTENT]

        parser.feed("ok</STATUS>")
        assert states == [ParserState.IN_TAG, ParserState.IN_CONTENT, ParserState.IDLE]
