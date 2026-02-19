# black_box_proxy API Reference

> **Source**: `src/thegent/agents/black_box_proxy.py`

WP-33001: Universal External Proxy (Donut Bridge).
Provides a generic wrapper to intercept and control I/O for black-box agents.
Supports stdio, HTTP, and LSP interception to enforce thegent's policies externally.

---

## BlackBoxProxy

Universal proxy for external agents.

### Methods

#### BlackBoxProxy.__init__

```python
__init__(self, agent_cmd, policy_enforcer)
```

---

