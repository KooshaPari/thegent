"""Unit tests for WSL SID-to-UID identity mapping."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from thegent.infra.wsl_interop import WslInterop


@pytest.mark.unit
def test_map_sid_to_uid_is_stable_across_process_restart_simulation() -> None:
    first_process = WslInterop()
    first_uid = first_process.map_sid_to_uid("S-1-5-21-111")

    second_process = WslInterop()
    restart_uid = second_process.map_sid_to_uid("S-1-5-21-111")

    assert first_uid == restart_uid


def test_map_sid_to_uid_uses_collision_resolution_with_stable_probe() -> None:
    first_process = WslInterop()
    second_process = WslInterop()

    def _fingerprint(sid: str, probe: int) -> int:
        collisions = {
            ("S-1-5-21-alpha", 0): 1_000,
            ("S-1-5-21-alpha", 1): 2_000,
            ("S-1-5-21-beta", 0): 1_000,
            ("S-1-5-21-beta", 1): 2_500,
        }
        return collisions[(sid, probe)]

    with patch.object(WslInterop, "_sid_fingerprint", _fingerprint):
        first_uid = first_process.map_sid_to_uid("S-1-5-21-alpha")
        second_uid = first_process.map_sid_to_uid("S-1-5-21-beta")

        restart_first_uid = second_process.map_sid_to_uid("S-1-5-21-alpha")
        restart_second_uid = second_process.map_sid_to_uid("S-1-5-21-beta")

    assert first_uid == restart_first_uid
    assert second_uid == restart_second_uid
    assert first_uid != second_uid
