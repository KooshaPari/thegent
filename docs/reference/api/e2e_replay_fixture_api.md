# e2e_replay_fixture API Reference

> **Source**: `src/thegent/integrations/e2e_replay_fixture.py`

End-to-end replay fixture.

Implements event recording and replay for end-to-end testing, enabling
deterministic test execution with recorded event sequences.

# @trace WL-198

---

## E2EReplayFixture

Records and replays events for end-to-end testing.

### Methods

#### E2EReplayFixture.__init__

```python
__init__(self: Any)
```

Initialize the replay fixture.

---

#### E2EReplayFixture.clear

```python
clear(self: Any)
```

Clear all recorded events.

---

#### E2EReplayFixture.events

```python
events(self: Any)
```

Get all recorded events.

**Returns**: List of ReplayEvent objects in recording order.

---

#### E2EReplayFixture.record

```python
record(self: Any, event_type: str, payload: dict[(str, Any)])
```

Record an event for later replay.

**Parameters**:

- `event_type`: Type/category of the event.
- `payload`: Data associated with the event.

**Returns**: The recorded ReplayEvent.

---

#### E2EReplayFixture.replay

```python
replay(self: Any, handler: Callable[(Any, None)])
```

Replay all recorded events through a handler.

**Parameters**:

- `handler`: Callable that processes each ReplayEvent.

**Returns**: Number of events replayed.

---

---

## ReplayEvent

A recorded event with metadata for replay.

---

## clear

```python
clear(self: Any)
```

Clear all recorded events.

---

## events

```python
events(self: Any)
```

Get all recorded events.

**Returns**: List of ReplayEvent objects in recording order.

---

## record

```python
record(self: Any, event_type: str, payload: dict[(str, Any)])
```

Record an event for later replay.

**Parameters**:

- `event_type`: Type/category of the event.
- `payload`: Data associated with the event.

**Returns**: The recorded ReplayEvent.

**Raises**:

- `ValueError`: If event_type is empty.

---

## replay

```python
replay(self: Any, handler: Callable[(Any, None)])
```

Replay all recorded events through a handler.

**Parameters**:

- `handler`: Callable that processes each ReplayEvent.

**Returns**: Number of events replayed.

---

