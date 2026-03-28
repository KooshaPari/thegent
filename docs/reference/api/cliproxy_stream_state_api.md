# cliproxy_stream_state API Reference

> **Source**: `src/thegent/cliproxy_stream_state.py`

## ResponsesStreamState

Stateful transformer: Chat Completions SSE -> Responses API v2 event sequence.

Codex 0.104.0 requires this exact 8-event sequence:
  response.created           (once, carries response.id)
  response.output_item.added (once)
  response.content_part.added (once)
  response.output_text.delta (repeating, per token)
  response.output_text.done  (once)
  response.content_part.done (once)
  response.output_item.done  (once)
  response.completed         (once, full response object + usage)

### Methods

#### ResponsesStreamState.__init__

```python
__init__(self: Any, model: str)
```

---

#### ResponsesStreamState.closing_events

```python
closing_events(self: Any)
```

Events after all deltas: done, part done, item done, response.completed.

OR-14: Includes usage.cost in response.completed when available from
OpenRouter's total_cost field in the upstream usage object.

---

#### ResponsesStreamState.delta_event

```python
delta_event(self: Any, text: str)
```

One response.output_text.delta event per token.

---

#### ResponsesStreamState.preamble_events

```python
preamble_events(self: Any)
```

Events emitted before any delta: created, output_item.added, content_part.added.

---

#### ResponsesStreamState.set_usage

```python
set_usage(self: Any, usage: dict[(str, Any)])
```

---

#### ResponsesStreamState.tool_call_closing_events

```python
tool_call_closing_events(self: Any)
```

Emit done events for all accumulated tool calls.

---

#### ResponsesStreamState.tool_call_delta_events

```python
tool_call_delta_events(self: Any, tool_calls: list[dict[(str, Any)]])
```

Convert Chat Completions tool_call deltas to Responses API events — GW-07.

---

---

## closing_events

```python
closing_events(self: Any)
```

Events after all deltas: done, part done, item done, response.completed.

OR-14: Includes usage.cost in response.completed when available from
OpenRouter's total_cost field in the upstream usage object.

---

## delta_event

```python
delta_event(self: Any, text: str)
```

One response.output_text.delta event per token.

---

## preamble_events

```python
preamble_events(self: Any)
```

Events emitted before any delta: created, output_item.added, content_part.added.

---

## set_usage

```python
set_usage(self: Any, usage: dict[(str, Any)]) -> None
```

---

## tool_call_closing_events

```python
tool_call_closing_events(self: Any)
```

Emit done events for all accumulated tool calls.

---

## tool_call_delta_events

```python
tool_call_delta_events(self: Any, tool_calls: list[dict[(str, Any)]])
```

Convert Chat Completions tool_call deltas to Responses API events — GW-07.

---

