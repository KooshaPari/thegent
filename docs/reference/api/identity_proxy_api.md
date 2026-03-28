# identity_proxy API Reference

> **Source**: `src/thegent/infra/identity_proxy.py`

SSH Identity Proxy Bridge.

Allows isolated L2 agents to use host SSH keys for Git operations
without exposing private keys to the guest environment.

---

## SSHIdentityProxy

Acts as a secure bridge between the host's SSH agent and isolated L2 agents.

Uses Unix Domain Sockets to forward signing requests.

### Methods

#### SSHIdentityProxy.__init__

```python
__init__(self: Any, proxy_socket_path: Path)
```

---

#### SSHIdentityProxy.get_env

```python
get_env(self: Any)
```

Return the environment variable for L2 agents to use this proxy.

---

#### SSHIdentityProxy.require_actor_identity

Require and validate actor identity metadata for write operations.

---

#### SSHIdentityProxy.start

```python
start(self: Any)
```

Start the proxy server.

---

#### SSHIdentityProxy.stop

```python
stop(self: Any)
```

Stop the proxy server.

---

---

## get_env

```python
get_env(self: Any)
```

Return the environment variable for L2 agents to use this proxy.

---

## require_actor_identity

Require and validate actor identity metadata for write operations.

---

## start

```python
start(self: Any)
```

Start the proxy server.

---

## stop

```python
stop(self: Any)
```

Stop the proxy server.

---

