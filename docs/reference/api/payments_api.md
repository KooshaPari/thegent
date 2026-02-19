# payments API Reference

> **Source**: `src/thegent/security/payments.py`

WP-30003: Micro-payment Settlement Bridge.
Interfaces with external payment gateways or blockchains to settle agent-to-agent debts.
Ensures that the virtual agent treasury can be backed by real-world liquidity.

---

## PaymentBridge

Bridges internal agent payments to external settlement providers.

### Methods

#### PaymentBridge.__init__

```python
__init__(self, provider)
```

#### PaymentBridge.initiate_settlement

Settle an agent's accumulated micro-debts with an external provider.

```python
initiate_settlement(self, agent_id, amount)
```

#### PaymentBridge.verify_liquidity

Check if an agent has enough real-world backing for its virtual treasury.

```python
verify_liquidity(self, agent_id)
```

---

## Settlement

Metadata for a settlement operation.

**Inherits from**: `BaseModel`

---

## initiate_settlement

Settle an agent's accumulated micro-debts with an external provider.

```python
initiate_settlement(self, agent_id, amount)
```

---

## verify_liquidity

Check if an agent has enough real-world backing for its virtual treasury.

```python
verify_liquidity(self, agent_id)
```

---

