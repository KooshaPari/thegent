# harness_base API Reference

> **Source**: `src/thegent/adapters/harness_base.py`

Abstract base class for unified harness pattern (Claude/Codex shared behavior).

---

## HarnessBase

Abstract harness base with common binary discovery, config isolation, and env setup.

**Inherits from**: `ABC`

### Methods

#### HarnessBase.__init__

```python
__init__(self: Any)
```

Initialize harness with settings.

---

#### HarnessBase.ensure_binary_installed

```python
ensure_binary_installed(self: Any, suggest_alt: bool, require_native: bool)
```

Auto-install binary via brew/bun/etc. or raise. Returns path.

---

#### HarnessBase.ensure_config_isolation

```python
ensure_config_isolation(self: Any, config_dir: Path)
```

Ensure isolated config directory (subclasses override as needed).

---

#### HarnessBase.ensure_proxy_running

```python
ensure_proxy_running(self: Any)
```

Ensure cliproxy is running (subclasses override as needed).

---

#### HarnessBase.fetch_metrics

```python
fetch_metrics(self: Any)
```

Fetch provider metrics for GLM/etc routing. Default: empty.

---

#### HarnessBase.find_binary

```python
find_binary(self: Any, require_native: bool)
```

Discover binary path. Can be overridden by subclass.

---

#### HarnessBase.get_binary_name

```python
get_binary_name(self: Any)
```

Return binary name (e.g. 'claude', 'codex').

---

#### HarnessBase.get_binary_search_paths

```python
get_binary_search_paths(self: Any)
```

Return ordered list of paths to search for binary.

---

#### HarnessBase.get_bypass_flag

```python
get_bypass_flag(self: Any)
```

Return CLI flag for permission bypass (e.g. '--dangerously-skip-permissions').

---

#### HarnessBase.get_env

```python
get_env(self: Any, provider: str, model_override: Optional[str])
```

Get environment variables for this harness pointing to proxy.

---

#### HarnessBase.get_model_alias_map

```python
get_model_alias_map(self: Any)
```

Return model alias -> canonical mapping.

---

#### HarnessBase.install_harness_link

```python
install_harness_link(self: Any, bin_dir: Path, harness: str, force: bool)
```

Install harness symlink to thegent-shims. Returns True if created/updated.

---

#### HarnessBase.resolve_provider_for_model

```python
resolve_provider_for_model(self: Any, model_alias: str)
```

Resolve provider for model-first routing.

---

#### HarnessBase.run_exec

```python
run_exec(self: Any, prompt: str)
```

Run in headless mode (print response and exit).

---

#### HarnessBase.run_interactive

```python
run_interactive(self: Any, provider: str, extra_args: Optional[list[str]], model_override: Optional[str])
```

Start interactive session. Uses os.execvpe (replaces current process).

---

---

## ensure_binary_installed

```python
ensure_binary_installed(self: Any, suggest_alt: bool, require_native: bool)
```

Auto-install binary via brew/bun/etc. or raise. Returns path.

---

## ensure_config_isolation

```python
ensure_config_isolation(self: Any, config_dir: Path)
```

Ensure isolated config directory (subclasses override as needed).

---

## ensure_proxy_running

```python
ensure_proxy_running(self: Any)
```

Ensure cliproxy is running (subclasses override as needed).

---

## fetch_metrics

```python
fetch_metrics(self: Any)
```

Fetch provider metrics for GLM/etc routing. Default: empty.

---

## find_binary

```python
find_binary(self: Any, require_native: bool)
```

Discover binary path. Can be overridden by subclass.

---

## get_binary_name

```python
get_binary_name(self: Any)
```

Return binary name (e.g. 'claude', 'codex').

---

## get_binary_search_paths

```python
get_binary_search_paths(self: Any)
```

Return ordered list of paths to search for binary.

---

## get_bypass_flag

```python
get_bypass_flag(self: Any)
```

Return CLI flag for permission bypass (e.g. '--dangerously-skip-permissions').

---

## get_env

```python
get_env(self: Any, provider: str, model_override: Optional[str])
```

Get environment variables for this harness pointing to proxy.

---

## get_model_alias_map

```python
get_model_alias_map(self: Any)
```

Return model alias -> canonical mapping.

---

## install_harness_link

```python
install_harness_link(self: Any, bin_dir: Path, harness: str, force: bool)
```

Install harness symlink to thegent-shims. Returns True if created/updated.

---

## resolve_provider_for_model

```python
resolve_provider_for_model(self: Any, model_alias: str)
```

Resolve provider for model-first routing.

---

## run_exec

```python
run_exec(self: Any, prompt: str)
```

Run in headless mode (print response and exit).

---

## run_interactive

```python
run_interactive(self: Any, provider: str, extra_args: Optional[list[str]], model_override: Optional[str])
```

Start interactive session. Uses os.execvpe (replaces current process).

---

