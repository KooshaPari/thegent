"""Tests for WL-198: End-to-End Replay Fixture.

Verifies event recording, replay, and management.

# @trace WL-198
"""

from __future__ import annotations

import pytest

from thegent.integrations.e2e_replay_fixture import E2EReplayFixture, ReplayEvent


@pytest.mark.requirement("WL-198")
class TestReplayEvent:
    """WL-198: ReplayEvent dataclass."""

    def test_replay_event_creation(self):
        """Create a replay event."""
        event = ReplayEvent(
            event_id="evt_1",
            event_type="request",
            payload={"url": "/api", "method": "GET"},
        )

        assert event.event_id == "evt_1"
        assert event.event_type == "request"
        assert event.payload == {"url": "/api", "method": "GET"}

    def test_replay_event_empty_payload(self):
        """Create event with empty payload."""
        event = ReplayEvent(event_id="evt_2", event_type="log", payload={})

        assert event.payload == {}

    def test_replay_event_nested_payload(self):
        """Create event with nested payload."""
        payload = {
            "data": {
                "nested": {"deep": "value"},
                "list": [1, 2, 3],
            }
        }
        event = ReplayEvent(event_id="evt_3", event_type="complex", payload=payload)

        assert event.payload["data"]["nested"]["deep"] == "value"


@pytest.mark.requirement("WL-198")
class TestE2EReplayFixtureRecord:
    """WL-198: Recording events."""

    def test_record_single_event(self):
        """Record a single event."""
        fixture = E2EReplayFixture()

        event = fixture.record("request", {"url": "/api"})

        assert event.event_type == "request"
        assert event.payload == {"url": "/api"}
        assert event.event_id == "event_1"

    def test_record_generates_incremental_ids(self):
        """Record generates incrementing event IDs."""
        fixture = E2EReplayFixture()

        evt1 = fixture.record("event1", {})
        evt2 = fixture.record("event2", {})
        evt3 = fixture.record("event3", {})

        assert evt1.event_id == "event_1"
        assert evt2.event_id == "event_2"
        assert evt3.event_id == "event_3"

    def test_record_empty_event_type_raises(self):
        """Reject empty event type."""
        fixture = E2EReplayFixture()

        with pytest.raises(ValueError, match="event_type cannot be empty"):
            fixture.record("", {})

    def test_record_whitespace_event_type_raises(self):
        """Reject whitespace-only event type."""
        fixture = E2EReplayFixture()

        with pytest.raises(ValueError, match="event_type cannot be empty"):
            fixture.record("   ", {})

    def test_record_none_payload_becomes_empty_dict(self):
        """None payload becomes empty dict."""
        fixture = E2EReplayFixture()

        event = fixture.record("test", None)

        assert event.payload == {}

    def test_record_multiple_events(self):
        """Record multiple events in sequence."""
        fixture = E2EReplayFixture()

        fixture.record("event1", {"a": 1})
        fixture.record("event2", {"b": 2})
        fixture.record("event3", {"c": 3})

        events = fixture.events()
        assert len(events) == 3


@pytest.mark.requirement("WL-198")
class TestE2EReplayFixtureReplay:
    """WL-198: Replaying events."""

    def test_replay_empty_fixture(self):
        """Replay with no recorded events."""
        fixture = E2EReplayFixture()

        call_count = {"n": 0}

        def handler(event):
            call_count["n"] += 1

        count = fixture.replay(handler)

        assert count == 0
        assert call_count["n"] == 0

    def test_replay_single_event(self):
        """Replay single recorded event."""
        fixture = E2EReplayFixture()
        fixture.record("test", {"val": 42})

        received_events = []

        def handler(event):
            received_events.append(event)

        count = fixture.replay(handler)

        assert count == 1
        assert len(received_events) == 1
        assert received_events[0].event_type == "test"
        assert received_events[0].payload == {"val": 42}

    def test_replay_multiple_events_in_order(self):
        """Replay multiple events in recording order."""
        fixture = E2EReplayFixture()
        fixture.record("first", {"order": 1})
        fixture.record("second", {"order": 2})
        fixture.record("third", {"order": 3})

        order = []

        def handler(event):
            order.append(event.payload["order"])

        count = fixture.replay(handler)

        assert count == 3
        assert order == [1, 2, 3]

    def test_replay_handler_called_for_each_event(self):
        """Handler is called for each recorded event."""
        fixture = E2EReplayFixture()
        fixture.record("a", {})
        fixture.record("b", {})
        fixture.record("c", {})

        call_count = {"n": 0}

        def handler(event):
            call_count["n"] += 1

        fixture.replay(handler)

        assert call_count["n"] == 3

    def test_replay_exception_in_handler_propagates(self):
        """Exception in handler propagates during replay."""
        fixture = E2EReplayFixture()
        fixture.record("test", {})

        def failing_handler(event):
            raise ValueError("Handler error")

        with pytest.raises(ValueError, match="Handler error"):
            fixture.replay(failing_handler)

    def test_replay_exception_stops_processing(self):
        """Exception stops further event processing."""
        fixture = E2EReplayFixture()
        fixture.record("event1", {})
        fixture.record("event2", {})
        fixture.record("event3", {})

        processed = []

        def failing_handler(event):
            if len(processed) == 1:
                raise RuntimeError("Stop here")
            processed.append(event.event_id)

        with pytest.raises(RuntimeError):
            fixture.replay(failing_handler)

        assert len(processed) == 1


@pytest.mark.requirement("WL-198")
class TestE2EReplayFixtureEvents:
    """WL-198: Retrieving recorded events."""

    def test_events_empty_fixture(self):
        """Get events from empty fixture."""
        fixture = E2EReplayFixture()

        events = fixture.events()

        assert events == []

    def test_events_returns_list_of_recorded_events(self):
        """Events returns all recorded events."""
        fixture = E2EReplayFixture()
        evt1 = fixture.record("type1", {"data": 1})
        evt2 = fixture.record("type2", {"data": 2})

        events = fixture.events()

        assert len(events) == 2
        assert events[0] is evt1
        assert events[1] is evt2

    def test_events_returns_in_recording_order(self):
        """Events are returned in recording order."""
        fixture = E2EReplayFixture()
        fixture.record("first", {})
        fixture.record("second", {})
        fixture.record("third", {})

        events = fixture.events()

        assert [e.event_type for e in events] == ["first", "second", "third"]

    def test_events_includes_complete_data(self):
        """Events include all payload data."""
        fixture = E2EReplayFixture()
        payload = {"user": "alice", "action": "login", "timestamp": 12345}
        fixture.record("auth", payload)

        events = fixture.events()

        assert events[0].payload == payload


@pytest.mark.requirement("WL-198")
class TestE2EReplayFixtureClear:
    """WL-198: Clearing recorded events."""

    def test_clear_removes_all_events(self):
        """Clear removes all recorded events."""
        fixture = E2EReplayFixture()
        fixture.record("event1", {})
        fixture.record("event2", {})

        fixture.clear()

        assert fixture.events() == []

    def test_clear_resets_event_counter(self):
        """Clear resets event ID counter."""
        fixture = E2EReplayFixture()
        fixture.record("event1", {})
        fixture.clear()

        evt = fixture.record("event2", {})

        assert evt.event_id == "event_1"  # Restarted from 1

    def test_clear_allows_rerecording(self):
        """Can record events again after clear."""
        fixture = E2EReplayFixture()
        fixture.record("old", {})
        fixture.clear()
        fixture.record("new", {})

        events = fixture.events()

        assert len(events) == 1
        assert events[0].event_type == "new"

    def test_clear_on_empty_fixture(self):
        """Clear on empty fixture does nothing."""
        fixture = E2EReplayFixture()

        fixture.clear()

        assert fixture.events() == []


@pytest.mark.requirement("WL-198")
class TestE2EReplayFixtureIntegration:
    """WL-198: Integration scenarios."""

    def test_record_replay_cycle(self):
        """Full record-replay cycle."""
        fixture = E2EReplayFixture()

        # Record
        fixture.record("http_request", {"method": "GET", "url": "/users"})
        fixture.record("http_response", {"status": 200, "body": "data"})

        # Replay
        results = []

        def collector(event):
            results.append({"type": event.event_type, "payload": event.payload})

        count = fixture.replay(collector)

        assert count == 2
        assert results[0]["type"] == "http_request"
        assert results[1]["type"] == "http_response"

    def test_multiple_replay_runs(self):
        """Can replay same events multiple times."""
        fixture = E2EReplayFixture()
        fixture.record("event", {"id": 1})

        call_counts = {"first": 0, "second": 0}

        def first_handler(event):
            call_counts["first"] += 1

        def second_handler(event):
            call_counts["second"] += 1

        fixture.replay(first_handler)
        fixture.replay(second_handler)

        assert call_counts["first"] == 1
        assert call_counts["second"] == 1
