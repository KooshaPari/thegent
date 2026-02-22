"""Unit tests for connector health scoreboard.

# @trace WL-209
"""

from __future__ import annotations

import pytest

from thegent.sync.health import ConnectorHealth, render_health_scoreboard


@pytest.mark.requirement("WL-209")
def test_health_score_penalizes_drift():
    row = ConnectorHealth(connector="github", success_rate=0.95, drift_count=3)
    assert row.score == 80
    assert row.band == "yellow"


@pytest.mark.requirement("WL-209")
def test_render_scoreboard_sorted_by_score_desc():
    rows = [
        ConnectorHealth(connector="linear", success_rate=0.8, drift_count=0),
        ConnectorHealth(connector="github", success_rate=0.99, drift_count=0),
    ]
    lines = render_health_scoreboard(rows)
    assert lines[0].startswith("github")
    assert lines[1].startswith("linear")

