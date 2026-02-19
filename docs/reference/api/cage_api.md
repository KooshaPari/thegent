# cage API Reference

> **Source**: `src/thegent/infra/cage.py`

WP-33003: External Policy Enforcement (The Cage).
Physically restricts black-box agents using runtime isolation and monitoring.
Provides a 'cage' that enforces governance regardless of the agent's internal logic.

---

## AgentCage

A hardened runtime environment for untrusted or black-box agents.

### Methods

#### AgentCage.__init__

```python
__init__(self, cage_id, base_dir)
```

#### AgentCage.cleanup

Tear down the cage and scrub data.

```python
cleanup(self)
```

#### AgentCage.run_command

Execute a command inside the cage with restricted CWD.

```python
run_command(self, cmd)
```

#### AgentCage.setup

Initialize the cage by mirroring only allowed files (Copy-on-Write style).

```python
setup(self, allowed_files)
```

---

## cleanup

Tear down the cage and scrub data.

```python
cleanup(self)
```

---

## run_command

Execute a command inside the cage with restricted CWD.

```python
run_command(self, cmd)
```

---

## setup

Initialize the cage by mirroring only allowed files (Copy-on-Write style).

```python
setup(self, allowed_files)
```

---

