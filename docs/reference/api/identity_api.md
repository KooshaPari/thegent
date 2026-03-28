# identity API Reference

> **Source**: `src/thegent/agents/identity.py`

Agent identity and sovereignty for thegent (WP-6004).

---

## AgentDIDDocument

W3C-compliant DID Document for an agent.

**Inherits from**: `BaseModel`

---

## AgentIdentity

WP-6004: Manages agent identity, DID, and signing keys.

### Methods

#### AgentIdentity.__init__

```python
__init__(self: Any, agent_name: str, swarm_id: str)
```

---

#### AgentIdentity.get_did_document

```python
get_did_document(self: Any)
```

Return the agent's DID document.

---

#### AgentIdentity.sign

```python
sign(self: Any, data: str)
```

Sign data with agent's private key (mocked).

---

#### AgentIdentity.verify

```python
verify(self: Any, data: str, signature: str)
```

Verify signature with agent's public key (mocked).

---

---

## VerifiableCredential

Proof of agent capability or identity.

**Inherits from**: `BaseModel`

---

## get_did_document

```python
get_did_document(self: Any)
```

Return the agent's DID document.

---

## sign

```python
sign(self: Any, data: str)
```

Sign data with agent's private key (mocked).

---

## sign_actor_payload

```python
sign_actor_payload(actor_id: str, payload: str, signing_key: str)
```

Produce deterministic actor signature for autosync write boundaries.

---

## verify

```python
verify(self: Any, data: str, signature: str)
```

Verify signature with agent's public key (mocked).

---

## verify_actor_signature

Verify actor signature using deterministic hash scheme.

---

