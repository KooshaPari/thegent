from pathlib import Path

import pytest

from thegent.routing.cost_tracker import get_cost_tracker
from thegent.routing.harvest import harvest_routing_metrics


def test_harvest_routing_metrics(tmp_path):
    tracker = get_cost_tracker()
    tracker.clear()

    session_id = "test-session-123"
    tracker.record_request(
        model="gpt-4",
        provider="openai",
        input_tokens=100,
        output_tokens=50,
        latency_ms=500.0,
        cost_usd=0.003,
        session_id=session_id,
    )

    output_path = tmp_path / "metrics.json"
    metrics = harvest_routing_metrics(session_id, output_path=output_path)

    assert metrics["session_id"] == session_id
    assert metrics["total_cost_usd"] == 0.003
    assert metrics["total_tokens"] == 150
    assert metrics["request_count"] == 1
    assert metrics["avg_latency_ms"] == 500.0

    assert output_path.exists()
    import json

    saved = json.loads(output_path.read_text())
    assert saved["session_id"] == session_id
    assert saved["total_cost_usd"] == 0.003
