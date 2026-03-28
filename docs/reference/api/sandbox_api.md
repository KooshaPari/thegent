# sandbox API Reference

> **Source**: `src/thegent/infra/sandbox.py`

WP-31002: Containerized Agent Sandboxes (Wasm).

Provides lightweight, secure execution environments for untrusted agent code using WebAssembly.
Ensures near-native performance with strict memory and capability isolation.

---

## ResourceUsage

Resource consumption recorded for a sandbox execution.

---

## SandboxConfig

Configuration for a Wasm sandbox.

**Inherits from**: `BaseModel`

---

## SandboxFeature

Optional capabilities that a sandbox may expose.

**Inherits from**: `str, Enum`

---

## SandboxStatus

Lifecycle status of a Wasm sandbox.

**Inherits from**: `str, Enum`

---

## WasmSandbox

Manages secure execution of agent code in a Wasm environment using Extism.

### Methods

#### WasmSandbox.__init__

```python
__init__(self: Any, sandbox_id: str, config: Any)
```

---

#### WasmSandbox.is_available

```python
is_available(self: Any)
```

Return True if the Extism runtime is importable.

---

#### WasmSandbox.run_function

```python
run_function(self: Any, wasm_binary_path: str, function_name: str, input_data: Any, fallback_fn: Any)
```

Execute a function inside the Wasm sandbox.

**Parameters**:

- `wasm_binary_path`: Path to the Wasm binary to load.
- `function_name`: Name of the function to invoke inside the Wasm module.
- `input_data`: Input passed to the Wasm function.
- `fallback_fn`: Optional callable invoked when execution fails. Its
return value is augmented with ``{"fallback": True}`` and returned.

**Returns**: Result dict with ``status``, ``result``/``error``, ``duration_ms``.

---

#### WasmSandbox.shutdown

```python
shutdown(self: Any)
```

Tear down the sandbox and release resources.

---

---

## check_wasm_support

Return a dict indicating which Wasm runtimes are available.

**Returns**: Dict with keys ``extism``, ``wasmer``, ``wasmtime`` mapping to bool.

---

## create_sandboxed_executor

```python
create_sandboxed_executor(config: Any)
```

Create and return a WasmSandbox instance ready for use.

**Parameters**:

- `config`: Optional SandboxConfig. Defaults to SandboxConfig().

**Returns**: Initialised WasmSandbox.

---

## is_available

```python
is_available(self: Any)
```

Return True if the Extism runtime is importable.

---

## run_function

```python
run_function(self: Any, wasm_binary_path: str, function_name: str, input_data: Any, fallback_fn: Any)
```

Execute a function inside the Wasm sandbox.

**Parameters**:

- `wasm_binary_path`: Path to the Wasm binary to load.
- `function_name`: Name of the function to invoke inside the Wasm module.
- `input_data`: Input passed to the Wasm function.
- `fallback_fn`: Optional callable invoked when execution fails. Its
return value is augmented with ``{"fallback": True}`` and returned.

**Returns**: Result dict with ``status``, ``result``/``error``, ``duration_ms``.

---

## shutdown

```python
shutdown(self: Any)
```

Tear down the sandbox and release resources.

---

