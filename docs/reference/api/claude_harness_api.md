# claude_harness API Reference

> **Source**: `src/thegent/adapters/claude_harness.py`

Claude-specific harness implementation (inherits from HarnessBase).

---

## ClaudeHarness

Claude Code harness with provider routing and model alias resolution.

**Inherits from**: `HarnessBase`

### Methods

#### ClaudeHarness.ensure_config_isolation

```python
ensure_config_isolation(self: Any, config_dir: Path)
```

Ensure isolated config dir for Claude.

---

#### ClaudeHarness.fetch_metrics

```python
fetch_metrics(self: Any)
```

Fetch provider metrics for GLM policy routing.

---

#### ClaudeHarness.find_binary

```python
find_binary(self: Any, require_native: bool)
```

Find claude binary in standard locations.

---

#### ClaudeHarness.get_binary_name

```python
get_binary_name(self: Any)
```

---

#### ClaudeHarness.get_binary_search_paths

```python
get_binary_search_paths(self: Any)
```

Return search paths for claude binary.

---

#### ClaudeHarness.get_bypass_flag

```python
get_bypass_flag(self: Any)
```

---

#### ClaudeHarness.get_env

```python
get_env(self: Any, provider: str, model_override: Optional[str])
```

Get environment for Claude Code pointing to thegent proxy.

---

#### ClaudeHarness.get_model_alias_map

```python
get_model_alias_map(self: Any)
```

Return Claude model alias mapping.

---

#### ClaudeHarness.resolve_provider_for_model

```python
resolve_provider_for_model(self: Any, model_alias: str)
```

Resolve provider for model-first routing with round-robin.

---

---

## ensure_config_isolation

```python
ensure_config_isolation(self: Any, config_dir: Path)
```

Ensure isolated config dir for Claude.

---

## fetch_metrics

```python
fetch_metrics(self: Any)
```

Fetch provider metrics for GLM policy routing.

---

## find_binary

```python
find_binary(self: Any, require_native: bool)
```

Find claude binary in standard locations.

---

## get_binary_name

```python
get_binary_name(self: Any) -> str
```

---

## get_binary_search_paths

```python
get_binary_search_paths(self: Any)
```

Return search paths for claude binary.

---

## get_bypass_flag

```python
get_bypass_flag(self: Any) -> str
```

---

## get_env

```python
get_env(self: Any, provider: str, model_override: Optional[str])
```

Get environment for Claude Code pointing to thegent proxy.

---

## get_model_alias_map

```python
get_model_alias_map(self: Any)
```

Return Claude model alias mapping.

---

## resolve_provider_for_model

```python
resolve_provider_for_model(self: Any, model_alias: str)
```

Resolve provider for model-first routing with round-robin.

---

