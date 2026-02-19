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
__init__(self, agent_name, swarm_id)
```

#### AgentIdentity.get_did_document

Return the agent's DID document.

```python
get_did_document(self)
```

#### AgentIdentity.sign

Sign data with agent's private key (mocked).

```python
sign(self, data)
```

#### AgentIdentity.verify

Verify signature with agent's public key (mocked).

```python
verify(self, data, signature)
```

---

## VerifiableCredential

Proof of agent capability or identity.

**Inherits from**: `BaseModel`

---

## get_did_document

Return the agent's DID document.

```python
get_did_document(self)
```

---

## sign

Sign data with agent's private key (mocked).

```python
sign(self, data)
```

---

## verify

Verify signature with agent's public key (mocked).

```python
verify(self, data, signature)
```

---

