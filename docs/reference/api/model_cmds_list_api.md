# model_cmds_list API Reference

> **Source**: `src/thegent/cli/commands/model_cmds_list.py`

Thegent CLI model/agent commands domain - extracted from cli.py (WL-124).

---

## cost_values_cmd

```python
cost_values_cmd(format: Any)
```

Show cost values ($/1k tokens) for all model-provider pairs.

Uses CLIProxyAPIPlus metrics when reachable; falls back to static values.

---

## list_agents_cmd

List available agents.

---

## list_droids_cmd

```python
list_droids_cmd(cd: Any)
```

List available droids.

---

## list_models_cmd

```python
list_models_cmd(provider: Any, by_model: bool, refresh: bool, include_contract: bool)
```

List available models (scraped from CLIs/config).

---

## metrics_cmd

```python
metrics_cmd(format: Any, no_cache: bool, limit: int)
```

Show cost, speed, and quality indices for all model-provider pairs (unified view).

---

## quality_index_cmd

```python
quality_index_cmd(format: Any, no_cache: bool)
```

Show quality index (0-1) for all models.

Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
falls back to Route.accuracy_score.

---

## resolve_model_route_cmd

```python
resolve_model_route_cmd(model: str, provider: Any, policy: str, quality_floor: float, lane: Any)
```

Resolve a model to a preferred route and emit contract-style output.

---

## speed_index_cmd

```python
speed_index_cmd(format: Any, no_cache: bool)
```

Show speed index (0-1, higher=faster) for all model-provider pairs.

Uses CLIProxyAPIPlus metrics (tps_1m, latency_p50_ms, success_rate) when reachable;
falls back to Route.latency_ms.

---

