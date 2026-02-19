# api_evolution API Reference

> **Source**: `src/thegent/tools/api_evolution.py`

WP-10009: Backward-compatible API evolution controls.

Manages version negotiation and compatibility flags for API changes.

---

## APIEvolutionManager

Manages compatibility between different API versions.

### Methods

#### APIEvolutionManager.__init__

```python
__init__(self, current_version)
```

#### APIEvolutionManager.is_feature_enabled

Check if a specific compatibility flag is enabled.

```python
is_feature_enabled(self, flag)
```

#### APIEvolutionManager.negotiate_version

Negotiate the best API version for the client.

```python
negotiate_version(self, client_version)
```

---

## is_feature_enabled

Check if a specific compatibility flag is enabled.

```python
is_feature_enabled(self, flag)
```

---

## negotiate_version

Negotiate the best API version for the client.

```python
negotiate_version(self, client_version)
```

---

