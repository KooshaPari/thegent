# droid API Reference

> **Source**: `src/thegent/agents/droid.py`

Droid runner - invokes Factory droid exec, OpenAI Codex CLI, or custom CLI backends.

---

## CodexRunner

Runs droids via OpenAI Codex CLI (codex exec).

**Inherits from**: `AgentRunner`

### Methods

#### CodexRunner.__init__

```python
__init__(self, droid_name, droids_dir, codex_cmd, model)
```

#### CodexRunner.run

Run droid via codex exec.

```python
run(self, prompt, cwd, mode, timeout)
```

---

## CustomCliRunner

Runs droids via a generic custom CLI (e.g. claudemax, claudeglm in ~/.local/bin).

**Inherits from**: `AgentRunner`

### Methods

#### CustomCliRunner.__init__

```python
__init__(self, droid_name, droids_dir, custom_cmd, model)
```

#### CustomCliRunner.run

Run droid via custom CLI. Prompt sent via stdin; expects --model and --cd support.

```python
run(self, prompt, cwd, mode, timeout)
```

---

## DroidRunner

Runs droids via Factory droid exec.

**Inherits from**: `AgentRunner`

### Methods

#### DroidRunner.__init__

```python
__init__(self, droid_name, droids_dir, droid_cmd, model)
```

#### DroidRunner.run

Run droid via droid exec.

```python
run(self, prompt, cwd, mode, timeout)
```

---

## get_droid_runner

Factory: return the appropriate droid runner for the given backend.

```python
get_droid_runner(backend, droid_name, droids_dir)
```

---

## run

Run droid via custom CLI. Prompt sent via stdin; expects --model and --cd support.

```python
run(self, prompt, cwd, mode, timeout)
```

---

