# a2a API Reference

> **Source**: `src/thegent/protocols/a2a.py`

GW-67: Agent-to-Agent (A2A) protocol support.

Implements the A2A message format for inter-agent communication.
Allows thegent to act as an A2A gateway, routing agent messages
to appropriate LLM backends.

A2A message format:
{
  "id": "<uuid>",
  "source_agent": "agent-A",
  "target_agent": "agent-B",
  "message_type": "request" | "response" | "event" | "error",
  "payload": {...},
  "metadata": {...},
  "timestamp": <unix_float>,
  "correlation_id": "<uuid>"  # links request->response
}

# @trace FR-PROTO-067

---

## A2AMessage

Represents an Agent-to-Agent protocol message.

---

## A2ARouter

Routes A2A messages to registered handler functions.

### Methods

#### A2ARouter.__init__

```python
__init__(self: Any)
```

---

#### A2ARouter.list_agents

```python
list_agents(self: Any)
```

Return sorted list of registered target agent names.

---

#### A2ARouter.register

```python
register(self: Any, target_agent: str, handler: Callable[(Any, Any)])
```

Register a handler for messages targeting target_agent.

---

#### A2ARouter.route

```python
route(self: Any, msg: A2AMessage)
```

Route message to registered handlers. Returns list of response messages.

---

#### A2ARouter.unregister

```python
unregister(self: Any, target_agent: str)
```

Remove all handlers for target_agent.

---

---

## a2a_message_from_dict

```python
a2a_message_from_dict(data: dict)
```

Deserialize an A2A message from a dict. Raises ValueError on missing required fields.

---

## a2a_message_to_dict

```python
a2a_message_to_dict(msg: A2AMessage)
```

Serialize an A2A message to a JSON-serializable dict.

---

## create_response

```python
create_response(request: A2AMessage, source_agent: str, payload: dict)
```

Create a response message correlated to a request.

---

## list_agents

```python
list_agents(self: Any)
```

Return sorted list of registered target agent names.

---

## register

```python
register(self: Any, target_agent: str, handler: Callable[(Any, Any)])
```

Register a handler for messages targeting target_agent.

---

## route

```python
route(self: Any, msg: A2AMessage)
```

Route message to registered handlers. Returns list of response messages.

---

## unregister

```python
unregister(self: Any, target_agent: str)
```

Remove all handlers for target_agent.

---

## validate_a2a_message

```python
validate_a2a_message(msg: A2AMessage)
```

Validate an A2A message. Returns list of validation errors (empty = valid).

---

