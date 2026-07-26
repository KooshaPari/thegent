from pathlib import Path

from thegent.mesh.command_share import CommandShareService
from thegent.mesh.contracts import CommandKey, MergeCommand


def test_service_shares_lock_queue_and_events(tmp_path: Path):
    service = CommandShareService(tmp_path / "mesh")
    key = CommandKey("abc")

    assert service.acquire_lock(key, "agent-a") is True
    assert service.acquire_lock(key, "agent-b") is False
    task_id = service.enqueue({"command": "echo hi"}, priority=2, owner_id="agent-a")
    assert service.dequeue("agent-a")["id"] == task_id
    service.ack(task_id)
    assert [event.event_type.value for event in service.events] == [
        "lock.acquired", "task.enqueued", "task.claimed", "task.acked"
    ]


def test_service_release_and_merge_delegate(tmp_path: Path, monkeypatch):
    service = CommandShareService(tmp_path / "mesh")
    key = CommandKey("abc")
    service.acquire_lock(key, "agent-a")
    assert service.release_lock(key, "agent-a") is True
    called = {}
    monkeypatch.setattr(service.merger, "merge", lambda *args, **kwargs: called.setdefault("args", args))
    result = service.merge(MergeCommand("base", "ours", "theirs"), "out")
    assert result == ("base", "ours", "theirs", "out")


def test_events_redact_secrets_and_bound_payload(tmp_path: Path):
    service = CommandShareService(tmp_path / "mesh")
    service.enqueue({"api_key": "secret", "nested": {"password": "pw", "ok": "x" * 500}})
    event = service.events[-1]
    assert event.payload["payload"]["api_key"] == "[REDACTED]"
    assert event.payload["payload"]["nested"]["password"] == "[REDACTED]"
    assert len(event.payload["payload"]["nested"]["ok"]) <= 256
