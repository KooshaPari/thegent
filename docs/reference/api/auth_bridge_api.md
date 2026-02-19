# auth_bridge API Reference

> **Source**: `src/thegent/security/auth_bridge.py`

WP-19003: Enterprise SSO Bridge (OIDC/SAML).
Enables enterprise identity federation for thegent instances.

---

## AuthBridge

Enterprise SSO integration for thegent instances.

### Methods

#### AuthBridge.__init__

```python
__init__(self, config)
```

#### AuthBridge.bridge_saml_response

WP-19003: Simple bridge for SAML assertions (mock).

```python
bridge_saml_response(self, saml_response)
```

---

## SSOConfig

Configuration for SSO (OIDC/SAML).

**Inherits from**: `BaseModel`

---

## bridge_saml_response

WP-19003: Simple bridge for SAML assertions (mock).

```python
bridge_saml_response(self, saml_response)
```

---

