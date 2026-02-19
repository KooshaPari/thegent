# sandbox API Reference

> **Source**: `src/thegent/infra/sandbox.py`

WP-31002: Containerized Agent Sandboxes (Wasm).
Provides lightweight, secure execution environments for untrusted agent code using WebAssembly.
Ensures near-native performance with strict memory and capability isolation.

---

## SandboxConfig

Configuration for a Wasm sandbox.

**Inherits from**: `BaseModel`

---

## WasmSandbox

Manages secure execution of agent code in a Wasm environment.

### Methods

#### WasmSandbox.__init__

```python
__init__(self, sandbox_id, config)
```

#### WasmSandbox.run_binary

Execute a function inside the Wasm sandbox.

```python
run_binary(self, wasm_binary_path, function_name, args)
```

#### WasmSandbox.shutdown

Tear down the sandbox and release resources.

```python
shutdown(self)
```

---

## run_binary

Execute a function inside the Wasm sandbox.

```python
run_binary(self, wasm_binary_path, function_name, args)
```

---

## shutdown

Tear down the sandbox and release resources.

```python
shutdown(self)
```

---

