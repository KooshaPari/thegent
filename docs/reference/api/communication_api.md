# communication API Reference

> **Source**: `src/thegent/swarm/communication.py`

Swarm Communication

Fast inter-agent communication with <5ms latency.

---

## Message

Message between agents.

---

## SwarmChannel

Fast communication channel for agents.

### Methods

#### SwarmChannel.__init__

```python
__init__(self: Any, max_queue_size: int)
```

---

#### SwarmChannel.average_latency

```python
average_latency(self: Any)
```

Get average message latency in ms.

---

#### SwarmChannel.receive

```python
receive(self: Any, agent_id: str, timeout: float)
```

Receive message for agent (non-blocking by default).

---

#### SwarmChannel.send

```python
send(self: Any, message: Message)
```

Send message to receiver.

---

#### SwarmChannel.stats

```python
stats(self: Any)
```

Get channel statistics.

---

#### SwarmChannel.subscribe

```python
subscribe(self: Any, agent_id: str, callback: Callable[(Any, None)])
```

Subscribe to messages for agent.

---

---

## average_latency

```python
average_latency(self: Any)
```

Get average message latency in ms.

---

## receive

```python
receive(self: Any, agent_id: str, timeout: float)
```

Receive message for agent (non-blocking by default).

---

## send

```python
send(self: Any, message: Message)
```

Send message to receiver.

---

## stats

```python
stats(self: Any)
```

Get channel statistics.

---

## subscribe

```python
subscribe(self: Any, agent_id: str, callback: Callable[(Any, None)])
```

Subscribe to messages for agent.

---

